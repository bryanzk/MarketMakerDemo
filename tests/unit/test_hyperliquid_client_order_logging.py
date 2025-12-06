import pytest
from unittest.mock import patch

from src.trading.hyperliquid_client import HyperliquidClient


def _make_client_stub() -> HyperliquidClient:
    """Create a lightweight HyperliquidClient stub without running __init__."""
    client = object.__new__(HyperliquidClient)
    client.symbol = "ETHUSDC"
    client.last_order_error = None
    return client


def test_place_orders_records_order_req_id_on_no_response():
    """When API returns no response, last_order_error should include order_req_id and order snapshot."""
    client = _make_client_stub()
    order = {"side": "buy", "type": "limit", "price": 1234.5, "quantity": 0.1}

    with patch.object(client, "_validate_order", return_value=None), patch.object(
        client, "_build_order_payload", return_value={}
    ), patch.object(client, "_make_request", return_value=None):
        created = client.place_orders([order])

    assert created == []
    assert client.last_order_error is not None
    assert client.last_order_error["type"] == "network_error"
    assert client.last_order_error["order"]["quantity"] == 0.1
    assert "order_req_id" in client.last_order_error


def test_place_orders_unknown_error_includes_trace_id():
    """Unexpected errors should be recorded with trace_id in last_order_error."""
    client = _make_client_stub()
    order = {"side": "sell", "type": "limit", "price": 1100, "quantity": 0.2}

    with patch.object(client, "_validate_order", return_value=None), patch.object(
        client, "_build_order_payload", return_value={}
    ), patch.object(
        client, "_make_request", side_effect=RuntimeError("boom")
    ), patch("src.trading.hyperliquid_client.get_trace_id", return_value="req-test"):
        client.place_orders([order])

    assert client.last_order_error is not None
    assert client.last_order_error["type"] == "unknown_error"
    assert client.last_order_error["trace_id"] == "req-test"
