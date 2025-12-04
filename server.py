import logging
import os
import threading
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional

import uvicorn

logger = logging.getLogger(__name__)
from fastapi import FastAPI, Query, Request, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Import the bot engine class
from src.trading.engine import AlphaLoop
from src.portfolio.manager import PortfolioManager, StrategyStatus
from src.portfolio.risk import RiskIndicators
from src.trading.strategies.funding_rate import FundingRateStrategy
from src.trading.strategies.fixed_spread import FixedSpreadStrategy

# Import evaluation modules
from src.ai.evaluation.evaluator import MultiLLMEvaluator
from src.ai.evaluation.schemas import MarketContext
from src.ai import create_all_providers

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application.
    Handles startup and shutdown events.
    FastAPI 应用程序的生命周期事件处理器。
    处理启动和关闭事件。
    """
    # Startup / 启动
    init_portfolio_capital()
    yield
    # Shutdown (if needed in the future) / 关闭（如果将来需要）
    pass


app = FastAPI(lifespan=lifespan)


# Setup Templates
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Global Bot Instance
bot_engine = AlphaLoop()
bot_thread = None
is_running = False


def get_default_exchange():
    """
    Get exchange from default strategy instance.
    Returns None if not available.
    """
    default_instance = bot_engine.strategy_instances.get("default")
    if default_instance and default_instance.use_real_exchange:
        return default_instance.exchange
    return None


def get_exchange_by_name(exchange_name: str):
    """
    Get exchange client by name (binance or hyperliquid).
    
    根据名称获取交易所客户端（binance 或 hyperliquid）。
    
    Args:
        exchange_name: "binance" or "hyperliquid"
        
    Returns:
        Exchange client instance or None if not found/connected
    """
    from src.trading.hyperliquid_client import HyperliquidClient
    from src.trading.exchange import BinanceClient
    
    if exchange_name == "hyperliquid":
        # Look for HyperliquidClient in strategy instances
        # 在策略实例中查找 HyperliquidClient
        if hasattr(bot_engine, "strategy_instances") and bot_engine.strategy_instances:
            try:
                for instance in bot_engine.strategy_instances.values():
                    if hasattr(instance, "use_real_exchange") and instance.use_real_exchange:
                        if hasattr(instance, "exchange") and instance.exchange is not None:
                            if isinstance(instance.exchange, HyperliquidClient):
                                if hasattr(instance.exchange, "is_connected") and instance.exchange.is_connected:
                                    return instance.exchange
            except (TypeError, AttributeError):
                # Handle case where bot_engine is a Mock in tests
                # 处理测试中 bot_engine 是 Mock 的情况
                pass
        
        # If not found in instances, try to create a new one
        # 如果在实例中未找到，尝试创建新的
        try:
            hyperliquid_client = HyperliquidClient()
            if hasattr(hyperliquid_client, "is_connected") and hyperliquid_client.is_connected:
                return hyperliquid_client
        except Exception as e:
            logger.debug(f"Failed to create HyperliquidClient: {e}")
        
        return None
    
    elif exchange_name == "binance":
        # For binance, use get_default_exchange which is usually BinanceClient
        # 对于 binance，使用 get_default_exchange，通常是 BinanceClient
        # This maintains compatibility with existing tests and code
        # 这保持了与现有测试和代码的兼容性
        return get_default_exchange()
    
    else:
        # Invalid exchange name, return None
        # 无效的交易所名称，返回 None
        return None


def _validate_exchange_parameter(exchange: str) -> tuple[bool, Optional[dict]]:
    """
    Validate exchange parameter / 验证交易所参数
    
    Args:
        exchange: Exchange name to validate
        
    Returns:
        Tuple of (is_valid, error_response)
        - is_valid: True if valid, False otherwise
        - error_response: Error response dict if invalid, None if valid
    """
    exchange_name = exchange.lower()
    if exchange_name not in ["binance", "hyperliquid"]:
        return False, {
            "error": (
                f"Invalid exchange parameter: {exchange}. "
                f"Must be 'binance' or 'hyperliquid'. "
                f"无效的交易所参数：{exchange}。必须是 'binance' 或 'hyperliquid'。"
            )
        }
    return True, None


def _check_exchange_connection(
    exchange_name: str, exchange: Optional[object], error_format: str = "error"
) -> tuple[bool, Optional[dict], Optional[int]]:
    """
    Check exchange connection status / 检查交易所连接状态
    
    Args:
        exchange_name: Exchange name ("binance" or "hyperliquid")
        exchange: Exchange client instance or None
        error_format: Response format ("error" for run endpoint, "status" for apply endpoint)
        
    Returns:
        Tuple of (is_connected, error_response, status_code)
        - is_connected: True if connected, False otherwise
        - error_response: Error response dict if not connected, None if connected
        - status_code: HTTP status code (503 for service unavailable)
    """
    if exchange is None:
        if exchange_name == "hyperliquid":
            error_msg = (
                "Hyperliquid exchange not connected. "
                "Please connect to Hyperliquid first. / "
                "Hyperliquid 交易所未连接。请先连接到 Hyperliquid。"
            )
            if error_format == "status":
                return False, {"status": "error", "error": error_msg}, 503
            else:
                return False, {"error": error_msg}, 503
        else:
            error_msg = "Exchange not available / 交易所不可用"
            if error_format == "status":
                return False, {"status": "error", "error": error_msg}, None
            else:
                return False, {"error": error_msg}, None
    
    # For Hyperliquid, check is_connected attribute
    # 对于 Hyperliquid，检查 is_connected 属性
    if exchange_name == "hyperliquid":
        from src.trading.hyperliquid_client import HyperliquidClient
        
        if isinstance(exchange, HyperliquidClient) and not exchange.is_connected:
            error_msg = (
                "Hyperliquid exchange not connected. "
                "Please connect to Hyperliquid first. / "
                "Hyperliquid 交易所未连接。请先连接到 Hyperliquid。"
            )
            if error_format == "status":
                return False, {"status": "error", "error": error_msg}, 503
            else:
                return False, {"error": error_msg}, 503
    
    return True, None, None


def _format_symbol_with_exchange(symbol: str, exchange_name: str) -> str:
    """
    Format symbol with exchange name for LLM context / 为 LLM 上下文格式化带交易所名称的交易对
    
    Args:
        symbol: Trading symbol
        exchange_name: Exchange name ("binance" or "hyperliquid")
        
    Returns:
        Formatted symbol string with exchange name
    """
    return f"{symbol} ({exchange_name.upper()})"

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
        # Fetch actual balance from Binance using default strategy instance's exchange
        exchange = get_default_exchange()
        if exchange is not None:
            account_data = exchange.fetch_account_data()
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
    strategy_id: Optional[str] = None
    skew_factor: float = 100.0


class PairUpdate(BaseModel):
    symbol: str
    strategy_id: Optional[str] = "default"


class SessionStartUpdate(BaseModel):
    """Model for updating session start time"""
    timestamp_ms: int = None  # Timestamp in milliseconds
    reset_to_9am: bool = False  # If True, reset to today's 9:00 AM


class RebalanceRequest(BaseModel):
    """Model for rebalancing request"""
    method: str = "composite"  # equal, sharpe, health, roi, composite, risk_adjusted
    weights: dict = None  # For composite method: {"sharpe": 0.4, "roi": 0.3, "health": 0.3}


class AllocationLimitsUpdate(BaseModel):
    """Model for updating allocation limits"""
    min_allocation: float = None
    max_allocation: float = None


class StrategyAllocationUpdate(BaseModel):
    """Model for updating single strategy allocation"""
    allocation: float  # 0-1


class EvaluationRunRequest(BaseModel):
    symbol: str
    simulation_steps: int = 500
    exchange: str = "binance"  # "binance" or "hyperliquid"


class EvaluationApplyRequest(BaseModel):
    source: str  # "consensus" or "individual"
    provider_name: Optional[str] = None
    exchange: str = "binance"  # "binance" or "hyperliquid"


def _get_or_create_strategy_instance(
    desired_id: Optional[str], strategy_type: str
):
    """
    Resolve or create a strategy instance with the requested type.
    """
    if desired_id and desired_id in bot_engine.strategy_instances:
        return bot_engine.strategy_instances[desired_id]

    for instance in bot_engine.strategy_instances.values():
        if instance.strategy_type == strategy_type:
            return instance

    instance_id = desired_id or strategy_type
    # Inherit symbol from default instance if available
    default_instance = bot_engine.strategy_instances.get("default")
    inherited_symbol = default_instance.symbol if default_instance else None
    success = bot_engine.add_strategy_instance(
        instance_id, strategy_type, symbol=inherited_symbol
    )
    if success:
        new_instance = bot_engine.strategy_instances.get(instance_id)
        if new_instance and default_instance and instance_id != "default":
            new_instance.strategy.spread = default_instance.strategy.spread
            new_instance.strategy.quantity = default_instance.strategy.quantity
            new_instance.strategy.leverage = default_instance.strategy.leverage
        return new_instance

    return bot_engine.strategy_instances.get(instance_id)


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
    exchange = get_default_exchange()
    if exchange and hasattr(exchange, "last_order_error"):
        exchange.last_order_error = None
    return templates.TemplateResponse(request, "index.html")


@app.get("/evaluation", response_class=HTMLResponse)
async def llm_trade_page(request: Request):
    """Render dedicated LLM Trade Lab page / 渲染专用 LLM 交易实验室页面"""
    return templates.TemplateResponse(request, "LLMTrade.html")


@app.get("/hyperliquid", response_class=HTMLResponse)
async def hyperliquid_trade_page(request: Request):
    """Render dedicated Hyperliquid Trading page / 渲染专用 Hyperliquid 交易页面"""
    return templates.TemplateResponse(request, "HyperliquidTrade.html")


@app.get("/api/debug/balance")
async def debug_balance():
    """Debug endpoint to check raw balance values from exchange"""
    result = {
        "exchange_connected": False,
        "raw_account_data": None,
        "error": None,
    }

    exchange = get_default_exchange()
    if exchange is not None:
        result["exchange_connected"] = True
        try:
            account_data = exchange.fetch_account_data()
            result["raw_account_data"] = account_data
        except Exception as e:
            result["error"] = str(e)

    return result


@app.get("/api/status")
async def get_status(exchange: Optional[str] = None):
    """
    Get bot status / 获取 Bot 状态
    
    Args:
        exchange: Optional exchange name ("binance" or "hyperliquid"). 
                  If not provided, returns default exchange status.
                  可选的交易所名称（"binance" 或 "hyperliquid"）。
                  如果未提供，返回默认交易所状态。
    """
    # If exchange parameter is provided, get exchange-specific status
    # 如果提供了交易所参数，获取特定交易所的状态
    if exchange and exchange.lower() == "hyperliquid":
        return await get_hyperliquid_status()
    
    # Default behavior: return default exchange status
    # 默认行为：返回默认交易所状态
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

    # Fetch Binance Exchange Limits for current trading pair
    exchange = get_default_exchange()
    if exchange is not None:
        try:
            limits = exchange.get_symbol_limits()
            status["limits"] = limits
        except Exception as e:
            # If limits fetch fails, set empty limits to avoid breaking UI
            status["limits"] = {
                "minQty": None,
                "maxQty": None,
                "stepSize": None,
                "minNotional": None,
            }
            print(f"Error fetching symbol limits: {e}")
    else:
        # No exchange connection, set empty limits
        status["limits"] = {
            "minQty": None,
            "maxQty": None,
            "stepSize": None,
            "minNotional": None,
        }

    # Add strategy instance running states (regardless of exchange connection)
    if hasattr(bot_engine, "strategy_instances"):
        status["strategy_instances_running"] = {
            strategy_id: instance.running 
            for strategy_id, instance in bot_engine.strategy_instances.items()
        }
        # Map strategy names to instance IDs for UI
        status["strategy_instance_status"] = {}
        
        # Initialize both strategy types to False
        status["strategy_instance_status"]["fixed_spread"] = False
        status["strategy_instance_status"]["funding_rate"] = False
        
        # Map instances to their strategy types
        # If multiple instances of the same type exist, use OR logic (if any is running, mark as running)
        for strategy_id, instance in bot_engine.strategy_instances.items():
            if instance.strategy_type == "fixed_spread":
                # If any fixed_spread instance is running, mark fixed_spread as running
                if instance.running:
                    status["strategy_instance_status"]["fixed_spread"] = True
            elif instance.strategy_type == "funding_rate":
                # If any funding_rate instance is running, mark funding_rate as running
                if instance.running:
                    status["strategy_instance_status"]["funding_rate"] = True

    return status


@app.get("/api/hyperliquid/status")
async def get_hyperliquid_status():
    """
    Get Hyperliquid-specific status including positions, balance, and orders
    获取 Hyperliquid 特定状态，包括仓位、余额和订单
    """
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange:
            return {
                "error": "Hyperliquid exchange not connected / Hyperliquid 交易所未连接",
                "connected": False,
                "testnet": False,  # Default to mainnet if not connected
            }
        
        if not exchange.is_connected:
            # Return testnet status even if not connected
            testnet_status = exchange.testnet if hasattr(exchange, "testnet") else False
            return {
                "error": "Hyperliquid exchange not connected / Hyperliquid 交易所未连接",
                "connected": False,
                "testnet": testnet_status,
            }
        
        # Fetch account data
        account_data = exchange.fetch_account_data()
        market_data = exchange.fetch_market_data()
        
        # Fetch positions
        positions = []
        try:
            positions = exchange.fetch_positions() or []
        except Exception as e:
            logger.warning(f"Failed to fetch positions: {e}")
        
        # Fetch open orders
        orders = []
        try:
            orders = exchange.fetch_open_orders() or []
        except Exception as e:
            logger.warning(f"Failed to fetch orders: {e}")
        
        # Build status response
        status = {
            "connected": True,
            "exchange": "hyperliquid",
            "testnet": exchange.testnet if hasattr(exchange, "testnet") else False,
            "symbol": exchange.symbol if hasattr(exchange, "symbol") else None,
            "mid_price": market_data.get("mid_price", 0.0) if market_data else 0.0,
            "balance": account_data.get("balance", 0.0) if account_data else 0.0,
            "available_balance": account_data.get("available_balance", 0.0) if account_data else 0.0,
            "position": account_data.get("position_amt", 0.0) if account_data else 0.0,
            "unrealized_pnl": account_data.get("unrealized_pnl", 0.0) if account_data else 0.0,
            "leverage": account_data.get("leverage", 1) if account_data else 1,
            "positions": positions,
            "orders": orders,
        }
        
        return status
    except Exception as e:
        logger.error(f"Error getting Hyperliquid status: {e}")
        return {
            "error": f"Failed to get Hyperliquid status: {str(e)} / 获取 Hyperliquid 状态失败：{str(e)}",
            "connected": False,
        }


@app.post("/api/hyperliquid/cancel-order")
async def cancel_hyperliquid_order(order_id: str = Body(..., embed=True)):
    """
    Cancel a Hyperliquid order / 取消 Hyperliquid 订单
    
    Args:
        order_id: Order ID to cancel
    """
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange or not exchange.is_connected:
            return {
                "error": "Hyperliquid exchange not connected / Hyperliquid 交易所未连接"
            }
        
        # Cancel the order
        exchange.cancel_orders([order_id])
        
        return {
            "status": "success",
            "message": f"Order {order_id} canceled / 订单 {order_id} 已取消",
            "order_id": order_id,
        }
    except Exception as e:
        logger.error(f"Error canceling Hyperliquid order: {e}")
        return {
            "error": f"Failed to cancel order: {str(e)} / 取消订单失败：{str(e)}"
        }


@app.post("/api/hyperliquid/config")
async def update_hyperliquid_config(config: ConfigUpdate):
    """
    Update Hyperliquid strategy configuration / 更新 Hyperliquid 策略配置
    """
    try:
        from src.trading.hyperliquid_client import HyperliquidClient
        
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange or not exchange.is_connected:
            return {
                "error": "Hyperliquid exchange not connected / Hyperliquid 交易所未连接"
            }
        
        # Find or create Hyperliquid strategy instance
        # 查找或创建 Hyperliquid 策略实例
        hyperliquid_instance = None
        for instance_id, instance in bot_engine.strategy_instances.items():
            if isinstance(instance.exchange, HyperliquidClient):
                hyperliquid_instance = instance
                break
        
        if not hyperliquid_instance:
            # Create a new instance for Hyperliquid
            # 为 Hyperliquid 创建新实例
            success = bot_engine.add_strategy_instance(
                "hyperliquid", "fixed_spread", symbol=exchange.symbol if hasattr(exchange, "symbol") else None
            )
            if success:
                hyperliquid_instance = bot_engine.strategy_instances.get("hyperliquid")
        
        if not hyperliquid_instance:
            return {"error": "Failed to get or create Hyperliquid strategy instance / 无法获取或创建 Hyperliquid 策略实例"}
        
        # Update strategy parameters
        new_spread = config.spread / 100
        hyperliquid_instance.strategy.spread = new_spread
        hyperliquid_instance.strategy.quantity = config.quantity
        
        return {
            "status": "updated",
            "config": {
                "spread": config.spread,
                "quantity": config.quantity,
                "strategy_type": config.strategy_type,
            }
        }
    except Exception as e:
        logger.error(f"Error updating Hyperliquid config: {e}")
        return {"error": f"Failed to update config: {str(e)} / 更新配置失败：{str(e)}"}


@app.post("/api/hyperliquid/leverage")
async def update_hyperliquid_leverage(leverage: int):
    """
    Update Hyperliquid leverage / 更新 Hyperliquid 杠杆
    """
    try:
        exchange = get_exchange_by_name("hyperliquid")
        if not exchange or not exchange.is_connected:
            return {
                "error": "Hyperliquid exchange not connected / Hyperliquid 交易所未连接"
            }
        
        if leverage < 1 or leverage > 125:
            return {"error": "Leverage must be between 1 and 125 / 杠杆必须在 1 到 125 之间"}
        
        success = exchange.set_leverage(leverage)
        if success:
            return {"status": "updated", "leverage": leverage}
        else:
            return {"error": "Failed to update leverage on Hyperliquid / 在 Hyperliquid 上更新杠杆失败"}
    except Exception as e:
        logger.error(f"Error updating Hyperliquid leverage: {e}")
        return {"error": f"Failed to update leverage: {str(e)} / 更新杠杆失败：{str(e)}"}


@app.post("/api/hyperliquid/pair")
async def update_hyperliquid_pair(pair: PairUpdate):
    """
    Update Hyperliquid trading pair / 更新 Hyperliquid 交易对
    
    Note: This endpoint allows updating the symbol even if Hyperliquid is not connected.
    The symbol will be updated when connection is established.
    注意：即使 Hyperliquid 未连接，此端点也允许更新交易对。连接建立时将更新交易对。
    """
    try:
        from src.trading.hyperliquid_client import HyperliquidClient
        
        exchange = get_exchange_by_name("hyperliquid")
        
        # If exchange is connected, update it immediately
        # 如果交易所已连接，立即更新
        if exchange and exchange.is_connected:
            success = exchange.set_symbol(pair.symbol)
            if success:
                # Also update strategy instance if exists
                # 如果存在，也更新策略实例
                for instance_id, instance in bot_engine.strategy_instances.items():
                    if isinstance(instance.exchange, HyperliquidClient):
                        instance.symbol = pair.symbol
                        instance.refresh_data()
                        break
                
                return {"status": "updated", "symbol": pair.symbol}
            else:
                return {
                    "status": "error",
                    "message": f"Failed to update to symbol {pair.symbol} / 更新到交易对 {pair.symbol} 失败",
                }
        else:
            # Exchange not connected, but we still allow symbol update for UI
            # Store the symbol preference for when connection is established
            # 交易所未连接，但我们仍然允许更新交易对以用于 UI
            # 存储交易对偏好，以便连接建立时使用
            for instance_id, instance in bot_engine.strategy_instances.items():
                if isinstance(instance.exchange, HyperliquidClient):
                    instance.symbol = pair.symbol
                    break
            
            # Return success with a warning that connection is needed for actual trading
            # 返回成功，但警告需要连接才能进行实际交易
            return {
                "status": "updated",
                "symbol": pair.symbol,
                "warning": "Hyperliquid not connected. Symbol updated for UI. Please connect to Hyperliquid for trading. / Hyperliquid 未连接。交易对已更新用于 UI。请连接到 Hyperliquid 进行交易。"
            }
    except Exception as e:
        logger.error(f"Error updating Hyperliquid pair: {e}")
        return {
            "status": "error",
            "message": f"Failed to update pair: {str(e)} / 更新交易对失败：{str(e)}",
        }


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
            exchange = get_default_exchange()
            if exchange and hasattr(exchange, "last_order_error"):
                exchange.last_order_error = None
            # Ensure every strategy instance is marked as running when global start is issued
            for instance in bot_engine.strategy_instances.values():
                instance.running = True
            is_running = True
            bot_thread = threading.Thread(target=run_bot_loop)
            bot_thread.daemon = True
            bot_thread.start()

        return {"status": "started"}
    elif action == "stop":
        is_running = False
        for instance in bot_engine.strategy_instances.values():
            instance.running = False
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

    # 2. Resolve target strategy instance
    target_instance = _get_or_create_strategy_instance(
        config.strategy_id, config.strategy_type
    )

    if not target_instance:
        return {"error": f"Failed to get or create strategy instance for {config.strategy_type}"}

    # Update parameters on the target instance's strategy
    target_instance.strategy.spread = new_spread
    target_instance.strategy.quantity = config.quantity

    # Update skew factor if applicable
    if hasattr(target_instance.strategy, "skew_factor"):
        target_instance.strategy.skew_factor = config.skew_factor
    
    # Update legacy default reference only when default instance was targeted
    default_instance = bot_engine.strategy_instances.get("default")
    if target_instance.strategy_id == "default" and default_instance:
        bot_engine.strategy = default_instance.strategy
    elif default_instance:
        bot_engine.strategy = default_instance.strategy

    # Clear any existing alerts / order errors since we fixed the config
    bot_engine.alert = None
    exchange = get_default_exchange()
    if exchange and hasattr(exchange, "last_order_error"):
        exchange.last_order_error = None

    return {"status": "updated", "config": config}


@app.post("/api/leverage")
async def update_leverage(leverage: int):
    if leverage < 1 or leverage > 125:
        return {"error": "Leverage must be between 1 and 125"}

    exchange = get_default_exchange()
    if not exchange:
        return {"error": "Exchange not available"}
    
    success = exchange.set_leverage(leverage)
    if success:
        return {"status": "updated", "leverage": leverage}
    else:
        return {"error": "Failed to update leverage on exchange"}


@app.post("/api/pair")
async def update_pair(pair: PairUpdate):
    target_strategy_id = pair.strategy_id or "default"
    success = bot_engine.set_symbol(pair.symbol, strategy_id=target_strategy_id)
    if success:
        # Immediately refresh data so UI gets updated even if bot is stopped
        target_instance = bot_engine.strategy_instances.get(target_strategy_id)
        if target_instance:
            target_instance.refresh_data()
        return {"status": "updated", "symbol": pair.symbol}
    else:
        return {
            "status": "error",
            "message": f"Failed to update to symbol {pair.symbol} for strategy '{target_strategy_id}'",
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
    exchange = get_default_exchange()
    if exchange is not None:
        try:
            # Pass start_time to fetch data from session start
            pnl_data = exchange.fetch_pnl_and_fees(start_time=start_time_ms)
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
        exchange = get_default_exchange()
        if exchange is None:
            return {"error": "Exchange not available"}

        # Fetch bulk funding rates
        funding_rates = exchange.fetch_bulk_funding_rates(symbols)

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
# Multi-LLM Evaluation APIs
# ============================================================================

# Store last evaluation results for apply endpoint
_last_evaluation_results = None
_last_evaluation_aggregated = None


@app.post("/api/evaluation/run")
async def run_evaluation(request: EvaluationRunRequest):
    """
    Run multi-LLM evaluation for a trading symbol.
    
    运行多 LLM 评估
    
    Args:
        request: EvaluationRunRequest with symbol, optional simulation_steps, and exchange parameter
        
    Returns:
        {
            "symbol": str,
            "exchange": str,
            "individual_results": List[EvaluationResult],
            "aggregated": AggregatedResult,
            "comparison_table": str,
            "consensus_report": dict,
            "market_data": dict
        }
    """
    global _last_evaluation_results, _last_evaluation_aggregated
    
    try:
        # Validate exchange parameter
        # 验证交易所参数
        is_valid, validation_error = _validate_exchange_parameter(request.exchange)
        if not is_valid:
            return validation_error
        
        exchange_name = request.exchange.lower()
        
        # Normalize symbol (remove / and :)
        symbol = request.symbol.upper().replace("/", "").replace(":", "")
        
        # Get exchange client by name
        # 根据名称获取交易所客户端
        exchange = get_exchange_by_name(exchange_name)
        
        # Check exchange connection
        # 检查交易所连接
        is_connected, connection_error, status_code = _check_exchange_connection(
            exchange_name, exchange, error_format="error"
        )
        if not is_connected:
            return connection_error, status_code if status_code else 400
        
        # Fetch market data
        # 获取市场数据
        try:
            # Temporarily set symbol if needed
            original_symbol = getattr(exchange, "symbol", None)
            if hasattr(exchange, "set_symbol"):
                exchange.set_symbol(symbol)
            
            market_data = exchange.fetch_market_data()
            account_data = exchange.fetch_account_data()
            
            # Restore original symbol
            if original_symbol and hasattr(exchange, "set_symbol"):
                exchange.set_symbol(original_symbol)
        except Exception as e:
            error_msg = f"Failed to fetch market data: {str(e)} / 获取市场数据失败：{str(e)}"
            return {"error": error_msg}
        
        if not market_data:
            return {"error": "No market data available / 无可用市场数据"}
        
        # Build MarketContext
        # 构建市场上下文
        mid_price = market_data.get("mid_price", 0.0)
        best_bid = market_data.get("best_bid", mid_price * 0.999)
        best_ask = market_data.get("best_ask", mid_price * 1.001)
        spread_bps = ((best_ask - best_bid) / mid_price * 10000) if mid_price > 0 else 10.0
        
        # Get funding rate if available
        # 获取资金费率（如果可用）
        funding_rate = market_data.get("funding_rate", 0.0)
        funding_rate_trend = "stable"  # Default, could be enhanced
        
        # Get position and account info
        # 获取仓位和账户信息
        position_amt = account_data.get("position_amt", 0.0) if account_data else 0.0
        position_side = "long" if position_amt > 0 else ("short" if position_amt < 0 else "neutral")
        unrealized_pnl = account_data.get("unrealizedProfit", 0.0) if account_data else 0.0
        balance = account_data.get("balance", 10000.0) if account_data else 10000.0
        leverage = account_data.get("leverage", 1.0) if account_data else 1.0
        
        # Get historical performance (simplified)
        # 获取历史绩效（简化版）
        win_rate = 0.0
        sharpe_ratio = 0.0
        recent_pnl = 0.0
        if hasattr(bot_engine, "data"):
            metrics = bot_engine.data.calculate_metrics()
            sharpe_ratio = metrics.get("sharpe_ratio", 0.0) or 0.0
            # Calculate win rate from trade history
            trades = bot_engine.data.trade_history
            if trades:
                winning = len([t for t in trades if t.get("pnl", 0) > 0])
                win_rate = winning / len(trades) if len(trades) > 0 else 0.0
                recent_pnl = sum(t.get("pnl", 0) for t in trades[-10:])  # Last 10 trades
        
        # Estimate volatility (simplified - could be enhanced)
        # 估算波动率（简化版 - 可以增强）
        volatility_24h = 0.03  # 3% default
        volatility_1h = 0.01   # 1% default
        
        # Add exchange information to symbol for LLM context
        # 在 symbol 中添加交易所信息以供 LLM 上下文使用
        # This ensures the LLM knows which exchange the evaluation is for
        # 这确保 LLM 知道评估是针对哪个交易所的
        symbol_with_exchange = _format_symbol_with_exchange(symbol, exchange_name)
        
        context = MarketContext(
            symbol=symbol_with_exchange,  # Include exchange name in symbol for LLM context
            mid_price=mid_price,
            best_bid=best_bid,
            best_ask=best_ask,
            spread_bps=spread_bps,
            volatility_24h=volatility_24h,
            volatility_1h=volatility_1h,
            funding_rate=funding_rate,
            funding_rate_trend=funding_rate_trend,
            current_position=position_amt,
            position_side=position_side,
            unrealized_pnl=unrealized_pnl,
            available_balance=balance,
            current_leverage=leverage,
            win_rate=win_rate,
            sharpe_ratio=sharpe_ratio,
            recent_pnl=recent_pnl,
        )
        
        # Create evaluator with all available providers
        try:
            providers = create_all_providers()
        except Exception as e:
            return {"error": f"Failed to create LLM providers: {str(e)}"}
        
        if not providers:
            return {"error": "No LLM providers available. Please configure API keys."}
        
        evaluator = MultiLLMEvaluator(
            providers=providers,
            simulation_steps=request.simulation_steps,
            parallel=True,
        )
        
        # Run evaluation (in thread to avoid blocking)
        import asyncio
        results = await asyncio.to_thread(evaluator.evaluate, context)
        
        # Aggregate results
        aggregated = evaluator.aggregate_results(results)
        
        # Generate comparison table and consensus report
        comparison_table = MultiLLMEvaluator.generate_comparison_table(results)
        consensus_report = MultiLLMEvaluator.generate_consensus_summary(aggregated)
        
        # Store results for apply endpoint
        _last_evaluation_results = results
        _last_evaluation_aggregated = aggregated
        
        # Convert results to dict for JSON response
        def result_to_dict(result):
            return {
                "provider_name": result.provider_name,
                "rank": result.rank,
                "score": result.score,
                "latency_ms": result.latency_ms,
                "proposal": {
                    "recommended_strategy": result.proposal.recommended_strategy,
                    "spread": result.proposal.spread,
                    "skew_factor": result.proposal.skew_factor,
                    "quantity": result.proposal.quantity,
                    "leverage": result.proposal.leverage,
                    "confidence": result.proposal.confidence,
                    "risk_level": result.proposal.risk_level,
                    "reasoning": result.proposal.reasoning,
                    "parse_success": result.proposal.parse_success,
                },
                "simulation": {
                    "realized_pnl": result.simulation.realized_pnl,
                    "total_trades": result.simulation.total_trades,
                    "win_rate": result.simulation.win_rate,
                    "sharpe_ratio": result.simulation.sharpe_ratio,
                    "simulation_steps": result.simulation.simulation_steps,
                },
            }
        
        def aggregated_to_dict(agg):
            return {
                "strategy_consensus": {
                    "consensus_strategy": agg.strategy_consensus.consensus_strategy,
                    "consensus_level": agg.strategy_consensus.consensus_level,
                    "consensus_ratio": agg.strategy_consensus.consensus_ratio,
                    "consensus_count": agg.strategy_consensus.consensus_count,
                    "total_models": agg.strategy_consensus.total_models,
                    "strategy_votes": agg.strategy_consensus.strategy_votes,
                    "strategy_percentages": agg.strategy_consensus.strategy_percentages,
                },
                "consensus_confidence": agg.consensus_confidence,
                "consensus_proposal": {
                    "recommended_strategy": agg.consensus_proposal.recommended_strategy,
                    "spread": agg.consensus_proposal.spread,
                    "skew_factor": agg.consensus_proposal.skew_factor,
                    "quantity": agg.consensus_proposal.quantity,
                    "leverage": agg.consensus_proposal.leverage,
                    "confidence": agg.consensus_proposal.confidence,
                    "reasoning": agg.consensus_proposal.reasoning,
                },
                "avg_pnl": agg.avg_pnl,
                "avg_sharpe": agg.avg_sharpe,
                "avg_win_rate": agg.avg_win_rate,
                "avg_latency_ms": agg.avg_latency_ms,
                "successful_evaluations": agg.successful_evaluations,
                "failed_evaluations": agg.failed_evaluations,
            }
        
        # Prepare market_data for response
        # 准备响应中的市场数据
        response_market_data = {
            "symbol": symbol,
            "mid_price": mid_price,
            "best_bid": best_bid,
            "best_ask": best_ask,
            "funding_rate": funding_rate,
            "spread_bps": spread_bps,
        }
        
        return {
            "symbol": symbol,
            "exchange": exchange_name,
            "individual_results": [result_to_dict(r) for r in results],
            "aggregated": aggregated_to_dict(aggregated),
            "comparison_table": comparison_table,
            "consensus_report": {"summary": consensus_report},
            "market_data": response_market_data,
        }
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)
        return {"error": str(e)}


@app.post("/api/evaluation/apply")
async def apply_evaluation(request: EvaluationApplyRequest):
    """
    Apply evaluation proposal to strategy configuration.
    
    应用评估建议到策略配置
    
    Args:
        request: EvaluationApplyRequest with source ("consensus" or "individual"), 
                 optional provider_name, and exchange parameter
        
    Returns:
        {
            "status": "success" or "error",
            "applied_config": {
                "strategy_type": str,
                "spread": float,
                "skew_factor": float,
                "quantity": float,
                "leverage": float
            },
            "exchange": str,
            "message": str (bilingual: English and Chinese)
        }
    """
    global _last_evaluation_results, _last_evaluation_aggregated
    
    # Validate exchange parameter
    # 验证交易所参数
    is_valid, validation_error = _validate_exchange_parameter(request.exchange)
    if not is_valid:
        return {
            "status": "error",
            "error": validation_error.get("error", "Invalid exchange parameter / 无效的交易所参数")
        }
    
    exchange_name = request.exchange.lower()
    
    if _last_evaluation_aggregated is None:
        return {
            "status": "error",
            "error": "No evaluation results available. Please run evaluation first. / 没有可用的评估结果。请先运行评估。"
        }
    
    try:
        # Check exchange connection if hyperliquid
        # 如果是 hyperliquid，检查交易所连接
        if exchange_name == "hyperliquid":
            exchange = get_exchange_by_name(exchange_name)
            is_connected, connection_error, status_code = _check_exchange_connection(
                exchange_name, exchange, error_format="status"
            )
            if not is_connected:
                return connection_error, status_code if status_code else 400
        
        proposal = None
        
        if request.source == "consensus":
            proposal = _last_evaluation_aggregated.consensus_proposal
        elif request.source == "individual":
            if not request.provider_name:
                return {
                    "status": "error",
                    "error": "provider_name required for individual source / 个人来源需要 provider_name"
                }
            
            # Find result by provider name
            found = False
            for result in _last_evaluation_results:
                if result.provider_name == request.provider_name:
                    proposal = result.proposal
                    found = True
                    break
            
            if not found:
                return {
                    "status": "error",
                    "error": f"Provider {request.provider_name} not found in evaluation results / 在评估结果中未找到提供商 {request.provider_name}"
                }
        else:
            return {
                "status": "error",
                "error": f"Invalid source: {request.source}. Use 'consensus' or 'individual'. / 无效的来源：{request.source}。使用 'consensus' 或 'individual'。"
            }
        
        if not proposal or not proposal.parse_success:
            return {
                "status": "error",
                "error": "Invalid proposal or proposal parsing failed / 无效的建议或建议解析失败"
            }
        
        # Map strategy name to strategy_type
        # 将策略名称映射到 strategy_type
        strategy_name = proposal.recommended_strategy
        if strategy_name == "FixedSpread":
            strategy_type = "fixed_spread"
        elif strategy_name == "FundingRate":
            strategy_type = "funding_rate"
        else:
            return {
                "status": "error",
                "error": f"Unsupported strategy: {strategy_name} / 不支持的策略：{strategy_name}"
            }
        
        # Apply configuration
        # 应用配置
        config_update = ConfigUpdate(
            spread=proposal.spread * 100,  # Convert to percentage
            quantity=proposal.quantity,
            strategy_type=strategy_type,
            strategy_id="default",
            skew_factor=proposal.skew_factor,
        )
        
        config_result = await update_config(config_update)
        if "error" in config_result:
            return {
                "status": "error",
                "error": config_result.get("error", "Failed to apply configuration / 应用配置失败"),
                "exchange": exchange_name,
            }
        
        # Apply leverage if provided
        # 如果提供了杠杆，应用杠杆
        if proposal.leverage:
            leverage_result = await update_leverage(int(proposal.leverage))
            if "error" in leverage_result:
                return {
                    "status": "error",
                    "error": leverage_result.get("error", "Failed to apply leverage / 应用杠杆失败"),
                    "exchange": exchange_name,
                }
        
        # Success message in bilingual format
        # 双语格式的成功消息
        success_message = (
            f"Configuration applied successfully to {exchange_name.upper()} exchange. / "
            f"配置已成功应用到 {exchange_name.upper()} 交易所。"
        )
        
        return {
            "status": "success",
            "applied_config": {
                "strategy_type": strategy_type,
                "spread": proposal.spread,
                "skew_factor": proposal.skew_factor,
                "quantity": proposal.quantity,
                "leverage": proposal.leverage,
            },
            "exchange": exchange_name,
            "message": success_message,
        }
        
    except Exception as e:
        logger.error(f"Apply evaluation error: {e}", exc_info=True)
        return {
            "status": "error",
            "error": f"Apply evaluation error: {str(e)} / 应用评估错误：{str(e)}",
            "exchange": exchange_name,
        }


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

    exchange = get_default_exchange()
    if exchange is not None:
        try:
            # Fetch PnL and commission from session start time
            pnl_data = exchange.fetch_pnl_and_fees(start_time=start_time_ms)
            commission = pnl_data.get("commission", 0.0)
            realized_pnl = pnl_data.get("realized_pnl", 0.0)
        except Exception:
            pass

        try:
            account_data = exchange.fetch_account_data()
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

    exchange = get_default_exchange()
    if exchange is not None:
        try:
            # Fetch market data for current price
            market_data = exchange.fetch_market_data()
            if market_data:
                current_price = market_data.get("mid_price", 0.0)

            # Fetch account data for position and liquidation price
            account_data = exchange.fetch_account_data()
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


@app.post("/api/strategy/{strategy_id}/control")
async def control_strategy_instance(strategy_id: str, action: str = Query(..., description="start 或 stop", alias="action")):
    """
    控制指定策略实例的启动/停止
    
    对应用户故事: 策略实例隔离运行
    
    Args:
        strategy_id: 策略实例 ID (如 "fixed_spread", "funding_rate", "default")
        action: "start" 或 "stop" (通过 query parameter 传递，例如: ?action=start)
    """
    # Map strategy_id to instance ID and strategy type
    strategy_type_map = {
        "fixed_spread": "fixed_spread",
        "funding_rate": "funding_rate",
    }
    
    # Determine the strategy type for this strategy_id
    target_strategy_type = strategy_type_map.get(strategy_id)
    
    # Find or create the appropriate instance
    instance = None
    instance_id = None
    
    if strategy_id == "default":
        # Use default instance
        instance = bot_engine.strategy_instances.get("default")
        if instance:
            instance_id = "default"
    elif target_strategy_type:
        # Look for an instance with matching strategy type
        resolved_instance = _get_or_create_strategy_instance(strategy_id, target_strategy_type)
        if resolved_instance:
            instance = resolved_instance
            instance_id = resolved_instance.strategy_id
    elif strategy_id in bot_engine.strategy_instances:
        instance_id = strategy_id
        instance = bot_engine.strategy_instances[instance_id]
    else:
        return {"error": f"Strategy instance '{strategy_id}' not found"}
    
    if not instance:
        return {"error": f"Failed to get or create strategy instance for '{strategy_id}'"}
    
    if action == "start":
        # Validate config before starting
        current_spread = instance.strategy.spread
        approved, reason = bot_engine.risk.validate_proposal({"spread": current_spread})
        
        if not approved:
            return {
                "error": f"Risk Rejection: {reason}",
                "suggestion": "Please adjust strategy parameters before starting"
            }
        
        # Start the strategy instance
        instance.running = True
        instance.alert = None
        
        # Ensure bot loop is running (if not already)
        global is_running, bot_thread
        if not is_running:
            is_running = True
            bot_thread = threading.Thread(target=run_bot_loop)
            bot_thread.daemon = True
            bot_thread.start()
        
        # Update portfolio manager status
        portfolio_manager.resume_strategy(strategy_id)
        
        return {"status": "started", "strategy_id": strategy_id}
    
    elif action == "stop":
        # Stop the strategy instance
        instance.running = False
        instance.alert = None
        
        # Cancel orders for this strategy instance using its own exchange connection
        if instance.use_real_exchange and instance.exchange is not None:
            try:
                # Cancel only orders tracked by this strategy instance
                if instance.tracked_order_ids:
                    current_orders = instance.exchange.fetch_open_orders()
                    orders_to_cancel = [
                        o for o in current_orders 
                        if o.get("id") in instance.tracked_order_ids
                    ]
                    for order in orders_to_cancel:
                        try:
                            instance.exchange.cancel_order(order["id"], order.get("symbol"))
                        except Exception as e:
                            logger.error(f"Error canceling order {order['id']} for strategy {strategy_id}: {e}")
            except Exception as e:
                logger.error(f"Error canceling orders for strategy {strategy_id}: {e}")
        
        # Update portfolio manager status
        portfolio_manager.pause_strategy(strategy_id)
        
        return {"status": "stopped", "strategy_id": strategy_id}
    
    return {"error": "Invalid action. Use 'start' or 'stop'"}


@app.post("/api/strategy/{strategy_id}/pause")
async def pause_strategy(strategy_id: str):
    """
    暂停指定策略

    对应用户故事: US-2.6
    """
    # Also stop the strategy instance
    result = await control_strategy_instance(strategy_id, "stop")
    if "error" in result:
        return result
    
    return {"status": "paused", "strategy_id": strategy_id}


@app.post("/api/strategy/{strategy_id}/resume")
async def resume_strategy(strategy_id: str):
    """
    恢复暂停的策略

    对应用户故事: US-2.6
    """
    # Also start the strategy instance
    result = await control_strategy_instance(strategy_id, "start")
    if "error" in result:
        return result
    
    return {"status": "live", "strategy_id": strategy_id}


@app.get("/api/portfolio/allocation")
async def get_allocation():
    """
    获取所有策略的资金分配情况

    Returns:
        {
            "total_capital": float,
            "min_allocation": float,
            "max_allocation": float,
            "auto_rebalance": bool,
            "strategies": [
                {
                    "strategy_id": str,
                    "name": str,
                    "allocation": float,  # 0-1
                    "allocated_capital": float,  # USDT
                    "status": str
                }
            ]
        }
    """
    _sync_portfolio_with_bot()
    
    strategies_data = []
    for strategy_id, strategy in portfolio_manager.strategies.items():
        allocated_capital = portfolio_manager.total_capital * strategy.allocation
        strategies_data.append({
            "strategy_id": strategy_id,
            "name": strategy.name,
            "allocation": round(strategy.allocation, 4),
            "allocated_capital": round(allocated_capital, 2),
            "status": strategy.status.value,
        })
    
    return {
        "total_capital": round(portfolio_manager.total_capital, 2),
        "min_allocation": portfolio_manager.min_allocation,
        "max_allocation": portfolio_manager.max_allocation,
        "auto_rebalance": portfolio_manager.auto_rebalance,
        "strategies": strategies_data,
    }


@app.post("/api/portfolio/rebalance")
async def rebalance_portfolio(request: RebalanceRequest):
    """
    手动触发资金再平衡

    支持的方法:
    - "equal": 等权重分配
    - "sharpe": 基于夏普比率加权
    - "health": 基于健康度加权
    - "roi": 基于 ROI 加权
    - "composite": 综合评分 (Sharpe + ROI + Health)
    - "risk_adjusted": 风险调整分配 (基于最大回撤)

    Args:
        request: RebalanceRequest with method and optional weights

    Returns:
        {
            "method": str,
            "new_allocations": {
                "strategy_id": float
            },
            "total_capital": float
        }
    """
    _sync_portfolio_with_bot()
    
    # Update metrics before rebalancing (ensure we have latest data)
    # This is done in _sync_portfolio_with_bot, but we call it again to be safe
    _sync_portfolio_with_bot()
    
    # Perform rebalancing
    new_allocations = portfolio_manager.rebalance_allocations(
        method=request.method,
        weights=request.weights,
    )
    
    return {
        "method": request.method,
        "new_allocations": {
            sid: round(alloc, 4) for sid, alloc in new_allocations.items()
        },
        "total_capital": round(portfolio_manager.total_capital, 2),
    }


@app.put("/api/portfolio/allocation/limits")
async def update_allocation_limits(request: AllocationLimitsUpdate):
    """
    更新资金分配限制

    Args:
        request: AllocationLimitsUpdate with min_allocation and/or max_allocation

    Returns:
        {
            "min_allocation": float,
            "max_allocation": float,
            "message": str
        }
    """
    portfolio_manager.set_allocation_limits(
        min_allocation=request.min_allocation,
        max_allocation=request.max_allocation,
    )
    
    return {
        "min_allocation": portfolio_manager.min_allocation,
        "max_allocation": portfolio_manager.max_allocation,
        "message": "Allocation limits updated successfully",
    }


@app.put("/api/portfolio/strategy/{strategy_id}/allocation")
async def update_strategy_allocation(strategy_id: str, request: StrategyAllocationUpdate):
    """
    手动设置单个策略的资金分配

    注意: 设置后会自动归一化所有策略的分配，确保总和为 100%

    Args:
        strategy_id: 策略标识
        request: StrategyAllocationUpdate with allocation (0-1)

    Returns:
        {
            "strategy_id": str,
            "old_allocation": float,
            "new_allocation": float,
            "allocated_capital": float,
            "all_strategies": {
                "strategy_id": float
            }
        }
    """
    if strategy_id not in portfolio_manager.strategies:
        return {"error": f"Strategy '{strategy_id}' not found"}
    
    # Validate allocation
    if request.allocation < 0 or request.allocation > 1:
        return {"error": "Allocation must be between 0 and 1"}
    
    # Get old allocation
    old_allocation = portfolio_manager.strategies[strategy_id].allocation
    
    # Update allocation
    portfolio_manager.strategies[strategy_id].allocation = request.allocation
    
    # Normalize all allocations
    portfolio_manager._normalize_allocations()
    
    # Get new allocation after normalization
    new_allocation = portfolio_manager.strategies[strategy_id].allocation
    allocated_capital = portfolio_manager.total_capital * new_allocation
    
    # Get all allocations
    all_allocations = {
        sid: round(s.allocation, 4)
        for sid, s in portfolio_manager.strategies.items()
    }
    
    return {
        "strategy_id": strategy_id,
        "old_allocation": round(old_allocation, 4),
        "new_allocation": round(new_allocation, 4),
        "allocated_capital": round(allocated_capital, 2),
        "all_strategies": all_allocations,
    }


@app.get("/api/portfolio/strategy/{strategy_id}/allocation")
async def get_strategy_allocation(strategy_id: str):
    """
    获取单个策略的资金分配

    Args:
        strategy_id: 策略标识

    Returns:
        {
            "strategy_id": str,
            "name": str,
            "allocation": float,
            "allocated_capital": float,
            "total_capital": float
        }
    """
    if strategy_id not in portfolio_manager.strategies:
        return {"error": f"Strategy '{strategy_id}' not found"}
    
    strategy = portfolio_manager.strategies[strategy_id]
    allocated_capital = portfolio_manager.total_capital * strategy.allocation
    
    return {
        "strategy_id": strategy_id,
        "name": strategy.name,
        "allocation": round(strategy.allocation, 4),
        "allocated_capital": round(allocated_capital, 2),
        "total_capital": round(portfolio_manager.total_capital, 2),
    }


def _sync_portfolio_with_bot():
    """
    同步 PortfolioManager 与当前 bot 状态

    将 bot_engine 的实时数据同步到 portfolio_manager
    支持多策略实例架构：为每个策略实例单独同步数据
    """
    global is_running, initial_capital

    # Get session start time for PnL calculation
    start_time_ms = get_session_start_time_ms()

    # Update capital from current balance if available (use default exchange)
    try:
        exchange = get_default_exchange()
        if exchange is not None:
            account_data = exchange.fetch_account_data()
            if account_data and "balance" in account_data:
                current_balance = account_data["balance"]
                if current_balance > 0:
                    # Update total capital to reflect current account value
                    # (initial capital + realized PnL)
                    portfolio_manager.total_capital = current_balance
    except Exception:
        pass  # Keep existing capital if fetch fails

    # Map strategy_type to strategy_id for portfolio_manager
    strategy_type_to_id = {
        "fixed_spread": "fixed_spread",
        "funding_rate": "funding_rate",
    }

    # Sync each strategy instance separately
    if hasattr(bot_engine, "strategy_instances") and bot_engine.strategy_instances:
        symbol_consumers = {}
        for instance_id, instance in bot_engine.strategy_instances.items():
            # Map instance to portfolio strategy_id
            # Use strategy_type to find the corresponding portfolio strategy
            portfolio_strategy_id = strategy_type_to_id.get(instance.strategy_type)
            
            # Skip if this instance type doesn't have a corresponding portfolio strategy
            if not portfolio_strategy_id or portfolio_strategy_id not in portfolio_manager.strategies:
                continue

            # Update strategy status based on instance running state
            strategy = portfolio_manager.strategies[portfolio_strategy_id]
            if instance.running:
                if strategy.status != StrategyStatus.PAUSED:
                    strategy.status = StrategyStatus.LIVE
            elif strategy.status == StrategyStatus.LIVE:
                # Only change to STOPPED if explicitly stopped, not if just not running
                # (PAUSED status is set via API, so we preserve it)
                if not instance.running:
                    strategy.status = StrategyStatus.STOPPED

            # Get performance data for this strategy instance
            realized_pnl = 0.0
            sharpe = None
            fill_rate = 0.85
            slippage = 0.0
            max_drawdown = 0.0
            total_trades = 0

            # Try to get data from instance's exchange
            if instance.use_real_exchange and instance.exchange is not None:
                symbol_key = getattr(instance.exchange, "symbol", None)
                duplicate_symbol = False
                if symbol_key:
                    if symbol_key in symbol_consumers:
                        logger.warning(
                            "Symbol %s already accounted for by %s, skipping duplicate PnL for %s",
                            symbol_key,
                            symbol_consumers[symbol_key],
                            portfolio_strategy_id,
                        )
                        duplicate_symbol = True
                    else:
                        symbol_consumers[symbol_key] = portfolio_strategy_id

                try:
                    if not duplicate_symbol:
                        pnl_data = instance.exchange.fetch_pnl_and_fees(
                            start_time=start_time_ms
                        )
                        realized_pnl = pnl_data.get("realized_pnl", 0.0)
                except Exception as e:
                    logger.debug(f"Error fetching PnL for {instance_id}: {e}")

                # Try to get metrics from instance's order history
                # Calculate basic metrics from order history
                if instance.order_history:
                    # Count total orders as trades (simplified)
                    total_trades = len([o for o in instance.order_history if o.get("status") == "filled"])
                    
                    # Calculate fill rate (orders filled / orders placed)
                    placed_orders = len([o for o in instance.order_history if o.get("status") in ["placed", "filled"]])
                    filled_orders = len([o for o in instance.order_history if o.get("status") == "filled"])
                    if placed_orders > 0:
                        fill_rate = filled_orders / placed_orders

            # Fallback: Use shared data agent if instance doesn't have its own data
            # This maintains backward compatibility
            if realized_pnl == 0.0 and hasattr(bot_engine, "data"):
                try:
                    # Filter trades by strategy_id if available
                    trades = [
                        t for t in bot_engine.data.trade_history
                        if t.get("strategy_id") == instance_id or t.get("strategy_type") == instance.strategy_type
                    ]
                    if not trades:
                        # If no strategy-specific trades, use all trades (backward compatibility)
                        trades = bot_engine.data.trade_history
                    
                    realized_pnl = sum(t.get("pnl", 0.0) for t in trades)
                    total_trades = len(trades)

                    # Get metrics from shared data agent
                    if trades:
                        metrics = bot_engine.data.calculate_metrics()
                        sharpe = metrics.get("sharpe_ratio", 0) if metrics.get("sharpe_ratio") else None
                        fill_rate = metrics.get("fill_rate", 0.85)
                        slippage = metrics.get("slippage_bps", 0.0)

                        # Calculate max drawdown from PnL history
                        cumulative = 0
                        peak = 0
                        for t in trades:
                            cumulative += t.get("pnl", 0.0)
                            if cumulative > peak:
                                peak = cumulative
                            if peak > 0:
                                dd = (peak - cumulative) / peak
                                if dd > max_drawdown:
                                    max_drawdown = dd
                except Exception as e:
                    logger.debug(f"Error getting metrics from data agent for {instance_id}: {e}")

            # Update this strategy's metrics in portfolio_manager
            portfolio_manager.update_strategy_metrics(
                strategy_id=portfolio_strategy_id,
                pnl=realized_pnl,
                sharpe=sharpe,
                fill_rate=fill_rate,
                slippage=slippage,
                max_drawdown=max_drawdown,
                total_trades=total_trades,
            )

    else:
        # Fallback: Legacy single-strategy mode (backward compatibility)
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
        trades = bot_engine.data.trade_history if hasattr(bot_engine, "data") else []
        realized_pnl = sum(t.get("pnl", 0.0) for t in trades)

        # Get metrics
        sharpe = None
        fill_rate = 0.85
        slippage = 0.0
        if hasattr(bot_engine, "data"):
            metrics = bot_engine.data.calculate_metrics()
            sharpe = metrics.get("sharpe_ratio", 0) if metrics.get("sharpe_ratio") else None
            fill_rate = metrics.get("fill_rate", 0.85)
            slippage = metrics.get("slippage_bps", 0.0)

        # Calculate max drawdown from PnL history
        max_drawdown = 0.0
        if trades:
            cumulative = 0
            peak = 0
            for t in trades:
                cumulative += t.get("pnl", 0.0)
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
            sharpe=sharpe,
            fill_rate=fill_rate,
            slippage=slippage,
            max_drawdown=max_drawdown,
            total_trades=len(trades),
        )

    # Record PnL snapshot for portfolio Sharpe calculation
    portfolio_manager.record_pnl_snapshot()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
