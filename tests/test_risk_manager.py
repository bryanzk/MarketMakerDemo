import pytest
from alphaloop.market.risk_manager import RiskManager


class TestRiskManager:
    """Test cases for RiskManager class"""

    def setup_method(self):
        """Setup for each test method"""
        self.risk_manager = RiskManager()

    def test_check_position_limits_within_range(self):
        """Test that both sides are allowed when position is within limits"""
        position = 0.0  # Neutral position

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" in allowed_sides
        assert len(allowed_sides) == 2

    def test_check_position_limits_small_long(self):
        """Test that both sides allowed with small long position"""
        position = 0.1  # Small long position

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" in allowed_sides

    def test_check_position_limits_small_short(self):
        """Test that both sides allowed with small short position"""
        position = -0.1  # Small short position

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" in allowed_sides

    def test_check_position_limits_at_max_long(self):
        """Test that buy orders blocked at max long position"""
        position = 0.5  # At MAX_POSITION (from config.py)

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" not in allowed_sides
        assert "sell" in allowed_sides
        assert len(allowed_sides) == 1

    def test_check_position_limits_at_max_short(self):
        """Test that sell orders blocked at max short position"""
        position = -0.5  # At -MAX_POSITION

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" not in allowed_sides
        assert len(allowed_sides) == 1

    def test_check_position_limits_beyond_max_long(self):
        """Test handling of position exceeding max long"""
        position = 0.6  # Beyond MAX_POSITION

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" not in allowed_sides
        assert "sell" in allowed_sides

    def test_check_position_limits_beyond_max_short(self):
        """Test handling of position exceeding max short"""
        position = -0.6  # Beyond -MAX_POSITION

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" not in allowed_sides

    def test_check_position_limits_just_below_max_long(self):
        """Test that buy is still allowed just below max long"""
        position = 0.49  # Just below MAX_POSITION

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" in allowed_sides

    def test_check_position_limits_just_below_max_short(self):
        """Test that sell is still allowed just below max short"""
        position = -0.49  # Just below -MAX_POSITION

        allowed_sides = self.risk_manager.check_position_limits(position)

        assert "buy" in allowed_sides
        assert "sell" in allowed_sides
