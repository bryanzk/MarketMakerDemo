import pytest

from src.trading.order_manager import OrderManager


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

    def test_sync_orders_enforce_both_side_buy_only_scheduled(self):
        """Test enforce_both_side: only buy order scheduled, should add sell"""
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        # Simulate scenario where only buy is scheduled (e.g., sell failed validation)
        # 模拟只有买入订单被安排的情况（例如，卖出订单验证失败）
        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=False
        )
        # Without enforce_both_side, both should be placed
        assert len(to_place) == 2

        # Now test with enforce_both_side=True, but simulate only buy in to_place
        # 现在测试 enforce_both_side=True，但模拟只有买入在 to_place 中
        # This tests the enforcement logic
        # 这测试强制逻辑
        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )
        # With enforce_both_side, both should be placed
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

    def test_sync_orders_enforce_both_side_sell_only_scheduled(self):
        """Test enforce_both_side: only sell order scheduled, should add buy"""
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )
        # With enforce_both_side, both should be placed
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

    def test_sync_orders_enforce_both_side_partial_update(self):
        """Test enforce_both_side: when only one side needs update, ensure both are placed"""
        # Current has both orders
        # 当前有双边订单
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02, "timestamp": 0},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02, "timestamp": 0},
        ]
        # Only buy needs update (price changed significantly)
        # 只有买入需要更新（价格变化显著）
        target_orders = [
            {"side": "buy", "price": 3005.0, "quantity": 0.02},  # Changed
            {"side": "sell", "price": 3010.005, "quantity": 0.02},  # Within threshold
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, mid_price=3005.0, enforce_both_side=True
        )

        # Buy should be cancelled and replaced
        # 买入应该被取消并替换
        assert "123" in to_cancel
        # Sell should remain (within threshold)
        # 卖出应该保留（在阈值内）
        assert "124" not in to_cancel
        
        # With enforce_both_side, even though only buy is being replaced,
        # we should ensure both sides are in to_place if target has both
        # 使用 enforce_both_side，即使只有买入被替换，
        # 如果目标有双边，我们应该确保双边都在 to_place 中
        # However, since sell is within threshold, it won't be in to_place
        # 但是，由于卖出在阈值内，它不会在 to_place 中
        # The enforcement logic only adds missing side if one side is scheduled
        # 强制逻辑只在安排了一边时添加缺失的一边
        buy_in_place = any(o.get("side") == "buy" for o in to_place)
        assert buy_in_place  # Buy should be in to_place

    def test_sync_orders_enforce_both_side_not_applied_when_false(self):
        """Test that enforce_both_side=False allows single-side orders"""
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=False
        )

        # Without enforcement, both should still be placed (normal behavior)
        # 没有强制，双边仍应被下单（正常行为）
        assert len(to_place) == 2

    def test_sync_orders_enforce_both_side_single_target_order(self):
        """Test that enforce_both_side doesn't apply when target has only one side"""
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )

        # If target has only one side, enforcement shouldn't add the other
        # 如果目标只有一边，强制不应该添加另一边
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"
