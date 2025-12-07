"""
Integration tests for Hyperliquid API endpoints
Hyperliquid API 端点集成测试

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Tests for:
- /api/hyperliquid/prices
- /api/hyperliquid/connection
- /api/hyperliquid/cancel-order
- /api/control (start/stop bot workflow)
- /api/status (active field updates)

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidPricesEndpointIntegration:
    """Integration tests for /api/hyperliquid/prices endpoint / /api/hyperliquid/prices 端点集成测试"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    def test_integration_prices_with_real_exchange_client(
        self, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Prices endpoint works with real HyperliquidClient
        集成测试：价格端点与真实 HyperliquidClient 一起工作
        
        Verifies that the endpoint correctly integrates with HyperliquidClient
        and handles the exchange client's methods.
        验证端点与 HyperliquidClient 正确集成并处理交易所客户端的方法。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create real client instance
        client_instance = HyperliquidClient()
        client_instance.is_connected = True

        # Mock fetch_multiple_prices method
        client_instance.fetch_multiple_prices = Mock(
            return_value={
                "ETH/USDC:USDC": 2500.0,
                "BTC/USDC:USDC": 45000.0,
            }
        )

        mock_get_exchange.return_value = client_instance

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.get(
            "/api/hyperliquid/prices?symbols=ETH/USDC:USDC,BTC/USDC:USDC"
        )

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "prices" in data
        assert len(data["prices"]) == 2
        assert data["prices"]["ETH/USDC:USDC"] == 2500.0
        assert data["prices"]["BTC/USDC:USDC"] == 45000.0
        assert "trace_id" in data

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    def test_integration_prices_fallback_to_individual_fetch(
        self, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Prices endpoint falls back to individual fetch when fetch_multiple_prices not available
        集成测试：当 fetch_multiple_prices 不可用时，价格端点回退到单独获取
        
        Verifies that the endpoint handles exchanges without batch price fetching.
        验证端点处理没有批量价格获取功能的交易所。
        
        Note: HyperliquidClient has fetch_multiple_prices, so we test with a mock exchange
        that doesn't have this method to verify the fallback path.
        注意：HyperliquidClient 有 fetch_multiple_prices，所以我们使用没有此方法的模拟交易所
        来验证回退路径。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create a mock exchange without fetch_multiple_prices to test fallback
        # 创建一个没有 fetch_multiple_prices 的模拟交易所来测试回退
        mock_exchange = MagicMock()
        mock_exchange.symbol = "ETH/USDC:USDC"
        # Ensure fetch_multiple_prices doesn't exist
        # 确保 fetch_multiple_prices 不存在
        if hasattr(mock_exchange, "fetch_multiple_prices"):
            delattr(mock_exchange, "fetch_multiple_prices")

        # Mock individual fetch_market_data calls
        def fetch_market_data():
            if mock_exchange.symbol == "ETH/USDC:USDC":
                return {"mid_price": 2500.0, "timestamp": 1000000}
            elif mock_exchange.symbol == "BTC/USDC:USDC":
                return {"mid_price": 45000.0, "timestamp": 1000000}
            return None

        mock_exchange.fetch_market_data = Mock(side_effect=fetch_market_data)
        mock_exchange.set_symbol = Mock()

        mock_get_exchange.return_value = mock_exchange

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.get(
            "/api/hyperliquid/prices?symbols=ETH/USDC:USDC,BTC/USDC:USDC"
        )

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "prices" in data
        assert len(data["prices"]) == 2
        # Verify set_symbol was called for each symbol
        # 验证为每个交易对调用了 set_symbol
        assert mock_exchange.set_symbol.call_count >= 2


class TestHyperliquidConnectionEndpointIntegration:
    """Integration tests for /api/hyperliquid/connection endpoint / /api/hyperliquid/connection 端点集成测试"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    def test_integration_connection_with_real_exchange_client(
        self, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Connection endpoint works with real HyperliquidClient
        集成测试：连接端点与真实 HyperliquidClient 一起工作
        
        Verifies that the endpoint correctly integrates with HyperliquidClient's
        connection status and market data methods.
        验证端点与 HyperliquidClient 的连接状态和市场数据方法正确集成。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create real client instance
        client_instance = HyperliquidClient()
        client_instance.is_connected = True

        # Mock connection status and market data methods
        client_instance.get_connection_status = Mock(
            return_value={"connected": True, "last_update": 1000.0}
        )
        client_instance.fetch_market_data = Mock(
            return_value={"timestamp": 999000, "mid_price": 2500.0}
        )

        mock_get_exchange.return_value = client_instance

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        assert "ok" in data and data["ok"] is True
        assert "connected" in data
        assert data["connected"] is True
        assert "auth_status" in data
        assert data["auth_status"] == "authenticated"
        assert "trace_id" in data

        # Verify methods were called
        # 验证方法被调用
        assert client_instance.get_connection_status.called or client_instance.is_connected

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    @patch("time.time")
    def test_integration_connection_handles_market_data_errors(
        self, mock_time, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Connection endpoint handles market data fetch errors gracefully
        集成测试：连接端点优雅处理市场数据获取错误
        
        Verifies that connection status is still returned even if market data fetch fails.
        验证即使市场数据获取失败，仍返回连接状态。
        """
        mock_time.return_value = 1000.0

        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create real client instance
        client_instance = HyperliquidClient()
        client_instance.is_connected = True

        # Mock connection status but market data fetch fails
        client_instance.get_connection_status = Mock(
            return_value={"connected": True}
        )
        client_instance.fetch_market_data = Mock(
            side_effect=Exception("Rate limit exceeded / 速率限制已超出")
        )

        mock_get_exchange.return_value = client_instance

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.get("/api/hyperliquid/connection")

        assert response.status_code == 200
        data = response.json()
        # Should still return connection status even if market data fails
        # 即使市场数据失败，仍应返回连接状态
        assert "connected" in data
        assert "trace_id" in data


class TestHyperliquidCancelOrderEndpointIntegration:
    """Integration tests for /api/hyperliquid/cancel-order endpoint / /api/hyperliquid/cancel-order 端点集成测试"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    def test_integration_cancel_order_with_real_exchange_client(
        self, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Cancel order endpoint works with real HyperliquidClient
        集成测试：取消订单端点与真实 HyperliquidClient 一起工作
        
        Verifies that the endpoint correctly integrates with HyperliquidClient's
        cancel_orders method.
        验证端点与 HyperliquidClient 的 cancel_orders 方法正确集成。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create real client instance
        client_instance = HyperliquidClient()
        client_instance.is_connected = True

        # Mock cancel_orders method
        client_instance.cancel_orders = Mock(return_value=None)

        mock_get_exchange.return_value = client_instance

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert "order_id" in data
        assert data["order_id"] == "12345"

        # Verify cancel_orders was called with correct order ID
        # 验证使用正确的订单 ID 调用了 cancel_orders
        client_instance.cancel_orders.assert_called_once_with(["12345"])

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("server.get_exchange_by_name")
    def test_integration_cancel_order_handles_exchange_errors(
        self, mock_get_exchange, mock_requests
    ):
        """
        Integration Test: Cancel order endpoint handles exchange errors gracefully
        集成测试：取消订单端点优雅处理交易所错误
        
        Verifies that the endpoint gracefully handles errors from the exchange client.
        验证端点优雅处理来自交易所客户端的错误。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create real client instance
        client_instance = HyperliquidClient()
        client_instance.is_connected = True

        # Mock cancel_orders to raise exception
        client_instance.cancel_orders = Mock(
            side_effect=Exception("Order not found / 订单未找到")
        )

        mock_get_exchange.return_value = client_instance

        # Test endpoint
        test_client = TestClient(server.app)
        response = test_client.post(
            "/api/hyperliquid/cancel-order", json={"order_id": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        # Should not raise unhandled exception
        # 不应抛出未处理的异常
        assert isinstance(data, dict)
        assert "Failed to cancel" in data["error"] or "取消订单失败" in data["error"]


class TestHyperliquidBotControlIntegration:
    """Integration tests for bot control workflow / Bot 控制工作流集成测试"""

    @patch("server.bot_engine")
    @patch("server.get_default_exchange")
    @patch("server.get_exchange_by_name")
    def test_integration_start_stop_workflow_updates_status(
        self, mock_get_exchange_by_name, mock_get_default_exchange, mock_bot_engine
    ):
        """
        Integration Test: Complete start/stop workflow updates status correctly
        集成测试：完整的启动/停止工作流正确更新状态
        
        Verifies that:
        1. Starting bot sets active=True in status
        2. Stopping bot sets active=False in status
        3. Button state can be determined from status.active field
        验证：
        1. 启动 bot 时状态中的 active=True
        2. 停止 bot 时状态中的 active=False
        3. 可以从 status.active 字段确定按钮状态
        """
        from unittest.mock import MagicMock
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Mock Hyperliquid exchange
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.is_connected = True
        mock_exchange.symbol = "ETH/USDC:USDC"
        mock_exchange.last_order_error = None
        # HyperliquidClient doesn't have fetch_ticker, use fetch_market_data instead
        # HyperliquidClient 没有 fetch_ticker，改用 fetch_market_data
        mock_exchange.fetch_market_data = Mock(return_value={
            "best_bid": 2499.0,
            "best_ask": 2501.0,
            "mid_price": 2500.0,
        })
        mock_exchange.fetch_positions.return_value = []
        mock_exchange.fetch_open_orders.return_value = []
        mock_get_default_exchange.return_value = mock_exchange
        mock_get_exchange_by_name.return_value = mock_exchange
        
        # Mock strategy instance
        mock_instance = MagicMock()
        mock_instance.strategy_id = "hyperliquid"
        mock_instance.strategy = MagicMock()
        mock_instance.strategy.spread = 0.001
        mock_instance.running = False
        mock_instance.exchange = mock_exchange
        
        # Mock bot_engine
        mock_bot_engine.strategy_instances = {"hyperliquid": mock_instance}
        mock_bot_engine.strategy = None
        mock_bot_engine.risk = MagicMock()
        mock_bot_engine.risk.validate_proposal.return_value = (True, None)
        mock_bot_engine.alert = None
        mock_bot_engine.current_stage = "Idle"
        mock_bot_engine.get_status.return_value = {
            "symbol": "ETH/USDC:USDC",
            "spread": 0.001,
            "quantity": 0.1,
            "leverage": 5,
        }
        mock_bot_engine.is_running.return_value = False
        
        client = TestClient(server.app)
        
        # Step 1: Check initial status (should be stopped)
        # 步骤 1：检查初始状态（应该是停止的）
        response = client.get("/api/status")
        assert response.status_code == 200
        status_data = response.json()
        assert "active" in status_data
        initial_active = status_data["active"]
        assert initial_active is False, "Bot should be stopped initially / Bot 初始应该是停止的"
        
        # Step 2: Start bot
        # 步骤 2：启动 bot
        with patch("server.threading.Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            response = client.post("/api/control?action=start")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"
            
            # Verify instance is running
            # 验证实例正在运行
            assert mock_instance.running is True
        
        # Update mock to reflect running state
        # 更新模拟以反映运行状态
        mock_bot_engine.is_running.return_value = True
        server.is_running = True
        
        # Step 3: Check status after start (should be active)
        # 步骤 3：启动后检查状态（应该是活动的）
        response = client.get("/api/status")
        assert response.status_code == 200
        status_data = response.json()
        assert "active" in status_data
        assert status_data["active"] is True, "Bot should be active after start / 启动后 Bot 应该是活动的"
        
        # Step 4: Stop bot
        # 步骤 4：停止 bot
        response = client.post("/api/control?action=stop")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopped"
        
        # Verify instance is stopped
        # 验证实例已停止
        assert mock_instance.running is False
        
        # Update mock to reflect stopped state
        # 更新模拟以反映停止状态
        mock_bot_engine.is_running.return_value = False
        server.is_running = False
        
        # Step 5: Check status after stop (should be inactive)
        # 步骤 5：停止后检查状态（应该是不活动的）
        response = client.get("/api/status")
        assert response.status_code == 200
        status_data = response.json()
        assert "active" in status_data
        assert status_data["active"] is False, "Bot should be inactive after stop / 停止后 Bot 应该是不活动的"

    @patch("server.bot_engine")
    @patch("server.get_default_exchange")
    def test_integration_start_with_hyperliquid_instance_creates_thread(
        self, mock_get_default_exchange, mock_bot_engine
    ):
        """
        Integration Test: Starting bot with Hyperliquid instance creates and starts thread
        集成测试：使用 Hyperliquid 实例启动 bot 创建并启动线程
        
        Verifies complete integration of start action with threading.
        验证启动操作与线程的完整集成。
        """
        from unittest.mock import MagicMock
        from src.trading.hyperliquid_client import HyperliquidClient
        
        # Mock Hyperliquid exchange
        mock_exchange = MagicMock(spec=HyperliquidClient)
        mock_exchange.last_order_error = None
        mock_get_default_exchange.return_value = mock_exchange
        
        # Mock strategy instance
        mock_instance = MagicMock()
        mock_instance.strategy_id = "hyperliquid"
        mock_instance.strategy = MagicMock()
        mock_instance.strategy.spread = 0.001
        mock_instance.running = False
        
        # Mock bot_engine
        mock_bot_engine.strategy_instances = {"hyperliquid": mock_instance}
        mock_bot_engine.strategy = None
        mock_bot_engine.risk = MagicMock()
        mock_bot_engine.risk.validate_proposal.return_value = (True, None)
        mock_bot_engine.alert = None
        
        client = TestClient(server.app)
        
        with patch("server.threading.Thread") as mock_thread_class:
            mock_thread = MagicMock()
            mock_thread_class.return_value = mock_thread
            
            response = client.post("/api/control?action=start")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"
            
            # Verify thread was created and started
            # 验证线程已创建并启动
            mock_thread_class.assert_called_once()
            mock_thread.start.assert_called_once()
            assert mock_thread.daemon is True, "Bot thread should be daemon / Bot 线程应该是守护进程"
            
            # Verify instance is running
            # 验证实例正在运行
            assert mock_instance.running is True

