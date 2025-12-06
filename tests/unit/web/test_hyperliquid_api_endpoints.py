"""
Unit tests for Hyperliquid API endpoints
Hyperliquid API 端点单元测试

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


class TestHyperliquidPricesEndpoint:
    """Unit tests for /api/hyperliquid/prices endpoint / /api/hyperliquid/prices 端点单元测试"""

    def test_prices_endpoint_missing_symbols_param(self):
        """Test prices endpoint returns error when symbols param is missing / 测试缺少 symbols 参数时返回错误"""
        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices")

        assert response.status_code == 200  # FastAPI returns 200 with error in body
        data = response.json()
        assert "error" in data or "error_type" in data
        assert "trace_id" in data

    def test_prices_endpoint_empty_symbols(self):
        """Test prices endpoint returns error when symbols is empty / 测试 symbols 为空时返回错误"""
        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "error_type" in data
        assert "trace_id" in data

    @patch("server.get_exchange_by_name")
    def test_prices_endpoint_exchange_not_initialized(self, mock_get_exchange):
        """Test prices endpoint returns error when exchange is not initialized / 测试交易所未初始化时返回错误"""
        mock_get_exchange.return_value = None

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=ETH/USDC:USDC")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "error_type" in data
        assert "EXCHANGE_NOT_INITIALIZED" in str(data)

    @patch("server.get_exchange_by_name")
    def test_prices_endpoint_single_symbol_success(self, mock_get_exchange):
        """Test prices endpoint returns price for single symbol / 测试单个交易对返回价格"""
        # Mock exchange client without fetch_multiple_prices (fallback path)
        # 模拟没有 fetch_multiple_prices 的交易所客户端（回退路径）
        mock_exchange = MagicMock()
        # Remove fetch_multiple_prices to force fallback path
        # 移除 fetch_multiple_prices 以强制使用回退路径
        del mock_exchange.fetch_multiple_prices
        mock_exchange.symbol = None
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 2500.0,
            "timestamp": 1000000,
        }
        mock_exchange.set_symbol = Mock()
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=ETH/USDC:USDC")

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "prices" in data
        assert "ETH/USDC:USDC" in data["prices"]
        assert data["prices"]["ETH/USDC:USDC"] == 2500.0
        assert "trace_id" in data

    @patch("server.get_exchange_by_name")
    def test_prices_endpoint_multiple_symbols_success(self, mock_get_exchange):
        """Test prices endpoint returns prices for multiple symbols / 测试多个交易对返回价格"""
        # Mock exchange client with fetch_multiple_prices
        mock_exchange = MagicMock()
        mock_exchange.fetch_multiple_prices = Mock(
            return_value={
                "ETH/USDC:USDC": 2500.0,
                "BTC/USDC:USDC": 45000.0,
            }
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get(
            "/api/hyperliquid/prices?symbols=ETH/USDC:USDC,BTC/USDC:USDC"
        )

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "prices" in data
        assert len(data["prices"]) == 2
        assert data["prices"]["ETH/USDC:USDC"] == 2500.0
        assert data["prices"]["BTC/USDC:USDC"] == 45000.0

    @patch("server.get_exchange_by_name")
    def test_prices_endpoint_symbol_fetch_error(self, mock_get_exchange):
        """Test prices endpoint handles symbol fetch errors gracefully / 测试端点优雅处理交易对获取错误"""
        # Mock exchange client that raises error for one symbol (fallback path)
        # 模拟对某个交易对抛出错误的交易所客户端（回退路径）
        mock_exchange = MagicMock()
        # Remove fetch_multiple_prices to force fallback path
        # 移除 fetch_multiple_prices 以强制使用回退路径
        del mock_exchange.fetch_multiple_prices
        mock_exchange.symbol = None
        mock_exchange.set_symbol = Mock()

        def fetch_market_data():
            raise Exception("Rate limit exceeded / 速率限制已超出")

        mock_exchange.fetch_market_data = Mock(side_effect=fetch_market_data)
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/prices?symbols=ETH/USDC:USDC")

        assert response.status_code == 200
        data = response.json()
        # Should still return prices dict with None for failed symbol
        # 应该仍然返回价格字典，失败的交易对为 None
        assert "prices" in data
        assert data["prices"]["ETH/USDC:USDC"] is None


class TestHyperliquidConnectionEndpoint:
    """Unit tests for /api/hyperliquid/connection endpoint / /api/hyperliquid/connection 端点单元测试"""

    @patch("server.get_exchange_by_name")
    def test_connection_endpoint_exchange_not_initialized(self, mock_get_exchange):
        """Test connection endpoint returns error when exchange is not initialized / 测试交易所未初始化时返回错误"""
        mock_get_exchange.return_value = None

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "error" in data or "error_type" in data
        assert "EXCHANGE_NOT_INITIALIZED" in str(data)

    @patch("server.get_exchange_by_name")
    def test_connection_endpoint_not_connected(self, mock_get_exchange):
        """Test connection endpoint returns not connected status / 测试返回未连接状态"""
        # Mock exchange client without get_connection_status
        # 模拟没有 get_connection_status 的交易所客户端
        mock_exchange = MagicMock()
        # Remove get_connection_status to force default {"connected": False}
        # 移除 get_connection_status 以强制使用默认值 {"connected": False}
        if hasattr(mock_exchange, "get_connection_status"):
            delattr(mock_exchange, "get_connection_status")
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "connected" in data
        assert data["connected"] is False
        assert "auth_status" in data
        assert data["auth_status"] == "not_authenticated"
        assert "warnings" in data
        assert "trace_id" in data

    @patch("server.get_exchange_by_name")
    @patch("time.time")
    def test_connection_endpoint_connected_with_fresh_data(
        self, mock_time, mock_get_exchange
    ):
        """Test connection endpoint returns connected status with fresh market data / 测试返回连接状态和新鲜市场数据"""
        mock_time.return_value = 1000.0

        # Mock exchange client with connection status
        mock_exchange = MagicMock()
        mock_exchange.get_connection_status = Mock(
            return_value={"connected": True}
        )
        mock_exchange.fetch_market_data = Mock(
            return_value={"timestamp": 999000, "mid_price": 2500.0}
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "connected" in data
        assert data["connected"] is True
        assert "auth_status" in data
        assert data["auth_status"] == "authenticated"
        assert "market_data_fresh" in data
        assert data["market_data_fresh"] is True
        assert "warnings" in data
        assert len(data["warnings"]) == 0

    @patch("server.get_exchange_by_name")
    @patch("time.time")
    def test_connection_endpoint_stale_market_data(self, mock_time, mock_get_exchange):
        """Test connection endpoint detects stale market data / 测试检测到过期市场数据"""
        mock_time.return_value = 2000.0  # Current time

        # Mock exchange client with stale data (timestamp 1000 = 1 second old, but we'll make it 70 seconds old)
        mock_exchange = MagicMock()
        mock_exchange.get_connection_status = Mock(
            return_value={"connected": True}
        )
        mock_exchange.fetch_market_data = Mock(
            return_value={"timestamp": 1930000, "mid_price": 2500.0}  # 70 seconds ago
        )
        mock_get_exchange.return_value = mock_exchange

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "market_data_fresh" in data
        assert data["market_data_fresh"] is False
        assert "warnings" in data
        assert len(data["warnings"]) > 0
        assert any("stale" in w.lower() or "过期" in w for w in data["warnings"])


class TestHyperliquidCancelOrderEndpoint:
    """Unit tests for /api/hyperliquid/cancel-order endpoint / /api/hyperliquid/cancel-order 端点单元测试"""

    @patch("server.get_exchange_by_name")
    def test_cancel_order_endpoint_exchange_not_connected(self, mock_get_exchange):
        """Test cancel order endpoint returns error when exchange is not connected / 测试交易所未连接时返回错误"""
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
    def test_cancel_order_endpoint_exchange_not_initialized(self, mock_get_exchange):
        """Test cancel order endpoint returns error when exchange is not initialized / 测试交易所未初始化时返回错误"""
        mock_get_exchange.return_value = None

        client = TestClient(server.app)
        response = client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    @patch("server.get_exchange_by_name")
    def test_cancel_order_endpoint_success(self, mock_get_exchange):
        """Test cancel order endpoint successfully cancels order / 测试成功取消订单"""
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
        assert "message" in data
        mock_exchange.cancel_orders.assert_called_once_with(["12345"])

    @patch("server.get_exchange_by_name")
    def test_cancel_order_endpoint_handles_exception(self, mock_get_exchange):
        """Test cancel order endpoint handles exceptions gracefully / 测试优雅处理异常"""
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
        assert "Failed to cancel" in data["error"] or "取消订单失败" in data["error"]

