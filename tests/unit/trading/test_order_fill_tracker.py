"""
Unit tests for OrderFillTracker / 订单填充跟踪器单元测试

Owner: Agent QA
"""

import time
import unittest
from unittest.mock import Mock, patch

from src.trading.order_fill_tracker import OrderFillTracker


class TestOrderFillTracker(unittest.TestCase):
    """Test OrderFillTracker class / 测试 OrderFillTracker 类"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.tracker = OrderFillTracker(max_history=100)

    def test_track_order_placed(self):
        """Test tracking order placement / 测试跟踪订单下单"""
        order_id = "test_order_001"
        self.tracker.track_order_placed(
            order_id=order_id,
            side="buy",
            price=1000.0,
            quantity=0.1,
            symbol="ETH/USDT:USDT",
            strategy_id="test_strategy",
            strategy_type="fixed_spread",
        )
        
        # Check order is in active orders
        # 检查订单在活跃订单中
        self.assertIn(order_id, self.tracker.active_orders)
        order_info = self.tracker.active_orders[order_id]
        self.assertEqual(order_info["side"], "buy")
        self.assertEqual(order_info["price"], 1000.0)
        self.assertEqual(order_info["quantity"], 0.1)
        self.assertEqual(order_info["status"], "placed")
        
        # Check statistics
        # 检查统计
        self.assertEqual(self.tracker.total_orders_placed, 1)
        self.assertEqual(self.tracker.recent_orders_placed, 1)

    def test_track_order_filled(self):
        """Test tracking order fill / 测试跟踪订单成交"""
        order_id = "test_order_001"
        self.tracker.track_order_placed(
            order_id=order_id,
            side="buy",
            price=1000.0,
            quantity=0.1,
            symbol="ETH/USDT:USDT",
            strategy_id="test_strategy",
            strategy_type="fixed_spread",
        )
        
        # Fill the order
        # 成交订单
        result = self.tracker.track_order_filled(
            order_id=order_id,
            filled_quantity=0.1,
            fill_price=1000.5,
        )
        
        self.assertTrue(result)
        # Order should be removed from active orders
        # 订单应从活跃订单中移除
        self.assertNotIn(order_id, self.tracker.active_orders)
        
        # Check statistics
        # 检查统计
        self.assertEqual(self.tracker.total_orders_filled, 1)
        self.assertEqual(self.tracker.recent_orders_filled, 1)

    def test_track_order_partially_filled(self):
        """Test tracking partial fill / 测试跟踪部分成交"""
        order_id = "test_order_001"
        self.tracker.track_order_placed(
            order_id=order_id,
            side="buy",
            price=1000.0,
            quantity=0.1,
            symbol="ETH/USDT:USDT",
            strategy_id="test_strategy",
            strategy_type="fixed_spread",
        )
        
        # Partially fill the order
        # 部分成交订单
        result = self.tracker.track_order_filled(
            order_id=order_id,
            filled_quantity=0.05,
            fill_price=1000.5,
        )
        
        self.assertTrue(result)
        # Order should still be in active orders
        # 订单应仍在活跃订单中
        self.assertIn(order_id, self.tracker.active_orders)
        order_info = self.tracker.active_orders[order_id]
        self.assertEqual(order_info["status"], "partially_filled")
        self.assertEqual(order_info["filled_quantity"], 0.05)
        
        # Check statistics
        # 检查统计
        self.assertEqual(self.tracker.total_orders_partial_filled, 1)

    def test_track_order_cancelled(self):
        """Test tracking order cancellation / 测试跟踪订单取消"""
        order_id = "test_order_001"
        self.tracker.track_order_placed(
            order_id=order_id,
            side="buy",
            price=1000.0,
            quantity=0.1,
            symbol="ETH/USDT:USDT",
            strategy_id="test_strategy",
            strategy_type="fixed_spread",
        )
        
        # Cancel the order
        # 取消订单
        result = self.tracker.track_order_cancelled(
            order_id=order_id,
            reason="sync_update",
        )
        
        self.assertTrue(result)
        # Order should be removed from active orders
        # 订单应从活跃订单中移除
        self.assertNotIn(order_id, self.tracker.active_orders)
        
        # Check statistics
        # 检查统计
        self.assertEqual(self.tracker.total_orders_cancelled, 1)
        self.assertEqual(self.tracker.recent_orders_cancelled, 1)

    def test_get_fill_rate(self):
        """Test fill rate calculation / 测试成交率计算"""
        # Place 10 orders
        # 下单 10 个订单
        for i in range(10):
            self.tracker.track_order_placed(
                order_id=f"order_{i}",
                side="buy",
                price=1000.0,
                quantity=0.1,
                symbol="ETH/USDT:USDT",
                strategy_id="test_strategy",
                strategy_type="fixed_spread",
            )
        
        # Fill 7 orders
        # 成交 7 个订单
        for i in range(7):
            self.tracker.track_order_filled(
                order_id=f"order_{i}",
                filled_quantity=0.1,
                fill_price=1000.0,
            )
        
        # Cancel 2 orders
        # 取消 2 个订单
        for i in range(7, 9):
            self.tracker.track_order_cancelled(
                order_id=f"order_{i}",
                reason="sync_update",
            )
        
        # Fill rate should be 7/10 = 0.7
        # 成交率应为 7/10 = 0.7
        fill_rate = self.tracker.get_fill_rate()
        self.assertAlmostEqual(fill_rate, 0.7, places=2)
        
        # Cancellation rate should be 2/10 = 0.2
        # 取消率应为 2/10 = 0.2
        cancellation_rate = self.tracker.get_cancellation_rate()
        self.assertAlmostEqual(cancellation_rate, 0.2, places=2)

    def test_get_fill_rate_no_orders(self):
        """Test fill rate with no orders / 测试无订单时的成交率"""
        fill_rate = self.tracker.get_fill_rate()
        self.assertEqual(fill_rate, 0.0)
        
        cancellation_rate = self.tracker.get_cancellation_rate()
        self.assertEqual(cancellation_rate, 0.0)

    def test_update_order_status_from_exchange(self):
        """Test updating order status from exchange / 测试从交易所更新订单状态"""
        # Place 3 orders
        # 下单 3 个订单
        for i in range(3):
            self.tracker.track_order_placed(
                order_id=f"order_{i}",
                side="buy",
                price=1000.0,
                quantity=0.1,
                symbol="ETH/USDT:USDT",
                strategy_id="test_strategy",
                strategy_type="fixed_spread",
            )
        
        # Exchange only has order_0 and order_1 (order_2 was filled)
        # 交易所只有 order_0 和 order_1（order_2 已成交）
        exchange_orders = [
            {"id": "order_0", "side": "buy", "price": 1000.0, "quantity": 0.1},
            {"id": "order_1", "side": "buy", "price": 1000.0, "quantity": 0.1},
        ]
        
        self.tracker.update_order_status_from_exchange(exchange_orders)
        
        # order_2 should be marked as filled
        # order_2 应被标记为已成交
        self.assertNotIn("order_2", self.tracker.active_orders)
        self.assertEqual(self.tracker.total_orders_filled, 1)

    def test_update_order_status_partial_fill(self):
        """Test updating order status with partial fill / 测试部分成交的订单状态更新"""
        order_id = "order_001"
        self.tracker.track_order_placed(
            order_id=order_id,
            side="buy",
            price=1000.0,
            quantity=0.1,
            symbol="ETH/USDT:USDT",
            strategy_id="test_strategy",
            strategy_type="fixed_spread",
        )
        
        # Exchange shows partial fill
        # 交易所显示部分成交
        exchange_orders = [
            {
                "id": order_id,
                "side": "buy",
                "price": 1000.0,
                "quantity": 0.1,
                "filled_quantity": 0.05,
                "fill_price": 1000.5,
            }
        ]
        
        self.tracker.update_order_status_from_exchange(exchange_orders)
        
        # Order should be partially filled
        # 订单应部分成交
        self.assertIn(order_id, self.tracker.active_orders)
        order_info = self.tracker.active_orders[order_id]
        self.assertEqual(order_info["status"], "partially_filled")
        self.assertEqual(order_info["filled_quantity"], 0.05)

    def test_get_average_order_age(self):
        """Test average order age calculation / 测试平均订单存活时间计算"""
        # Place and fill orders with different ages
        # 下单并成交不同存活时间的订单
        base_time = time.time()
        
        for i in range(3):
            with patch("time.time", return_value=base_time + i * 10):
                self.tracker.track_order_placed(
                    order_id=f"order_{i}",
                    side="buy",
                    price=1000.0,
                    quantity=0.1,
                    symbol="ETH/USDT:USDT",
                    strategy_id="test_strategy",
                    strategy_type="fixed_spread",
                )
        
        # Fill orders at different times
        # 在不同时间成交订单
        for i in range(3):
            with patch("time.time", return_value=base_time + i * 10 + 5):
                self.tracker.track_order_filled(
                    order_id=f"order_{i}",
                    filled_quantity=0.1,
                    fill_price=1000.0,
                )
        
        # Average age should be 5 seconds
        # 平均存活时间应为 5 秒
        avg_age = self.tracker.get_average_order_age(status="filled")
        self.assertAlmostEqual(avg_age, 5.0, places=1)

    def test_get_statistics(self):
        """Test getting comprehensive statistics / 测试获取综合统计"""
        # Place and fill some orders
        # 下单并成交一些订单
        for i in range(5):
            self.tracker.track_order_placed(
                order_id=f"order_{i}",
                side="buy",
                price=1000.0,
                quantity=0.1,
                symbol="ETH/USDT:USDT",
                strategy_id="test_strategy",
                strategy_type="fixed_spread",
            )
        
        for i in range(3):
            self.tracker.track_order_filled(
                order_id=f"order_{i}",
                filled_quantity=0.1,
                fill_price=1000.0,
            )
        
        for i in range(3, 4):
            self.tracker.track_order_cancelled(
                order_id=f"order_{i}",
                reason="sync_update",
            )
        
        stats = self.tracker.get_statistics()
        
        self.assertEqual(stats["total_orders_placed"], 5)
        self.assertEqual(stats["total_orders_filled"], 3)
        self.assertEqual(stats["total_orders_cancelled"], 1)
        self.assertAlmostEqual(stats["fill_rate"], 0.6, places=2)
        self.assertAlmostEqual(stats["fill_rate_pct"], 60.0, places=2)
        self.assertAlmostEqual(stats["cancellation_rate"], 0.2, places=2)
        self.assertAlmostEqual(stats["cancellation_rate_pct"], 20.0, places=2)

    def test_reset_statistics(self):
        """Test resetting statistics / 测试重置统计"""
        # Place and fill some orders
        # 下单并成交一些订单
        for i in range(5):
            self.tracker.track_order_placed(
                order_id=f"order_{i}",
                side="buy",
                price=1000.0,
                quantity=0.1,
                symbol="ETH/USDT:USDT",
                strategy_id="test_strategy",
                strategy_type="fixed_spread",
            )
        
        for i in range(3):
            self.tracker.track_order_filled(
                order_id=f"order_{i}",
                filled_quantity=0.1,
                fill_price=1000.0,
            )
        
        # Reset statistics
        # 重置统计
        self.tracker.reset_statistics()
        
        # Statistics should be reset but history kept
        # 统计应被重置但历史保留
        self.assertEqual(self.tracker.total_orders_placed, 0)
        self.assertEqual(self.tracker.total_orders_filled, 0)
        self.assertEqual(self.tracker.total_orders_cancelled, 0)
        # History should still exist
        # 历史应仍存在
        self.assertGreater(len(self.tracker.order_history), 0)


if __name__ == "__main__":
    unittest.main()

