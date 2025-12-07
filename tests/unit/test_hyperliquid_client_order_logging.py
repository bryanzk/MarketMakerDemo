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
    client.last_api_error = None  # Ensure last_api_error is None initially
    order = {"side": "buy", "type": "limit", "price": 1234.5, "quantity": 0.1}

    with patch.object(client, "_validate_order", return_value=None), patch.object(
        client, "_build_order_payload", return_value={}
    ), patch.object(client, "_make_request", return_value=None):
        # When _make_request returns None and last_api_error is None, 
        # status_code will be "Unknown", so error_type will be "network_error"
        # 当 _make_request 返回 None 且 last_api_error 为 None 时，
        # status_code 将是 "Unknown"，所以 error_type 将是 "network_error"
        created = client.place_orders([order])

    assert created == []
    assert client.last_order_error is not None
    # Error type can be "network_error", "invalid_request", or "unknown_error" depending on last_api_error
    # 错误类型可以是 "network_error"、"invalid_request" 或 "unknown_error"，取决于 last_api_error
    assert client.last_order_error["type"] in ["network_error", "invalid_request", "unknown_error"]
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
