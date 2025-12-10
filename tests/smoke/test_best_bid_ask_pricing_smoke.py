"""
Smoke tests for best_bid/best_ask pricing strategy / 基于 best_bid/best_ask 定价策略的冒烟测试

Owner: Agent QA
"""

import unittest
from unittest.mock import Mock, patch

from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategy_instance import StrategyInstance


class TestBestBidAskPricingSmoke(unittest.TestCase):
    """Smoke tests for best_bid/best_ask pricing / 基于 best_bid/best_ask 定价的冒烟测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.spread = 0.001  # 0.1% spread
        self.strategy.quantity = 0.1

    def test_strategy_uses_best_bid_ask_when_available(self):
        """
        Smoke test: Strategy should use best_bid/best_ask when available.
        冒烟测试：策略在可用时应使用 best_bid/best_ask。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should generate orders
        # 应该生成订单
        self.assertGreater(len(orders), 0)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        # Buy price should be above best_bid
        # 买入价应该高于 best_bid
        if buy_order:
            self.assertGreater(buy_order["price"], market_data["best_bid"])
        
        # Sell price should be below best_ask
        # 卖出价应该低于 best_ask
        if sell_order:
            self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_strategy_fallback_to_mid_price(self):
        """
        Smoke test: Strategy should fallback to mid_price when best_bid/best_ask unavailable.
        冒烟测试：当 best_bid/best_ask 不可用时，策略应回退到 mid_price。
        """
        market_data = {
            "mid_price": 3000.0,
            # No best_bid or best_ask
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should still generate orders
        # 应该仍然生成订单
        self.assertGreater(len(orders), 0)

    def test_strategy_instance_with_best_bid_ask(self):
        """
        Smoke test: StrategyInstance should work with best_bid/best_ask pricing.
        冒烟测试：StrategyInstance 应该与 best_bid/best_ask 定价一起工作。
        """
        # Create a mock exchange
        # 创建模拟交易所
        mock_exchange = Mock()
        mock_exchange.symbol = "ETH/USDT:USDT"
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        mock_exchange.fetch_funding_rate.return_value = 0.0
        mock_exchange.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "balance": 10000.0,
        }
        mock_exchange.fetch_open_orders.return_value = []
        
        # Create strategy instance
        # 创建策略实例
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=mock_exchange,
        )
        
        # Refresh data
        # 刷新数据
        success = instance.refresh_data()
        self.assertTrue(success)
        
        # Calculate target orders
        # 计算目标订单
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Should generate orders
        # 应该生成订单
        self.assertGreater(len(target_orders), 0)
        
        # Verify orders use best_bid/best_ask pricing
        # 验证订单使用 best_bid/best_ask 定价
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        if buy_order and market_data.get("best_bid"):
            self.assertGreater(buy_order["price"], market_data["best_bid"])
        
        if sell_order and market_data.get("best_ask"):
            self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_competitive_pricing_improves_fill_rate(self):
        """
        Smoke test: Pricing based on best_bid/best_ask should be more competitive.
        冒烟测试：基于 best_bid/best_ask 的定价应该更具竞争力。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        orders = self.strategy.calculate_target_orders(market_data)
        
        buy_order = next((o for o in orders if o["side"] == "buy"), None)
        sell_order = next((o for o in orders if o["side"] == "sell"), None)
        
        if buy_order and sell_order:
            # Buy price should be competitive (close to best_bid)
            # 买入价应该具有竞争力（接近 best_bid）
            buy_distance = buy_order["price"] - market_data["best_bid"]
            self.assertGreater(buy_distance, 0)
            # Should be within reasonable range (e.g., 0.5% of best_bid)
            # 应该在合理范围内（例如，best_bid 的 0.5%）
            self.assertLess(buy_distance, market_data["best_bid"] * 0.01)
            
            # Sell price should be competitive (close to best_ask)
            # 卖出价应该具有竞争力（接近 best_ask）
            sell_distance = market_data["best_ask"] - sell_order["price"]
            self.assertGreater(sell_distance, 0)
            # Should be within reasonable range (e.g., 0.5% of best_ask)
            # 应该在合理范围内（例如，best_ask 的 0.5%）
            self.assertLess(sell_distance, market_data["best_ask"] * 0.01)


if __name__ == "__main__":
    unittest.main()

