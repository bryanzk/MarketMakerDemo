from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

import server


@patch("server.get_exchange_by_name")
def test_hyperliquid_status_connected(mock_get_exchange_by_name):
    """Integration-style test to ensure /api/hyperliquid/status returns connected payload when exchange is mocked."""
    mock_exchange = Mock()
    mock_exchange.is_connected = True
    mock_exchange.testnet = False
    mock_exchange.symbol = "ETHUSDC"
    mock_exchange.fetch_account_data.return_value = {
        "balance": 100.0,
        "available_balance": 90.0,
        "position_amt": 0.0,
        "unrealized_pnl": 0.0,
        "leverage": 5,
    }
    mock_exchange.fetch_market_data.return_value = {"mid_price": 1234.56}
    mock_exchange.fetch_open_orders.return_value = []
    mock_exchange.fetch_positions.return_value = []

    mock_get_exchange_by_name.return_value = mock_exchange

    client = TestClient(server.app)
    response = client.get("/api/hyperliquid/status")

    assert response.status_code == 200
    data = response.json()
    assert data["connected"] is True
    assert data["exchange"] == "hyperliquid"
    trace_header = response.headers.get("X-Trace-ID")
    assert trace_header or "trace_id" in data
