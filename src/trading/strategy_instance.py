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

        Args:
            market_data: Market data dict
            funding_rate: Funding rate (for funding_rate strategy)

        Returns:
            List of target orders
        """
        if hasattr(self.strategy.calculate_target_orders, "__code__") and (
            "funding_rate" in self.strategy.calculate_target_orders.__code__.co_varnames
        ):
            return self.strategy.calculate_target_orders(
                market_data, funding_rate=funding_rate
            )
        else:
            return self.strategy.calculate_target_orders(market_data)

    def _requires_both_side_orders(self, target_orders: List[Dict[str, Any]]) -> bool:
        """
        Determine if this strategy requires both-side orders (buy and sell).
        This method is extensible for future strategies.
        判断此策略是否需要双边订单（买入和卖出）。
        此方法可扩展以支持未来的策略。

        Args:
            target_orders: List of target orders from strategy

        Returns:
            True if strategy requires both buy and sell orders, False otherwise
        """
        # Check if target_orders contains both buy and sell orders
        # 检查 target_orders 是否包含买入和卖出订单
        has_buy = any(o.get("side") == "buy" for o in target_orders)
        has_sell = any(o.get("side") == "sell" for o in target_orders)
        
        # Only enforce both-side if:
        # 1. Strategy type is market making (fixed_spread, funding_rate) AND
        # 2. Target orders actually contain both sides
        # 只有当以下条件都满足时才强制双边：
        # 1. 策略类型是做市策略（fixed_spread, funding_rate）且
        # 2. 目标订单实际包含双边
        if self.strategy_type in ["fixed_spread", "funding_rate"]:
            # Market making strategies should return both-side orders
            # If target_orders has both sides, enforce both-side placement
            # 做市策略应该返回双边订单
            # 如果 target_orders 包含双边，强制双边下单
            if has_buy and has_sell:
                return True
            # If strategy type is market making but target_orders is single-sided,
            # it might be due to risk limits or other constraints - don't enforce
            # 如果策略类型是做市但 target_orders 是单边，
            # 可能是由于风险限制或其他约束 - 不强制
            return False
        
        # For other strategies, check if target_orders contains both sides
        # 对于其他策略，检查 target_orders 是否包含双边
        if has_buy and has_sell:
            return True
        
        # Future strategies can override this method or add their type here
        # 未来的策略可以重写此方法或在此处添加其类型
        return False

    def sync_orders(
        self, 
        current_orders: List[Dict[str, Any]], 
        target_orders: List[Dict[str, Any]],
        mid_price: float = None
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Sync orders for this strategy instance.

        Args:
            current_orders: Current open orders for this strategy
            target_orders: Target orders to place
            mid_price: Current mid price for adaptive threshold (optional)

        Returns:
            Tuple of (order_ids_to_cancel, orders_to_place)
        """
        # Filter current_orders to only include tracked orders for this strategy
        filtered_orders = [
            o for o in current_orders if o.get("id") in self.tracked_order_ids
        ]
        # Use mid_price from latest market data if available / 如果可用，使用最新市场数据的中间价
        if mid_price is None and self.latest_market_data:
            mid_price = self.latest_market_data.get("mid_price")
        
        # Determine if this strategy requires both-side orders
        # 判断此策略是否需要双边订单
        enforce_both_side = self._requires_both_side_orders(target_orders)
        
        return self.order_manager.sync_orders(
            filtered_orders, target_orders, mid_price, enforce_both_side=enforce_both_side
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
            # Ensure exchange symbol matches instance symbol before fetching data
            # 在获取数据前确保交易所交易对与实例交易对匹配
            if hasattr(self.exchange, 'set_symbol') and hasattr(self.exchange, 'symbol'):
                if self.symbol and self.exchange.symbol != self.symbol:
                    logger.info(
                        f"Strategy '{self.strategy_id}': Syncing exchange symbol to instance symbol: {self.symbol}"
                    )
                    self.exchange.set_symbol(self.symbol)
            
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

            # Calculate volatility if exchange supports it / 如果交易所支持，计算波动率
            try:
                from src.trading.volatility import calculate_volatility_1h_24h, VolatilityCalculator
                
                # Use a shared calculator instance for caching / 使用共享计算器实例进行缓存
                if not hasattr(self, "_volatility_calculator"):
                    self._volatility_calculator = VolatilityCalculator(cache_ttl=300)  # 5 min cache
                
                volatility_1h, volatility_24h = calculate_volatility_1h_24h(
                    self.exchange,
                    self.symbol,
                    calculator=self._volatility_calculator
                )
                
                # Add volatility to market_data / 将波动率添加到 market_data
                market_data["volatility_1h"] = volatility_1h
                market_data["volatility_24h"] = volatility_24h
                
                # Calculate market spread if best_bid and best_ask are available / 如果 best_bid 和 best_ask 可用，计算市场价差
                best_bid = market_data.get("best_bid")
                best_ask = market_data.get("best_ask")
                if best_bid and best_ask and best_bid > 0:
                    market_spread = (best_ask - best_bid) / best_bid  # Market spread as percentage
                    market_data["market_spread"] = market_spread
            except Exception as e:
                logger.warning(
                    f"Strategy '{self.strategy_id}': Failed to calculate volatility for {self.symbol}: {e}. "
                    f"Continuing without volatility data. "
                    f"策略 '{self.strategy_id}'：计算 {self.symbol} 的波动率失败: {e}。继续但不使用波动率数据。"
                )
                # Continue without volatility data / 继续但不使用波动率数据

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
        mid_price = None
        position = 0.0
        pnl = 0.0
        funding_rate = 0.0

        if self.use_real_exchange and self.exchange:
            # Try to get mid_price from cached data first
            # 首先尝试从缓存数据获取 mid_price
            if self.latest_market_data and self.latest_market_data.get("mid_price"):
                mid_price = self.latest_market_data["mid_price"]
            else:
                # If cache is empty or missing mid_price, try to fetch fresh data
                # 如果缓存为空或缺少 mid_price，尝试获取新数据
                try:
                    market_data = self.exchange.fetch_market_data()
                    if market_data and market_data.get("mid_price"):
                        mid_price = market_data["mid_price"]
                        # Update cache for next time
                        # 更新缓存以供下次使用
                        self.latest_market_data = market_data
                except Exception as e:
                    logger.warning(
                        f"Strategy '{self.strategy_id}': Failed to fetch market data for status: {e}. "
                        f"策略 '{self.strategy_id}'：获取状态的市场数据失败：{e}。"
                    )
            
            # Fallback to 0.0 if still no mid_price (instead of 2000.0)
            # 如果仍然没有 mid_price，回退到 0.0（而不是 2000.0）
            if mid_price is None:
                mid_price = 0.0
                logger.warning(
                    f"Strategy '{self.strategy_id}': No mid_price available, using 0.0. "
                    f"策略 '{self.strategy_id}'：没有可用的 mid_price，使用 0.0。"
                )
            
            funding_rate = self.latest_funding_rate
            if self.latest_account_data:
                position = self.latest_account_data.get("position_amt", 0.0)
                if (
                    position != 0
                    and self.latest_account_data.get("entry_price", 0) != 0
                    and mid_price > 0
                ):
                    pnl = (
                        mid_price - self.latest_account_data["entry_price"]
                    ) * position

        # Get volatility from latest market data / 从最新市场数据获取波动率
        volatility_1h = None
        volatility_24h = None
        volatility_level = None  # "low", "medium", "high", "very_high"
        
        if self.latest_market_data:
            volatility_1h = self.latest_market_data.get("volatility_1h")
            volatility_24h = self.latest_market_data.get("volatility_24h")
            
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
            "quantity": getattr(self.strategy, "quantity", None),
            "leverage": getattr(self.strategy, "leverage", None),
            "volatility_1h": volatility_1h,
            "volatility_24h": volatility_24h,
            "volatility_level": volatility_level,  # For frontend display / 用于前端显示
            "alert": self.alert,
            "active_orders": self.active_orders,
            "order_count": len(self.active_orders),
            "use_real_exchange": self.use_real_exchange,
        }
