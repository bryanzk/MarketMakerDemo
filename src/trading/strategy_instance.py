"""
Strategy Instance Module / 策略实例模块

Encapsulates a single strategy instance with isolated state.
封装单个策略实例，确保状态隔离。

Owner: Agent TRADING
"""

import time
from collections import deque
from typing import Any, Dict, List, Optional, Set, Tuple

from src.shared.config import SYMBOL
from src.shared.logger import setup_logger
from src.trading.exchange import BinanceClient
from src.trading.order_fill_tracker import OrderFillTracker
from src.trading.order_manager import OrderManager
from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategies.funding_rate import FundingRateStrategy

logger = setup_logger("StrategyInstance")


class StrategyInstance:
    """
    Encapsulates a single strategy instance with isolated state.
    封装单个策略实例，包含独立的状态管理。

    Each instance has its own exchange connection, ensuring complete isolation.
    每个实例都有自己的交易所连接，确保完全隔离。
    """

    def __init__(
        self,
        strategy_id: str,
        strategy_type: str = "fixed_spread",
        symbol: str = None,
        exchange: Optional[Any] = None,
    ):
        """
        Initialize a strategy instance with its own exchange connection.

        Args:
            strategy_id: Unique identifier for this strategy instance
            strategy_type: "fixed_spread" or "funding_rate"
            symbol: Trading symbol for this instance (defaults to SYMBOL from config)
            exchange: Optional exchange client instance. If not provided and strategy_id is not "hyperliquid",
                     will attempt to create a BinanceClient. For "hyperliquid" strategy_id, exchange must be provided.
        """
        self.strategy_id = strategy_id
        self.strategy_type = strategy_type
        self.symbol = symbol or SYMBOL

        # Initialize strategy
        if strategy_type == "funding_rate":
            self.strategy = FundingRateStrategy()
        else:
            self.strategy = FixedSpreadStrategy()

        # Independent order manager for this strategy
        self.order_manager = OrderManager()

        # Independent exchange connection for this strategy instance
        # If exchange is provided, use it; otherwise, only create BinanceClient for non-hyperliquid instances
        # 如果提供了 exchange，使用它；否则，仅对非 hyperliquid 实例创建 BinanceClient
        self.exchange: Optional[Any] = None
        self.use_real_exchange = False

        if exchange is not None:
            # Use provided exchange client / 使用提供的交易所客户端
            self.exchange = exchange
            self.use_real_exchange = True
            # Set symbol for this instance's exchange
            if self.symbol != SYMBOL and hasattr(self.exchange, "set_symbol"):
                self.exchange.set_symbol(self.symbol)
            logger.info(
                f"Strategy instance '{strategy_id}' using provided exchange client (symbol: {self.symbol})"
            )
        elif strategy_id != "hyperliquid":
            # Only create BinanceClient for non-hyperliquid instances
            # 仅对非 hyperliquid 实例创建 BinanceClient
            try:
                self.exchange = BinanceClient()
                # Set symbol for this instance's exchange
                if self.symbol != SYMBOL:
                    self.exchange.set_symbol(self.symbol)
                self.use_real_exchange = True
                logger.info(
                    f"Strategy instance '{strategy_id}' exchange connected successfully (symbol: {self.symbol})"
                )
            except Exception as e:
                logger.error(
                    f"Strategy instance '{strategy_id}' failed to connect to exchange: {e}. Using simulation mode."
                )
                self.exchange = None
                self.use_real_exchange = False
        else:
            # For hyperliquid instances without provided exchange, use simulation mode
            # 对于没有提供 exchange 的 hyperliquid 实例，使用模拟模式
            logger.warning(
                f"Strategy instance '{strategy_id}' (hyperliquid) created without exchange client. "
                f"Exchange must be set before use. / "
                f"策略实例 '{strategy_id}' (hyperliquid) 创建时没有交易所客户端。使用前必须设置交易所。"
            )
            self.exchange = None
            self.use_real_exchange = False

        # Strategy-specific state
        self.strategy_switched = False
        self.alert: Optional[str] = None
        self.active_orders: List[Dict[str, Any]] = []
        self.order_history: deque = deque(maxlen=200)
        self.error_history: deque = deque(maxlen=200)
        # Track order IDs for this strategy instance
        self.tracked_order_ids: Set[str] = set()
        # Order fill tracking
        # 订单填充跟踪
        self.fill_tracker = OrderFillTracker(max_history=500)
        # Running state for this strategy instance
        self.running = False

        # Data cache for this strategy instance
        self.latest_market_data: Optional[Dict[str, Any]] = None
        self.latest_funding_rate = 0.0
        self.latest_account_data: Optional[Dict[str, Any]] = None

    def get_strategy_name(self) -> str:
        """Get human-readable strategy name."""
        if isinstance(self.strategy, FundingRateStrategy):
            return "Funding Rate Skew"
        return "Fixed Spread"

    def reset_to_safe_defaults(self) -> Dict[str, Any]:
        """Reset strategy parameters to safe defaults."""
        return self.strategy.reset_to_safe_defaults()

    def get_safe_defaults(self) -> Dict[str, Any]:
        """Get safe default parameters."""
        return self.strategy.get_safe_defaults()

    def calculate_target_orders(
        self, market_data: Dict[str, Any], funding_rate: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Calculate target orders for this strategy instance.
        Automatically adjusts spread based on volatility and market spread if available.

        Args:
            market_data: Market data dict
            funding_rate: Funding rate (for funding_rate strategy)

        Returns:
            List of target orders
        """
        # Adjust spread based on volatility and market spread if strategy supports it
        # 如果策略支持，根据波动率和市场价差调整价差
        if hasattr(self.strategy, "calculate_adaptive_spread"):
            volatility_1h = market_data.get("volatility_1h")
            volatility_24h = market_data.get("volatility_24h")
            market_spread = market_data.get("market_spread")
            
            # Calculate adaptive spread
            # 计算自适应价差
            self.strategy.calculate_adaptive_spread(
                volatility_1h=volatility_1h,
                volatility_24h=volatility_24h,
                market_spread=market_spread,
            )
        
        if hasattr(self.strategy.calculate_target_orders, "__code__") and (
            "funding_rate" in self.strategy.calculate_target_orders.__code__.co_varnames
        ):
            return self.strategy.calculate_target_orders(
                market_data, funding_rate=funding_rate
            )
        else:
            return self.strategy.calculate_target_orders(market_data)

    def sync_orders(
        self,
        current_orders: List[Dict[str, Any]],
        target_orders: List[Dict[str, Any]],
        mid_price: Optional[float] = None,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Sync orders for this strategy instance.
        Includes stability window check based on volatility.

        Args:
            current_orders: Current open orders for this strategy
            target_orders: Target orders to place
            mid_price: Mid price for adaptive threshold calculation (optional)

        Returns:
            Tuple of (order_ids_to_cancel, orders_to_place)
        """
        # Filter current_orders to only include tracked orders for this strategy
        filtered_orders = [
            o for o in current_orders if o.get("id") in self.tracked_order_ids
        ]
        
        # Get volatility from latest market data for stability window calculation
        # 从最新市场数据获取波动率，用于稳定性窗口计算
        volatility_1h = None
        volatility_24h = None
        if self.latest_market_data:
            volatility_1h = self.latest_market_data.get("volatility_1h")
            volatility_24h = self.latest_market_data.get("volatility_24h")
        
        return self.order_manager.sync_orders(
            filtered_orders,
            target_orders,
            mid_price=mid_price,
            volatility_1h=volatility_1h,
            volatility_24h=volatility_24h,
        )

    def add_tracked_order(self, order_id: str) -> None:
        """Add an order ID to the tracked set for this strategy."""
        self.tracked_order_ids.add(order_id)

    def remove_tracked_order(self, order_id: str) -> None:
        """Remove an order ID from the tracked set."""
        self.tracked_order_ids.discard(order_id)

    def clear_tracked_orders(self) -> None:
        """Clear all tracked order IDs."""
        self.tracked_order_ids.clear()

    def refresh_data(self) -> bool:
        """
        Fetch fresh data from exchange and update cache.

        Returns:
            True if data refreshed successfully, False otherwise
        """
        if not self.use_real_exchange or not self.exchange:
            return False

        try:
            # Fetch current market data
            market_data = self.exchange.fetch_market_data()
            if not market_data or not market_data.get("mid_price"):
                logger.error(
                    f"Strategy '{self.strategy_id}': Failed to fetch market data"
                )
                return False

            # Validate data freshness
            current_time_ms = time.time() * 1000
            data_timestamp = market_data.get("timestamp", current_time_ms)
            data_age_seconds = (current_time_ms - data_timestamp) / 1000

            if data_age_seconds > 5.0:
                logger.warning(
                    f"Strategy '{self.strategy_id}': Market data is stale ({data_age_seconds:.1f}s old)"
                )

            # Fetch funding rate
            funding_rate = self.exchange.fetch_funding_rate()

            # Fetch Account Data
            account_data = self.exchange.fetch_account_data()

            # Update Cache
            self.latest_market_data = market_data
            self.latest_funding_rate = funding_rate
            self.latest_account_data = account_data
            return True
        except Exception as e:
            logger.error(f"Strategy '{self.strategy_id}': Error refreshing data: {e}")
            return False

    def set_symbol(self, symbol: str) -> bool:
        """
        Update the trading symbol for this strategy instance.

        Args:
            symbol: New trading symbol

        Returns:
            True if symbol updated successfully
        """
        if self.exchange:
            success = self.exchange.set_symbol(symbol)
            if success:
                self.symbol = symbol
                # Invalidate cache
                self.latest_market_data = None
                self.latest_funding_rate = 0.0
                self.latest_account_data = None
                logger.info(
                    f"Strategy '{self.strategy_id}': Symbol updated to {symbol}"
                )
                return True
            else:
                logger.error(
                    f"Strategy '{self.strategy_id}': Failed to update symbol to {symbol}"
                )
                return False
        return False

    def get_status(self) -> Dict[str, Any]:
        """Get status information for this strategy instance."""
        # Use cached data for status
        mid_price = 2000.0
        position = 0.0
        pnl = 0.0
        funding_rate = 0.0

        if self.use_real_exchange and self.exchange:
            if self.latest_market_data and self.latest_market_data.get("mid_price"):
                mid_price = self.latest_market_data["mid_price"]
            funding_rate = self.latest_funding_rate
            if self.latest_account_data:
                position = self.latest_account_data.get("position_amt", 0.0)
                if (
                    position != 0
                    and self.latest_account_data.get("entry_price", 0) != 0
                ):
                    pnl = (
                        mid_price - self.latest_account_data["entry_price"]
                    ) * position

        # Get volatility from latest market data / 从最新市场数据获取波动率
        volatility_1h = None
        volatility_24h = None
        volatility_level = None  # "low", "medium", "high", "very_high"
        market_spread = None
        
        if self.latest_market_data:
            volatility_1h = self.latest_market_data.get("volatility_1h")
            volatility_24h = self.latest_market_data.get("volatility_24h")
            market_spread = self.latest_market_data.get("market_spread")
            
            # Determine volatility level for display / 确定波动率级别用于显示
            volatility = volatility_1h if volatility_1h is not None else volatility_24h
            if volatility is not None:
                if volatility < 0.02:
                    volatility_level = "low"
                elif volatility < 0.05:
                    volatility_level = "medium"
                elif volatility < 0.10:
                    volatility_level = "high"
                else:
                    volatility_level = "very_high"
        
        # Get base spread from strategy / 从策略获取基础价差
        base_spread = None
        if hasattr(self.strategy, "base_spread"):
            base_spread = self.strategy.base_spread

        # Get fill rate statistics / 获取成交率统计
        fill_stats = self.fill_tracker.get_statistics()
        
        return {
            "strategy_id": self.strategy_id,
            "strategy_type": self.strategy_type,
            "strategy_name": self.get_strategy_name(),
            "symbol": self.symbol,
            "mid_price": mid_price,
            "funding_rate": funding_rate,
            "position": position,
            "pnl": pnl,
            "spread": getattr(self.strategy, "spread", None),
            "base_spread": base_spread,  # Base spread for comparison / 基础价差用于对比
            "quantity": getattr(self.strategy, "quantity", None),
            "leverage": getattr(self.strategy, "leverage", None),
            "volatility_1h": volatility_1h,
            "volatility_24h": volatility_24h,
            "volatility_level": volatility_level,  # For frontend display / 用于前端显示
            "market_spread": market_spread,  # Market spread for adjustment context / 市场价差用于调整上下文
            "alert": self.alert,
            "active_orders": self.active_orders,
            "order_count": len(self.active_orders),
            "use_real_exchange": self.use_real_exchange,
            # Fill rate statistics / 成交率统计
            "fill_rate": fill_stats.get("fill_rate", 0.0),
            "fill_rate_pct": fill_stats.get("fill_rate_pct", 0.0),
            "recent_fill_rate": fill_stats.get("recent_fill_rate", 0.0),
            "recent_fill_rate_pct": fill_stats.get("recent_fill_rate_pct", 0.0),
            "cancellation_rate": fill_stats.get("cancellation_rate", 0.0),
            "cancellation_rate_pct": fill_stats.get("cancellation_rate_pct", 0.0),
            "total_orders_placed": fill_stats.get("total_orders_placed", 0),
            "total_orders_filled": fill_stats.get("total_orders_filled", 0),
            "total_orders_cancelled": fill_stats.get("total_orders_cancelled", 0),
            "average_fill_age_seconds": fill_stats.get("average_fill_age_seconds", 0.0),
            "average_cancel_age_seconds": fill_stats.get("average_cancel_age_seconds", 0.0),
        }
