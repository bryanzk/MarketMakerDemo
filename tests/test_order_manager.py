import pytest
from alphaloop.market.order_manager import OrderManager


class TestOrderManager:
    """Test cases for OrderManager class"""

    def setup_method(self):
        """Setup for each test method"""
        self.om = OrderManager()

    def test_sync_orders_no_current_no_target(self):
        """Test sync when no current orders and no target orders"""
        current_orders = []
        target_orders = []

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        assert len(to_cancel) == 0
        assert len(to_place) == 0

    def test_sync_orders_no_current_with_target(self):
        """Test sync when no current orders but have target orders"""
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        assert len(to_cancel) == 0
        assert len(to_place) == 2
        assert to_place[0]["side"] == "buy"
        assert to_place[1]["side"] == "sell"

    def test_sync_orders_with_current_no_target(self):
        """Test sync when have current orders but no target orders"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders = []

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        assert len(to_cancel) == 2
        assert "123" in to_cancel
        assert "124" in to_cancel
        assert len(to_place) == 0

    def test_sync_orders_no_price_change(self):
        """Test sync when current and target prices match (within tolerance)"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders = [
            {
                "side": "buy",
                "price": 3000.005,
                "quantity": 0.02,
            },  # Within 0.01 tolerance
            {"side": "sell", "price": 3010.005, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        # No changes needed since prices are within tolerance
        assert len(to_cancel) == 0
        assert len(to_place) == 0

    def test_sync_orders_price_changed(self):
        """Test sync when price changes beyond tolerance"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders = [
            {"side": "buy", "price": 3005.0, "quantity": 0.02},  # Changed > 0.01
            {"side": "sell", "price": 3015.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        # Both orders should be replaced
        assert len(to_cancel) == 2
        assert len(to_place) == 2
        assert "123" in to_cancel
        assert "124" in to_cancel

    def test_sync_orders_only_buy_changed(self):
        """Test sync when only buy order price changed"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders = [
            {"side": "buy", "price": 3005.0, "quantity": 0.02},  # Changed
            {"side": "sell", "price": 3010.0, "quantity": 0.02},  # Same
        ]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        # Only buy order should be replaced
        assert len(to_cancel) == 1
        assert "123" in to_cancel
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"

    def test_sync_orders_only_sell_changed(self):
        """Test sync when only sell order price changed"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},  # Same
            {"side": "sell", "price": 3020.0, "quantity": 0.02},  # Changed
        ]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        # Only sell order should be replaced
        assert len(to_cancel) == 1
        assert "124" in to_cancel
        assert len(to_place) == 1
        assert to_place[0]["side"] == "sell"

    def test_sync_orders_only_buy_side(self):
        """Test sync with only buy side orders"""
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02}
        ]
        target_orders = [{"side": "buy", "price": 3005.0, "quantity": 0.02}]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        assert len(to_cancel) == 1
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"

    def test_sync_orders_only_sell_side(self):
        """Test sync with only sell side orders"""
        current_orders = [
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02}
        ]
        target_orders = [{"side": "sell", "price": 3020.0, "quantity": 0.02}]

        to_cancel, to_place = self.om.sync_orders(current_orders, target_orders)

        assert len(to_cancel) == 1
        assert len(to_place) == 1
        assert to_place[0]["side"] == "sell"
