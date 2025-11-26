"""
Unit Tests for Portfolio Health Functions / 组合健康度函数单元测试

Tests for:
- calculate_strategy_health()
- get_health_status()
- get_health_color()
"""

import pytest
from alphaloop.portfolio.health import (
    HEALTH_WEIGHTS,
    calculate_strategy_health,
    get_health_color,
    get_health_status,
)


class TestCalculateStrategyHealth:
    """Test cases for calculate_strategy_health()"""

    def test_health_score_profitability_positive(self):
        """Test profitability scoring with positive PnL"""
        metrics = {
            "pnl": 5000,
            "sharpe": 0,
            "fill_rate": 0.8,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # PnL = 5000 → profitability = min(100, max(0, 50 + 5000/100)) = 100
        assert health >= 40  # At least profitability weight (40%)

    def test_health_score_profitability_negative(self):
        """Test profitability scoring with negative PnL"""
        metrics = {
            "pnl": -5000,
            "sharpe": 0,
            "fill_rate": 0.8,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # PnL = -5000 → profitability = min(100, max(0, 50 - 5000/100)) = 0
        assert health < 40  # Profitability is 0

    def test_health_score_risk_adjusted(self):
        """Test risk-adjusted return scoring"""
        metrics = {
            "pnl": 0,
            "sharpe": 2.5,
            "fill_rate": 0.8,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # Sharpe = 2.5 → risk_adjusted = min(100, max(0, 2.5 * 40)) = 100
        assert health >= 30  # At least risk_adjusted weight (30%)

    def test_health_score_risk_adjusted_negative_sharpe(self):
        """Test risk-adjusted return scoring with negative Sharpe ratio"""
        metrics = {
            "pnl": 0,
            "sharpe": -5.0,  # Negative Sharpe
            "fill_rate": 0.8,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # Sharpe = -5.0 → risk_adjusted = min(100, max(0, -5.0 * 40)) = 0
        # Should still be in valid range due to final clamp
        assert 0 <= health <= 100
        # Risk adjusted component should be 0
        # Other components: profitability=50*0.4=20, execution=80*0.2=16, stability=100*0.1=10
        # Total = 20 + 0 + 16 + 10 = 46
        assert health == pytest.approx(46.0, rel=0.1)

    def test_health_score_execution_quality(self):
        """Test execution quality scoring"""
        metrics = {
            "pnl": 0,
            "sharpe": 0,
            "fill_rate": 1.0,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # fill_rate = 1.0, slippage = 0 → execution = 100
        assert health >= 20  # At least execution weight (20%)

    def test_health_score_stability(self):
        """Test stability scoring"""
        metrics = {
            "pnl": 0,
            "sharpe": 0,
            "fill_rate": 0.8,
            "slippage": 0,
            "max_drawdown": 0,
        }
        health = calculate_strategy_health(metrics)
        # max_drawdown = 0 → stability = 100
        assert health >= 10  # At least stability weight (10%)

    def test_health_score_range(self):
        """Test that health score is always in 0-100 range"""
        test_cases = [
            {"pnl": 10000, "sharpe": 5.0, "fill_rate": 1.0, "slippage": 0, "max_drawdown": 0},
            {"pnl": -10000, "sharpe": -5.0, "fill_rate": 0, "slippage": 100, "max_drawdown": 1.0},
            {"pnl": 0, "sharpe": 0, "fill_rate": 0.5, "slippage": 5, "max_drawdown": 0.5},
        ]

        for metrics in test_cases:
            health = calculate_strategy_health(metrics)
            assert 0 <= health <= 100, f"Health score {health} out of range for metrics {metrics}"

    def test_health_score_missing_fields(self):
        """Test health score calculation with missing fields uses defaults"""
        metrics = {}  # Empty metrics
        health = calculate_strategy_health(metrics)
        # Should use defaults: pnl=0, sharpe=0, fill_rate=0.8, slippage=0, max_drawdown=0
        assert 0 <= health <= 100

    def test_health_score_weights_sum_to_one(self):
        """Test that health weights sum to 1.0"""
        total = sum(HEALTH_WEIGHTS.values())
        assert total == pytest.approx(1.0, rel=0.01)


class TestGetHealthStatus:
    """Test cases for get_health_status()"""

    def test_health_status_excellent(self):
        """Test status for excellent health (>= 80)"""
        assert get_health_status(80) == "excellent"
        assert get_health_status(90) == "excellent"
        assert get_health_status(100) == "excellent"

    def test_health_status_good(self):
        """Test status for good health (60-79)"""
        assert get_health_status(60) == "good"
        assert get_health_status(70) == "good"
        assert get_health_status(79) == "good"

    def test_health_status_fair(self):
        """Test status for fair health (40-59)"""
        assert get_health_status(40) == "fair"
        assert get_health_status(50) == "fair"
        assert get_health_status(59) == "fair"

    def test_health_status_poor(self):
        """Test status for poor health (< 40)"""
        assert get_health_status(0) == "poor"
        assert get_health_status(20) == "poor"
        assert get_health_status(39) == "poor"

    def test_health_status_boundary_values(self):
        """Test status at boundary values"""
        assert get_health_status(80) == "excellent"
        assert get_health_status(79.9) == "good"
        assert get_health_status(60) == "good"
        assert get_health_status(59.9) == "fair"
        assert get_health_status(40) == "fair"
        assert get_health_status(39.9) == "poor"


class TestGetHealthColor:
    """Test cases for get_health_color()"""

    def test_health_color_excellent(self):
        """Test color for excellent health (>= 80) - green"""
        assert get_health_color(80) == "#10b981"  # Green
        assert get_health_color(90) == "#10b981"
        assert get_health_color(100) == "#10b981"

    def test_health_color_good(self):
        """Test color for good health (60-79) - yellow"""
        assert get_health_color(60) == "#f59e0b"  # Yellow
        assert get_health_color(70) == "#f59e0b"
        assert get_health_color(79) == "#f59e0b"

    def test_health_color_fair(self):
        """Test color for fair health (40-59) - orange"""
        assert get_health_color(40) == "#f97316"  # Orange
        assert get_health_color(50) == "#f97316"
        assert get_health_color(59) == "#f97316"

    def test_health_color_poor(self):
        """Test color for poor health (< 40) - red"""
        assert get_health_color(0) == "#ef4444"  # Red
        assert get_health_color(20) == "#ef4444"
        assert get_health_color(39) == "#ef4444"

    def test_health_color_boundary_values(self):
        """Test color at boundary values"""
        assert get_health_color(80) == "#10b981"  # Green
        assert get_health_color(79.9) == "#f59e0b"  # Yellow
        assert get_health_color(60) == "#f59e0b"  # Yellow
        assert get_health_color(59.9) == "#f97316"  # Orange
        assert get_health_color(40) == "#f97316"  # Orange
        assert get_health_color(39.9) == "#ef4444"  # Red

