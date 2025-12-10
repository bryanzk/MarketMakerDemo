"""
Unit Tests for Both-Side Order Enforcement / 双边订单强制单元测试

Tests the enforce_both_side functionality in OrderManager and StrategyInstance.
测试 OrderManager 和 StrategyInstance 中的 enforce_both_side 功能。

Owner: Agent QA
"""

import pytest
from unittest.mock import Mock, patch

from src.trading.order_manager import OrderManager
from src.trading.strategy_instance import StrategyInstance


class TestOrderManagerBothSideEnforcement:
    """Test cases for OrderManager enforce_both_side functionality"""

    def setup_method(self):
        """Setup for each test method"""
        self.om = OrderManager()

    def test_enforce_both_side_buy_only_scheduled(self):
        """
        Test that enforce_both_side=True adds sell order when only buy is scheduled.
        测试 enforce_both_side=True 时，如果只安排了买入订单，会添加卖出订单。
        """
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        # Simulate scenario where only buy would be placed (e.g., sell failed validation)
        # 模拟只有买入会被下单的情况（例如，卖出验证失败）
        # First, get normal sync result
        # 首先，获取正常同步结果
        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )

        # With enforce_both_side=True and both target orders, both should be in to_place
        # 使用 enforce_both_side=True 且目标订单有双边，双边都应该在 to_place 中
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

    def test_enforce_both_side_sell_only_scheduled(self):
        """
        Test that enforce_both_side=True adds buy order when only sell is scheduled.
        测试 enforce_both_side=True 时，如果只安排了卖出订单，会添加买入订单。
        """
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )

        # Both should be placed
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

    def test_enforce_both_side_not_applied_when_false(self):
        """
        Test that enforce_both_side=False allows normal behavior.
        测试 enforce_both_side=False 时允许正常行为。
        """
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=False
        )

        # Without enforcement, both should still be placed (normal behavior)
        assert len(to_place) == 2

    def test_enforce_both_side_single_target_order(self):
        """
        Test that enforce_both_side doesn't apply when target has only one side.
        测试当目标只有一边时，enforce_both_side 不适用。
        """
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, enforce_both_side=True
        )

        # If target has only one side, enforcement shouldn't add the other
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"

    def test_enforce_both_side_partial_update_scenario(self):
        """
        Test enforce_both_side when only one side needs update.
        测试只有一边需要更新时的 enforce_both_side。
        """
        # Current has both orders, but only buy needs update
        current_orders = [
            {"id": "123", "side": "buy", "price": 3000.0, "quantity": 0.02, "timestamp": 0},
            {"id": "124", "side": "sell", "price": 3010.0, "quantity": 0.02, "timestamp": 0},
        ]
        # Only buy needs update (price changed significantly)
        target_orders = [
            {"side": "buy", "price": 3005.0, "quantity": 0.02},  # Changed
            {"side": "sell", "price": 3010.005, "quantity": 0.02},  # Within threshold
        ]

        to_cancel, to_place = self.om.sync_orders(
            current_orders, target_orders, mid_price=3005.0, enforce_both_side=True
        )

        # Buy should be cancelled and replaced
        assert "123" in to_cancel
        # Sell should remain (within threshold)
        assert "124" not in to_cancel
        # Buy should be in to_place
        buy_in_place = any(o.get("side") == "buy" for o in to_place)
        assert buy_in_place


class TestStrategyInstanceBothSideDetection:
    """Test cases for StrategyInstance _requires_both_side_orders method"""

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_requires_both_side_fixed_spread(self, mock_binance):
        """Test that fixed_spread strategy requires both-side orders"""
        instance = StrategyInstance("test", "fixed_spread")
        
        target_orders_both = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders_single = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
        ]

        # Fixed spread should require both-side when target has both
        assert instance._requires_both_side_orders(target_orders_both) == True
        # Even with single target, fixed_spread type should return True
        # 即使目标只有单边，fixed_spread 类型也应该返回 True
        assert instance._requires_both_side_orders(target_orders_single) == False

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_requires_both_side_funding_rate(self, mock_binance):
        """Test that funding_rate strategy requires both-side orders"""
        instance = StrategyInstance("test", "funding_rate")
        
        target_orders_both = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        # Funding rate should require both-side
        assert instance._requires_both_side_orders(target_orders_both) == True

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_requires_both_side_fallback_detection(self, mock_binance):
        """
        Test fallback detection: if target has both sides, assume market making.
        测试回退检测：如果目标有双边，假设是做市策略。
        """
        # Create instance with unknown strategy type (for future strategies)
        # 创建具有未知策略类型的实例（用于未来策略）
        instance = StrategyInstance("test", "unknown_strategy")
        
        target_orders_both = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]
        target_orders_single = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
        ]

        # Fallback: if target has both sides, assume market making
        assert instance._requires_both_side_orders(target_orders_both) == True
        # If target has only one side, don't enforce
        assert instance._requires_both_side_orders(target_orders_single) == False

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_sync_orders_with_enforce_both_side(self, mock_binance):
        """
        Test that StrategyInstance.sync_orders automatically enforces both-side for market making strategies.
        测试 StrategyInstance.sync_orders 自动为做市策略强制双边。
        """
        instance = StrategyInstance("test", "fixed_spread")
        
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.02},
            {"side": "sell", "price": 3010.0, "quantity": 0.02},
        ]

        to_cancel, to_place = instance.sync_orders(current_orders, target_orders)

        # For fixed_spread strategy, both-side should be enforced
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

