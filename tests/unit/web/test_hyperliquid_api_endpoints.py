"""
Unit tests for Hyperliquid API endpoints
Hyperliquid API 端点单元测试

Tests for:
- /api/hyperliquid/prices
- /api/hyperliquid/connection
- /api/hyperliquid/cancel-order
- /api/hyperliquid/status (strategy instance creation)

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


class TestHyperliquidStatusEndpoint:
    """
    Unit tests for /api/hyperliquid/status endpoint strategy instance creation
    /api/hyperliquid/status 端点策略实例创建的单元测试
    
    Tests that the endpoint creates a Hyperliquid strategy instance when the page loads.
    测试端点是否在页面加载时创建 Hyperliquid 策略实例。
    """

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_status_endpoint_creates_strategy_instance_when_missing(
        self, mock_bot_engine, mock_get_exchange
    ):
        """
        Test that /api/hyperliquid/status creates strategy instance if it doesn't exist
        测试 /api/hyperliquid/status 在策略实例不存在时创建它
        """
        # Mock exchange client / 模拟交易所客户端
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.symbol = "ETH/USDC:USDC"
        mock_exchange.testnet = False
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "available_balance": 5000.0,
            "position_amt": 0.1,
            "leverage": 5,
        }
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
        }
        mock_exchange.fetch_positions.return_value = []
        mock_exchange.fetch_open_orders.return_value = []
        mock_get_exchange.return_value = mock_exchange

        # Mock bot_engine with no existing hyperliquid instance
        # 模拟 bot_engine，没有现有的 hyperliquid 实例
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock(return_value=True)

        # Create a new instance after add_strategy_instance is called
        # 在 add_strategy_instance 被调用后创建新实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_exchange
        mock_strategy_instances.get = Mock(
            side_effect=lambda key: mock_instance if key == "hyperliquid" else None
        )

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["exchange"] == "hyperliquid"

        # Verify that add_strategy_instance was called
        # 验证 add_strategy_instance 被调用
        mock_bot_engine.add_strategy_instance.assert_called_once()
        call_args = mock_bot_engine.add_strategy_instance.call_args
        assert call_args[0][0] == "hyperliquid"  # strategy_id
        assert call_args[0][1] == "fixed_spread"  # strategy_type
        assert call_args[1]["symbol"] == "ETH/USDC:USDC"  # symbol
        assert call_args[1]["exchange"] == mock_exchange  # exchange

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_status_endpoint_reuses_existing_strategy_instance(
        self, mock_bot_engine, mock_get_exchange
    ):
        """
        Test that /api/hyperliquid/status reuses existing strategy instance
        测试 /api/hyperliquid/status 重用现有的策略实例
        """
        # Mock exchange client / 模拟交易所客户端
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.symbol = "ETH/USDC:USDC"
        mock_exchange.testnet = False
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "available_balance": 5000.0,
            "position_amt": 0.1,
            "leverage": 5,
        }
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
        }
        mock_exchange.fetch_positions.return_value = []
        mock_exchange.fetch_open_orders.return_value = []
        mock_get_exchange.return_value = mock_exchange

        # Mock bot_engine with existing hyperliquid instance
        # 模拟 bot_engine，有现有的 hyperliquid 实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_exchange
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = [("hyperliquid", mock_instance)]
        mock_strategy_instances.get.return_value = mock_instance
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock()

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True

        # Verify that add_strategy_instance was NOT called (instance already exists)
        # 验证 add_strategy_instance 未被调用（实例已存在）
        mock_bot_engine.add_strategy_instance.assert_not_called()

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_status_endpoint_does_not_create_instance_when_not_connected(
        self, mock_bot_engine, mock_get_exchange
    ):
        """
        Test that /api/hyperliquid/status does not create instance when exchange is not connected
        测试当交易所未连接时，/api/hyperliquid/status 不创建实例
        """
        # Mock exchange client that is not connected
        # 模拟未连接的交易所客户端
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = False
        mock_exchange.testnet = False
        mock_get_exchange.return_value = mock_exchange

        # Mock bot_engine
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock()

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/status")

        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is False
        assert "error" in data

        # Verify that add_strategy_instance was NOT called
        # 验证 add_strategy_instance 未被调用
        mock_bot_engine.add_strategy_instance.assert_not_called()

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_status_endpoint_handles_add_instance_failure(
        self, mock_bot_engine, mock_get_exchange
    ):
        """
        Test that /api/hyperliquid/status handles failure to add strategy instance gracefully
        测试 /api/hyperliquid/status 优雅处理添加策略实例失败的情况
        """
        # Mock exchange client / 模拟交易所客户端
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.symbol = "ETH/USDC:USDC"
        mock_exchange.testnet = False
        mock_exchange.fetch_account_data.return_value = {
            "balance": 10000.0,
            "available_balance": 5000.0,
            "position_amt": 0.1,
            "leverage": 5,
        }
        mock_exchange.fetch_market_data.return_value = {
            "mid_price": 3000.0,
            "best_bid": 2999.0,
            "best_ask": 3001.0,
        }
        mock_exchange.fetch_positions.return_value = []
        mock_exchange.fetch_open_orders.return_value = []
        mock_get_exchange.return_value = mock_exchange

        # Mock bot_engine where add_strategy_instance fails
        # 模拟 bot_engine，add_strategy_instance 失败
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock(return_value=False)

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/status")

        # Should still return status even if instance creation fails
        # 即使实例创建失败，仍应返回状态
        assert response.status_code == 200
        data = response.json()
        # Status should still be returned (instance creation is best-effort)
        # 仍应返回状态（实例创建是尽力而为的）
        assert "connected" in data or "error" in data


class TestHyperliquidBotControl:
    """Unit tests for bot control endpoints (/api/control) in Hyperliquid context / Hyperliquid 上下文中的 bot 控制端点单元测试"""

    @patch("server.bot_engine")
    @patch("server.get_default_exchange")
    def test_control_start_with_hyperliquid_instance(self, mock_get_default_exchange, mock_bot_engine):
        """
        Test starting bot with Hyperliquid strategy instance
        测试使用 Hyperliquid 策略实例启动 bot
        """
        from unittest.mock import MagicMock
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Mock Hyperliquid exchange
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.last_order_error = None
        mock_get_default_exchange.return_value = mock_exchange
        
        # Mock strategy instance with HyperliquidClient
        mock_instance = MagicMock()
        mock_instance.strategy_id = "hyperliquid"
        mock_instance.strategy = MagicMock()
        mock_instance.strategy.spread = 0.001  # Valid spread
        mock_instance.running = False
        mock_instance.exchange = mock_exchange
        
        # Mock bot_engine
        mock_bot_engine.strategy_instances = {"hyperliquid": mock_instance}
        mock_bot_engine.strategy = None  # No legacy strategy
        mock_bot_engine.risk = MagicMock()
        mock_bot_engine.risk.validate_proposal.return_value = (True, None)
        mock_bot_engine.alert = None
        
        # Mock threading
        with patch("server.threading.Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            client = TestClient(server.app)
            response = client.post("/api/control?action=start")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"
            
            # Verify instance was marked as running
            assert mock_instance.running is True
            # Verify thread was started
            mock_thread.start.assert_called_once()

    @patch("server.bot_engine")
    @patch("server.get_default_exchange")
    @patch("server.is_running", False)
    def test_control_start_without_strategy_instance(self, mock_get_default_exchange, mock_bot_engine):
        """
        Test starting bot fails when no strategy instance is available
        测试当没有策略实例可用时启动 bot 失败
        """
        # Ensure is_running is False
        server.is_running = False
        
        # Mock bot_engine with no instances
        mock_bot_engine.strategy_instances = {}
        mock_bot_engine.strategy = None
        
        client = TestClient(server.app)
        response = client.post("/api/control?action=start")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "No strategy instance available" in data["error"] or "没有可用的策略实例" in data["error"]

    @patch("server.bot_engine")
    @patch("server.get_default_exchange")
    def test_control_start_with_invalid_spread(self, mock_get_default_exchange, mock_bot_engine):
        """
        Test starting bot fails when strategy spread is not configured
        测试当策略价差未配置时启动 bot 失败
        """
        from unittest.mock import MagicMock
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Ensure is_running is False
        server.is_running = False
        
        # Mock Hyperliquid exchange
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.last_order_error = None
        mock_get_default_exchange.return_value = mock_exchange
        
        # Mock strategy instance without spread
        mock_instance = MagicMock()
        mock_instance.strategy_id = "hyperliquid"
        mock_instance.strategy = MagicMock()
        # Use getattr to simulate None spread
        type(mock_instance.strategy).spread = None  # No spread configured
        mock_instance.running = False
        
        # Mock bot_engine
        mock_bot_engine.strategy_instances = {"hyperliquid": mock_instance}
        mock_bot_engine.strategy = None
        
        client = TestClient(server.app)
        response = client.post("/api/control?action=start")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "spread" in data["error"].lower() or "价差" in data["error"]

    @patch("server.bot_engine")
    def test_control_stop(self, mock_bot_engine):
        """
        Test stopping bot
        测试停止 bot
        """
        from unittest.mock import MagicMock
        
        # Mock strategy instances
        mock_instance1 = MagicMock()
        mock_instance1.running = True
        mock_instance2 = MagicMock()
        mock_instance2.running = True
        
        mock_bot_engine.strategy_instances = {
            "hyperliquid": mock_instance1,
            "default": mock_instance2,
        }
        mock_bot_engine.alert = None
        mock_bot_engine.current_stage = "Running"
        
        # Set global is_running
        server.is_running = True
        
        client = TestClient(server.app)
        response = client.post("/api/control?action=stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopped"
        
        # Verify all instances were marked as stopped
        assert mock_instance1.running is False
        assert mock_instance2.running is False
        # Verify alert was cleared
        assert mock_bot_engine.alert is None

    @patch("server.bot_engine")
    def test_control_invalid_action(self, mock_bot_engine):
        """
        Test control endpoint with invalid action
        测试使用无效操作的控制端点
        """
        client = TestClient(server.app)
        response = client.post("/api/control?action=invalid")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Invalid action" in data["error"]

    @patch("server.bot_engine")
    @patch("server.is_running", False)
    def test_status_endpoint_returns_active_field(self, mock_bot_engine):
        """
        Test /api/status endpoint returns active field for button state
        测试 /api/status 端点返回 active 字段以用于按钮状态
        """
        from unittest.mock import MagicMock
        
        # Ensure is_running is False
        server.is_running = False
        
        # Mock bot_engine
        mock_bot_engine.get_status.return_value = {
            "symbol": "ETH/USDC:USDC",
            "spread": 0.001,
            "quantity": 0.1,
            "leverage": 5,
        }
        mock_bot_engine.strategy_instances = {}
        mock_bot_engine.strategy = MagicMock()
        mock_bot_engine.current_stage = "Idle"
        
        client = TestClient(server.app)
        response = client.get("/api/status")
        
        assert response.status_code == 200
        data = response.json()
        # Verify active field is present
        assert "active" in data
        assert isinstance(data["active"], bool)
        assert data["active"] is False  # Should be False when is_running is False

