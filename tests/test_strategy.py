import pytest
from alphaloop.strategies.strategy import FixedSpreadStrategy


class TestFixedSpreadStrategy:
    """Test cases for FixedSpreadStrategy class"""

    def setup_method(self):
        """Setup for each test method"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.spread = 0.002  # 0.2% spread in decimal
        self.strategy.quantity = 0.02

    def test_calculate_target_orders_normal(self):
        """Test normal order calculation with valid market data"""
        market_data = {"mid_price": 3000.0, "best_bid": 2999.5, "best_ask": 3000.5}

        orders = self.strategy.calculate_target_orders(market_data)

        assert len(orders) == 2
        assert orders[0]["side"] == "buy"
        assert orders[1]["side"] == "sell"

        # Buy order should be below mid price
        assert orders[0]["price"] < market_data["mid_price"]
        # Sell order should be above mid price
        assert orders[1]["price"] > market_data["mid_price"]

        # Both should have correct quantity
        assert orders[0]["quantity"] == 0.02
        assert orders[1]["quantity"] == 0.02

    def test_calculate_target_orders_with_small_spread(self):
        """Test order calculation with very small spread (0.005%)"""
        self.strategy.spread = 0.005 / 100  # 0.005% spread

        market_data = {"mid_price": 3000.0, "best_bid": 2999.9, "best_ask": 3000.1}

        orders = self.strategy.calculate_target_orders(market_data)

        # Expected prices with 0.005% spread
        # buy: 3000 * (1 - 0.00005/2) = 3000 * 0.999975 = 2999.925
        # sell: 3000 * (1 + 0.00005/2) = 3000 * 1.000025 = 3000.075

        assert orders[0]["price"] < market_data["mid_price"]
        assert orders[1]["price"] > market_data["mid_price"]

        # Verify spread is very tight
        spread_pct = (orders[1]["price"] - orders[0]["price"]) / market_data[
            "mid_price"
        ]
        assert spread_pct < 0.0001  # Less than 0.01%

    def test_calculate_target_orders_no_mid_price(self):
        """Test handling of missing mid_price"""
        market_data = {"best_bid": 2999.5, "best_ask": 3000.5}

        orders = self.strategy.calculate_target_orders(market_data)

        assert orders == []

    def test_calculate_target_orders_empty_data(self):
        """Test handling of empty market data"""
        market_data = {}

        orders = self.strategy.calculate_target_orders(market_data)

        assert orders == []

    def test_price_rounding(self):
        """Test that prices are properly rounded to tick size"""
        market_data = {
            "mid_price": 3000.556,  # Non-round price
            "best_bid": 3000.0,
            "best_ask": 3001.0,
        }

        orders = self.strategy.calculate_target_orders(market_data)

        # Prices should be rounded to 0.01 (tick size)
        # Use approximate equality due to floating point precision
        assert abs(orders[0]["price"] % 0.01) < 0.0001
        assert abs(orders[1]["price"] % 0.01) < 0.0001

    def test_spread_calculation_symmetry(self):
        """Test that spread is symmetric around mid price"""
        market_data = {"mid_price": 3000.0, "best_bid": 2999.0, "best_ask": 3001.0}

        orders = self.strategy.calculate_target_orders(market_data)

        bid_distance = market_data["mid_price"] - orders[0]["price"]
        ask_distance = orders[1]["price"] - market_data["mid_price"]

        # Distances should be approximately equal (within rounding tolerance)
        assert abs(bid_distance - ask_distance) < 0.1

    def test_quantity_rounding(self):
        """Test that quantities are properly rounded to step size"""
        self.strategy.quantity = 0.0234  # Non-round quantity

        market_data = {"mid_price": 3000.0, "best_bid": 2999.0, "best_ask": 3001.0}

        orders = self.strategy.calculate_target_orders(market_data)

        # Quantity should be rounded to 0.001 (step size)
        # Verify the quantity rounds down correctly
        for order in orders:
            # Should round 0.0234 down to 0.023
            assert order["quantity"] == 0.023
