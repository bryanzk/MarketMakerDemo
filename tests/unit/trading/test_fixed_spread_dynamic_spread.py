"""
Unit Tests for FixedSpreadStrategy Dynamic Spread Adjustment
固定价差策略动态价差调整单元测试

Tests the dynamic spread adjustment based on market volatility.
测试基于市场波动率的动态价差调整。

Owner: Agent QA
"""

import pytest

from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class TestFixedSpreadDynamicSpread:
    """Test cases for dynamic spread adjustment in FixedSpreadStrategy"""

    def setup_method(self):
        """Setup for each test method"""
        self.strategy = FixedSpreadStrategy()
        self.strategy.base_spread = 0.015  # 1.5% base spread
        self.strategy.quantity = 0.02

    def test_calculate_adaptive_spread_low_volatility(self):
        """
        Test spread reduction in low volatility market (< 2%).
        测试低波动市场（< 2%）中的价差减小。
        """
        # Low volatility: 1% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.01)
        
        # Should reduce spread by 20% (multiplier = 0.8)
        expected_spread = 0.015 * 0.8  # 1.2%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)
        assert adjusted_spread < self.strategy.base_spread

    def test_calculate_adaptive_spread_medium_volatility(self):
        """
        Test spread unchanged in medium volatility market (2-5%).
        测试中等波动市场（2-5%）中的价差不变。
        """
        # Medium volatility: 3% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.03)
        
        # Should use base spread (multiplier = 1.0)
        assert adjusted_spread == pytest.approx(self.strategy.base_spread, rel=1e-6)

    def test_calculate_adaptive_spread_high_volatility(self):
        """
        Test spread increase in high volatility market (5-10%).
        测试高波动市场（5-10%）中的价差增大。
        """
        # High volatility: 7% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.07)
        
        # Should increase spread by 30% (multiplier = 1.3)
        expected_spread = 0.015 * 1.3  # 1.95%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)
        assert adjusted_spread > self.strategy.base_spread

    def test_calculate_adaptive_spread_very_high_volatility(self):
        """
        Test spread significant increase in very high volatility market (> 10%).
        测试极高波动市场（> 10%）中的价差显著增大。
        """
        # Very high volatility: 15% (1h)
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_1h=0.15)
        
        # Should increase spread by 50% (multiplier = 1.5)
        expected_spread = 0.015 * 1.5  # 2.25%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)
        assert adjusted_spread > self.strategy.base_spread

    def test_calculate_adaptive_spread_no_volatility_data(self):
        """
        Test fallback to base spread when no volatility data available.
        测试没有波动率数据时回退到基础价差。
        """
        adjusted_spread = self.strategy.calculate_adaptive_spread()
        
        # Should use base spread
        assert adjusted_spread == pytest.approx(self.strategy.base_spread, rel=1e-6)

    def test_calculate_adaptive_spread_uses_1h_over_24h(self):
        """
        Test that 1h volatility is preferred over 24h volatility.
        测试优先使用 1h 波动率而不是 24h 波动率。
        """
        # Provide both, 1h should be used
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.01,  # Low volatility
            volatility_24h=0.15  # Very high volatility (should be ignored)
        )
        
        # Should use 1h volatility (low), so spread reduced
        expected_spread = 0.015 * 0.8  # 1.2%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)

    def test_calculate_adaptive_spread_fallback_to_24h(self):
        """
        Test fallback to 24h volatility when 1h not available.
        测试当 1h 波动率不可用时回退到 24h 波动率。
        """
        # Only provide 24h volatility
        adjusted_spread = self.strategy.calculate_adaptive_spread(volatility_24h=0.07)
        
        # Should use 24h volatility (high), so spread increased
        expected_spread = 0.015 * 1.3  # 1.95%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)

    def test_calculate_adaptive_spread_with_market_spread(self):
        """
        Test spread adjustment considers market spread in high volatility.
        测试在高波动时价差调整考虑市场价差。
        """
        # High volatility with market spread
        adjusted_spread = self.strategy.calculate_adaptive_spread(
            volatility_1h=0.07,
            market_spread=0.02  # 2% market spread
        )
        
        # Should be at least 1.3x market spread in high volatility
        min_spread = 0.02 * 1.3  # 2.6%
        # Also should be base * 1.3 = 1.95%
        # Should use the larger of the two
        expected_spread = max(0.015 * 1.3, min_spread)  # 2.6%
        assert adjusted_spread == pytest.approx(expected_spread, rel=1e-6)

    def test_calculate_target_orders_with_volatility_low(self):
        """
        Test target orders calculation with low volatility data.
        测试使用低波动率数据计算目标订单。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.01,  # Low volatility
        }

        orders = self.strategy.calculate_target_orders(market_data)

        assert len(orders) == 2
        # Spread should be reduced (0.8 * 1.5% = 1.2%)
        # Buy: 3000 * (1 - 0.012/2) = 3000 * 0.994 = 2982
        # Sell: 3000 * (1 + 0.012/2) = 3000 * 1.006 = 3018
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.2% (with rounding)
        assert actual_spread == pytest.approx(0.012, abs=0.001)

    def test_calculate_target_orders_with_volatility_high(self):
        """
        Test target orders calculation with high volatility data.
        测试使用高波动率数据计算目标订单。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.07,  # High volatility
        }

        orders = self.strategy.calculate_target_orders(market_data)

        assert len(orders) == 2
        # Spread should be increased (1.3 * 1.5% = 1.95%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.95% (with rounding)
        assert actual_spread == pytest.approx(0.0195, abs=0.001)

    def test_calculate_target_orders_without_volatility(self):
        """
        Test target orders calculation without volatility data (backward compatibility).
        测试没有波动率数据时的目标订单计算（向后兼容）。
        """
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            # No volatility data
        }

        orders = self.strategy.calculate_target_orders(market_data)

        assert len(orders) == 2
        # Should use base spread (1.5%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.5% (with rounding)
        assert actual_spread == pytest.approx(0.015, abs=0.001)

    def test_calculate_target_orders_volatility_boundary_low(self):
        """
        Test spread adjustment at low volatility boundary (2%).
        测试低波动率边界（2%）的价差调整。
        """
        # Exactly at low threshold (2%)
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.02,  # Exactly at threshold
        }

        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should use medium volatility (no adjustment)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately base spread (1.5%)
        assert actual_spread == pytest.approx(0.015, abs=0.001)

    def test_calculate_target_orders_volatility_boundary_high(self):
        """
        Test spread adjustment at high volatility boundary (5%).
        测试高波动率边界（5%）的价差调整。
        """
        # Exactly at high threshold (5%)
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.05,  # Exactly at threshold
        }

        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should use high volatility (increase by 30%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.95% (with rounding)
        assert actual_spread == pytest.approx(0.0195, abs=0.001)

    def test_calculate_target_orders_volatility_boundary_very_high(self):
        """
        Test spread adjustment at very high volatility boundary (10%).
        测试极高波动率边界（10%）的价差调整。
        """
        # Exactly at very high threshold (10%)
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.10,  # Exactly at threshold
        }

        orders = self.strategy.calculate_target_orders(market_data)
        
        # Should use very high volatility (increase by 50%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 2.25% (with rounding)
        assert actual_spread == pytest.approx(0.0225, abs=0.001)


