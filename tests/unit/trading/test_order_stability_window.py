"""
Unit tests for order stability window / 订单稳定性窗口单元测试

Tests extended order stability window to give orders more time to fill.
测试延长的订单稳定性窗口，给订单更多时间成交。

Owner: Agent QA
"""

import time
import unittest
from unittest.mock import Mock, patch

from src.trading.order_manager import OrderManager


class TestOrderStabilityWindow(unittest.TestCase):
    """Test order stability window / 测试订单稳定性窗口"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.order_manager = OrderManager()

    def test_orders_younger_than_min_age_not_cancelled(self):
        """
        Test that orders younger than MIN_ORDER_AGE_SECONDS are not cancelled.
        测试小于 MIN_ORDER_AGE_SECONDS 的订单不会被取消。
        """
        # Create a current order with recent timestamp
        # 创建一个带有最近时间戳的当前订单
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 20,  # 20 seconds old (less than 60s minimum)
        }
        
        # Target order with different price (would normally trigger cancellation)
        # 目标订单价格不同（通常会触发取消）
        target_order = {
            "side": "buy",
            "price": 1010.0,  # Different price
            "quantity": 0.1,
        }
        
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1005.0,
            min_order_age_seconds=60.0,  # 60 seconds minimum age
        )
        
        # Order should NOT be cancelled because it's too young
        # 订单不应该被取消，因为它太新了
        self.assertNotIn(current_order["id"], to_cancel)
        self.assertEqual(len(to_place), 0)  # No new order to place

    def test_orders_older_than_min_age_can_be_cancelled(self):
        """
        Test that orders older than MIN_ORDER_AGE_SECONDS can be cancelled.
        测试大于 MIN_ORDER_AGE_SECONDS 的订单可以被取消。
        """
        # Create a current order with old timestamp
        # 创建一个带有旧时间戳的当前订单
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 70,  # 70 seconds old (more than 60s minimum)
        }
        
        # Target order with different price
        # 目标订单价格不同
        target_order = {
            "side": "buy",
            "price": 1010.0,  # Different price
            "quantity": 0.1,
        }
        
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1005.0,
            min_order_age_seconds=60.0,
        )
        
        # Order should be cancelled because it's old enough
        # 订单应该被取消，因为它足够旧了
        self.assertIn(current_order["id"], to_cancel)
        self.assertEqual(len(to_place), 1)  # New order to place

    def test_dynamic_stability_window_low_volatility(self):
        """
        Test that stability window is extended in low volatility markets.
        测试在低波动市场中稳定性窗口被延长。
        """
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1010.0,  # Different price
            "quantity": 0.1,
        }
        
        # Low volatility: should use extended window (e.g., 90 seconds)
        # 低波动：应该使用延长的窗口（例如，90 秒）
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1005.0,
            min_order_age_seconds=90.0,  # Extended window for low volatility
            volatility_1h=0.01,  # Low volatility: 1%
        )
        
        # Order should NOT be cancelled (50s < 90s)
        # 订单不应该被取消（50秒 < 90秒）
        self.assertNotIn(current_order["id"], to_cancel)

    def test_dynamic_stability_window_high_volatility(self):
        """
        Test that stability window is shorter in high volatility markets.
        测试在高波动市场中稳定性窗口更短。
        """
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1010.0,  # Different price
            "quantity": 0.1,
        }
        
        # High volatility: should use shorter window (e.g., 30 seconds)
        # 高波动：应该使用更短的窗口（例如，30 秒）
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1005.0,
            min_order_age_seconds=30.0,  # Shorter window for high volatility
            volatility_1h=0.10,  # High volatility: 10%
        )
        
        # Order should be cancelled (50s > 30s)
        # 订单应该被取消（50秒 > 30秒）
        self.assertIn(current_order["id"], to_cancel)

    def test_stability_window_with_no_timestamp(self):
        """
        Test that orders without timestamp are treated as old enough to cancel.
        测试没有时间戳的订单被视为足够旧可以取消。
        """
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            # No timestamp field
        }
        
        target_order = {
            "side": "buy",
            "price": 1010.0,  # Different price
            "quantity": 0.1,
        }
        
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1005.0,
            min_order_age_seconds=60.0,
        )
        
        # Order without timestamp should be cancellable (assumed old)
        # 没有时间戳的订单应该可以取消（假设为旧订单）
        self.assertIn(current_order["id"], to_cancel)

    def test_stability_window_respects_price_threshold(self):
        """
        Test that stability window only applies when price difference exceeds threshold.
        测试稳定性窗口仅在价格差异超过阈值时适用。
        """
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 20,  # 20 seconds old
        }
        
        # Target order with small price difference (within threshold)
        # 目标订单价格差异很小（在阈值内）
        target_order = {
            "side": "buy",
            "price": 1000.005,  # Very small difference (< 0.01 threshold)
            "quantity": 0.1,
        }
        
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            mid_price=1000.0,
            min_order_age_seconds=60.0,
        )
        
        # Should not cancel because price difference is too small
        # 不应该取消，因为价格差异太小
        self.assertNotIn(current_order["id"], to_cancel)
        self.assertEqual(len(to_place), 0)

    def test_stability_window_does_not_apply_to_missing_target(self):
        """
        Test that stability window does not prevent cancellation when target order is missing.
        测试当目标订单缺失时，稳定性窗口不会阻止取消。
        """
        current_time = time.time()
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 20,  # 20 seconds old
        }
        
        # No target order (should cancel regardless of age)
        # 没有目标订单（无论年龄都应该取消）
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [],  # No target orders
            mid_price=1000.0,
            min_order_age_seconds=60.0,
        )
        
        # Should cancel even if order is young (no target order)
        # 即使订单很新也应该取消（没有目标订单）
        self.assertIn(current_order["id"], to_cancel)

    def test_volatility_based_window_calculation(self):
        """
        Test that window is calculated based on volatility levels.
        测试窗口根据波动率级别计算。
        """
        # Test low volatility -> extended window
        # 测试低波动 -> 延长窗口
        window_low = self.order_manager._calculate_stability_window(
            volatility_1h=0.01,  # Low volatility
            base_min_age=60.0,
        )
        self.assertGreater(window_low, 60.0)  # Should be extended
        
        # Test medium volatility -> base window
        # 测试中等波动 -> 基础窗口
        window_medium = self.order_manager._calculate_stability_window(
            volatility_1h=0.03,  # Medium volatility
            base_min_age=60.0,
        )
        self.assertEqual(window_medium, 60.0)  # Should be base
        
        # Test high volatility -> shorter window
        # 测试高波动 -> 更短窗口
        window_high = self.order_manager._calculate_stability_window(
            volatility_1h=0.10,  # High volatility
            base_min_age=60.0,
        )
        self.assertLess(window_high, 60.0)  # Should be shorter


if __name__ == "__main__":
    unittest.main()

