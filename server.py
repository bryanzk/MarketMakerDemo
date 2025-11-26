import os
import threading
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import the bot engine class
from alphaloop.main import AlphaLoop
from alphaloop.portfolio.manager import PortfolioManager, StrategyStatus
from alphaloop.strategies.funding import FundingRateStrategy
from alphaloop.strategies.strategy import FixedSpreadStrategy

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    """Initialize portfolio capital from Binance on server startup."""
    init_portfolio_capital()


# Setup Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Global Bot Instance
bot_engine = AlphaLoop()
bot_thread = None
is_running = False

# Portfolio Manager for multi-strategy management
# Initial capital will be fetched from Binance on startup
portfolio_manager = PortfolioManager(total_capital=10000.0)  # Default fallback

# Store initial capital for reference
initial_capital = 10000.0


def init_portfolio_capital():
    """
    Initialize portfolio capital from Binance Demo Trading account.
    Fetches actual USDT balance and stores it as the initial capital.
    """
    global initial_capital

    try:
        # Fetch actual balance from Binance
        if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
            account_data = bot_engine.exchange.fetch_account_data()
            if account_data and "balance" in account_data:
                actual_balance = account_data["balance"]
                if actual_balance > 0:
                    initial_capital = actual_balance
                    portfolio_manager.total_capital = actual_balance
                    print(
                        f"✅ Portfolio capital initialized from Binance: ${actual_balance:.2f} USDT"
                    )
                    return actual_balance
    except Exception as e:
        print(f"⚠️ Failed to fetch balance from Binance: {e}")
        print(f"   Using default capital: ${initial_capital:.2f} USDT")

    return initial_capital


# Register available strategies
portfolio_manager.register_strategy(
    strategy_id="fixed_spread",
    name="Fixed Spread",
    allocation=0.6,
    status=StrategyStatus.STOPPED,
)
portfolio_manager.register_strategy(
    strategy_id="funding_rate",
    name="Funding Rate",
    allocation=0.4,
    status=StrategyStatus.STOPPED,
)

# Initialize capital on module load (will be called when server starts)
# Note: This runs synchronously during import, so exchange might not be ready yet.
# We'll also refresh it in the first API call.


class ConfigUpdate(BaseModel):
    spread: float
    quantity: float
    strategy_type: str = "fixed_spread"
    skew_factor: float = 100.0


class PairUpdate(BaseModel):
    symbol: str


def run_bot_loop():
    global is_running
    while is_running:
        bot_engine.run_cycle()
        time.sleep(1)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    # Clear any stale alerts on page load
    bot_engine.alert = None
    # 页面刷新时也重置即时错误提示，避免过期错误面板一直显示
    if hasattr(bot_engine, "exchange") and hasattr(
        bot_engine.exchange, "last_order_error"
    ):
        bot_engine.exchange.last_order_error = None
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/debug/balance")
async def debug_balance():
    """Debug endpoint to check raw balance values from exchange"""
    result = {
        "exchange_connected": False,
        "raw_account_data": None,
        "error": None,
    }

    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        result["exchange_connected"] = True
        try:
            account_data = bot_engine.exchange.fetch_account_data()
            result["raw_account_data"] = account_data
        except Exception as e:
            result["error"] = str(e)

    return result


@app.get("/api/status")
async def get_status():
    status = bot_engine.get_status()
    status["active"] = is_running
    status["stage"] = bot_engine.current_stage

    # Add strategy info & core config for UI display
    strategy_type_name = type(bot_engine.strategy).__name__
    status["strategy_type"] = (
        "funding_rate"
        if strategy_type_name == "FundingRateStrategy"
        else "fixed_spread"
    )

    # Expose current spread, quantity, leverage from engine strategy when they are simple numeric types.
    spread = getattr(bot_engine.strategy, "spread", None)
    quantity = getattr(bot_engine.strategy, "quantity", None)
    leverage = getattr(bot_engine.strategy, "leverage", None)
    if isinstance(spread, (int, float)):
        status["spread"] = spread
    if isinstance(quantity, (int, float)):
        status["quantity"] = quantity
    if isinstance(leverage, (int, float)):
        status["leverage"] = leverage

    # Only add skew_factor for funding strategies and when it's numeric
    skew = getattr(bot_engine.strategy, "skew_factor", None)
    if isinstance(skew, (int, float)):
        status["skew_factor"] = skew

    return status


@app.post("/api/control")
async def control_bot(action: str):
    global is_running, bot_thread

    if action == "start":
        if not is_running:
            # Validate current config before starting
            current_spread = bot_engine.strategy.spread

            approved, reason = bot_engine.risk.validate_proposal(
                {"spread": current_spread}
            )

            if not approved:
                # Generate 3 suggestions
                min_spread = bot_engine.risk.risk_limits["MIN_SPREAD"]
                max_spread = bot_engine.risk.risk_limits["MAX_SPREAD"]

                suggestions = [
                    {
                        "label": "Conservative",
                        "spread": round(max_spread * 0.9, 4),  # 90% of max allowed
                        "desc": "Safe choice",
                    },
                    {
                        "label": "Balanced",
                        "spread": round((min_spread + max_spread) / 2, 4),  # Midpoint
                        "desc": "Middle ground",
                    },
                    {
                        "label": "Boundary",
                        "spread": (
                            round(max_spread * 0.99, 4)
                            if current_spread > max_spread
                            else round(min_spread * 1.01, 4)
                        ),
                        "desc": "Limit edge",
                    },
                ]

                # Set alert so it shows up in status polling
                bot_engine.alert = {
                    "type": "warning",
                    "message": f"Risk Rejection: {reason}",
                    "suggestion": "Select a compliant setting below:",
                    "options": suggestions,
                }

                # Return error with suggestions
                return {
                    "error": f"Risk Rejection: {reason}",
                    "suggestions": suggestions,
                }

            # Risk check passed - clear any previous alerts / order errors and start bot
            bot_engine.alert = None
            # 清理最近一次下单错误，让前端错误提示在重新启动后立即消失
            if hasattr(bot_engine, "exchange") and hasattr(
                bot_engine.exchange, "last_order_error"
            ):
                bot_engine.exchange.last_order_error = None
            is_running = True
            bot_thread = threading.Thread(target=run_bot_loop)
            bot_thread.daemon = True
            bot_thread.start()

        return {"status": "started"}
    elif action == "stop":
        is_running = False
        bot_engine.alert = None  # Clear alerts on stop
        bot_engine.current_stage = "Idle"
        return {"status": "stopped"}
    return {"error": "Invalid action"}


@app.post("/api/config")
async def update_config(config: ConfigUpdate):
    # Convert spread from percentage (e.g., 0.005%) to decimal (0.00005)
    new_spread = config.spread / 100

    # 1. Validate with Risk Agent FIRST
    proposal = {
        "spread": new_spread,
        "skew_factor": (
            config.skew_factor if config.strategy_type == "funding_rate" else None
        ),
    }
    approved, reason = bot_engine.risk.validate_proposal(proposal)

    if not approved:
        return {"error": f"Risk Rejection: {reason}"}

    # 2. Apply if approved

    # Check if strategy type changed
    current_strategy_type = (
        "funding_rate"
        if isinstance(bot_engine.strategy, FundingRateStrategy)
        else "fixed_spread"
    )
    if config.strategy_type != current_strategy_type:
        success = bot_engine.set_strategy(config.strategy_type)
        if not success:
            return {"error": f"Failed to switch strategy to {config.strategy_type}"}

    # Update parameters
    bot_engine.strategy.spread = new_spread
    bot_engine.strategy.quantity = config.quantity

    # Update skew factor if applicable
    if hasattr(bot_engine.strategy, "skew_factor"):
        bot_engine.strategy.skew_factor = config.skew_factor

    # Clear any existing alerts / order errors since we fixed the config
    bot_engine.alert = None
    if hasattr(bot_engine, "exchange") and hasattr(
        bot_engine.exchange, "last_order_error"
    ):
        bot_engine.exchange.last_order_error = None

    return {"status": "updated", "config": config}


@app.post("/api/leverage")
async def update_leverage(leverage: int):
    if leverage < 1 or leverage > 125:
        return {"error": "Leverage must be between 1 and 125"}

    success = bot_engine.exchange.set_leverage(leverage)
    if success:
        return {"status": "updated", "leverage": leverage}
    else:
        return {"error": "Failed to update leverage on exchange"}


@app.post("/api/pair")
async def update_pair(pair: PairUpdate):
    success = bot_engine.set_symbol(pair.symbol)
    if success:
        # Immediately refresh data so UI gets updated even if bot is stopped
        bot_engine.refresh_data()
        return {"status": "updated", "symbol": pair.symbol}
    else:
        return {
            "status": "error",
            "message": f"Failed to update to symbol {pair.symbol}",
        }


@app.get("/api/suggestions")
async def get_suggestions():
    # Get metrics from DataAgent
    metrics = bot_engine.data.calculate_metrics()
    sharpe = metrics.get("sharpe_ratio", 0)

    # Get current config
    current_spread = (
        bot_engine.strategy.spread * 100
    )  # Convert back to percentage for display
    current_leverage = bot_engine.strategy.leverage  # Assuming strategy has leverage

    # Risk-aware suggestions
    suggestion = {
        "spread": current_spread,
        "leverage": current_leverage,
        "condition": "Stable",
        "reason": "Current settings are stable.",
    }

    # Check for high volatility
    volatility = metrics.get("volatility", 0)
    if volatility > 0.005:  # Example threshold for high volatility
        suggestion["spread"] = round(current_spread * 1.2, 2)  # Widen spread by 20%
        suggestion["leverage"] = max(1, current_leverage - 2)  # Reduce leverage
        suggestion["condition"] = "High Volatility"
        suggestion["reason"] = (
            "Market is volatile. Widening spread and reducing leverage to mitigate risk."
        )

    # Check for low Sharpe Ratio
    if (
        sharpe < 1.0 and volatility < 0.005
    ):  # Only suggest if not already adjusting for volatility
        suggestion["spread"] = round(current_spread * 1.1, 2)  # Slightly widen spread
        suggestion["leverage"] = max(
            1, current_leverage - 1
        )  # Slightly reduce leverage
        suggestion["condition"] = "Low Sharpe Ratio"
        suggestion["reason"] = (
            "Performance is low. Adjusting spread and leverage to improve risk-adjusted returns."
        )

    # Check for high PnL and low risk
    if sharpe > 2.0 and volatility < 0.002:  # Example for good performance
        suggestion["spread"] = round(current_spread * 0.9, 2)  # Tighten spread
        suggestion["leverage"] = current_leverage + 1  # Increase leverage
        suggestion["condition"] = "Excellent Performance"
        suggestion["reason"] = (
            "Strong performance with low risk. Optimizing for higher returns."
        )

    # Ensure spread is within reasonable bounds (e.g., 0.01% to 1%)
    suggestion["spread"] = max(0.01, min(1.0, suggestion["spread"]))
    # Ensure leverage is within reasonable bounds (e.g., 1 to 10)
    suggestion["leverage"] = max(1, min(10, suggestion["leverage"]))

    return suggestion


@app.get("/api/order-history")
async def get_order_history(
    symbol: str = None,
    status: str = None,
    from_time: float = None,
    to_time: float = None,
    strategy_type: str = None,
):
    """
    Get order history with optional filters
    :param symbol: Filter by symbol (e.g., 'ETH/USDT:USDT')
    :param status: Filter by status ('placed', 'cancelled', 'filled')
    :param from_time: Filter by start timestamp
    :param to_time: Filter by end timestamp
    :param strategy_type: Filter by strategy type ('fixed_spread', 'funding_rate')
    """
    history = list(bot_engine.order_history)

    # Apply filters
    if symbol:
        history = [o for o in history if o["symbol"] == symbol]
    if status:
        history = [o for o in history if o["status"] == status]
    if from_time:
        history = [o for o in history if o["timestamp"] >= from_time]
    if to_time:
        history = [o for o in history if o["timestamp"] <= to_time]
    if strategy_type:
        history = [o for o in history if o.get("strategy_type") == strategy_type]

    # Sort by timestamp descending (newest first)
    history.sort(key=lambda x: x["timestamp"], reverse=True)

    return history


@app.get("/api/error-history")
async def get_error_history(
    symbol: str = None,
    error_type: str = None,
    strategy_type: str = None,
    from_time: float = None,
    to_time: float = None,
):
    """
    Get error history with optional filters.
    :param symbol: Filter by symbol (e.g., 'ETH/USDT:USDT')
    :param error_type: Filter by error type (e.g., 'invalid_price', 'invalid_quantity')
    :param strategy_type: Filter by strategy type ('fixed_spread', 'funding_rate')
    :param from_time: Filter by start timestamp (seconds since epoch)
    :param to_time: Filter by end timestamp (seconds since epoch)
    """
    # AlphaLoop maintains a deque error_history; fall back to empty list if not present.
    history = list(getattr(bot_engine, "error_history", []))

    if symbol:
        history = [e for e in history if e.get("symbol") == symbol]
    if error_type:
        history = [e for e in history if e.get("type") == error_type]
    if strategy_type:
        history = [e for e in history if e.get("strategy_type") == strategy_type]
    if from_time:
        history = [e for e in history if e.get("timestamp", 0) >= from_time]
    if to_time:
        history = [e for e in history if e.get("timestamp", 0) <= to_time]

    # Sort newest first
    history.sort(key=lambda x: x.get("timestamp", 0), reverse=True)

    return history


@app.get("/api/performance")
async def get_performance():
    # Get metrics from DataAgent
    metrics = bot_engine.data.calculate_metrics()

    # Calculate additional stats from trade history
    trades = bot_engine.data.trade_history
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t["pnl"] > 0])
    losing_trades = len([t for t in trades if t["pnl"] <= 0])

    realized_pnl = sum(t["pnl"] for t in trades)

    # Fetch commission/fees from exchange if available
    commission = 0.0
    net_pnl = realized_pnl
    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        try:
            pnl_data = bot_engine.exchange.fetch_pnl_and_fees()
            commission = pnl_data.get("commission", 0.0)
            # Use exchange's realized PnL if available, otherwise use local calculation
            if pnl_data.get("realized_pnl", 0) != 0:
                realized_pnl = pnl_data["realized_pnl"]
                net_pnl = pnl_data["net_pnl"]
            else:
                net_pnl = realized_pnl - commission
        except Exception:
            # Fallback to local calculation if exchange call fails
            pass

    # Construct PnL history for chart
    pnl_history = []
    cumulative_pnl = 0
    # Add initial point
    if trades:
        pnl_history.append([trades[0]["timestamp"] * 1000 - 1000, 0])

    for t in trades:
        cumulative_pnl += t["pnl"]
        pnl_history.append([t["timestamp"] * 1000, cumulative_pnl])

    return {
        "realized_pnl": realized_pnl,
        "commission": commission,
        "net_pnl": net_pnl,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": (winning_trades / total_trades * 100) if total_trades > 0 else 0,
        "metrics": metrics,
        "pnl_history": pnl_history,
    }


@app.get("/api/funding-rates")
async def get_funding_rates():
    """
    Get funding rates for all supported trading pairs, sorted by absolute value.
    This helps identify the best pairs for funding rate arbitrage strategies.
    """
    # Define supported symbols
    symbols = [
        "BTC/USDT:USDT",
        "ETH/USDT:USDT",
        "SOL/USDT:USDT",
        "DOGE/USDT:USDT",
        "1000SHIB/USDT:USDT",
        "1000PEPE/USDT:USDT",
        "WIF/USDT:USDT",
        "1000FLOKI/USDT:USDT",
    ]

    try:
        # Check if exchange is available
        if not hasattr(bot_engine, "exchange") or bot_engine.exchange is None:
            return {"error": "Exchange not available"}

        # Fetch bulk funding rates
        funding_rates = bot_engine.exchange.fetch_bulk_funding_rates(symbols)

        # Build response with metadata
        result = []
        for symbol, rate in funding_rates.items():
            # Determine trading direction preference
            if rate > 0.0001:  # Positive funding rate (> 0.01%)
                direction = "short_favored"  # Shorts receive funding
            elif rate < -0.0001:  # Negative funding rate (< -0.01%)
                direction = "long_favored"  # Longs receive funding
            else:
                direction = "neutral"

            result.append(
                {
                    "symbol": symbol,
                    "funding_rate": rate,
                    "daily_yield": rate * 3,  # 3 funding periods per day
                    "direction": direction,
                    "abs_rate": abs(rate),  # For sorting
                }
            )

        # Sort by absolute funding rate (highest arbitrage opportunity first)
        result.sort(key=lambda x: x["abs_rate"], reverse=True)

        # Remove abs_rate from response (used only for sorting)
        for item in result:
            del item["abs_rate"]

        return result

    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Portfolio Management APIs (US-1.x, US-2.x)
# ============================================================================


@app.get("/api/portfolio")
async def get_portfolio():
    """
    获取组合概览和策略对比数据

    对应用户故事: US-1.1 ~ US-1.4, US-2.1 ~ US-2.5
    参考文档: docs/user_guide/portfolio_management.md

    Returns:
        {
            "total_pnl": float,           # 组合总盈亏
            "commission": float,          # 已缴纳交易费
            "net_pnl": float,             # 净盈亏 (扣除费用后)
            "portfolio_sharpe": float,    # 组合夏普比率
            "active_count": int,          # 活跃策略数
            "total_count": int,           # 总策略数
            "risk_level": str,            # 风险等级 (low/medium/high/critical)
            "total_capital": float,       # 总资金
            "strategies": [               # 策略列表 (按 PnL 降序)
                {
                    "id": str,
                    "name": str,
                    "status": str,        # live/paper/paused/stopped
                    "pnl": float,
                    "sharpe": float,
                    "health": int,        # 0-100
                    "allocation": float,  # 0-1
                    "roi": float,
                }
            ]
        }
    """
    # Sync strategy status with bot state
    _sync_portfolio_with_bot()

    # Get base portfolio data
    data = portfolio_manager.get_portfolio_data()

    # Fetch commission, wallet_balance and available_balance from exchange
    commission = 0.0
    wallet_balance = data.get("total_capital", 0.0)
    available_balance = wallet_balance
    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        try:
            pnl_data = bot_engine.exchange.fetch_pnl_and_fees()
            commission = pnl_data.get("commission", 0.0)
        except Exception:
            pass

        try:
            account_data = bot_engine.exchange.fetch_account_data()
            if account_data:
                # Get real-time balances from exchange
                wallet_balance = account_data.get("balance", wallet_balance)
                available_balance = account_data.get(
                    "available_balance", available_balance
                )
        except Exception:
            pass

    # Add commission, net_pnl, wallet and available_balance to response
    data["commission"] = round(commission, 4)
    data["net_pnl"] = round(data["total_pnl"] - commission, 4)
    data["total_capital"] = round(
        wallet_balance, 2
    )  # Override with real-time wallet balance
    data["available_balance"] = round(available_balance, 2)

    return data


@app.post("/api/strategy/{strategy_id}/pause")
async def pause_strategy(strategy_id: str):
    """
    暂停指定策略

    对应用户故事: US-2.6
    """
    success = portfolio_manager.pause_strategy(strategy_id)
    if not success:
        return {"error": f"Strategy '{strategy_id}' not found"}

    # If this is the active strategy, stop the bot
    if is_running:
        current_strategy = type(bot_engine.strategy).__name__
        if (
            strategy_id == "fixed_spread" and current_strategy == "FixedSpreadStrategy"
        ) or (
            strategy_id == "funding_rate" and current_strategy == "FundingRateStrategy"
        ):
            # Optionally stop the bot when its strategy is paused
            pass  # For now, just update status without stopping

    return {"status": "paused", "strategy_id": strategy_id}


@app.post("/api/strategy/{strategy_id}/resume")
async def resume_strategy(strategy_id: str):
    """
    恢复暂停的策略

    对应用户故事: US-2.6
    """
    success = portfolio_manager.resume_strategy(strategy_id)
    if not success:
        return {"error": f"Strategy '{strategy_id}' not found"}

    return {"status": "live", "strategy_id": strategy_id}


def _sync_portfolio_with_bot():
    """
    同步 PortfolioManager 与当前 bot 状态

    将 bot_engine 的实时数据同步到 portfolio_manager
    """
    global is_running, initial_capital

    # Update capital from current balance if available
    try:
        if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
            account_data = bot_engine.exchange.fetch_account_data()
            if account_data and "balance" in account_data:
                current_balance = account_data["balance"]
                if current_balance > 0:
                    # Update total capital to reflect current account value
                    # (initial capital + realized PnL)
                    portfolio_manager.total_capital = current_balance
    except Exception:
        pass  # Keep existing capital if fetch fails

    # Determine current active strategy
    current_strategy_type = type(bot_engine.strategy).__name__
    current_strategy_id = (
        "funding_rate"
        if current_strategy_type == "FundingRateStrategy"
        else "fixed_spread"
    )

    # Update strategy statuses based on bot running state
    for strategy_id, strategy in portfolio_manager.strategies.items():
        if is_running and strategy_id == current_strategy_id:
            if strategy.status != StrategyStatus.PAUSED:
                strategy.status = StrategyStatus.LIVE
        elif strategy.status == StrategyStatus.LIVE:
            strategy.status = StrategyStatus.STOPPED

    # Get performance data
    trades = bot_engine.data.trade_history
    realized_pnl = sum(t["pnl"] for t in trades)

    # Get metrics
    metrics = bot_engine.data.calculate_metrics()
    sharpe = metrics.get("sharpe_ratio", 0)
    fill_rate = metrics.get("fill_rate", 0.85)
    slippage = metrics.get("slippage_bps", 0)

    # Calculate max drawdown from PnL history
    max_drawdown = 0.0
    if trades:
        cumulative = 0
        peak = 0
        for t in trades:
            cumulative += t["pnl"]
            if cumulative > peak:
                peak = cumulative
            if peak > 0:
                dd = (peak - cumulative) / peak
                if dd > max_drawdown:
                    max_drawdown = dd

    # Update the currently active strategy's metrics
    portfolio_manager.update_strategy_metrics(
        strategy_id=current_strategy_id,
        pnl=realized_pnl,
        sharpe=sharpe if sharpe else None,
        fill_rate=fill_rate if fill_rate else 0.85,
        slippage=slippage if slippage else 0,
        max_drawdown=max_drawdown,
        total_trades=len(trades),
    )

    # Record PnL snapshot for portfolio Sharpe calculation
    portfolio_manager.record_pnl_snapshot()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
