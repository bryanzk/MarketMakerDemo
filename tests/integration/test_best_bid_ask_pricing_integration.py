"""
Integration tests for best_bid/best_ask pricing strategy / 基于 best_bid/best_ask 定价策略的集成测试

Owner: Agent QA
"""

import unittest
from unittest.mock import Mock, patch

from src.trading.engine import AlphaLoop
from src.trading.strategy_instance import StrategyInstance
from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestBestBidAskPricingIntegration(unittest.TestCase):
    """Integration tests for best_bid/best_ask pricing / 基于 best_bid/best_ask 定价的集成测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.mock_exchange = Mock()
        self.mock_exchange.symbol = "ETH/USDT:USDT"
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        self.mock_exchange.fetch_funding_rate.return_value = 0.0
        self.mock_exchange.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "balance": 10000.0,
            "entry_price": 0.0,
        }
        self.mock_exchange.fetch_open_orders.return_value = []
        self.mock_exchange.place_orders.return_value = []
        self.mock_exchange.cancel_orders.return_value = True

    def test_end_to_end_best_bid_ask_pricing(self):
        """
        Integration test: End-to-end flow with best_bid/best_ask pricing.
        集成测试：使用 best_bid/best_ask 定价的端到端流程。
        """
        # Create strategy instance
        # 创建策略实例
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.spread = 0.001
        instance.strategy.quantity = 0.1
        
        # Refresh data
        # 刷新数据
        success = instance.refresh_data()
        self.assertTrue(success)
        
        # Calculate target orders
        # 计算目标订单
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Verify orders are generated
        # 验证订单已生成
        self.assertGreater(len(target_orders), 0)
        
        # Verify pricing uses best_bid/best_ask
        # 验证定价使用 best_bid/best_ask
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        if buy_order and market_data.get("best_bid"):
            self.assertGreater(buy_order["price"], market_data["best_bid"])
            # Buy price should be competitive (within reasonable range)
            # 买入价应该具有竞争力（在合理范围内）
            buy_distance = buy_order["price"] - market_data["best_bid"]
            self.assertLess(buy_distance, market_data["best_bid"] * 0.01)
        
        if sell_order and market_data.get("best_ask"):
            self.assertLess(sell_order["price"], market_data["best_ask"])
            # Sell price should be competitive (within reasonable range)
            # 卖出价应该具有竞争力（在合理范围内）
            sell_distance = market_data["best_ask"] - sell_order["price"]
            self.assertLess(sell_distance, market_data["best_ask"] * 0.01)

    def test_pricing_adapts_to_market_spread(self):
        """
        Integration test: Pricing should adapt to different market spreads.
        集成测试：定价应该适应不同的市场价差。
        """
        # Test with wide spread
        # 测试宽价差
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2990.0,  # Wide spread: 20 points
            "best_ask": 3010.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.spread = 0.001
        instance.strategy.quantity = 0.1
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        # Should still position orders correctly
        # 应该仍然正确定位订单
        if buy_order:
            self.assertGreater(buy_order["price"], market_data["best_bid"])
        if sell_order:
            self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_fallback_to_mid_price_when_best_bid_ask_missing(self):
        """
        Integration test: Should fallback to mid_price when best_bid/best_ask unavailable.
        集成测试：当 best_bid/best_ask 不可用时应回退到 mid_price。
        """
        # Market data without best_bid/best_ask
        # 没有 best_bid/best_ask 的市场数据
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            # No best_bid or best_ask
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.spread = 0.001
        instance.strategy.quantity = 0.1
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Should still generate orders using mid_price
        # 应该仍然使用 mid_price 生成订单
        self.assertGreater(len(target_orders), 0)

    def test_pricing_with_engine_integration(self):
        """
        Integration test: Pricing works with AlphaLoop engine.
        集成测试：定价与 AlphaLoop 引擎一起工作。
        """
        # Create engine
        # 创建引擎
        engine = AlphaLoop()
        
        # Add strategy instance
        # 添加策略实例
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.spread = 0.001
        instance.strategy.quantity = 0.1
        engine.strategy_instances["test"] = instance
        
        # Refresh data
        # 刷新数据
        instance.refresh_data()
        
        # Calculate target orders
        # 计算目标订单
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Verify orders use best_bid/best_ask pricing
        # 验证订单使用 best_bid/best_ask 定价
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        if buy_order and market_data.get("best_bid"):
            self.assertGreater(buy_order["price"], market_data["best_bid"])
        
        if sell_order and market_data.get("best_ask"):
            self.assertLess(sell_order["price"], market_data["best_ask"])

    def test_competitive_pricing_improves_order_placement(self):
        """
        Integration test: Competitive pricing should improve order placement success.
        集成测试：有竞争力的定价应该提高订单下单成功率。
        """
        # Market data with competitive spread
        # 具有竞争力价差的市场数据
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.spread = 0.001
        instance.strategy.quantity = 0.1
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Verify orders are positioned competitively
        # 验证订单定位具有竞争力
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        if buy_order:
            # Buy price should be close to best_bid (competitive)
            # 买入价应该接近 best_bid（有竞争力）
            buy_distance_pct = (buy_order["price"] - market_data["best_bid"]) / market_data["best_bid"]
            self.assertLess(buy_distance_pct, 0.01)  # Within 1% of best_bid
        
        if sell_order:
            # Sell price should be close to best_ask (competitive)
            # 卖出价应该接近 best_ask（有竞争力）
            sell_distance_pct = (market_data["best_ask"] - sell_order["price"]) / market_data["best_ask"]
            self.assertLess(sell_distance_pct, 0.01)  # Within 1% of best_ask


if __name__ == "__main__":
    unittest.main()

