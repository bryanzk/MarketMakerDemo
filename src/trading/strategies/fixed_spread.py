"""
Fixed Spread Strategy / 固定点差策略

Market making strategy with fixed spread around mid price.
围绕中间价固定点差的做市策略。

Owner: Agent TRADING
"""

from typing import Any, Dict, List

from src.shared.config import LEVERAGE, QUANTITY, SPREAD_PCT
from src.shared.utils import round_step_size, round_tick_size


class FixedSpreadStrategy:
    """Fixed spread market making strategy."""

    def __init__(self):
        self.spread = SPREAD_PCT
        self.quantity = QUANTITY
        self.leverage = LEVERAGE
        # Store initial safe defaults for risk fallback
        self._safe_defaults = {
            "spread": SPREAD_PCT,
            "quantity": QUANTITY,
            "leverage": LEVERAGE,
        }

    def reset_to_safe_defaults(self) -> Dict[str, Any]:
        """
        Reset strategy parameters to initial safe defaults.
        Called when risk validation fails.

        Returns:
            Dict with the reset values
        """
        self.spread = self._safe_defaults["spread"]
        self.quantity = self._safe_defaults["quantity"]
        self.leverage = self._safe_defaults["leverage"]
        return self._safe_defaults.copy()

    def get_safe_defaults(self) -> Dict[str, Any]:
        """Return a copy of the safe default parameters."""
        return self._safe_defaults.copy()

    def calculate_target_orders(
        self, market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculates target orders based on fixed spread.

        Args:
            market_data: Dict with 'mid_price', 'best_bid', 'best_ask', 'tick_size', 'step_size'

        Returns:
            List of order dicts with 'side', 'price', 'quantity'
        """
        mid_price = market_data.get("mid_price")
        if not mid_price:
            return []

        # Get tick_size and step_size from market_data if available
        # 如果可用，从 market_data 获取 tick_size 和 step_size
        tick_size = market_data.get("tick_size")
        step_size = market_data.get("step_size")
        
        # Fallback to defaults if not available
        # 如果不可用，使用默认值
        if tick_size is None:
            tick_size = 0.1  # Default for ETH (changed from 0.01)
        if step_size is None:
            step_size = 0.001  # Default for ETH

        # Calculate raw prices
        bid_price = mid_price * (1 - self.spread / 2)
        ask_price = mid_price * (1 + self.spread / 2)

        # Safety check: Ensure we don't cross the spread
        best_ask = market_data.get("best_ask")
        best_bid = market_data.get("best_bid")

        if best_ask and bid_price >= best_ask:
            bid_price = best_ask * 0.9995
        if best_bid and ask_price <= best_bid:
            ask_price = best_bid * 1.0005

        # Use dynamic tick_size and step_size
        # 使用动态的 tick_size 和 step_size
        final_bid = round_tick_size(bid_price, tick_size)
        final_ask = round_tick_size(ask_price, tick_size)
        
        # Ensure ask price is always above mid_price after rounding
        # If rounding down causes ask to be <= mid_price, round up one tick
        # 确保卖出价格在舍入后始终大于 mid_price
        # 如果向下舍入导致卖出价格 <= mid_price，则向上舍入一个 tick
        if final_ask <= mid_price:
            from decimal import Decimal
            ask_decimal = Decimal(str(ask_price))
            tick_size_decimal = Decimal(str(tick_size))
            # Round up one tick / 向上舍入一个 tick
            ticks_rounded = (ask_decimal // tick_size_decimal) + Decimal("1")
            final_ask = float(ticks_rounded * tick_size_decimal)
        
        qty = round_step_size(self.quantity, step_size)

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]
