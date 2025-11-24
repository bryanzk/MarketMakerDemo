"""
Unit tests for enhanced exception handling in exchange.py
Tests specific ccxt exception types: InsufficientFunds, InvalidOrder, RateLimitExceeded, etc.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from ccxt import (
    InsufficientFunds,
    InvalidOrder,
    RateLimitExceeded,
    NetworkError,
    ExchangeError,
    OrderNotFound,
)
from alphaloop.market.exchange import BinanceClient


class TestExceptionHandling:
    """Test enhanced exception handling in place_orders and cancel_orders"""

    @pytest.fixture
    def mock_client(self):
        """Create a properly mocked BinanceClient for testing"""
        with patch("alphaloop.market.exchange.ccxt.binanceusdm") as mock_binance:
            mock_exchange = MagicMock()
            mock_exchange.load_markets.return_value = {
                "ETH/USDT:USDT": {"id": "ETHUSDT", "symbol": "ETH/USDT:USDT"}
            }
            mock_binance.return_value = mock_exchange

            with patch("alphaloop.market.exchange.LEVERAGE", 5):
                client = BinanceClient()

            # Reset error tracking
            client.last_order_error = None
            client.last_api_error = None
            yield client

    def test_place_orders_insufficient_funds(self, mock_client):
        """Test that InsufficientFunds exception is properly caught and stored"""
        # Setup: create_order raises InsufficientFunds
        mock_client.exchange.create_order.side_effect = InsufficientFunds(
            "binance {\"code\":-2019,\"msg\":\"Margin is insufficient.\"}"
        )

        orders = [{"side": "buy", "price": 1000.0, "quantity": 0.01}]
        result = mock_client.place_orders(orders)

        # Should return empty list (no orders placed)
        assert result == []

        # Should store error details
        assert mock_client.last_order_error is not None
        assert mock_client.last_order_error["type"] == "insufficient_funds"
        assert "Insufficient balance" in mock_client.last_order_error["message"]
        assert "buy" in mock_client.last_order_error["message"]

    def test_place_orders_invalid_order(self, mock_client):
        """Test that InvalidOrder exception captures Binance rejection details"""
        mock_client.exchange.create_order.side_effect = InvalidOrder(
            "binance {\"code\":-1111,\"msg\":\"Precision is over the maximum defined for this asset.\"}"
        )

        orders = [{"side": "sell", "price": 2000.0, "quantity": 0.001}]
        result = mock_client.place_orders(orders)

        assert result == []
        assert mock_client.last_order_error is not None
        assert mock_client.last_order_error["type"] == "invalid_order"
        assert "Invalid order rejected" in mock_client.last_order_error["message"]
        assert "details" in mock_client.last_order_error

    def test_place_orders_rate_limit(self, mock_client):
        """Test that RateLimitExceeded is logged and bot pauses"""
        mock_client.exchange.create_order.side_effect = RateLimitExceeded(
            "binance {\"code\":-1003,\"msg\":\"Too many requests.\"}"
        )

        orders = [{"side": "buy", "price": 1500.0, "quantity": 0.01}]
        
        with patch("time.sleep") as mock_sleep:
            result = mock_client.place_orders(orders)

        assert result == []
        assert mock_client.last_order_error is not None
        assert mock_client.last_order_error["type"] == "rate_limit"
        mock_sleep.assert_called_once_with(1)  # Should pause 1 second

    def test_place_orders_network_error(self, mock_client):
        """Test NetworkError is properly logged"""
        mock_client.exchange.create_order.side_effect = NetworkError(
            "Connection timeout"
        )

        orders = [{"side": "buy", "price": 1000.0, "quantity": 0.01}]
        result = mock_client.place_orders(orders)

        assert result == []
        assert mock_client.last_order_error is not None
        assert mock_client.last_order_error["type"] == "network_error"
        assert "Network error" in mock_client.last_order_error["message"]

    def test_place_orders_exchange_error(self, mock_client):
        """Test generic ExchangeError is caught with full details"""
        mock_client.exchange.create_order.side_effect = ExchangeError(
            "binance {\"code\":-4131,\"msg\":\"The counterparty's best price does not meet the PERCENT_PRICE filter limit.\"}"
        )

        orders = [{"side": "sell", "price": 500.0, "quantity": 0.01}]
        result = mock_client.place_orders(orders)

        assert result == []
        assert mock_client.last_order_error is not None
        assert mock_client.last_order_error["type"] == "exchange_error"
        assert "Binance API error" in mock_client.last_order_error["message"]

    def test_place_orders_success_clears_error(self, mock_client):
        """Test that successful order placement clears last_order_error"""
        # First, set an error
        mock_client.last_order_error = {
            "type": "test_error",
            "message": "Previous error",
        }

        # Now place a successful order
        mock_client.exchange.create_order.return_value = {
            "id": "12345",
            "side": "buy",
            "price": 1000.0,
            "amount": 0.01,
        }

        orders = [{"side": "buy", "price": 1000.0, "quantity": 0.01}]
        result = mock_client.place_orders(orders)

        assert len(result) == 1
        assert mock_client.last_order_error is None  # Should be cleared

    def test_place_orders_partial_success(self, mock_client):
        """Test that one failure doesn't stop other orders, successful order clears error"""
        # First order fails, second succeeds
        mock_client.exchange.create_order.side_effect = [
            InsufficientFunds("Not enough balance"),
            {"id": "67890", "side": "sell", "price": 2000.0, "amount": 0.01},
        ]

        orders = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
            {"side": "sell", "price": 2000.0, "quantity": 0.01},
        ]
        result = mock_client.place_orders(orders)

        # Should have one successful order
        assert len(result) == 1
        assert result[0]["id"] == "67890"

        # Error should be cleared by successful second order
        assert mock_client.last_order_error is None

    def test_cancel_orders_order_not_found(self, mock_client):
        """Test that OrderNotFound is handled gracefully (warning only)"""
        mock_client.exchange.cancel_order.side_effect = OrderNotFound(
            "Order not found (may be already filled)"
        )

        # Should not raise exception
        mock_client.cancel_orders(["12345"])

        # Should NOT store in last_api_error (just a warning)
        # (Current implementation doesn't store OrderNotFound)

    def test_cancel_orders_network_error(self, mock_client):
        """Test that NetworkError in cancel is stored"""
        mock_client.exchange.cancel_order.side_effect = NetworkError(
            "Connection lost"
        )

        mock_client.cancel_orders(["12345"])

        assert mock_client.last_api_error is not None
        assert mock_client.last_api_error["type"] == "network_error"
        assert "12345" in mock_client.last_api_error["message"]

    def test_cancel_orders_exchange_error(self, mock_client):
        """Test that ExchangeError in cancel is stored"""
        mock_client.exchange.cancel_order.side_effect = ExchangeError(
            "API error"
        )

        mock_client.cancel_orders(["54321"])

        assert mock_client.last_api_error is not None
        assert mock_client.last_api_error["type"] == "exchange_error"

    def test_error_tracking_fields_initialized(self, mock_client):
        """Test that error tracking fields exist on BinanceClient"""
        assert hasattr(mock_client, "last_order_error")
        assert hasattr(mock_client, "last_api_error")
        assert mock_client.last_order_error is None
        assert mock_client.last_api_error is None
