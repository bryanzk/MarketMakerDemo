"""
Unit tests for StrategyInstance.refresh_data method
StrategyInstance.refresh_data 方法的单元测试

Note: The refresh_data method was moved from AlphaLoop to StrategyInstance
as part of the per-instance exchange architecture change.
注意：作为每实例独立交易所连接架构变更的一部分，refresh_data 方法已从 AlphaLoop 移至 StrategyInstance。
"""

import time
from unittest.mock import Mock, patch

import pytest

from src.trading.strategy_instance import StrategyInstance


class TestRefreshData:
    """Test cases for the StrategyInstance.refresh_data method"""

    @pytest.fixture
    def mock_exchange(self):
        """Create a mock exchange with basic functionality"""
        exchange = Mock()
        exchange.symbol = "ETH/USDT:USDT"
        exchange.fetch_market_data.return_value = {
            "best_bid": 1000.0,
            "best_ask": 1002.0,
            "mid_price": 1001.0,
            "timestamp": time.time() * 1000,  # Current time in ms
        }
        exchange.fetch_funding_rate.return_value = 0.0001
        exchange.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 1000.0,
        }
        exchange.set_symbol.return_value = True
        return exchange

    def test_refresh_data_success(self, mock_exchange):
        """Test successful data refresh updates all caches"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            # Clear cache
            instance.latest_market_data = None
            instance.latest_funding_rate = 0.0
            instance.latest_account_data = None

            # Refresh data
            result = instance.refresh_data()

            assert result is True
            assert instance.latest_market_data is not None
            assert instance.latest_market_data["mid_price"] == 1001.0
            assert instance.latest_funding_rate == 0.0001
            assert instance.latest_account_data is not None
            assert instance.latest_account_data["position_amt"] == 0.1

    def test_refresh_data_no_exchange(self):
        """Test refresh_data returns False when exchange not available"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            side_effect=Exception("No exchange"),
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")
            # Should be in simulation mode due to exception
            assert instance.use_real_exchange is False

            result = instance.refresh_data()

            assert result is False

    def test_refresh_data_fetch_failure(self, mock_exchange):
        """Test refresh_data returns False when fetch fails"""
        mock_exchange.fetch_market_data.return_value = None

        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            result = instance.refresh_data()

            assert result is False

    def test_refresh_data_no_mid_price(self, mock_exchange):
        """Test refresh_data returns False when mid_price is missing"""
        mock_exchange.fetch_market_data.return_value = {
            "best_bid": 1000.0,
            "best_ask": 1002.0,
            "mid_price": None,
        }

        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            result = instance.refresh_data()

            assert result is False

    def test_refresh_data_stale_data_warning(self, mock_exchange):
        """Test refresh_data logs warning but still updates cache with stale data"""
        # Return stale data (10 seconds old)
        stale_time = (time.time() - 10) * 1000
        mock_exchange.fetch_market_data.return_value = {
            "best_bid": 1000.0,
            "best_ask": 1002.0,
            "mid_price": 1001.0,
            "timestamp": stale_time,
        }

        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            result = instance.refresh_data()

            # Should still return True and update cache
            assert result is True
            assert instance.latest_market_data is not None
            assert instance.latest_market_data["mid_price"] == 1001.0

    def test_refresh_data_exception_handling(self, mock_exchange):
        """Test refresh_data handles exceptions gracefully"""
        mock_exchange.fetch_market_data.side_effect = Exception("API error")

        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            result = instance.refresh_data()

            assert result is False

    def test_refresh_data_updates_all_three_caches(self, mock_exchange):
        """Verify all three cache fields are updated"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_strategy", "fixed_spread")

            # Set initial values
            instance.latest_market_data = {"mid_price": 999.0}
            instance.latest_funding_rate = 0.0002
            instance.latest_account_data = {"position_amt": 0.0}

            # Refresh should update all
            instance.refresh_data()

            assert instance.latest_market_data["mid_price"] == 1001.0
            assert instance.latest_funding_rate == 0.0001
            assert instance.latest_account_data["position_amt"] == 0.1

    def test_refresh_data_with_different_strategy_types(self, mock_exchange):
        """Test refresh_data works for different strategy types"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            # Test with fixed_spread
            instance_fixed = StrategyInstance("test_fixed", "fixed_spread")
            result_fixed = instance_fixed.refresh_data()
            assert result_fixed is True

            # Test with funding_rate
            instance_funding = StrategyInstance("test_funding", "funding_rate")
            result_funding = instance_funding.refresh_data()
            assert result_funding is True

    def test_refresh_data_with_custom_symbol(self, mock_exchange):
        """Test refresh_data works with custom trading symbol"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            instance = StrategyInstance("test_btc", "fixed_spread", symbol="BTC/USDT:USDT")

            assert instance.symbol == "BTC/USDT:USDT"

            result = instance.refresh_data()

            assert result is True
            assert instance.latest_market_data is not None
