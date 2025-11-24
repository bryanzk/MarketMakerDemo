"""
Tests for leverage and symbol limits methods in BinanceClient
Covers: get_leverage, set_leverage, get_max_leverage, get_symbol_limits
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from alphaloop.market.exchange import BinanceClient


class TestLeverageManagement:
    """Test cases for leverage-related methods"""

    @pytest.fixture
    def mock_client(self):
        """Create a properly mocked BinanceClient"""
        with patch("alphaloop.market.exchange.ccxt.binanceusdm") as mock_binance:
            mock_exchange = MagicMock()
            mock_exchange.load_markets.return_value = {
                "ETH/USDT:USDT": {
                    "id": "ETHUSDT",
                    "symbol": "ETH/USDT:USDT",
                    "limits": {
                        "leverage": {"max": 125},
                        "amount": {"min": 0.001, "max": 10000},
                        "cost": {"min": 5.0},
                    },
                    "precision": {"amount": 0.001, "price": 0.01},
                }
            }
            mock_binance.return_value = mock_exchange

            with patch("alphaloop.market.exchange.LEVERAGE", 5):
                client = BinanceClient()
            yield client

    def test_get_leverage_success(self, mock_client):
        """Test successful leverage retrieval"""
        mock_client.exchange.fapiPrivateV2GetPositionRisk.return_value = [
            {"symbol": "ETHUSDT", "leverage": "10"},
            {"symbol": "BTCUSDT", "leverage": "5"},
        ]

        leverage = mock_client.get_leverage()

        assert leverage == 10
        mock_client.exchange.fapiPrivateV2GetPositionRisk.assert_called_once()

    def test_get_leverage_no_position(self, mock_client):
        """Test leverage retrieval when no position exists"""
        mock_client.exchange.fapiPrivateV2GetPositionRisk.return_value = [
            {"symbol": "BTCUSDT", "leverage": "5"}
        ]

        leverage = mock_client.get_leverage()

        assert leverage is None

    def test_get_leverage_error(self, mock_client):
        """Test leverage retrieval error handling"""
        mock_client.exchange.fapiPrivateV2GetPositionRisk.side_effect = Exception(
            "API Error"
        )

        leverage = mock_client.get_leverage()

        assert leverage is None

    def test_set_leverage_success(self, mock_client):
        """Test successful leverage setting"""
        # Reset call count from __init__
        mock_client.exchange.fapiPrivatePostLeverage.reset_mock()
        
        mock_client.exchange.fapiPrivatePostLeverage.return_value = {
            "leverage": 10,
            "maxNotionalValue": "1000000",
        }

        result = mock_client.set_leverage(10)

        assert result is True
        mock_client.exchange.fapiPrivatePostLeverage.assert_called_once_with(
            {"symbol": "ETHUSDT", "leverage": 10}
        )

    def test_set_leverage_error(self, mock_client):
        """Test leverage setting error handling"""
        mock_client.exchange.fapiPrivatePostLeverage.side_effect = Exception(
            "Invalid leverage"
        )

        result = mock_client.set_leverage(150)  # Invalid leverage

        assert result is False

    def test_get_max_leverage_from_market_limits(self, mock_client):
        """Test max leverage from market info limits"""
        max_lev = mock_client.get_max_leverage()

        assert max_lev == 125  # From market limits

    def test_get_max_leverage_from_brackets(self, mock_client):
        """Test max leverage from leverage brackets"""
        # Remove limits from market
        mock_client.market = {"id": "ETHUSDT", "symbol": "ETH/USDT:USDT"}

        mock_client.exchange.fapiPrivateGetLeverageBracket.return_value = [
            {
                "symbol": "ETHUSDT",
                "brackets": [
                    {"initialLeverage": 50, "notionalCap": 50000},
                    {"initialLeverage": 25, "notionalCap": 250000},
                ],
            }
        ]

        max_lev = mock_client.get_max_leverage()

        assert max_lev == 50  # First bracket's initialLeverage

    def test_get_max_leverage_fallback(self, mock_client):
        """Test max leverage fallback to default"""
        mock_client.market = {"id": "ETHUSDT"}
        mock_client.exchange.fapiPrivateGetLeverageBracket.return_value = []

        max_lev = mock_client.get_max_leverage()

        assert max_lev == 20  # Default fallback

    def test_get_max_leverage_error(self, mock_client):
        """Test max leverage error handling"""
        mock_client.market = {"id": "ETHUSDT"}
        mock_client.exchange.fapiPrivateGetLeverageBracket.side_effect = Exception(
            "API Error"
        )

        max_lev = mock_client.get_max_leverage()

        assert max_lev == 20  # Default fallback


class TestSymbolLimits:
    """Test cases for get_symbol_limits method"""

    @pytest.fixture
    def mock_client(self):
        """Create a properly mocked BinanceClient"""
        with patch("alphaloop.market.exchange.ccxt.binanceusdm") as mock_binance:
            mock_exchange = MagicMock()
            mock_exchange.load_markets.return_value = {
                "ETH/USDT:USDT": {
                    "id": "ETHUSDT",
                    "symbol": "ETH/USDT:USDT",
                    "limits": {
                        "amount": {"min": 0.001, "max": 10000},
                        "cost": {"min": 5.0},
                    },
                    "precision": {"amount": 0.001},
                }
            }
            mock_binance.return_value = mock_exchange

            with patch("alphaloop.market.exchange.LEVERAGE", 5):
                client = BinanceClient()
            yield client

    def test_get_symbol_limits_success(self, mock_client):
        """Test successful symbol limits retrieval"""
        limits = mock_client.get_symbol_limits()

        assert limits["minQty"] == 0.001
        assert limits["maxQty"] == 10000
        assert limits["stepSize"] == 0.001
        assert limits["minNotional"] == 5.0

    def test_get_symbol_limits_with_market_notional(self, mock_client):
        """Test limits with market-specific minNotional"""
        mock_client.market["limits"]["market"] = {"min": 10.0}

        limits = mock_client.get_symbol_limits()

        assert limits["minNotional"] == 10.0

    def test_get_symbol_limits_missing_fields(self, mock_client):
        """Test limits with missing optional fields"""
        mock_client.market = {"id": "ETHUSDT"}

        limits = mock_client.get_symbol_limits()

        # Should return defaults
        assert limits["minQty"] == 0.001
        assert limits["maxQty"] == 100000
        assert limits["stepSize"] == 0.001
        assert limits["minNotional"] == 5.0

    def test_get_symbol_limits_error(self, mock_client):
        """Test limits retrieval error handling"""
        # Make market property raise exception
        mock_client.market = None

        limits = mock_client.get_symbol_limits()

        # Should return defaults
        assert limits["minQty"] == 0.001
        assert limits["maxQty"] == 100000


class TestTickerAndAccount:
    """Test cases for fetch_ticker_stats and fetch_account_data"""

    @pytest.fixture
    def mock_client(self):
        """Create a properly mocked BinanceClient"""
        with patch("alphaloop.market.exchange.ccxt.binanceusdm") as mock_binance:
            mock_exchange = MagicMock()
            mock_exchange.load_markets.return_value = {
                "ETH/USDT:USDT": {"id": "ETHUSDT", "symbol": "ETH/USDT:USDT"}
            }
            mock_binance.return_value = mock_exchange

            with patch("alphaloop.market.exchange.LEVERAGE", 5):
                client = BinanceClient()
            yield client

    def test_fetch_ticker_stats_success(self, mock_client):
        """Test successful ticker stats retrieval"""
        mock_client.exchange.fetch_ticker.return_value = {
            "symbol": "ETH/USDT:USDT",
            "percentage": 5.25,
            "quoteVolume": 1234567.89,
        }

        stats = mock_client.fetch_ticker_stats()

        assert stats["percentage"] == 5.25
        assert stats["quoteVolume"] == 1234567.89

    def test_fetch_ticker_stats_error(self, mock_client):
        """Test ticker stats error handling"""
        mock_client.exchange.fetch_ticker.side_effect = Exception("API Error")

        stats = mock_client.fetch_ticker_stats()

        assert stats is None

    def test_fetch_account_data_success(self, mock_client):
        """Test successful account data retrieval"""
        mock_client.exchange.fapiPrivateV2GetAccount.return_value = {
            "assets": [
                {"asset": "USDT", "availableBalance": "1000.50"},
                {"asset": "BTC", "availableBalance": "0.5"},
            ],
            "positions": [
                {
                    "symbol": "ETHUSDT",
                    "positionAmt": "2.5",
                    "entryPrice": "2000.0",
                },
                {"symbol": "BTCUSDT", "positionAmt": "0", "entryPrice": "0"},
            ],
        }

        data = mock_client.fetch_account_data()

        assert data["balance"] == 1000.50
        assert data["position_amt"] == 2.5
        assert data["entry_price"] == 2000.0

    def test_fetch_account_data_no_position(self, mock_client):
        """Test account data with no position"""
        mock_client.exchange.fapiPrivateV2GetAccount.return_value = {
            "assets": [{"asset": "USDT", "availableBalance": "1000.0"}],
            "positions": [{"symbol": "BTCUSDT", "positionAmt": "0", "entryPrice": "0"}],
        }

        data = mock_client.fetch_account_data()

        assert data["balance"] == 1000.0
        assert data["position_amt"] == 0.0
        assert data["entry_price"] == 0.0

    def test_fetch_account_data_error(self, mock_client):
        """Test account data error handling"""
        mock_client.exchange.fapiPrivateV2GetAccount.side_effect = Exception(
            "API Error"
        )

        data = mock_client.fetch_account_data()

        assert data is None

    def test_fetch_open_orders_success(self, mock_client):
        """Test successful open orders fetch"""
        mock_client.exchange.fetch_open_orders.return_value = [
            {"id": "123", "side": "buy", "price": 2000.0, "amount": 1.0}
        ]

        orders = mock_client.fetch_open_orders()

        assert len(orders) == 1
        assert orders[0]["id"] == "123"

    def test_fetch_open_orders_error(self, mock_client):
        """Test open orders error handling"""
        mock_client.exchange.fetch_open_orders.side_effect = Exception("API Error")

        orders = mock_client.fetch_open_orders()

        assert orders == []
