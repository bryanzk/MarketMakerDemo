"""
Integration tests for aggressive spread adjustment / 更激进价差调整集成测试

Owner: Agent QA
"""

import unittest
from unittest.mock import Mock

from src.trading.engine import AlphaLoop
from src.trading.strategy_instance import StrategyInstance
from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestAggressiveSpreadAdjustmentIntegration(unittest.TestCase):
    """Integration tests for aggressive spread adjustment / 更激进价差调整集成测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.mock_exchange = Mock()
        self.mock_exchange.symbol = "ETH/USDT:USDT"
        self.mock_exchange.fetch_funding_rate.return_value = 0.0
        self.mock_exchange.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "balance": 10000.0,
            "entry_price": 0.0,
        }
        self.mock_exchange.fetch_open_orders.return_value = []
        self.mock_exchange.place_orders.return_value = []
        self.mock_exchange.cancel_orders.return_value = True

    def test_end_to_end_aggressive_spread_adjustment(self):
        """
        Integration test: End-to-end flow with aggressive spread adjustment.
        集成测试：使用更激进价差调整的端到端流程。
        """
        # Market data with low volatility and small market spread
        # 具有低波动和小市场价差的市场数据
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.02,
            "market_spread": 0.0005,  # Small market spread
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        # Create strategy instance
        # 创建策略实例
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        
        # Refresh data
        # 刷新数据
        success = instance.refresh_data()
        self.assertTrue(success)
        
        # Calculate target orders (should trigger spread adjustment)
        # 计算目标订单（应该触发价差调整）
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Verify orders are generated
        # 验证订单已生成
        self.assertGreater(len(target_orders), 0)
        
        # Verify spread was adjusted (should be less than base spread)
        # 验证价差已调整（应该小于基础价差）
        adjusted_spread = instance.strategy.spread
        self.assertLess(adjusted_spread, instance.strategy.base_spread)

    def test_aggressive_adjustment_improves_fill_rate(self):
        """
        Integration test: Aggressive spread adjustment should improve fill rate.
        集成测试：更激进价差调整应该提高成交率。
        """
        # Low volatility + small market spread = aggressive pricing
        # 低波动 + 小市场价差 = 激进定价
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.02,
            "market_spread": 0.0005,  # Small market spread
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        
        # Calculate spread adjustment
        # 计算价差调整
        adjusted_spread = instance.strategy.calculate_adaptive_spread(
            volatility_1h=market_data.get("volatility_1h"),
            volatility_24h=market_data.get("volatility_24h"),
            market_spread=market_data.get("market_spread"),
        )
        
        # Adjusted spread should be much smaller (more aggressive)
        # 调整后的价差应该小得多（更激进）
        self.assertLess(adjusted_spread, instance.strategy.base_spread * 0.5)
        
        # Calculate target orders with adjusted spread
        # 使用调整后的价差计算目标订单
        target_orders = instance.calculate_target_orders(market_data)
        
        # Orders should be positioned competitively
        # 订单应该定位具有竞争力
        buy_order = next((o for o in target_orders if o["side"] == "buy"), None)
        sell_order = next((o for o in target_orders if o["side"] == "sell"), None)
        
        if buy_order and sell_order:
            # Spread between buy and sell should reflect adjusted spread
            # 买卖之间的价差应该反映调整后的价差
            order_spread = (sell_order["price"] - buy_order["price"]) / buy_order["price"]
            # Should be competitive (close to adjusted spread)
            # 应该具有竞争力（接近调整后的价差）
            self.assertLess(order_spread, instance.strategy.base_spread)

    def test_market_spread_priority_in_adjustment(self):
        """
        Integration test: Market spread should take priority when very small.
        集成测试：当市场价差很小时，应该优先考虑市场价差。
        """
        # Very small market spread, even with high volatility
        # 非常小的市场价差，即使在高波动率下
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.08,  # High volatility (would normally increase spread)
            "volatility_24h": 0.10,
            "market_spread": 0.0003,  # Very small market spread
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        
        # Calculate spread adjustment
        # 计算价差调整
        adjusted_spread = instance.strategy.calculate_adaptive_spread(
            volatility_1h=market_data.get("volatility_1h"),
            volatility_24h=market_data.get("volatility_24h"),
            market_spread=market_data.get("market_spread"),
        )
        
        # Market spread should influence adjustment (even with high volatility)
        # 市场价差应该影响调整（即使在高波动率下）
        # Should be adjusted based on market spread
        # 应该根据市场价差调整
        self.assertLess(adjusted_spread, market_data["market_spread"] * 5.0)

    def test_engine_integration_with_aggressive_adjustment(self):
        """
        Integration test: AlphaLoop engine works with aggressive spread adjustment.
        集成测试：AlphaLoop 引擎与更激进价差调整一起工作。
        """
        # Create engine
        # 创建引擎
        engine = AlphaLoop()
        
        # Market data with conditions for aggressive adjustment
        # 具有激进调整条件市场数据
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.02,
            "market_spread": 0.0005,  # Small market spread
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        # Add strategy instance
        # 添加策略实例
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        engine.strategy_instances["test"] = instance
        
        # Refresh data
        # 刷新数据
        instance.refresh_data()
        
        # Calculate target orders
        # 计算目标订单
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Verify spread was adjusted
        # 验证价差已调整
        adjusted_spread = instance.strategy.spread
        self.assertLess(adjusted_spread, instance.strategy.base_spread)
        
        # Verify orders are generated
        # 验证订单已生成
        self.assertGreater(len(target_orders), 0)

    def test_risk_limits_enforced_in_integration(self):
        """
        Integration test: Risk limits are enforced even with aggressive adjustment.
        集成测试：即使有激进调整，风险限制也会被执行。
        """
        from src.shared.config import RISK_LIMITS
        
        min_spread = RISK_LIMITS.get("MIN_SPREAD", 0.001)
        
        # Very aggressive conditions
        # 非常激进的条件
        self.mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.005,  # Very low volatility
            "volatility_24h": 0.01,
            "market_spread": 0.0001,  # Very small market spread
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        
        instance = StrategyInstance(
            strategy_id="test",
            strategy_type="fixed_spread",
            symbol="ETH/USDT:USDT",
            exchange=self.mock_exchange,
        )
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        
        instance.refresh_data()
        market_data = instance.latest_market_data
        
        # Calculate spread adjustment
        # 计算价差调整
        adjusted_spread = instance.strategy.calculate_adaptive_spread(
            volatility_1h=market_data.get("volatility_1h"),
            volatility_24h=market_data.get("volatility_24h"),
            market_spread=market_data.get("market_spread"),
        )
        
        # Should respect minimum spread limit
        # 应该遵守最小价差限制
        self.assertGreaterEqual(adjusted_spread, min_spread)


if __name__ == "__main__":
    unittest.main()

