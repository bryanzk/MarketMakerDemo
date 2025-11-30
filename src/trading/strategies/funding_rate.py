"""
Funding Rate Strategy / 资金费率策略

Market making strategy with spread skewed by funding rate.
根据资金费率调整点差的做市策略。

Owner: Agent TRADING
"""

from typing import Any, Dict, List

from src.shared.config import LEVERAGE, QUANTITY, SKEW_FACTOR, SPREAD_PCT
from src.shared.utils import round_step_size, round_tick_size


class FundingRateStrategy:
    """Funding rate skew market making strategy."""

    def __init__(self):
        self.spread = SPREAD_PCT
        self.quantity = QUANTITY
        self.leverage = LEVERAGE
        self.skew_factor = SKEW_FACTOR
        # Store initial safe defaults for risk fallback
        self._safe_defaults = {
            "spread": SPREAD_PCT,
            "quantity": QUANTITY,
            "leverage": LEVERAGE,
            "skew_factor": SKEW_FACTOR,
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
        self.skew_factor = self._safe_defaults["skew_factor"]
        return self._safe_defaults.copy()

    def get_safe_defaults(self) -> Dict[str, Any]:
        """Return a copy of the safe default parameters."""
        return self._safe_defaults.copy()

    def calculate_target_orders(
        self, market_data: Dict[str, Any], funding_rate: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Calculates target orders based on fixed spread and funding rate skew.

        Args:
            market_data: Dict with 'mid_price', 'best_bid', 'best_ask',
                        optional 'tick_size', 'step_size'
            funding_rate: Funding rate (e.g., 0.0001 for 0.01%)

        Returns:
            List of order dicts with 'side', 'price', 'quantity'
        """
        mid_price = market_data.get("mid_price")
        if not mid_price or mid_price <= 0:
            return []

        # Calculate skew based on funding rate
        # If rate > 0 (Longs pay Shorts), we want to be Short -> Sell closer, Buy further
        skew_offset = funding_rate * self.skew_factor * mid_price

        # Calculate raw prices with skew
        bid_price = mid_price * (1 - self.spread / 2) - skew_offset
        ask_price = mid_price * (1 + self.spread / 2) - skew_offset

        # Safety check: Ensure we don't cross the spread
        best_ask = market_data.get("best_ask")
        best_bid = market_data.get("best_bid")

        if best_ask and bid_price >= best_ask:
            bid_price = best_ask * 0.9995
        if best_bid and ask_price <= best_bid:
            ask_price = best_bid * 1.0005

        # Use dynamic tick_size and step_size from market data
        if mid_price < 0.0001:
            default_tick = 0.00000001
        elif mid_price < 0.01:
            default_tick = 0.0000001
        elif mid_price < 1:
            default_tick = 0.000001
        elif mid_price < 100:
            default_tick = 0.0001
        else:
            default_tick = 0.01

        tick_size = market_data.get("tick_size", default_tick)
        step_size = market_data.get("step_size", 0.001)

        final_bid = round_tick_size(bid_price, tick_size)
        final_ask = round_tick_size(ask_price, tick_size)
        qty = round_step_size(self.quantity, step_size)

        # Final validation: ensure prices are positive after rounding
        if final_bid <= 0 or final_ask <= 0:
            return []

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]

