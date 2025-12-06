"""
Smoke tests for Hyperliquid API endpoints
Hyperliquid API 端点冒烟测试

Smoke tests verify critical paths without full integration.
冒烟测试验证关键路径，无需完整集成。

Tests for:
- /api/hyperliquid/prices
- /api/hyperliquid/connection
- /api/hyperliquid/cancel-order

Owner: Agent QA
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidPricesEndpointSmoke:
    """Smoke tests for /api/hyperliquid/prices endpoint / /api/hyperliquid/prices 端点冒烟测试"""

    @patch("server.get_exchange_by_name")
    def test_smoke_prices_endpoint_returns_trace_id(self, mock_get_exchange):
        """
        Smoke Test: Prices endpoint returns trace_id
        冒烟测试：价格端点返回 trace_id
        
        Critical path: All API responses must include trace_id for debugging.
        关键路径：所有 API 响应必须包含 trace_id 以便调试。
        """
        mock_exchange = MagicMock()
        mock_exchange.fetch_multiple_prices = Mock(
            return_value={"ETH/USDC:USDC": 2500.0}
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=ETH/USDC:USDC")

        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data, "Prices endpoint must return trace_id / 价格端点必须返回 trace_id"

    @patch("server.get_exchange_by_name")
    def test_smoke_prices_endpoint_handles_multiple_symbols(self, mock_get_exchange):
        """
        Smoke Test: Prices endpoint handles multiple symbols
        冒烟测试：价格端点处理多个交易对
        
        Critical path: Frontend requests prices for multiple pairs simultaneously.
        关键路径：前端同时请求多个交易对的价格。
        """
        mock_exchange = MagicMock()
        mock_exchange.fetch_multiple_prices = Mock(
            return_value={
                "ETH/USDC:USDC": 2500.0,
                "BTC/USDC:USDC": 45000.0,
                "SOL/USDC:USDC": 100.0,
            }
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get(
            "/api/hyperliquid/prices?symbols=ETH/USDC:USDC,BTC/USDC:USDC,SOL/USDC:USDC"
        )

        assert response.status_code == 200
        data = response.json()
        assert "prices" in data
        assert len(data["prices"]) == 3
        assert all(
            symbol in data["prices"] for symbol in ["ETH/USDC:USDC", "BTC/USDC:USDC", "SOL/USDC:USDC"]
        )

    @patch("server.get_exchange_by_name")
    def test_smoke_prices_endpoint_handles_missing_exchange(self, mock_get_exchange):
        """
        Smoke Test: Prices endpoint handles missing exchange gracefully
        冒烟测试：价格端点优雅处理缺失的交易所
        
        Critical path: System must handle exchange initialization failures.
        关键路径：系统必须处理交易所初始化失败。
        """
        mock_get_exchange.return_value = None

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=ETH/USDC:USDC")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "error_type" in data
        assert "trace_id" in data


class TestHyperliquidConnectionEndpointSmoke:
    """Smoke tests for /api/hyperliquid/connection endpoint / /api/hyperliquid/connection 端点冒烟测试"""

    @patch("server.get_exchange_by_name")
    def test_smoke_connection_endpoint_returns_trace_id(self, mock_get_exchange):
        """
        Smoke Test: Connection endpoint returns trace_id
        冒烟测试：连接端点返回 trace_id
        
        Critical path: All API responses must include trace_id for debugging.
        关键路径：所有 API 响应必须包含 trace_id 以便调试。
        """
        mock_exchange = MagicMock()
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "trace_id" in data, "Connection endpoint must return trace_id / 连接端点必须返回 trace_id"

    @patch("server.get_exchange_by_name")
    def test_smoke_connection_endpoint_returns_required_fields(self, mock_get_exchange):
        """
        Smoke Test: Connection endpoint returns all required fields
        冒烟测试：连接端点返回所有必需字段
        
        Critical path: Frontend depends on these fields for connection status display.
        关键路径：前端依赖这些字段来显示连接状态。
        """
        mock_exchange = MagicMock()
        mock_exchange.get_connection_status = Mock(return_value={"connected": False})
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        required_fields = ["connected", "auth_status", "market_data_fresh", "warnings", "trace_id", "ok"]
        for field in required_fields:
            assert field in data, f"Connection endpoint must return {field} / 连接端点必须返回 {field}"

    @patch("server.get_exchange_by_name")
    @patch("time.time")
    def test_smoke_connection_endpoint_detects_stale_data(
        self, mock_time, mock_get_exchange
    ):
        """
        Smoke Test: Connection endpoint detects stale market data
        冒烟测试：连接端点检测过期市场数据
        
        Critical path: System must warn users when market data is outdated.
        关键路径：当市场数据过时时，系统必须警告用户。
        """
        mock_time.return_value = 2000.0

        mock_exchange = MagicMock()
        mock_exchange.get_connection_status = Mock(return_value={"connected": True})
        mock_exchange.fetch_market_data = Mock(
            return_value={"timestamp": 1930000}  # 70 seconds ago
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "market_data_fresh" in data
        assert data["market_data_fresh"] is False
        assert len(data["warnings"]) > 0


class TestHyperliquidCancelOrderEndpointSmoke:
    """Smoke tests for /api/hyperliquid/cancel-order endpoint / /api/hyperliquid/cancel-order 端点冒烟测试"""

    @patch("server.get_exchange_by_name")
    def test_smoke_cancel_order_endpoint_success(self, mock_get_exchange):
        """
        Smoke Test: Cancel order endpoint successfully cancels order
        冒烟测试：取消订单端点成功取消订单
        
        Critical path: Order cancellation is essential for risk management.
        关键路径：订单取消对风险管理至关重要。
        """
        mock_exchange = MagicMock()
        mock_exchange.is_connected = True
        mock_exchange.cancel_orders = Mock(return_value=None)
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "order_id" in data
        assert data["order_id"] == "12345"
        mock_exchange.cancel_orders.assert_called_once_with(["12345"])

    @patch("server.get_exchange_by_name")
    def test_smoke_cancel_order_endpoint_handles_not_connected(self, mock_get_exchange):
        """
        Smoke Test: Cancel order endpoint handles not connected state
        冒烟测试：取消订单端点处理未连接状态
        
        Critical path: System must prevent order operations when not connected.
        关键路径：系统必须在未连接时阻止订单操作。
        """
        mock_exchange = MagicMock()
        mock_exchange.is_connected = False
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "not connected" in data["error"].lower() or "未连接" in data["error"]

    @patch("server.get_exchange_by_name")
    def test_smoke_cancel_order_endpoint_handles_exception(self, mock_get_exchange):
        """
        Smoke Test: Cancel order endpoint handles exceptions gracefully
        冒烟测试：取消订单端点优雅处理异常
        
        Critical path: System must not crash on order cancellation errors.
        关键路径：系统不得因订单取消错误而崩溃。
        """
        mock_exchange = MagicMock()
        mock_exchange.is_connected = True
        mock_exchange.cancel_orders = Mock(
            side_effect=Exception("Order not found / 订单未找到")
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        # Should not raise exception / 不应抛出异常
        assert isinstance(data, dict)

