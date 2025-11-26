"""
Unit tests for funding rate fetching functionality.
Tests fetch_funding_rate_for_symbol and fetch_bulk_funding_rates methods.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from alphaloop.market.exchange import BinanceClient


@pytest.fixture
def mock_exchange():
    """Create a mocked BinanceClient for testing"""
    with patch("alphaloop.market.exchange.ccxt.binanceusdm") as mock_ccxt:
        # Mock the exchange instance
        mock_instance = Mock()
        mock_ccxt.return_value = mock_instance

        # Mock urls as a dict (to support item assignment in __init__)
        mock_instance.urls = {"api": {}, "test": {}}

        # Mock has as a dict
        mock_instance.has = {}

        # Mock markets data
        mock_instance.markets = {
            "BTC/USDT:USDT": {"id": "BTCUSDT"},
            "ETH/USDT:USDT": {"id": "ETHUSDT"},
            "SOL/USDT:USDT": {"id": "SOLUSDT"},
        }
        mock_instance.load_markets.return_value = mock_instance.markets

        # Mock leverage setting
        mock_instance.fapiPrivatePostLeverage.return_value = {}

        # Create client
        client = BinanceClient()
        yield client


class TestFetchFundingRateForSymbol:
    """Tests for fetch_funding_rate_for_symbol method"""

    def test_fetch_funding_rate_for_symbol_success(self, mock_exchange):
        """Test successful funding rate fetch for a specific symbol"""
        # Mock API response
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = {
            "symbol": "BTCUSDT",
            "predictedFundingRate": "0.0001",
            "lastFundingRate": "0.00009",
        }

        rate = mock_exchange.fetch_funding_rate_for_symbol("BTC/USDT:USDT")

        assert rate == 0.0001  # Should use predicted rate
        mock_exchange.exchange.fapiPublicGetPremiumIndex.assert_called_once_with(
            {"symbol": "BTCUSDT"}
        )

    def test_fetch_funding_rate_fallback_to_last(self, mock_exchange):
        """Test fallback to lastFundingRate when predicted is None"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = {
            "symbol": "ETHUSDT",
            "predictedFundingRate": None,
            "lastFundingRate": "0.00012",
        }

        rate = mock_exchange.fetch_funding_rate_for_symbol("ETH/USDT:USDT")

        assert rate == 0.00012

    def test_fetch_funding_rate_missing_data(self, mock_exchange):
        """Test handling of missing funding rate data"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = {
            "symbol": "SOLUSDT"
        }

        rate = mock_exchange.fetch_funding_rate_for_symbol("SOL/USDT:USDT")

        assert rate == 0.0  # Should default to 0.0

    def test_fetch_funding_rate_invalid_symbol(self, mock_exchange):
        """Test handling of invalid symbol"""
        rate = mock_exchange.fetch_funding_rate_for_symbol("INVALID/USDT:USDT")

        assert rate == 0.0

    def test_fetch_funding_rate_api_error(self, mock_exchange):
        """Test handling of API errors"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.side_effect = Exception(
            "API Error"
        )

        rate = mock_exchange.fetch_funding_rate_for_symbol("BTC/USDT:USDT")

        assert rate == 0.0


class TestFetchBulkFundingRates:
    """Tests for fetch_bulk_funding_rates method"""

    def test_fetch_bulk_funding_rates_success(self, mock_exchange):
        """Test successful bulk funding rate fetch"""
        # Mock API response with all symbols
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = [
            {
                "symbol": "BTCUSDT",
                "predictedFundingRate": "0.0001",
                "lastFundingRate": "0.00009",
            },
            {
                "symbol": "ETHUSDT",
                "predictedFundingRate": "0.00015",
                "lastFundingRate": "0.00012",
            },
            {
                "symbol": "SOLUSDT",
                "predictedFundingRate": None,
                "lastFundingRate": "0.0002",
            },
        ]

        symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"]
        rates = mock_exchange.fetch_bulk_funding_rates(symbols)

        assert rates["BTC/USDT:USDT"] == 0.0001
        assert rates["ETH/USDT:USDT"] == 0.00015
        assert rates["SOL/USDT:USDT"] == 0.0002
        mock_exchange.exchange.fapiPublicGetPremiumIndex.assert_called_once_with()

    def test_fetch_bulk_funding_rates_partial_data(self, mock_exchange):
        """Test bulk fetch with only some symbols returned"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = [
            {
                "symbol": "BTCUSDT",
                "predictedFundingRate": "0.0001",
                "lastFundingRate": "0.00009",
            },
        ]

        symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
        rates = mock_exchange.fetch_bulk_funding_rates(symbols)

        assert rates["BTC/USDT:USDT"] == 0.0001
        assert rates["ETH/USDT:USDT"] == 0.0  # Missing should default to 0.0

    def test_fetch_bulk_funding_rates_empty_list(self, mock_exchange):
        """Test bulk fetch with empty symbol list"""
        rates = mock_exchange.fetch_bulk_funding_rates([])

        assert rates == {}

    def test_fetch_bulk_funding_rates_api_error(self, mock_exchange):
        """Test handling of API errors in bulk fetch"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.side_effect = Exception(
            "API Error"
        )

        symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
        rates = mock_exchange.fetch_bulk_funding_rates(symbols)

        # Should return 0.0 for all symbols on error
        assert rates["BTC/USDT:USDT"] == 0.0
        assert rates["ETH/USDT:USDT"] == 0.0


class TestFundingRateNegativeValues:
    """Tests for negative funding rates"""

    def test_negative_funding_rate(self, mock_exchange):
        """Test handling of negative funding rates"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = {
            "symbol": "BTCUSDT",
            "predictedFundingRate": "-0.0003",
            "lastFundingRate": "-0.00025",
        }

        rate = mock_exchange.fetch_funding_rate_for_symbol("BTC/USDT:USDT")

        assert rate == -0.0003

    def test_bulk_mixed_positive_negative_rates(self, mock_exchange):
        """Test bulk fetch with mixed positive and negative rates"""
        mock_exchange.exchange.fapiPublicGetPremiumIndex.return_value = [
            {
                "symbol": "BTCUSDT",
                "predictedFundingRate": "0.0001",
                "lastFundingRate": "0.00009",
            },
            {
                "symbol": "ETHUSDT",
                "predictedFundingRate": "-0.00015",
                "lastFundingRate": "-0.00012",
            },
        ]

        symbols = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
        rates = mock_exchange.fetch_bulk_funding_rates(symbols)

        assert rates["BTC/USDT:USDT"] == 0.0001
        assert rates["ETH/USDT:USDT"] == -0.00015
