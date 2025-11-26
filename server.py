import os
import threading
import time
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import the bot engine class
from alphaloop.main import AlphaLoop
from alphaloop.portfolio.manager import PortfolioManager, StrategyStatus
from alphaloop.portfolio.risk import RiskIndicators
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

# Session start time for PnL calculation (default: today 9:00 AM UTC+8)
# This can be updated via API
session_start_time_ms: int = None


def get_today_9am_timestamp_ms() -> int:
    """
    Get today's 9:00 AM timestamp in milliseconds (UTC+8 Beijing time).

    Returns:
        int: Timestamp in milliseconds
    """
    from datetime import timedelta

    # Get current time in UTC
    now_utc = datetime.now(timezone.utc)

    # Convert to UTC+8 (Beijing time)
    utc_plus_8 = timezone(timedelta(hours=8))
    now_beijing = now_utc.astimezone(utc_plus_8)

    # Get today's 9:00 AM in Beijing time
    today_9am_beijing = now_beijing.replace(hour=9, minute=0, second=0, microsecond=0)

    # If current time is before 9:00 AM, use yesterday's 9:00 AM
    if now_beijing < today_9am_beijing:
        today_9am_beijing = today_9am_beijing - timedelta(days=1)

    # Convert to UTC then to milliseconds timestamp
    today_9am_utc = today_9am_beijing.astimezone(timezone.utc)
    return int(today_9am_utc.timestamp() * 1000)


def get_session_start_time_ms() -> int:
    """
    Get the session start time for PnL calculation.
    If not set, defaults to today's 9:00 AM (UTC+8).

    Returns:
        int: Timestamp in milliseconds
    """
    global session_start_time_ms
    if session_start_time_ms is None:
        session_start_time_ms = get_today_9am_timestamp_ms()
    return session_start_time_ms


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


class SessionStartUpdate(BaseModel):
    """Model for updating session start time"""

    timestamp_ms: int = None  # Timestamp in milliseconds
    reset_to_9am: bool = False  # If True, reset to today's 9:00 AM


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
    """
    Get performance data starting from session start time (default: today 9:00 AM UTC+8).

    All PnL and commission data is fetched from Binance starting from the session start time.
    """
    # Get session start time for filtering
    start_time_ms = get_session_start_time_ms()

    # Get metrics from DataAgent
    metrics = bot_engine.data.calculate_metrics()

    # Calculate additional stats from trade history (filter by start time)
    trades = bot_engine.data.trade_history
    # Filter trades that happened after session start
    start_time_sec = start_time_ms / 1000
    filtered_trades = [t for t in trades if t.get("timestamp", 0) >= start_time_sec]

    total_trades = len(filtered_trades)
    winning_trades = len([t for t in filtered_trades if t["pnl"] > 0])
    losing_trades = len([t for t in filtered_trades if t["pnl"] <= 0])

    realized_pnl = sum(t["pnl"] for t in filtered_trades)

    # Fetch commission/fees from exchange starting from session start time
    commission = 0.0
    net_pnl = realized_pnl
    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        try:
            # Pass start_time to fetch data from session start
            pnl_data = bot_engine.exchange.fetch_pnl_and_fees(start_time=start_time_ms)
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

    # Construct PnL history for chart (only include trades after session start)
    pnl_history = []
    cumulative_pnl = 0
    # Add initial point at session start
    pnl_history.append([start_time_ms, 0])

    for t in filtered_trades:
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
        "session_start_time": start_time_ms,
    }


@app.get("/api/session-start")
async def get_session_start():
    """
    获取当前会话起始时间

    Returns:
        {
            "session_start_time": int,       # 会话起始时间 (ms)
            "session_start_datetime": str,   # ISO 格式的日期时间
            "description": str               # 描述信息
        }
    """
    start_time_ms = get_session_start_time_ms()

    # Convert to ISO datetime string for display
    start_datetime = datetime.fromtimestamp(
        start_time_ms / 1000, tz=timezone.utc
    ).isoformat()

    return {
        "session_start_time": start_time_ms,
        "session_start_datetime": start_datetime,
        "description": "PnL and commission data are calculated from this time onwards",
    }


@app.post("/api/session-start")
async def update_session_start(update: SessionStartUpdate):
    """
    更新会话起始时间

    可以设置自定义时间戳，或重置为今天上午9点。

    Args:
        update: SessionStartUpdate with either:
            - timestamp_ms: Custom timestamp in milliseconds
            - reset_to_9am: If True, reset to today's 9:00 AM (UTC+8)

    Returns:
        {
            "status": "updated",
            "session_start_time": int,
            "session_start_datetime": str
        }
    """
    global session_start_time_ms

    if update.reset_to_9am:
        session_start_time_ms = get_today_9am_timestamp_ms()
    elif update.timestamp_ms is not None:
        session_start_time_ms = update.timestamp_ms
    else:
        return {"error": "Please provide either timestamp_ms or set reset_to_9am=true"}

    # Convert to ISO datetime string for display
    start_datetime = datetime.fromtimestamp(
        session_start_time_ms / 1000, tz=timezone.utc
    ).isoformat()

    return {
        "status": "updated",
        "session_start_time": session_start_time_ms,
        "session_start_datetime": start_datetime,
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

    All PnL data is calculated from session start time (default: today 9:00 AM UTC+8).

    对应用户故事: US-1.1 ~ US-1.4, US-2.1 ~ US-2.5
    参考文档: docs/user_guide/portfolio_management.md

    Returns:
        {
            "total_pnl": float,           # 组合总盈亏 (from session start)
            "commission": float,          # 已缴纳交易费 (from session start)
            "net_pnl": float,             # 净盈亏 (扣除费用后)
            "portfolio_sharpe": float,    # 组合夏普比率
            "active_count": int,          # 活跃策略数
            "total_count": int,           # 总策略数
            "risk_level": str,            # 风险等级 (low/medium/high/critical)
            "total_capital": float,       # 总资金
            "session_start_time": int,    # 会话起始时间 (ms)
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
    # Get session start time for filtering
    start_time_ms = get_session_start_time_ms()

    # Sync strategy status with bot state
    _sync_portfolio_with_bot()

    # Get base portfolio data
    data = portfolio_manager.get_portfolio_data()

    # Fetch commission, wallet_balance and available_balance from exchange
    # Use session start time for PnL and commission calculation
    commission = 0.0
    realized_pnl = 0.0
    wallet_balance = data.get("total_capital", 0.0)
    available_balance = wallet_balance

    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        try:
            # Fetch PnL and commission from session start time
            pnl_data = bot_engine.exchange.fetch_pnl_and_fees(start_time=start_time_ms)
            commission = pnl_data.get("commission", 0.0)
            realized_pnl = pnl_data.get("realized_pnl", 0.0)
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

    # Override total_pnl with exchange's realized PnL from session start
    if realized_pnl != 0:
        data["total_pnl"] = round(realized_pnl, 4)

    # Add commission, net_pnl, wallet and available_balance to response
    data["commission"] = round(commission, 4)
    data["net_pnl"] = round(data["total_pnl"] - commission, 4)
    data["total_capital"] = round(
        wallet_balance, 2
    )  # Override with real-time wallet balance
    data["available_balance"] = round(available_balance, 2)
    data["session_start_time"] = start_time_ms

    return data


@app.get("/api/risk-indicators")
async def get_risk_indicators():
    """
    获取风险指标数据

    返回:
    - liquidation_buffer: 强平缓冲百分比
    - inventory_drift: 库存偏移百分比
    - max_drawdown: 最大回撤百分比
    - overall_risk_level: 综合风险等级

    对应用户故事: US-R1, US-R2, US-R3, US-R4, US-R5
    """
    # Get current price and position data from exchange
    current_price = 0.0
    position_amt = 0.0
    liquidation_price = 0.0
    max_position = 1.0  # Default max position

    if hasattr(bot_engine, "exchange") and bot_engine.exchange is not None:
        try:
            # Fetch market data for current price
            market_data = bot_engine.exchange.fetch_market_data()
            if market_data:
                current_price = market_data.get("mid_price", 0.0)

            # Fetch account data for position and liquidation price
            account_data = bot_engine.exchange.fetch_account_data()
            if account_data:
                position_amt = account_data.get("position_amt", 0.0)
                # Get liquidation price from position info
                liquidation_price = account_data.get("liquidation_price", 0.0)

            # Get max position from strategy config
            if hasattr(bot_engine, "strategy") and bot_engine.strategy:
                max_position = getattr(bot_engine.strategy, "quantity", 1.0) * 10
        except Exception as e:
            print(f"Error fetching exchange data for risk indicators: {e}")

    # Build PnL history from trade history
    pnl_history = [0.0]  # Start with 0
    cumulative_pnl = 0.0
    for trade in bot_engine.data.trade_history:
        cumulative_pnl += trade.get("pnl", 0.0)
        pnl_history.append(cumulative_pnl)

    # Calculate risk indicators
    indicators = RiskIndicators.from_exchange_data(
        current_price=current_price,
        position_amt=position_amt,
        liquidation_price=liquidation_price,
        max_position=max_position,
        pnl_history=pnl_history
    )

    return indicators


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
