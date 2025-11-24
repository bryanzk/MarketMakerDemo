from alphaloop.core.config import LEVERAGE, QUANTITY, SKEW_FACTOR, SPREAD_PCT
from alphaloop.core.utils import round_step_size, round_tick_size


class FundingRateStrategy:
    def __init__(self):
        self.spread = SPREAD_PCT
        self.quantity = QUANTITY
        self.leverage = LEVERAGE
        self.skew_factor = SKEW_FACTOR

    def calculate_target_orders(self, market_data, funding_rate=0.0):
        """
        Calculates target orders based on fixed spread and funding rate skew.
        market_data: {'mid_price': float, 'best_bid': float, 'best_ask': float}
        funding_rate: float (e.g., 0.0001 for 0.01%)
        Returns: list of dicts
        """
        mid_price = market_data.get("mid_price")
        if not mid_price:
            return []

        # Calculate skew based on funding rate
        # If rate > 0 (Longs pay Shorts), we want to be Short -> Sell closer, Buy further
        # Skew > 0 shifts both quotes down (lower bid, lower ask)
        # Target: Sell more if rate > 0.
        # Standard: Bid = Mid - Spread/2, Ask = Mid + Spread/2
        # Skewed: Bid = Mid - Spread/2 - Skew, Ask = Mid + Spread/2 - Skew
        # If Skew > 0: Bid is lower (harder to fill), Ask is lower (easier to fill). Correct.

        skew_offset = funding_rate * self.skew_factor * mid_price

        # Calculate raw prices with skew
        bid_price = mid_price * (1 - self.spread / 2) - skew_offset
        ask_price = mid_price * (1 + self.spread / 2) - skew_offset

        # Safety check: Ensure we don't cross the spread
        best_ask = market_data.get("best_ask")
        best_bid = market_data.get("best_bid")

        if best_ask and bid_price >= best_ask:
            bid_price = best_ask * 0.9995  # Back off
        if best_bid and ask_price <= best_bid:
            ask_price = best_bid * 1.0005  # Back off

        # Rounding (Assuming ETHUSDT for defaults)
        tick_size = 0.01
        step_size = 0.001

        final_bid = round_tick_size(bid_price, tick_size)
        final_ask = round_tick_size(ask_price, tick_size)
        qty = round_step_size(self.quantity, step_size)

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]
