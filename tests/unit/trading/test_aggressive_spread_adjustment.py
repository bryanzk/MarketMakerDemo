"""
Unit tests for aggressive spread adjustment / 更激进价差调整单元测试

Tests more aggressive spread reduction in low volatility and market spread-based adjustment.
测试在低波动时更激进的价差减小和基于市场价差的调整。

Owner: Agent QA
"""

import unittest

from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestAggressiveSpreadAdjustment(unittest.TestCase):
    """Test aggressive spread adjustment / 测试更激进价差调整"""

    def setUp(self):
        """Set up test fixtures / 设置测试夹具"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.base_spread = 0.015  # 1.5% base spread
        self.strategy.spread = 0.015  # Current spread
        self.strategy.quantity = 0.1

    def test_low_volatility_uses_aggressive_multiplier(self):
        """
        Test that low volatility uses more aggressive multiplier (0.2-0.3 instead of 0.5).
        测试低波动时使用更激进的乘数（0.2-0.3 而不是 0.5）。
        """
        # Low volatility: 1% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.01)
        
        # Should use more aggressive multiplier (0.2 or 0.3)
        # 应该使用更激进的乘数（0.2 或 0.3）
        # With 0.3 multiplier: 0.015 * 0.3 = 0.0045 (0.45%)
        expected_spread_max = 0.015 * 0.3  # 0.45% (more aggressive)
        expected_spread_min = 0.015 * 0.2  # 0.3% (very aggressive)
        
        self.assertLessEqual(adjusted_spread, expected_spread_max)
        self.assertGreaterEqual(adjusted_spread, expected_spread_min)
        self.assertLess(adjusted_spread, self.strategy.base_spread)

    def test_market_spread_based_adjustment_small_market_spread(self):
        """
        Test that when market spread is very small (<0.1%), our spread should also be small.
        测试当市场价差很小（<0.1%）时，我们的价差也应该很小。
        """
        # Very small market spread: 0.05% (0.0005)
        market_spread = 0.0005
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.01,  # Low volatility
            market_spread=market_spread
        )
        
        # Our spread should be adjusted based on market spread
        # 我们的价差应该根据市场价差调整
        # Should be competitive but not too small (at least market_spread * 1.5)
        # 应该具有竞争力但不要太小（至少 market_spread * 1.5）
        min_spread = market_spread * 1.5
        max_spread = market_spread * 3.0  # Not more than 3x market spread
        
        self.assertGreaterEqual(adjusted_spread, min_spread)
        self.assertLessEqual(adjusted_spread, max_spread)

    def test_market_spread_based_adjustment_normal_market_spread(self):
        """
        Test that normal market spread doesn't force aggressive reduction.
        测试正常市场价差不会强制激进减小。
        """
        # Normal market spread: 0.2% (0.002)
        market_spread = 0.002
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.01,  # Low volatility
            market_spread=market_spread
        )
        
        # Should still use volatility-based adjustment, but consider market spread
        # 应该仍然使用基于波动率的调整，但考虑市场价差
        # Should be reasonable (not forced to be too small)
        # 应该是合理的（不要强制太小）
        self.assertGreater(adjusted_spread, 0.001)  # At least 0.1%
        self.assertLess(adjusted_spread, self.strategy.base_spread)

    def test_market_spread_priority_over_volatility_when_very_small(self):
        """
        Test that very small market spread takes priority over volatility adjustment.
        测试非常小的市场价差优先于波动率调整。
        """
        # Very small market spread: 0.03% (0.0003)
        market_spread = 0.0003
        # Even with high volatility, should adjust to market spread
        # 即使在高波动率下，也应该根据市场价差调整
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.08,  # High volatility (would normally increase spread)
            market_spread=market_spread
        )
        
        # Market spread should influence the adjustment
        # 市场价差应该影响调整
        # Should be competitive with market spread
        # 应该与市场价差具有竞争力
        max_spread = market_spread * 5.0  # Not more than 5x very small market spread
        self.assertLessEqual(adjusted_spread, max_spread)

    def test_combined_low_volatility_and_small_market_spread(self):
        """
        Test aggressive adjustment when both low volatility and small market spread.
        测试当低波动和小市场价差同时存在时的激进调整。
        """
        # Low volatility + small market spread = very aggressive pricing
        # 低波动 + 小市场价差 = 非常激进的价格
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.01,  # Low volatility
            market_spread=0.0005  # Small market spread
        )
        
        # Should be very aggressive (small spread)
        # 应该非常激进（小价差）
        # Combined effect: low volatility multiplier + market spread consideration
        # 组合效果：低波动乘数 + 市场价差考虑
        self.assertLess(adjusted_spread, 0.01)  # Less than 1%
        self.assertGreater(adjusted_spread, 0.0001)  # But still positive

    def test_aggressive_multiplier_range(self):
        """
        Test that aggressive multiplier is in the range 0.2-0.3 for low volatility.
        测试低波动时激进乘数在 0.2-0.3 范围内。
        """
        # Test with different low volatility values
        # 使用不同的低波动值测试
        for vol in [0.005, 0.01, 0.015]:  # Very low to low volatility
            adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=vol)
            multiplier = adjusted_spread / self.strategy.base_spread
            
            # Multiplier should be in aggressive range (0.2-0.3)
            # 乘数应该在激进范围内（0.2-0.3）
            self.assertGreaterEqual(multiplier, 0.2)
            self.assertLessEqual(multiplier, 0.3)

    def test_market_spread_threshold_0_1_percent(self):
        """
        Test that market spread threshold of 0.1% triggers aggressive adjustment.
        测试 0.1% 的市场价差阈值触发激进调整。
        """
        # Market spread just below threshold: 0.09% (0.0009)
        market_spread_below = 0.0009
        adjusted_spread_below = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.02,  # Medium volatility
            market_spread=market_spread_below
        )
        
        # Market spread just above threshold: 0.11% (0.0011)
        market_spread_above = 0.0011
        adjusted_spread_above = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.02,  # Medium volatility
            market_spread=market_spread_above
        )
        
        # Below threshold should be more aggressive (smaller spread)
        # 低于阈值应该更激进（更小的价差）
        self.assertLess(adjusted_spread_below, adjusted_spread_above)

    def test_risk_limits_respected_with_aggressive_adjustment(self):
        """
        Test that aggressive adjustment still respects risk limits (MIN_SPREAD, MAX_SPREAD).
        测试激进调整仍然遵守风险限制（MIN_SPREAD, MAX_SPREAD）。
        """
        from src.shared.config import RISK_LIMITS
        
        min_spread = RISK_LIMITS.get("MIN_SPREAD", 0.0001)
        max_spread = RISK_LIMITS.get("MAX_SPREAD", 0.1)
        
        # Even with very aggressive adjustment, should respect limits
        # 即使是非常激进的调整，也应该遵守限制
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.005,  # Very low volatility
            market_spread=0.0001  # Very small market spread
        )
        
        self.assertGreaterEqual(adjusted_spread, min_spread)
        self.assertLessEqual(adjusted_spread, max_spread)


if __name__ == "__main__":
    unittest.main()

