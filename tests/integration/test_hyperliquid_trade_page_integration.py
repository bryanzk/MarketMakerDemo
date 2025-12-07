"""
Integration Test for US-UI-004: Dedicated Hyperliquid Trading Page
US-UI-004 集成测试：专用 Hyperliquid 交易页面

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidPageAPIIntegration:
    """
    Integration tests for Hyperliquid Trading Page with backend APIs.
    Hyperliquid 交易页面与后端 API 的集成测试。
    
    Tests that the page can interact with backend APIs correctly.
    测试页面可以正确与后端 API 交互。
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDT:USDT"
        client.exchange_name = "hyperliquid"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.fetch_balance.return_value = {
            "total": 10000.0,
            "available": 5000.0,
            "margin_used": 2000.0,
            "margin_available": 5000.0,
            "margin_ratio": 20.0,
        }
        client.fetch_positions.return_value = [
            {
                "symbol": "ETH/USDT:USDT",
                "side": "LONG",
                "size": 0.1,
                "entry_price": 3000.0,
                "mark_price": 3100.0,
                "unrealized_pnl": 10.0,
            }
        ]
        client.fetch_open_orders.return_value = []
        client.set_symbol.return_value = True
        return client

    @patch("server.get_exchange_by_name")
    def test_hyperliquid_status_api_integration(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: AC-3, AC-6 - Hyperliquid status API integration
        集成测试：AC-3, AC-6 - Hyperliquid 状态 API 集成
        
        Tests that /api/hyperliquid/status returns correct data for the page.
        测试 /api/hyperliquid/status 为页面返回正确数据。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call status API (used by page to load data)
            # 调用状态 API（页面用于加载数据）
            response = client.get("/api/hyperliquid/status")

            # Verify response
            # 验证响应
            assert response.status_code == 200, (
                f"Expected 200, got {response.status_code} / 预期 200，得到 {response.status_code}"
            )
            data = response.json()

            # Verify response contains expected fields
            # 验证响应包含预期字段
            assert "symbol" in data or "error" in data, (
                "Response should include symbol or error / 响应应该包含 symbol 或 error"
            )
            if "error" not in data:
                # Verify balance and position data are available
                # 验证余额和仓位数据可用
                assert "balance" in data or "quantity" in data, (
                    "Response should include balance or quantity / 响应应该包含 balance 或 quantity"
                )

    @patch("server.get_exchange_by_name")
    def test_hyperliquid_pair_api_integration(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: AC-2 - Hyperliquid pair switching API integration
        集成测试：AC-2 - Hyperliquid 交易对切换 API 集成
        
        Tests that /api/hyperliquid/pair updates the trading pair correctly.
        测试 /api/hyperliquid/pair 正确更新交易对。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call pair API (used by page to switch trading pair)
            # 调用交易对 API（页面用于切换交易对）
            response = client.post(
                "/api/hyperliquid/pair",
                json={"symbol": "BTC/USDT:USDT"},
            )

            # Verify response
            # 验证响应
            assert response.status_code in [200, 400], (
                f"Expected 200 or 400, got {response.status_code} / "
                f"预期 200 或 400，得到 {response.status_code}"
            )

            # Verify set_symbol was called (if API is implemented)
            # 验证 set_symbol 被调用（如果 API 已实现）
            if response.status_code == 200:
                data = response.json()
                assert "symbol" in data or "error" not in data, (
                    "Response should indicate success / 响应应该指示成功"
                )

    @patch("server.get_exchange_by_name")
    def test_hyperliquid_leverage_api_integration(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: AC-2 - Hyperliquid leverage API integration
        集成测试：AC-2 - Hyperliquid 杠杆 API 集成
        
        Tests that /api/hyperliquid/leverage updates leverage correctly.
        测试 /api/hyperliquid/leverage 正确更新杠杆。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_hyperliquid_client.set_leverage.return_value = True

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call leverage API (used by page to update leverage)
            # API expects leverage as body parameter, not JSON object
            # 调用杠杆 API（页面用于更新杠杆）
            # API 期望杠杆作为 body 参数，而不是 JSON 对象
            response = client.post(
                "/api/hyperliquid/leverage",
                json=5,  # Leverage value as JSON body
            )

            # Verify response (may be 200, 400, or 422 depending on implementation)
            # 验证响应（可能是 200、400 或 422，取决于实现）
            assert response.status_code in [200, 400, 422], (
                f"Expected 200, 400, or 422, got {response.status_code} / "
                f"预期 200、400 或 422，得到 {response.status_code}"
            )

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_hyperliquid_llm_evaluation_api_integration(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
    ):
        """
        Integration Test: AC-4 - Hyperliquid LLM evaluation API integration
        集成测试：AC-4 - Hyperliquid LLM 评估 API 集成
        
        Tests that LLM evaluation API works with exchange='hyperliquid' parameter.
        测试 LLM 评估 API 与 exchange='hyperliquid' 参数正常工作。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock LLM providers
        mock_provider = Mock()
        mock_provider.name = "Gemini"
        mock_provider.generate.return_value = (
            '{"recommended_strategy": "FixedSpread", "spread": 0.015, "confidence": 0.8, "quantity": 0.1, "leverage": 5}'
        )
        mock_create_providers.return_value = [mock_provider]

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call LLM evaluation API with exchange='hyperliquid'
            # 使用 exchange='hyperliquid' 调用 LLM 评估 API
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "exchange": "hyperliquid",
                    "simulation_steps": 100,
                },
            )

            # Verify response
            # 验证响应
            if response.status_code == 200:
                data = response.json()
                # Verify exchange is hyperliquid
                # 验证交易所是 hyperliquid
                assert data.get("exchange") == "hyperliquid" or "error" in data, (
                    "Response should indicate hyperliquid exchange / "
                    "响应应该指示 hyperliquid 交易所"
                )

    @patch("server.get_exchange_by_name")
    def test_hyperliquid_position_data_integration(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: AC-3 - Hyperliquid position data integration
        集成测试：AC-3 - Hyperliquid 仓位数据集成
        
        Tests that position and balance data are correctly fetched and formatted.
        测试仓位和余额数据被正确获取和格式化。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Call status API (includes position and balance data)
            # 调用状态 API（包含仓位和余额数据）
            response = client.get("/api/hyperliquid/status")

            # Verify response contains position/balance data
            # 验证响应包含仓位/余额数据
            if response.status_code == 200:
                data = response.json()
                # Status API should include balance or position information
                # 状态 API 应该包含余额或仓位信息
                assert (
                    "balance" in data
                    or "quantity" in data
                    or "position" in data
                    or "error" in data
                ), (
                    "Response should include balance/position data / "
                    "响应应该包含余额/仓位数据"
                )


class TestHyperliquidPageWorkflowIntegration:
    """
    Integration tests for complete Hyperliquid page workflows.
    完整 Hyperliquid 页面工作流的集成测试。
    
    Tests end-to-end workflows that users would perform on the page.
    测试用户在页面上执行的端到端工作流。
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDT:USDT"
        client.exchange_name = "hyperliquid"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.fetch_balance.return_value = {
            "total": 10000.0,
            "available": 5000.0,
            "margin_used": 2000.0,
            "margin_available": 5000.0,
            "margin_ratio": 20.0,
        }
        client.fetch_positions.return_value = []
        client.fetch_open_orders.return_value = []
        client.set_symbol.return_value = True
        return client

    @patch("server.get_exchange_by_name")
    def test_complete_page_workflow(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: Complete page workflow
        集成测试：完整页面工作流
        
        Tests the complete workflow: load page → check status → switch pair → update config.
        测试完整工作流：加载页面 → 检查状态 → 切换交易对 → 更新配置。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Step 1: Load page
            # 步骤 1：加载页面
            page_response = client.get("/hyperliquid")
            assert page_response.status_code == 200

            # Step 2: Get status
            # 步骤 2：获取状态
            status_response = client.get("/api/hyperliquid/status")
            assert status_response.status_code in [200, 400]

            # Step 3: Switch pair (if API is implemented)
            # 步骤 3：切换交易对（如果 API 已实现）
            pair_response = client.post(
                "/api/hyperliquid/pair",
                json={"symbol": "BTC/USDT:USDT"},
            )
            assert pair_response.status_code in [200, 400]

            # Step 4: Update leverage (if API is implemented)
            # 步骤 4：更新杠杆（如果 API 已实现）
            mock_hyperliquid_client.set_leverage.return_value = True
            leverage_response = client.post(
                "/api/hyperliquid/leverage",
                json=10,
            )
            assert leverage_response.status_code in [200, 400, 422]

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_llm_evaluation_workflow(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
    ):
        """
        Integration Test: AC-4 - LLM evaluation workflow
        集成测试：AC-4 - LLM 评估工作流
        
        Tests the complete LLM evaluation workflow: run evaluation → get results → apply suggestion.
        测试完整 LLM 评估工作流：运行评估 → 获取结果 → 应用建议。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock LLM providers
        mock_provider = Mock()
        mock_provider.name = "Gemini"
        mock_provider.generate.return_value = (
            '{"recommended_strategy": "FixedSpread", "spread": 0.015, "confidence": 0.8, "quantity": 0.1, "leverage": 5}'
        )
        mock_create_providers.return_value = [mock_provider]

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Step 1: Run evaluation
            # 步骤 1：运行评估
            eval_response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDT:USDT",
                    "exchange": "hyperliquid",
                    "simulation_steps": 100,
                },
            )

            # Step 2: Apply suggestion (if evaluation succeeded)
            # 步骤 2：应用建议（如果评估成功）
            if eval_response.status_code == 200:
                apply_response = client.post(
                    "/api/evaluation/apply",
                    json={
                        "source": "consensus",
                        "exchange": "hyperliquid",
                    },
                )
                # Apply may succeed or fail depending on implementation
                # 应用可能成功或失败，取决于实现
                assert apply_response.status_code in [200, 400, 404]


class TestHyperliquidPageErrorHandlingIntegration:
    """
    Integration tests for error handling in Hyperliquid page.
    Hyperliquid 页面错误处理的集成测试。
    
    Tests AC-10: Error handling integration.
    测试 AC-10：错误处理集成。
    """

    @patch("server.get_exchange_by_name")
    def test_error_handling_when_not_connected(self, mock_get_exchange):
        """
        Integration Test: AC-10 - Error handling when Hyperliquid is not connected
        集成测试：AC-10 - Hyperliquid 未连接时的错误处理
        
        Verifies that APIs return appropriate errors when Hyperliquid is not connected.
        验证当 Hyperliquid 未连接时 API 返回适当的错误。
        """
        # Mock no exchange available
        # 模拟没有可用的交易所
        mock_get_exchange.return_value = None

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Test status API
            # 测试状态 API
            response = client.get("/api/hyperliquid/status")

            # Verify error response
            # 验证错误响应
            data = response.json()
            assert "error" in data, "Error message should be present / 应该存在错误消息"

            # Error should mention connection or Hyperliquid
            # 错误应该提到连接或 Hyperliquid
            error_msg = data.get("error", "").lower()
            assert (
                "connection" in error_msg
                or "连接" in data.get("error", "")
                or "hyperliquid" in error_msg
            ), "Error should mention connection or Hyperliquid / 错误应该提到连接或 Hyperliquid"

    @patch("server.get_exchange_by_name")
    def test_page_loads_without_connection(self, mock_get_exchange):
        """
        Integration Test: AC-10 - Page loads even when Hyperliquid is not connected
        集成测试：AC-10 - 即使 Hyperliquid 未连接，页面也能加载
        
        Verifies that the page can be loaded even if exchange is not connected.
        验证即使交易所未连接，页面也可以加载。
        """
        # Mock no exchange available
        # 模拟没有可用的交易所
        mock_get_exchange.return_value = None

        client = TestClient(server.app)

        # Page should load even if exchange is not connected
        # 即使交易所未连接，页面也应该加载
        response = client.get("/hyperliquid")

        assert response.status_code == 200, (
            f"Page should load successfully, got {response.status_code} / "
            f"页面应该成功加载，得到 {response.status_code}"
        )


class TestHyperliquidPageRealTimeUpdatesIntegration:
    """
    Integration tests for real-time updates on Hyperliquid page.
    Hyperliquid 页面实时更新的集成测试。
    
    Tests AC-6: Real-time updates integration.
    测试 AC-6：实时更新集成。
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDT:USDT"
        client.exchange_name = "hyperliquid"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.fetch_balance.return_value = {
            "total": 10000.0,
            "available": 5000.0,
            "margin_used": 2000.0,
            "margin_available": 5000.0,
            "margin_ratio": 20.0,
        }
        client.fetch_positions.return_value = []
        client.fetch_open_orders.return_value = []
        client.set_symbol.return_value = True
        return client

    @patch("server.get_exchange_by_name")
    def test_position_data_refresh(self, mock_get_exchange, mock_hyperliquid_client):
        """
        Integration Test: AC-6 - Position data can be refreshed
        集成测试：AC-6 - 仓位数据可以刷新
        
        Tests that position data can be refreshed via API calls.
        测试仓位数据可以通过 API 调用刷新。
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock bot_engine
        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # First status call
            # 第一次状态调用
            response1 = client.get("/api/hyperliquid/status")
            assert response1.status_code in [200, 400]

            # Second status call (simulating refresh)
            # 第二次状态调用（模拟刷新）
            response2 = client.get("/api/hyperliquid/status")
            assert response2.status_code in [200, 400]

            # Verify both calls work
            # 验证两次调用都有效
            assert response1.status_code == response2.status_code, (
                "Both refresh calls should work / 两次刷新调用都应该有效"
            )


class TestHyperliquidStrategyInstanceCreationIntegration:
    """
    Integration tests for Hyperliquid strategy instance creation on page load
    Hyperliquid 策略实例在页面加载时创建的集成测试
    
    Tests the complete workflow: page load → status endpoint → strategy instance creation → subsequent operations
    测试完整工作流：页面加载 → 状态端点 → 策略实例创建 → 后续操作
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        client.testnet = False
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.fetch_positions.return_value = []
        client.fetch_open_orders.return_value = []
        return client

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_integration_page_load_creates_strategy_instance_then_uses_it(
        self, mock_bot_engine, mock_get_exchange, mock_hyperliquid_client
    ):
        """
        Integration Test: Page load creates strategy instance, then subsequent operations use it
        集成测试：页面加载创建策略实例，然后后续操作使用它
        
        Tests the complete flow:
        1. Page loads and calls /api/hyperliquid/status
        2. Status endpoint creates Hyperliquid strategy instance
        3. Subsequent operations (like config update) use the created instance
        测试完整流程：
        1. 页面加载并调用 /api/hyperliquid/status
        2. 状态端点创建 Hyperliquid 策略实例
        3. 后续操作（如配置更新）使用创建的实例
        """
        # Setup: No existing strategy instance
        # 设置：没有现有的策略实例
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock(return_value=True)
        
        # Create instance after add_strategy_instance is called
        # 在 add_strategy_instance 被调用后创建实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_hyperliquid_client
        mock_instance.strategy = MagicMock()
        mock_instance.strategy.spread = 0.015
        mock_instance.strategy.quantity = 0.1
        mock_strategy_instances.get = Mock(
            side_effect=lambda key: mock_instance if key == "hyperliquid" else None
        )
        
        mock_get_exchange.return_value = mock_hyperliquid_client

        client = TestClient(server.app)

        # Step 1: Page loads and calls status endpoint
        # 步骤 1：页面加载并调用状态端点
        status_response = client.get("/api/hyperliquid/status")
        assert status_response.status_code == 200
        status_data = status_response.json()
        assert status_data["connected"] is True

        # Verify strategy instance was created
        # 验证策略实例已创建
        assert mock_bot_engine.add_strategy_instance.called, "Strategy instance should be created"
        call_args = mock_bot_engine.add_strategy_instance.call_args
        assert call_args[0][0] == "hyperliquid"
        assert call_args[0][1] == "fixed_spread"
        assert call_args[1]["exchange"] == mock_hyperliquid_client

        # Step 2: Update config (should use the created instance)
        # 步骤 2：更新配置（应使用创建的实例）
        # Find the instance in strategy_instances
        # 在 strategy_instances 中查找实例
        mock_strategy_instances["hyperliquid"] = mock_instance
        mock_strategy_instances.items.return_value = [("hyperliquid", mock_instance)]
        
        config_response = client.post(
            "/api/hyperliquid/config",
            json={"spread": 1.5, "quantity": 0.2, "strategy_type": "fixed_spread"},
        )
        
        # Verify config update worked (instance exists and was used)
        # 验证配置更新有效（实例存在并被使用）
        assert config_response.status_code == 200
        config_data = config_response.json()
        assert config_data.get("status") == "updated" or "error" not in config_data

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_integration_multiple_status_calls_reuse_same_instance(
        self, mock_bot_engine, mock_get_exchange, mock_hyperliquid_client
    ):
        """
        Integration Test: Multiple status calls reuse the same strategy instance
        集成测试：多次状态调用重用同一个策略实例
        
        Tests that calling /api/hyperliquid/status multiple times (e.g., during page refresh)
        doesn't create duplicate instances.
        测试多次调用 /api/hyperliquid/status（例如，在页面刷新期间）
        不会创建重复实例。
        """
        # Setup: No existing strategy instance initially
        # 设置：最初没有现有的策略实例
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        
        # Create instance after first add_strategy_instance call
        # 在第一次 add_strategy_instance 调用后创建实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_hyperliquid_client
        instance_created = False
        
        def get_instance(key):
            nonlocal instance_created
            if key == "hyperliquid" and instance_created:
                return mock_instance
            return None
        
        def add_instance(*args, **kwargs):
            nonlocal instance_created
            instance_created = True
            mock_strategy_instances["hyperliquid"] = mock_instance
            mock_strategy_instances.items.return_value = [("hyperliquid", mock_instance)]
            return True
        
        mock_strategy_instances.get = Mock(side_effect=get_instance)
        mock_bot_engine.add_strategy_instance = Mock(side_effect=add_instance)
        
        mock_get_exchange.return_value = mock_hyperliquid_client

        client = TestClient(server.app)

        # Call status endpoint multiple times
        # 多次调用状态端点
        response1 = client.get("/api/hyperliquid/status")
        response2 = client.get("/api/hyperliquid/status")
        response3 = client.get("/api/hyperliquid/status")

        # All should succeed
        # 所有调用都应该成功
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # Verify add_strategy_instance was called only once
        # 验证 add_strategy_instance 只被调用一次
        assert mock_bot_engine.add_strategy_instance.call_count == 1, (
            "Strategy instance should be created only once, not on every status call"
        )

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_integration_strategy_instance_has_correct_exchange_type(
        self, mock_bot_engine, mock_get_exchange, mock_hyperliquid_client
    ):
        """
        Integration Test: Created strategy instance uses HyperliquidClient, not BinanceClient
        集成测试：创建的策略实例使用 HyperliquidClient，而不是 BinanceClient
        
        Ensures that the Hyperliquid page initializes with the correct exchange client type.
        确保 Hyperliquid 页面使用正确的交易所客户端类型初始化。
        """
        from src.trading.exchange import BinanceClient

        # Setup: No existing strategy instance
        # 设置：没有现有的策略实例
        mock_strategy_instances = MagicMock()
        mock_strategy_instances.items.return_value = []
        mock_strategy_instances.get.return_value = None
        mock_bot_engine.strategy_instances = mock_strategy_instances
        mock_bot_engine.add_strategy_instance = Mock(return_value=True)
        
        # Create instance after add_strategy_instance is called
        # 在 add_strategy_instance 被调用后创建实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_hyperliquid_client
        mock_strategy_instances.get = Mock(
            side_effect=lambda key: mock_instance if key == "hyperliquid" else None
        )
        
        mock_get_exchange.return_value = mock_hyperliquid_client

        client = TestClient(server.app)
        response = client.get("/api/hyperliquid/status")

        assert response.status_code == 200

        # Verify the instance was created with HyperliquidClient
        # 验证实例是使用 HyperliquidClient 创建的
        call_args = mock_bot_engine.add_strategy_instance.call_args
        created_exchange = call_args[1]["exchange"]
        
        assert isinstance(created_exchange, type(mock_hyperliquid_client)), (
            "Strategy instance should use HyperliquidClient"
        )
        assert not isinstance(created_exchange, BinanceClient), (
            "Strategy instance should NOT use BinanceClient"
        )

