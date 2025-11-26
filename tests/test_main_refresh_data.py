"""
Unit tests for AlphaLoop.refresh_data method
"""

import time
from unittest.mock import Mock, patch

import pytest

from alphaloop.main import AlphaLoop


class TestRefreshData:
    """Test cases for the refresh_data method"""

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
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Clear cache
            bot.latest_market_data = None
            bot.latest_funding_rate = 0.0
            bot.latest_account_data = None

            # Refresh data
            result = bot.refresh_data()

            assert result is True
            assert bot.latest_market_data is not None
            assert bot.latest_market_data["mid_price"] == 1001.0
            assert bot.latest_funding_rate == 0.0001
            assert bot.latest_account_data is not None
            assert bot.latest_account_data["position_amt"] == 0.1

    def test_refresh_data_no_exchange(self):
        """Test refresh_data returns False when exchange not available"""
        with patch(
            "alphaloop.main.BinanceClient", side_effect=Exception("No exchange")
        ):
            bot = AlphaLoop()
            bot.use_real_exchange = False

            result = bot.refresh_data()

            assert result is False

    def test_refresh_data_fetch_failure(self, mock_exchange):
        """Test refresh_data returns False when fetch fails"""
        mock_exchange.fetch_market_data.return_value = None

        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            result = bot.refresh_data()

            assert result is False

    def test_refresh_data_no_mid_price(self, mock_exchange):
        """Test refresh_data returns False when mid_price is missing"""
        mock_exchange.fetch_market_data.return_value = {
            "best_bid": 1000.0,
            "best_ask": 1002.0,
            "mid_price": None,
        }

        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            result = bot.refresh_data()

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

        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            result = bot.refresh_data()

            # Should still return True and update cache
            assert result is True
            assert bot.latest_market_data is not None
            assert bot.latest_market_data["mid_price"] == 1001.0

    def test_refresh_data_exception_handling(self, mock_exchange):
        """Test refresh_data handles exceptions gracefully"""
        mock_exchange.fetch_market_data.side_effect = Exception("API error")

        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            result = bot.refresh_data()

            assert result is False

    def test_refresh_data_called_by_run_cycle(self, mock_exchange):
        """Test that run_cycle uses refresh_data"""
        mock_exchange.fetch_open_orders.return_value = []
        mock_exchange.place_orders.return_value = []

        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Clear cache
            bot.latest_market_data = None

            # Run cycle
            bot.run_cycle()

            # Cache should be populated by refresh_data
            assert bot.latest_market_data is not None
            assert mock_exchange.fetch_market_data.called

    def test_refresh_data_updates_all_three_caches(self, mock_exchange):
        """Verify all three cache fields are updated"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Set initial values
            bot.latest_market_data = {"mid_price": 999.0}
            bot.latest_funding_rate = 0.0002
            bot.latest_account_data = {"position_amt": 0.0}

            # Refresh should update all
            bot.refresh_data()

            assert bot.latest_market_data["mid_price"] == 1001.0
            assert bot.latest_funding_rate == 0.0001
            assert bot.latest_account_data["position_amt"] == 0.1
