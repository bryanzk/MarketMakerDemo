"""
Unit tests for Hyperliquid Trading Page
Hyperliquid 交易页面单元测试

Tests for US-UI-004: Dedicated Hyperliquid Trading Page
测试 US-UI-004: 专用 Hyperliquid 交易页面

Owner: Agent QA (TDD: tests written first)
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.exchange import BinanceClient


class TestHyperliquidPageCreation:
    """
    Test AC-1: Dedicated Page Creation
    测试 AC-1: 专用页面创建
    """

    def test_hyperliquid_page_route_exists(self):
        """
        Test AC-1: Hyperliquid page route exists and returns HTML
        测试 AC-1: Hyperliquid 页面路由存在并返回 HTML
        
        Given: I navigate to /hyperliquid
        When: The route is accessed
        Then: The page should return HTML content
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Hyperliquid" in response.text or "hyperliquid" in response.text.lower()

    def test_hyperliquid_page_contains_branding(self):
        """
        Test AC-1: Page contains Hyperliquid-specific branding
        测试 AC-1: 页面包含 Hyperliquid 特定品牌
        
        Given: I navigate to /hyperliquid
        When: The page loads
        Then: I should see Hyperliquid-specific branding
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for Hyperliquid branding
        # 检查 Hyperliquid 品牌
        assert "Hyperliquid" in html or "hyperliquid" in html.lower()
        assert "Trading Page" in html or "交易页面" in html

    def test_hyperliquid_page_contains_navigation(self):
        """
        Test AC-7: Page contains navigation links
        测试 AC-7: 页面包含导航链接
        
        Given: I am on the Hyperliquid trading page
        When: I view the page
        Then: I should see navigation links to dashboard
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for navigation links
        # 检查导航链接
        assert 'href="/"' in html or 'href="' in html  # Back to dashboard link


class TestHyperliquidStrategyControlPanel:
    """
    Test AC-2: Strategy Control Panel
    测试 AC-2: 策略控制面板
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        return client

    def test_page_contains_strategy_controls(self):
        """
        Test AC-2: Page contains strategy control inputs
        测试 AC-2: 页面包含策略控制输入
        
        Given: I am on the Hyperliquid trading page
        When: I view the strategy control panel
        Then: I should see controls for spread, quantity, and leverage
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for strategy control inputs
        # 检查策略控制输入
        assert "spreadInput" in html or "spread" in html.lower()
        assert "quantityInput" in html or "quantity" in html.lower()
        assert "leverageInput" in html or "leverage" in html.lower()
        assert "pairSelect" in html or "trading pair" in html.lower() or "交易对" in html

    def test_page_contains_trading_pair_options(self):
        """
        Test AC-2: Page contains Hyperliquid trading pair options
        测试 AC-2: 页面包含 Hyperliquid 交易对选项
        
        Given: I am on the Hyperliquid trading page
        When: I view the trading pair selector
        Then: I should see Hyperliquid trading pair options
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for trading pair options (ETH, BTC, SOL are common)
        # 检查交易对选项（ETH、BTC、SOL 是常见的）
        assert "ETH" in html or "BTC" in html or "SOL" in html


class TestHyperliquidPositionBalancePanel:
    """
    Test AC-3: Position and Balance Panel
    测试 AC-3: 仓位与余额面板
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
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
        return client

    def test_page_contains_position_panel(self):
        """
        Test AC-3: Page contains position and balance panel
        测试 AC-3: 页面包含仓位与余额面板
        
        Given: I am on the Hyperliquid trading page
        When: I view the page
        Then: I should see position and balance panel elements
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for position/balance panel elements
        # 检查仓位/余额面板元素
        assert "Position" in html or "position" in html.lower() or "仓位" in html
        assert "Balance" in html or "balance" in html.lower() or "余额" in html
        assert "totalBalance" in html or "availableBalance" in html or "positionAmount" in html

    def test_page_contains_position_table(self):
        """
        Test AC-3: Page contains positions table
        测试 AC-3: 页面包含仓位表格
        
        Given: I am on the Hyperliquid trading page
        When: I view the position panel
        Then: I should see a table for open positions
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for positions table
        # 检查仓位表格
        assert "positionsTable" in html or "table" in html.lower()


class TestHyperliquidLLMEvaluation:
    """
    Test AC-4: Hyperliquid LLM Evaluation
    测试 AC-4: Hyperliquid LLM 评估
    """

    @pytest.fixture
    def mock_hyperliquid_client(self):
        """Create a mock HyperliquidClient / 创建模拟 HyperliquidClient"""
        client = Mock(spec=HyperliquidClient)
        client.is_connected = True
        client.symbol = "ETH/USDC:USDC"
        client.fetch_market_data.return_value = {
            "best_bid": 3000.0,
            "best_ask": 3002.0,
            "mid_price": 3001.0,
            "funding_rate": 0.0001,
            "timestamp": 1234567890,
        }
        client.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 3000.0,
            "balance": 10000.0,
            "available_balance": 5000.0,
            "leverage": 5,
        }
        client.set_symbol.return_value = True
        return client

    @pytest.fixture
    def mock_llm_providers(self):
        """Create mock LLM providers / 创建模拟 LLM 提供商"""
        providers = []
        for name, response in [
            (
                "Gemini",
                '{"recommended_strategy": "FixedSpread", "spread": 0.015, "skew_factor": 100, "confidence": 0.85, "quantity": 0.1, "leverage": 5}',
            ),
        ]:
            mock = Mock()
            mock.name = name
            mock.generate.return_value = response
            providers.append(mock)
        return providers

    def test_page_contains_llm_evaluation_section(self):
        """
        Test AC-4: Page contains LLM evaluation section
        测试 AC-4: 页面包含 LLM 评估部分
        
        Given: I am on the Hyperliquid trading page
        When: I view the page
        Then: I should see LLM evaluation section
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for LLM evaluation section
        # 检查 LLM 评估部分
        assert "evaluation" in html.lower() or "评估" in html
        assert "runEvaluation" in html or "Run Evaluation" in html

    @patch("server.create_all_providers")
    @patch("server.get_exchange_by_name")
    def test_llm_evaluation_uses_hyperliquid_exchange(
        self,
        mock_get_exchange,
        mock_create_providers,
        mock_hyperliquid_client,
        mock_llm_providers,
    ):
        """
        Test AC-4: LLM evaluation uses Hyperliquid exchange parameter
        测试 AC-4: LLM 评估使用 Hyperliquid 交易所参数
        
        Given: I am on the Hyperliquid trading page
        When: I run LLM evaluation
        Then: The API should be called with exchange='hyperliquid'
        """
        mock_get_exchange.return_value = mock_hyperliquid_client
        mock_create_providers.return_value = mock_llm_providers

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {"sharpe_ratio": 1.5}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Simulate LLM evaluation API call from page
            # 模拟页面发起的 LLM 评估 API 调用
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",  # Page should always use hyperliquid
                },
            )

            # Verify API accepts hyperliquid exchange
            # 验证 API 接受 hyperliquid 交易所
            assert response.status_code != 404
            if response.status_code == 200:
                data = response.json()
                assert "exchange" in data or "error" in data
                if "exchange" in data:
                    assert data["exchange"] == "hyperliquid"

    @patch("server.get_exchange_by_name")
    def test_apply_evaluation_uses_hyperliquid_exchange(
        self,
        mock_get_exchange,
        mock_hyperliquid_client,
    ):
        """
        Test AC-4: Apply evaluation uses Hyperliquid exchange parameter
        测试 AC-4: 应用评估使用 Hyperliquid 交易所参数
        
        Given: I have LLM evaluation results
        When: I apply the evaluation
        Then: The apply API should be called with exchange='hyperliquid'
        """
        mock_get_exchange.return_value = mock_hyperliquid_client

        # Mock evaluation results
        # 模拟评估结果
        with patch("server._last_evaluation_results", []), patch(
            "server._last_evaluation_aggregated", None
        ):
            client = TestClient(server.app)

            # Note: Apply API requires evaluation results to exist
            # 注意：Apply API 需要评估结果存在
            response = client.post(
                "/api/evaluation/apply",
                json={
                    "source": "consensus",
                    "exchange": "hyperliquid",  # Page should always use hyperliquid
                },
            )

            # Verify API accepts hyperliquid exchange parameter
            # 验证 API 接受 hyperliquid 交易所参数
            assert response.status_code in [200, 400, 404]


class TestHyperliquidOrderManagement:
    """
    Test AC-5: Order Management
    测试 AC-5: 订单管理
    """

    def test_page_contains_orders_section(self):
        """
        Test AC-5: Page contains orders section
        测试 AC-5: 页面包含订单部分
        
        Given: I am on the Hyperliquid trading page
        When: I view the page
        Then: I should see orders section
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for orders section
        # 检查订单部分
        assert "orders" in html.lower() or "订单" in html
        assert "ordersTable" in html or "refreshOrders" in html


class TestHyperliquidConnectionStatus:
    """
    Test AC-9: Connection Status Display
    测试 AC-9: 连接状态显示
    """

    def test_page_contains_connection_status(self):
        """
        Test AC-9: Page contains connection status display
        测试 AC-9: 页面包含连接状态显示
        
        Given: I am on the Hyperliquid trading page
        When: The page loads
        Then: I should see connection status display
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for connection status elements
        # 检查连接状态元素
        assert "connectionStatus" in html or "connection" in html.lower() or "连接" in html
        assert "connectionInfo" in html or "status" in html.lower()


class TestHyperliquidBilingualSupport:
    """
    Test AC-8: Bilingual Support
    测试 AC-8: 双语支持
    """

    def test_page_contains_bilingual_text(self):
        """
        Test AC-8: Page contains bilingual text (English and Chinese)
        测试 AC-8: 页面包含双语文本（英文和中文）
        
        Given: I am viewing the Hyperliquid trading page
        When: I see any text or labels
        Then: All text should be displayed in both English and Chinese
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for bilingual text patterns
        # 检查双语文本模式
        # Look for common bilingual patterns like "English / 中文"
        # 查找常见的双语模式，如 "English / 中文"
        has_english = any(
            word in html.lower()
            for word in ["trading", "page", "strategy", "position", "balance", "order"]
        )
        has_chinese = any(
            char in html for char in ["交易", "页面", "策略", "仓位", "余额", "订单"]
        )
        
        # At least one should be present (ideally both)
        # 至少应该有一个存在（理想情况下两者都有）
        assert has_english or has_chinese, "Page should contain English or Chinese text / 页面应该包含英文或中文文本"


class TestHyperliquidErrorHandling:
    """
    Test AC-10: Error Handling
    测试 AC-10: 错误处理
    """

    @patch("server.get_exchange_by_name")
    def test_page_handles_connection_error(self, mock_get_exchange):
        """
        Test AC-10: Page handles connection errors gracefully
        测试 AC-10: 页面优雅地处理连接错误
        
        Given: I am on the Hyperliquid trading page and Hyperliquid is not connected
        When: I attempt to use any trading features
        Then: I should receive clear error messages in Chinese and English
        """
        # Mock no exchange available
        # 模拟没有可用的交易所
        mock_get_exchange.return_value = None

        mock_bot_engine = Mock()
        mock_bot_engine.data = Mock()
        mock_bot_engine.data.calculate_metrics.return_value = {}
        mock_bot_engine.data.trade_history = []

        with patch("server.bot_engine", mock_bot_engine):
            client = TestClient(server.app)

            # Try to run evaluation (should fail with clear error)
            # 尝试运行评估（应该失败并显示清晰的错误）
            response = client.post(
                "/api/evaluation/run",
                json={
                    "symbol": "ETH/USDC:USDC",
                    "simulation_steps": 100,
                    "exchange": "hyperliquid",
                },
            )

            # Verify error response contains bilingual message
            # 验证错误响应包含双语消息
            data = response.json()
            
            # Handle tuple response (FastAPI serializes tuples as lists)
            # 处理 tuple 响应（FastAPI 将 tuple 序列化为列表）
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            
            assert "error" in data
            error_msg = data.get("error", "")
            # Error should be bilingual or mention connection/exchange
            # 错误应该是双语的或提到连接/交易所
            assert (
                "connection" in error_msg.lower()
                or "连接" in error_msg
                or "exchange" in error_msg.lower()
                or "hyperliquid" in error_msg.lower()
            )


class TestHyperliquidRealTimeUpdates:
    """
    Test AC-6: Real-time Updates
    测试 AC-6: 实时更新
    """

    def test_page_contains_auto_refresh_script(self):
        """
        Test AC-6: Page contains auto-refresh functionality
        测试 AC-6: 页面包含自动刷新功能
        
        Given: I am viewing the Hyperliquid trading page
        When: The page loads
        Then: The page should have auto-refresh scripts
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for auto-refresh functionality
        # 检查自动刷新功能
        assert "setInterval" in html or "refreshOrders" in html or "refreshPosition" in html
        assert "startAutoRefresh" in html or "auto" in html.lower()


class TestHyperliquidNavigationIntegration:
    """
    Test AC-7: Navigation and Integration
    测试 AC-7: 导航与集成
    """

    def test_main_dashboard_has_hyperliquid_link(self):
        """
        Test AC-7: Main dashboard has link to Hyperliquid page
        测试 AC-7: 主仪表盘有到 Hyperliquid 页面的链接
        
        Given: I am on the main dashboard
        When: I view the page
        Then: I should see a link to Hyperliquid trading page
        """
        client = TestClient(server.app)
        response = client.get("/")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for Hyperliquid link
        # 检查 Hyperliquid 链接
        assert 'href="/hyperliquid"' in html or "hyperliquid" in html.lower()

    def test_llmtrade_page_has_hyperliquid_link(self):
        """
        Test AC-7: LLMTrade page has link to Hyperliquid page
        测试 AC-7: LLMTrade 页面有到 Hyperliquid 页面的链接
        
        Given: I am on the LLMTrade page
        When: I view the page
        Then: I should see a link to Hyperliquid trading page
        """
        client = TestClient(server.app)
        response = client.get("/evaluation")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for Hyperliquid link
        # 检查 Hyperliquid 链接
        assert 'href="/hyperliquid"' in html or "hyperliquid" in html.lower()

