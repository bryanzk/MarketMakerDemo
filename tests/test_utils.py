import pytest
from utils import round_tick_size, round_step_size


class TestUtils:
    """Test cases for utility functions"""
    
    def test_round_tick_size_normal(self):
        """Test normal tick size rounding"""
        price = 3000.556
        tick_size = 0.01
        
        result = round_tick_size(price, tick_size)
        
        assert result == 3000.55
    
    def test_round_tick_size_already_rounded(self):
        """Test tick size rounding when already at tick size"""
        price = 3000.50
        tick_size = 0.01
        
        result = round_tick_size(price, tick_size)
        
        assert result == 3000.50
    
    def test_round_tick_size_larger_tick(self):
        """Test rounding with larger tick size"""
        price = 3005.67
        tick_size = 0.1
        
        result = round_tick_size(price, tick_size)
        
        assert result == 3005.6
    
    def test_round_tick_size_very_small_tick(self):
        """Test rounding with very small tick size"""
        price = 3000.123456
        tick_size = 0.0001
        
        result = round_tick_size(price, tick_size)
        
        assert result == 3000.1234
    
    def test_round_step_size_normal(self):
        """Test normal step size rounding"""
        quantity = 0.0234
        step_size = 0.001
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.023
    
    def test_round_step_size_already_rounded(self):
        """Test step size rounding when already at step size"""
        quantity = 0.020
        step_size = 0.001
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.020
    
    def test_round_step_size_larger_step(self):
        """Test rounding with larger step size"""
        quantity = 0.567
        step_size = 0.01
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.56
    
    def test_round_step_size_very_small_step(self):
        """Test rounding with very small step size"""
        quantity = 0.123456
        step_size = 0.0001
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.1234
    
    def test_round_step_size_rounds_down(self):
        """Test that step size always rounds down"""
        quantity = 0.0239
        step_size = 0.001
        
        result = round_step_size(quantity, step_size)
        
        # Should round down to 0.023, not up to 0.024
        assert result == 0.023
    
    def test_round_tick_size_zero_price(self):
        """Test tick size rounding with zero price"""
        price = 0.0
        tick_size = 0.01
        
        result = round_tick_size(price, tick_size)
        
        assert result == 0.0
    
    def test_round_step_size_zero_quantity(self):
        """Test step size rounding with zero quantity"""
        quantity = 0.0
        step_size = 0.001
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.0
    
    def test_round_tick_size_precision(self):
        """Test that tick size rounding maintains precision"""
        price = 0.0001234
        tick_size = 0.00001
        
        result = round_tick_size(price, tick_size)
        
        assert result == 0.00012
    
    def test_round_step_size_precision(self):
        """Test that step size rounding maintains precision"""
        quantity = 0.0001234
        step_size = 0.00001
        
        result = round_step_size(quantity, step_size)
        
        assert result == 0.00012
    
    def test_round_tick_size_large_numbers(self):
        """Test tick size rounding with large numbers"""
        price = 50000.556
        tick_size = 0.01
        
        result = round_tick_size(price, tick_size)
        
        assert result == 50000.55
    
    def test_round_step_size_large_numbers(self):
        """Test step size rounding with large numbers"""
        quantity = 1000.5678
        step_size = 0.01
        
        result = round_step_size(quantity, step_size)
        
        assert result == 1000.56
