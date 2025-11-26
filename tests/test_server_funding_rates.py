"""
Additional unit tests for /api/funding-rates endpoint in server.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_bot_engine():
    """Create a mocked bot_engine for server testing"""
    mock_engine = Mock()
    mock_exchange = Mock()
    mock_engine.exchange = mock_exchange
    return mock_engine, mock_exchange


class TestFundingRatesEndpoint:
    """Tests for /api/funding-rates endpoint"""

    def test_funding_rates_success(self, mock_bot_engine):
        """Test successful funding rates retrieval"""
        mock_engine, mock_exchange = mock_bot_engine

        # Mock bulk funding rates response
        mock_exchange.fetch_bulk_funding_rates.return_value = {
            "BTC/USDT:USDT": 0.0001,
            "ETH/USDT:USDT": -0.00015,
            "SOL/USDT:USDT": 0.0002,
            "DOGE/USDT:USDT": 0.00005,
        }

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert isinstance(data, list)
        assert len(data) > 0

        # Check first item (should be highest absolute rate: SOL at 0.0002)
        assert data[0]["symbol"] == "SOL/USDT:USDT"
        assert data[0]["funding_rate"] == 0.0002
        assert data[0]["daily_yield"] == pytest.approx(0.0006, rel=1e-9)  # 3x per day
        assert data[0]["direction"] == "short_favored"

        # Check negative rate handling
        eth_item = next(item for item in data if item["symbol"] == "ETH/USDT:USDT")
        assert eth_item["funding_rate"] == -0.00015
        assert eth_item["direction"] == "long_favored"

    def test_funding_rates_sorting(self, mock_bot_engine):
        """Test that funding rates are sorted by absolute value"""
        mock_engine, mock_exchange = mock_bot_engine

        mock_exchange.fetch_bulk_funding_rates.return_value = {
            "BTC/USDT:USDT": 0.00005,  # Low
            "ETH/USDT:USDT": -0.0003,  # High (negative)
            "SOL/USDT:USDT": 0.00025,  # Medium
        }

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        data = response.json()

        # Should be sorted by absolute value: ETH (0.0003), SOL (0.00025), BTC (0.00005)
        assert data[0]["symbol"] == "ETH/USDT:USDT"
        assert data[1]["symbol"] == "SOL/USDT:USDT"
        assert data[2]["symbol"] == "BTC/USDT:USDT"

    def test_funding_rates_direction_labels(self, mock_bot_engine):
        """Test direction labeling for different funding rates"""
        mock_engine, mock_exchange = mock_bot_engine

        mock_exchange.fetch_bulk_funding_rates.return_value = {
            "BTC/USDT:USDT": 0.0002,  # Positive > 0.01%
            "ETH/USDT:USDT": -0.0003,  # Negative < -0.01%
            "SOL/USDT:USDT": 0.00005,  # Near zero
        }

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        data = response.json()

        btc = next(item for item in data if item["symbol"] == "BTC/USDT:USDT")
        eth = next(item for item in data if item["symbol"] == "ETH/USDT:USDT")
        sol = next(item for item in data if item["symbol"] == "SOL/USDT:USDT")

        assert btc["direction"] == "short_favored"
        assert eth["direction"] == "long_favored"
        assert sol["direction"] == "neutral"

    def test_funding_rates_no_exchange(self):
        """Test error handling when exchange is not available"""
        mock_engine = Mock()
        mock_engine.exchange = None

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["error"] == "Exchange not available"

    def test_funding_rates_api_error(self, mock_bot_engine):
        """Test error handling when API call fails"""
        mock_engine, mock_exchange = mock_bot_engine
        mock_exchange.fetch_bulk_funding_rates.side_effect = Exception(
            "API connection failed"
        )

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "API connection failed" in data["error"]

    def test_funding_rates_daily_yield_calculation(self, mock_bot_engine):
        """Test that daily yield is correctly calculated as 3x funding rate"""
        mock_engine, mock_exchange = mock_bot_engine

        mock_exchange.fetch_bulk_funding_rates.return_value = {
            "BTC/USDT:USDT": 0.0001,
        }

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            response = client.get("/api/funding-rates")

        data = response.json()
        assert data[0]["daily_yield"] == pytest.approx(0.0003, rel=1e-9)  # 0.0001 * 3

    def test_funding_rates_all_supported_symbols(self, mock_bot_engine):
        """Test that all expected symbols are queried"""
        mock_engine, mock_exchange = mock_bot_engine

        mock_exchange.fetch_bulk_funding_rates.return_value = {}

        with patch("server.bot_engine", mock_engine):
            from server import app

            client = TestClient(app)
            client.get("/api/funding-rates")

        # Check that fetch was called with expected symbols
        call_args = mock_exchange.fetch_bulk_funding_rates.call_args[0][0]
        expected_symbols = [
            "BTC/USDT:USDT",
            "ETH/USDT:USDT",
            "SOL/USDT:USDT",
            "DOGE/USDT:USDT",
            "1000SHIB/USDT:USDT",
            "1000PEPE/USDT:USDT",
            "WIF/USDT:USDT",
            "1000FLOKI/USDT:USDT",
        ]
        assert set(call_args) == set(expected_symbols)
