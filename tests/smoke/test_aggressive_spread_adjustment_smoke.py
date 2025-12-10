"""
Smoke tests for aggressive spread adjustment / 更激进价差调整冒烟测试

Owner: Agent QA
"""

import unittest
from unittest.mock import Mock

from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategy_instance import StrategyInstance


class TestAggressiveSpreadAdjustmentSmoke(unittest.TestCase):
    """Smoke tests for aggressive spread adjustment / 更激进价差调整冒烟测试"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.base_spread = 0.015  # 1.5% base spread
        self.strategy.spread = 0.015

    def test_low_volatility_reduces_spread_aggressively(self):
        """
        Smoke test: Low volatility should reduce spread more aggressively.
        冒烟测试：低波动应该更激进地减小价差。
        """
        # Low volatility: 1% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.01)
        
        # Should be more aggressive than before (0.3x instead of 0.5x)
        # 应该比以前更激进（0.3x 而不是 0.5x）
        expected_max = 0.015 * 0.3  # 0.45%
        self.assertLessEqual(adjusted_spread, expected_max)
        self.assertLess(adjusted_spread, self.strategy.base_spread)

    def test_small_market_spread_triggers_adjustment(self):
        """
        Smoke test: Small market spread (<0.1%) should trigger aggressive adjustment.
        冒烟测试：小市场价差（<0.1%）应该触发激进调整。
        """
        # Very small market spread: 0.05%
        market_spread = 0.0005
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.02,  # Medium volatility
            market_spread=market_spread
        )
        
        # Should be adjusted based on market spread
        # 应该根据市场价差调整
        self.assertLess(adjusted_spread, self.strategy.base_spread)
        # Should be competitive with market spread
        # 应该与市场价差具有竞争力
        self.assertLess(adjusted_spread, market_spread * 3.0)

    def test_combined_low_volatility_and_small_market_spread(self):
        """
        Smoke test: Combined low volatility and small market spread = very aggressive.
        冒烟测试：低波动和小市场价差组合 = 非常激进。
        """
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.01,  # Low volatility
            market_spread=0.0005  # Small market spread
        )
        
        # Should be very aggressive (small spread)
        # 应该非常激进（小价差）
        self.assertLess(adjusted_spread, 0.01)  # Less than 1%

    def test_strategy_instance_uses_aggressive_adjustment(self):
        """
        Smoke test: StrategyInstance should use aggressive spread adjustment.
        冒烟测试：StrategyInstance 应该使用激进价差调整。
        """
        # Create a mock exchange
        # 创建模拟交易所
        mock_exchange = Mock()
        mock_exchange.symbol = "ETH/USDT:USDT"
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
            "volatility_1h": 0.01,  # Low volatility
            "volatility_24h": 0.02,
            "market_spread": 0.0005,  # Small market spread
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
        instance.strategy.base_spread = 0.015
        instance.strategy.spread = 0.015
        
        # Refresh data (this should trigger spread adjustment)
        # 刷新数据（这应该触发价差调整）
        success = instance.refresh_data()
        self.assertTrue(success)
        
        # Check that spread was adjusted
        # 检查价差是否已调整
        # The spread should be adjusted in calculate_target_orders via calculate_adaptive_spread
        # 价差应该在 calculate_target_orders 中通过 calculate_adaptive_spread 调整
        market_data = instance.latest_market_data
        target_orders = instance.calculate_target_orders(market_data)
        
        # Should generate orders with adjusted spread
        # 应该使用调整后的价差生成订单
        self.assertGreater(len(target_orders), 0)

    def test_risk_limits_respected(self):
        """
        Smoke test: Aggressive adjustment should still respect risk limits.
        冒烟测试：激进调整应该仍然遵守风险限制。
        """
        from src.shared.config import RISK_LIMITS
        
        min_spread = RISK_LIMITS.get("MIN_SPREAD", 0.001)
        
        # Even with very aggressive adjustment
        # 即使是非常激进的调整
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.005,  # Very low volatility
            market_spread=0.0001  # Very small market spread
        )
        
        # Should respect minimum spread
        # 应该遵守最小价差
        self.assertGreaterEqual(adjusted_spread, min_spread)


if __name__ == "__main__":
    unittest.main()

