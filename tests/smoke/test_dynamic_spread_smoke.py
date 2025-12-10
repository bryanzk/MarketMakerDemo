"""
Smoke Tests for Dynamic Spread Adjustment / 动态价差调整冒烟测试

Smoke tests verify basic functionality works end-to-end.
冒烟测试验证基本功能端到端工作。

Owner: Agent QA
"""

import pytest
from unittest.mock import Mock, patch

from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategy_instance import StrategyInstance


class TestDynamicSpreadSmoke:
    """Smoke tests for dynamic spread adjustment"""

    def test_dynamic_spread_low_volatility_smoke(self):
        """
        Smoke Test: Dynamic spread reduces in low volatility market.
        冒烟测试：低波动市场中动态价差减小。
        """
        strategy = FixedSpreadStrategy()
        strategy.base_spread = 0.015  # 1.5%
        
        # Low volatility market
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.01,  # 1% - low volatility
        }
        
        orders = strategy.calculate_target_orders(market_data)
        
        # Should have both orders
        assert len(orders) == 2
        
        # Spread should be reduced (0.5 * 1.5% = 0.75%)
        # Note: Low volatility multiplier changed from 0.8 to 0.5 for more aggressive reduction
        # 注意：低波动率倍数从 0.8 改为 0.5 以实现更激进的降低
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 0.75% (reduced from 1.5% using 0.5 multiplier)
        assert actual_spread < 0.015  # Less than base spread
        assert actual_spread == pytest.approx(0.0075, abs=0.001)

    def test_dynamic_spread_high_volatility_smoke(self):
        """
        Smoke Test: Dynamic spread increases in high volatility market.
        冒烟测试：高波动市场中动态价差增大。
        """
        strategy = FixedSpreadStrategy()
        strategy.base_spread = 0.015  # 1.5%
        
        # High volatility market
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            "volatility_1h": 0.07,  # 7% - high volatility
        }
        
        orders = strategy.calculate_target_orders(market_data)
        
        # Should have both orders
        assert len(orders) == 2
        
        # Spread should be increased (1.3 * 1.5% = 1.95%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.95% (increased from 1.5%)
        assert actual_spread > 0.015  # Greater than base spread
        assert actual_spread == pytest.approx(0.0195, abs=0.001)

    def test_dynamic_spread_no_volatility_data_smoke(self):
        """
        Smoke Test: Falls back to base spread when no volatility data.
        冒烟测试：没有波动率数据时回退到基础价差。
        """
        strategy = FixedSpreadStrategy()
        strategy.base_spread = 0.015  # 1.5%
        
        # No volatility data
        market_data = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
            # No volatility fields
        }
        
        orders = strategy.calculate_target_orders(market_data)
        
        # Should have both orders
        assert len(orders) == 2
        
        # Should use base spread (1.5%)
        buy_price = orders[0]["price"]
        sell_price = orders[1]["price"]
        actual_spread = (sell_price - buy_price) / market_data["mid_price"]
        
        # Should be approximately 1.5% (base spread)
        assert actual_spread == pytest.approx(0.015, abs=0.001)

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_strategy_instance_volatility_calculation_smoke(self, mock_binance):
        """
        Smoke Test: StrategyInstance calculates and includes volatility in market_data.
        冒烟测试：StrategyInstance 计算并在 market_data 中包含波动率。
        """
        # Mock exchange
        mock_exchange = Mock()
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        mock_exchange.fetch_funding_rate.return_value = 0.0001
        mock_exchange.fetch_account_data.return_value = {"position_amt": 0.0}
        mock_exchange.set_symbol.return_value = True
        mock_binance.return_value = mock_exchange
        
        # Mock volatility calculation
        with patch("src.trading.volatility.calculate_volatility_1h_24h") as mock_vol:
            mock_vol.return_value = (0.03, 0.05)  # 1h: 3%, 24h: 5%
            
            instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
            success = instance.refresh_data()
            
            assert success is True
            assert instance.latest_market_data is not None
            assert "volatility_1h" in instance.latest_market_data
            assert "volatility_24h" in instance.latest_market_data
            assert instance.latest_market_data["volatility_1h"] == 0.03
            assert instance.latest_market_data["volatility_24h"] == 0.05

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_strategy_instance_status_includes_volatility_smoke(self, mock_binance):
        """
        Smoke Test: StrategyInstance.get_status() includes volatility and level.
        冒烟测试：StrategyInstance.get_status() 包含波动率和级别。
        """
        # Mock exchange
        mock_exchange = Mock()
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.5,
            "best_ask": 3000.5,
        }
        mock_exchange.fetch_funding_rate.return_value = 0.0001
        mock_exchange.fetch_account_data.return_value = {"position_amt": 0.0}
        mock_exchange.set_symbol.return_value = True
        mock_binance.return_value = mock_exchange
        
        instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
        
        # Set market data with volatility
        instance.latest_market_data = {
            "mid_price": 3000.0,
            "volatility_1h": 0.03,  # 3% - medium
            "volatility_24h": 0.05,  # 5% - medium
        }
        
        status = instance.get_status()
        
        # Should include volatility fields
        assert "volatility_1h" in status
        assert "volatility_24h" in status
        assert "volatility_level" in status
        assert status["volatility_1h"] == 0.03
        assert status["volatility_24h"] == 0.05
        assert status["volatility_level"] == "medium"







