"""
Integration Tests for Dynamic Spread Adjustment / 动态价差调整集成测试

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import pytest
from unittest.mock import Mock, patch

from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategy_instance import StrategyInstance


class TestDynamicSpreadIntegration:
    """Integration tests for dynamic spread adjustment"""

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_end_to_end_volatility_to_spread_adjustment(self, mock_binance):
        """
        Integration Test: End-to-end flow from volatility calculation to spread adjustment.
        集成测试：从波动率计算到价差调整的端到端流程。
        """
        # Mock exchange with market data
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
        
        # Mock volatility calculation to return low volatility
        with patch("src.trading.volatility.calculate_volatility_1h_24h") as mock_vol:
            mock_vol.return_value = (0.01, 0.02)  # 1h: 1% (low), 24h: 2% (low)
            
            # Create strategy instance
            instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
            instance.strategy.base_spread = 0.015  # 1.5%
            
            # Refresh data (should calculate volatility)
            success = instance.refresh_data()
            assert success is True
            
            # Verify volatility is in market_data
            assert "volatility_1h" in instance.latest_market_data
            assert instance.latest_market_data["volatility_1h"] == 0.01
            
            # Calculate target orders (should use adjusted spread)
            target_orders = instance.calculate_target_orders(instance.latest_market_data)
            
            # Verify orders are created
            assert len(target_orders) == 2
            
            # Verify spread is reduced (low volatility should reduce spread by 20%)
            buy_price = target_orders[0]["price"]
            sell_price = target_orders[1]["price"]
            actual_spread = (sell_price - buy_price) / instance.latest_market_data["mid_price"]
            
            # Should be approximately 1.2% (0.8 * 1.5%)
            assert actual_spread < 0.015  # Less than base spread
            assert actual_spread == pytest.approx(0.012, abs=0.001)

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_end_to_end_high_volatility_spread_increase(self, mock_binance):
        """
        Integration Test: High volatility increases spread in end-to-end flow.
        集成测试：高波动在端到端流程中增大价差。
        """
        # Mock exchange with market data
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
        
        # Mock volatility calculation to return high volatility
        with patch("src.trading.volatility.calculate_volatility_1h_24h") as mock_vol:
            mock_vol.return_value = (0.07, 0.12)  # 1h: 7% (high), 24h: 12% (very high)
            
            # Create strategy instance
            instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
            instance.strategy.base_spread = 0.015  # 1.5%
            
            # Refresh data (should calculate volatility)
            success = instance.refresh_data()
            assert success is True
            
            # Verify volatility is in market_data
            assert "volatility_1h" in instance.latest_market_data
            assert instance.latest_market_data["volatility_1h"] == 0.07
            
            # Calculate target orders (should use adjusted spread)
            target_orders = instance.calculate_target_orders(instance.latest_market_data)
            
            # Verify orders are created
            assert len(target_orders) == 2
            
            # Verify spread is increased (high volatility should increase spread by 30%)
            buy_price = target_orders[0]["price"]
            sell_price = target_orders[1]["price"]
            actual_spread = (sell_price - buy_price) / instance.latest_market_data["mid_price"]
            
            # Should be approximately 1.95% (1.3 * 1.5%)
            assert actual_spread > 0.015  # Greater than base spread
            assert actual_spread == pytest.approx(0.0195, abs=0.001)

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_volatility_calculation_failure_graceful_degradation(self, mock_binance):
        """
        Integration Test: System continues working when volatility calculation fails.
        集成测试：波动率计算失败时系统继续工作。
        """
        # Mock exchange with market data
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
        
        # Mock volatility calculation to fail
        with patch("src.trading.volatility.calculate_volatility_1h_24h") as mock_vol:
            mock_vol.side_effect = Exception("Volatility calculation failed")
            
            # Create strategy instance
            instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
            instance.strategy.base_spread = 0.015  # 1.5%
            
            # Refresh data (should handle volatility calculation failure gracefully)
            success = instance.refresh_data()
            assert success is True  # Should still succeed
            
            # Verify market_data exists but without volatility
            assert instance.latest_market_data is not None
            assert "volatility_1h" not in instance.latest_market_data
            
            # Calculate target orders (should use base spread as fallback)
            target_orders = instance.calculate_target_orders(instance.latest_market_data)
            
            # Verify orders are created
            assert len(target_orders) == 2
            
            # Verify spread is base spread (no adjustment)
            buy_price = target_orders[0]["price"]
            sell_price = target_orders[1]["price"]
            actual_spread = (sell_price - buy_price) / instance.latest_market_data["mid_price"]
            
            # Should be approximately 1.5% (base spread)
            assert actual_spread == pytest.approx(0.015, abs=0.001)

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_status_includes_volatility_level_for_display(self, mock_binance):
        """
        Integration Test: Status includes volatility level for frontend display.
        集成测试：状态包含波动率级别以供前端显示。
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
        
        # Test different volatility levels
        test_cases = [
            (0.01, "low"),        # 1% - low
            (0.03, "medium"),     # 3% - medium
            (0.07, "high"),       # 7% - high
            (0.15, "very_high"),  # 15% - very high
        ]
        
        for volatility_1h, expected_level in test_cases:
            instance.latest_market_data = {
                "mid_price": 3000.0,
                "volatility_1h": volatility_1h,
                "volatility_24h": volatility_1h * 2,
            }
            
            status = instance.get_status()
            
            assert "volatility_1h" in status
            assert "volatility_24h" in status
            assert "volatility_level" in status
            assert status["volatility_1h"] == volatility_1h
            assert status["volatility_level"] == expected_level

    @patch("src.trading.strategy_instance.BinanceClient")
    def test_market_spread_consideration_in_high_volatility(self, mock_binance):
        """
        Integration Test: Market spread is considered when adjusting spread in high volatility.
        集成测试：在高波动调整价差时考虑市场价差。
        """
        # Mock exchange with wide market spread
        mock_exchange = Mock()
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2994.0,  # Wide spread: 6 points
            "best_ask": 3006.0,  # Market spread = 12/3000 = 0.4% = 0.004
            "tick_size": 0.1,
            "step_size": 0.001,
        }
        mock_exchange.fetch_funding_rate.return_value = 0.0001
        mock_exchange.fetch_account_data.return_value = {"position_amt": 0.0}
        mock_exchange.set_symbol.return_value = True
        mock_binance.return_value = mock_exchange
        
        # Mock high volatility
        with patch("src.trading.volatility.calculate_volatility_1h_24h") as mock_vol:
            mock_vol.return_value = (0.07, 0.10)  # High volatility
            
            instance = StrategyInstance("test", "fixed_spread", exchange=mock_exchange)
            instance.strategy.base_spread = 0.015  # 1.5%
            
            # Refresh data
            success = instance.refresh_data()
            assert success is True
            
            # Verify market_spread is calculated
            assert "market_spread" in instance.latest_market_data
            market_spread = instance.latest_market_data["market_spread"]
            assert market_spread == pytest.approx(0.004, abs=0.0001)  # 0.4%
            
            # Calculate target orders
            target_orders = instance.calculate_target_orders(instance.latest_market_data)
            
            # Verify spread is at least 1.3x market spread (0.004 * 1.3 = 0.0052)
            # Or base * 1.3 = 0.0195, whichever is larger
            buy_price = target_orders[0]["price"]
            sell_price = target_orders[1]["price"]
            actual_spread = (sell_price - buy_price) / instance.latest_market_data["mid_price"]
            
            # Should be max(0.0195, 0.0052) = 0.0195
            assert actual_spread == pytest.approx(0.0195, abs=0.001)







