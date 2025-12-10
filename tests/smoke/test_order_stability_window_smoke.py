"""
Smoke tests for order stability window / 订单稳定性窗口冒烟测试

Quick verification that stability window works in realistic scenarios.
快速验证稳定性窗口在真实场景中工作。

Owner: Agent QA
"""

import time
import unittest
from unittest.mock import Mock, patch

from src.trading.order_manager import OrderManager


class TestOrderStabilityWindowSmoke(unittest.TestCase):
    """Smoke tests for order stability window / 订单稳定性窗口冒烟测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.order_manager = OrderManager()

    def test_stability_window_prevents_premature_cancellation(self):
        """
        Smoke test: Verify that stability window prevents premature cancellation.
        冒烟测试：验证稳定性窗口防止过早取消。
        """
        current_time = time.time()
        
        # Create a very recent order (10 seconds old)
        # 创建一个非常新的订单（10 秒前）
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 10,  # 10 seconds old
        }
        
        # Target order with significantly different price
        # 目标订单价格显著不同
        target_order = {
            "side": "buy",
            "price": 1050.0,  # 5% difference
            "quantity": 0.1,
        }
        
        # With default 60s window, order should NOT be cancelled
        # 使用默认 60 秒窗口，订单不应该被取消
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
        )
        
        # Verify order is protected by stability window
        # 验证订单受稳定性窗口保护
        self.assertNotIn(current_order["id"], to_cancel, 
                        "Order should be protected by stability window")
        self.assertEqual(len(to_place), 0, "No new order should be placed")

    def test_stability_window_allows_cancellation_after_time(self):
        """
        Smoke test: Verify that stability window allows cancellation after time.
        冒烟测试：验证稳定性窗口在时间过后允许取消。
        """
        current_time = time.time()
        
        # Create an old order (70 seconds old)
        # 创建一个旧订单（70 秒前）
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 70,  # 70 seconds old
        }
        
        # Target order with different price
        # 目标订单价格不同
        target_order = {
            "side": "buy",
            "price": 1050.0,  # Different price
            "quantity": 0.1,
        }
        
        # With default 60s window, order should be cancelled
        # 使用默认 60 秒窗口，订单应该被取消
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
        )
        
        # Verify order can be cancelled after stability window
        # 验证订单在稳定性窗口后可以被取消
        self.assertIn(current_order["id"], to_cancel,
                     "Order should be cancellable after stability window")
        self.assertEqual(len(to_place), 1, "New order should be placed")

    def test_low_volatility_extends_window(self):
        """
        Smoke test: Verify that low volatility extends stability window.
        冒烟测试：验证低波动延长稳定性窗口。
        """
        current_time = time.time()
        
        # Create an order that's 50 seconds old
        # 创建一个 50 秒前的订单
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1050.0,  # Different price
            "quantity": 0.1,
        }
        
        # With low volatility, window should be extended to ~90s (60 * 1.5)
        # 低波动时，窗口应延长至约 90 秒（60 * 1.5）
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            volatility_1h=0.01,  # Low volatility: 1%
        )
        
        # Order should NOT be cancelled (50s < 90s extended window)
        # 订单不应该被取消（50 秒 < 90 秒延长窗口）
        self.assertNotIn(current_order["id"], to_cancel,
                        "Order should be protected by extended window in low volatility")

    def test_high_volatility_shortens_window(self):
        """
        Smoke test: Verify that high volatility shortens stability window.
        冒烟测试：验证高波动缩短稳定性窗口。
        """
        current_time = time.time()
        
        # Create an order that's 50 seconds old
        # 创建一个 50 秒前的订单
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1050.0,  # Different price
            "quantity": 0.1,
        }
        
        # With high volatility, window should be shortened to ~45s (60 * 0.75)
        # 高波动时，窗口应缩短至约 45 秒（60 * 0.75）
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_order],
            [target_order],
            volatility_1h=0.08,  # High volatility: 8%
        )
        
        # Order should be cancelled (50s > 45s shortened window)
        # 订单应该被取消（50 秒 > 45 秒缩短窗口）
        self.assertIn(current_order["id"], to_cancel,
                     "Order should be cancellable with shortened window in high volatility")

    def test_stability_window_with_both_sides(self):
        """
        Smoke test: Verify stability window works for both buy and sell orders.
        冒烟测试：验证稳定性窗口对买入和卖出订单都有效。
        """
        current_time = time.time()
        
        # Create both buy and sell orders
        # 创建买入和卖出订单
        current_buy = {
            "id": "buy_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 10,  # 10 seconds old (too young)
        }
        
        current_sell = {
            "id": "sell_001",
            "side": "sell",
            "price": 1010.0,
            "quantity": 0.1,
            "timestamp": current_time - 70,  # 70 seconds old (old enough)
        }
        
        target_buy = {
            "side": "buy",
            "price": 1050.0,  # Different price
            "quantity": 0.1,
        }
        
        target_sell = {
            "side": "sell",
            "price": 1060.0,  # Different price
            "quantity": 0.1,
        }
        
        to_cancel, to_place = self.order_manager.sync_orders(
            [current_buy, current_sell],
            [target_buy, target_sell],
        )
        
        # Buy order should be protected (too young)
        # 买入订单应该被保护（太新）
        self.assertNotIn(current_buy["id"], to_cancel,
                        "Buy order should be protected by stability window")
        
        # Sell order should be cancelled (old enough)
        # 卖出订单应该被取消（足够旧）
        self.assertIn(current_sell["id"], to_cancel,
                     "Sell order should be cancellable after stability window")
        
        # Only sell order should trigger a new placement
        # 只有卖出订单应该触发新下单
        self.assertEqual(len(to_place), 1, "Only sell order should trigger placement")
        self.assertEqual(to_place[0]["side"], "sell", "New order should be sell")


if __name__ == "__main__":
    unittest.main()

