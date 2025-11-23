from alphaloop.core.config import LEVERAGE, QUANTITY, SPREAD_PCT
from alphaloop.core.utils import round_step_size, round_tick_size


class FixedSpreadStrategy:
    def __init__(self):
        self.spread = SPREAD_PCT
        self.quantity = QUANTITY
        self.leverage = LEVERAGE

    def calculate_target_orders(self, market_data):
        """
        Calculates target orders based on fixed spread.
        market_data: {'mid_price': float, 'best_bid': float, 'best_ask': float}
        Returns: list of dicts
        """
        mid_price = market_data.get("mid_price")
        if not mid_price:
            return []

        # Calculate raw prices
        bid_price = mid_price * (1 - self.spread / 2)
        ask_price = mid_price * (1 + self.spread / 2)

        # Safety check: Ensure we don't cross the spread (though fixed spread usually prevents this)
        # If spread is very tight, bid_price might be > best_ask.
        best_ask = market_data.get("best_ask")
        best_bid = market_data.get("best_bid")

        if best_ask and bid_price >= best_ask:
            bid_price = best_ask * 0.9995  # Back off
        if best_bid and ask_price <= best_bid:
            ask_price = best_bid * 1.0005  # Back off

        # Rounding (Assuming ETHUSDT for defaults, but should ideally get precision from exchange info)
        # For MVP, we hardcode common precisions or rely on utils defaults if passed
        # ETHUSDT: Tick size 0.01, Step size 0.001

        # TODO: Pass precision from Exchange module in future
        tick_size = 0.01
        step_size = 0.001

        final_bid = round_tick_size(bid_price, tick_size)
        final_ask = round_tick_size(ask_price, tick_size)
        qty = round_step_size(self.quantity, step_size)

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]
