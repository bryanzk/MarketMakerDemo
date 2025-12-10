"""
Integration tests for order stability window / 订单稳定性窗口集成测试

End-to-end tests verifying stability window integration with strategy instance and engine.
端到端测试验证稳定性窗口与策略实例和引擎的集成。

Owner: Agent QA
"""

import time
import unittest
from unittest.mock import Mock, patch

from src.trading.order_manager import OrderManager
from src.trading.strategy_instance import StrategyInstance
from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestOrderStabilityWindowIntegration(unittest.TestCase):
    """Integration tests for order stability window / 订单稳定性窗口集成测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.mock_exchange = Mock()
        self.mock_exchange.symbol = "ETH/USDT:USDT"
        self.mock_exchange.fetch_open_orders = Mock(return_value=[])
        self.mock_exchange.place_orders = Mock(return_value=[])
        self.mock_exchange.cancel_orders = Mock(return_value=None)
        
        self.strategy_instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            exchange=self.mock_exchange,
        )

    def test_strategy_instance_passes_volatility_to_order_manager(self):
        """
        Integration test: Verify strategy instance passes volatility to order manager.
        集成测试：验证策略实例将波动率传递给订单管理器。
        """
        current_time = time.time()
        
        # Set up market data with volatility
        # 设置包含波动率的市场数据
        market_data = {
            "mid_price": 1000.0,
            "best_bid": 999.0,
            "best_ask": 1001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.015,
        }
        self.strategy_instance.latest_market_data = market_data
        
        # Create a recent order (should be protected by extended window)
        # 创建一个新订单（应该受延长窗口保护）
        current_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        # Mock fetch_open_orders to return our current order
        # 模拟 fetch_open_orders 返回我们的当前订单
        self.mock_exchange.fetch_open_orders.return_value = [current_order]
        self.strategy_instance.tracked_order_ids.add("order_001")
        
        # Create target orders with different price
        # 创建价格不同的目标订单
        target_orders = [
            {
                "side": "buy",
                "price": 1050.0,  # Different price
                "quantity": 0.1,
            }
        ]
        
        # Sync orders (should use extended window due to low volatility)
        # 同步订单（由于低波动应使用延长窗口）
        to_cancel, to_place = self.strategy_instance.sync_orders(
            [current_order],
            target_orders,
        )
        
        # With low volatility, window should be extended to ~90s
        # 低波动时，窗口应延长至约 90 秒
        # Order is 50s old, so it should be protected
        # 订单是 50 秒前，所以应该被保护
        self.assertNotIn(current_order["id"], to_cancel,
                        "Order should be protected by extended window in low volatility")

    def test_engine_integrates_stability_window(self):
        """
        Integration test: Verify engine integrates stability window with order lifecycle.
        集成测试：验证引擎将稳定性窗口与订单生命周期集成。
        """
        from src.trading.engine import AlphaLoop
        
        # Create engine with mock exchange
        # 使用模拟交易所创建引擎
        mock_exchange = Mock()
        mock_exchange.symbol = "ETH/USDT:USDT"
        mock_exchange.fetch_open_orders = Mock(return_value=[])
        mock_exchange.place_orders = Mock(return_value=[
            {"id": "order_001", "side": "buy", "price": 1000.0, "quantity": 0.1}
        ])
        mock_exchange.cancel_orders = Mock(return_value=None)
        mock_exchange.fetch_market_data = Mock(return_value={
            "mid_price": 1000.0,
            "best_bid": 999.0,
            "best_ask": 1001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.015,
        })
        
        engine = AlphaLoop(hyperliquid_exchange=mock_exchange)
        engine.add_strategy_instance("test", "fixed_spread", exchange=mock_exchange)
        
        # Get the strategy instance
        # 获取策略实例
        instance = engine.strategy_instances.get("test")
        self.assertIsNotNone(instance, "Strategy instance should exist")
        
        # Verify order manager has stability window support
        # 验证订单管理器支持稳定性窗口
        self.assertIsNotNone(instance.order_manager, "Order manager should exist")
        self.assertTrue(hasattr(instance.order_manager, "_calculate_stability_window"),
                       "Order manager should have stability window calculation")

    def test_stability_window_with_realistic_order_flow(self):
        """
        Integration test: Verify stability window in realistic order flow scenario.
        集成测试：在真实订单流场景中验证稳定性窗口。
        """
        current_time = time.time()
        
        # Simulate order placement and subsequent price change
        # 模拟订单下单和随后的价格变化
        placed_order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 10,  # Just placed 10 seconds ago
        }
        
        # Add to tracked orders
        # 添加到跟踪订单
        self.strategy_instance.tracked_order_ids.add("order_001")
        
        # Market price moves, creating new target order
        # 市场价格移动，创建新的目标订单
        target_order = {
            "side": "buy",
            "price": 1020.0,  # 2% price change
            "quantity": 0.1,
        }
        
        # First sync: Order is too young, should be protected
        # 第一次同步：订单太新，应该被保护
        to_cancel_1, to_place_1 = self.strategy_instance.sync_orders(
            [placed_order],
            [target_order],
        )
        
        self.assertNotIn(placed_order["id"], to_cancel_1,
                         "Order should be protected in first sync")
        
        # Wait for stability window to pass (simulate time passing)
        # 等待稳定性窗口过去（模拟时间流逝）
        old_order = placed_order.copy()
        old_order["timestamp"] = current_time - 70  # Now 70 seconds old
        
        # Second sync: Order is old enough, should be cancelled
        # 第二次同步：订单足够旧，应该被取消
        to_cancel_2, to_place_2 = self.strategy_instance.sync_orders(
            [old_order],
            [target_order],
        )
        
        self.assertIn(old_order["id"], to_cancel_2,
                     "Order should be cancellable after stability window")
        self.assertEqual(len(to_place_2), 1, "New order should be placed")

    def test_stability_window_respects_volatility_changes(self):
        """
        Integration test: Verify stability window adapts to volatility changes.
        集成测试：验证稳定性窗口适应波动率变化。
        """
        current_time = time.time()
        
        # Order that's 50 seconds old (protected in low vol, cancellable in high vol)
        # 50 秒前的订单（低波动时受保护，高波动时可取消）
        order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1050.0,
            "quantity": 0.1,
        }
        
        # Low volatility: Extended window (~90s), order should be protected
        # 低波动：延长窗口（~90 秒），订单应该被保护
        market_data_low_vol = {
            "mid_price": 1000.0,
            "volatility_1h": 0.01,  # Low volatility
        }
        self.strategy_instance.latest_market_data = market_data_low_vol
        
        to_cancel_low, _ = self.strategy_instance.sync_orders(
            [order],
            [target_order],
        )
        self.assertNotIn(order["id"], to_cancel_low,
                         "Order should be protected in low volatility")
        
        # High volatility: Shortened window (~45s), order should be cancelled
        # 高波动：缩短窗口（~45 秒），订单应该被取消
        # Use a slightly older order (55s) to ensure it's definitely cancellable
        # 使用稍旧的订单（55 秒）以确保它肯定可以被取消
        current_time_high_vol = time.time()
        order_high_vol = {
            "id": "order_002",  # Different ID to avoid confusion
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time_high_vol - 55,  # 55 seconds old (definitely > 45s)
        }
        
        # Add to tracked orders so it's not filtered out
        # 添加到跟踪订单，这样它不会被过滤掉
        self.strategy_instance.tracked_order_ids.add("order_002")
        
        market_data_high_vol = {
            "mid_price": 1000.0,
            "volatility_1h": 0.08,  # High volatility (window = 60 * 0.75 = 45s)
        }
        self.strategy_instance.latest_market_data = market_data_high_vol
        
        to_cancel_high, _ = self.strategy_instance.sync_orders(
            [order_high_vol],
            [target_order],
        )
        self.assertIn(order_high_vol["id"], to_cancel_high,
                     f"Order should be cancellable in high volatility (55s > 45s window), got to_cancel={to_cancel_high}")

    def test_stability_window_with_missing_volatility_data(self):
        """
        Integration test: Verify stability window uses default when volatility data is missing.
        集成测试：验证当波动率数据缺失时，稳定性窗口使用默认值。
        """
        current_time = time.time()
        
        # Order that's 50 seconds old
        # 50 秒前的订单
        order = {
            "id": "order_001",
            "side": "buy",
            "price": 1000.0,
            "quantity": 0.1,
            "timestamp": current_time - 50,  # 50 seconds old
        }
        
        target_order = {
            "side": "buy",
            "price": 1050.0,
            "quantity": 0.1,
        }
        
        # No volatility data: Should use default 60s window
        # 没有波动率数据：应该使用默认 60 秒窗口
        self.strategy_instance.latest_market_data = {
            "mid_price": 1000.0,
            # No volatility fields
        }
        
        to_cancel, _ = self.strategy_instance.sync_orders(
            [order],
            [target_order],
        )
        
        # Order is 50s old, default window is 60s, so it should be protected
        # 订单是 50 秒前，默认窗口是 60 秒，所以应该被保护
        self.assertNotIn(order["id"], to_cancel,
                         "Order should be protected with default window when volatility is missing")


if __name__ == "__main__":
    unittest.main()

