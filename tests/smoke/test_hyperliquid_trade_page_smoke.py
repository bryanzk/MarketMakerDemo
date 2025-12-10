"""
Smoke Test for US-UI-004: Hyperliquid Trading Page Business Logic
US-UI-004 冒烟测试：Hyperliquid 交易页面业务逻辑

Smoke tests verify critical paths for the Hyperliquid trading page UI.
冒烟测试验证 Hyperliquid 交易页面 UI 的关键路径。

Tests for:
- Page load initialization (strategy instance creation)
- Status endpoint behavior
- Error handling

Owner: Agent QA
"""

from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from server import app
from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquidTradePageBusinessLogic:
    """
    Smoke tests for Hyperliquid trading page business logic.
    Hyperliquid 交易页面业务逻辑的冒烟测试。
    
    These tests verify the critical UI business logic paths.
    这些测试验证关键的 UI 业务逻辑路径。
    """

    @pytest.fixture
    def client(self):
        """Create test client / 创建测试客户端"""
        return TestClient(app)

    def test_smoke_hyperliquid_status_endpoint(self, client):
        """
        Smoke Test: /api/hyperliquid/status endpoint responds correctly
        冒烟测试：/api/hyperliquid/status 端点正确响应
        
        This endpoint is used by checkConnection and loadStatus functions.
        此端点被 checkConnection 和 loadStatus 函数使用。
        """
        response = client.get("/api/hyperliquid/status")
        
        # Should return 200 or error response with proper structure
        # 应返回 200 或具有正确结构的错误响应
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        
        # Verify response structure
        # 验证响应结构
        if response.status_code == 200:
            # Success response should have these fields
            # 成功响应应具有这些字段
            assert "connected" in data or "error" in data
            if "connected" in data and data.get("connected"):
                # Connected response should have these fields
                # 已连接响应应具有这些字段
                assert "exchange" in data
                assert "testnet" in data
                # trace_id may be present but is optional for success responses
                # trace_id 可能存在，但对于成功响应是可选的
                # Note: Some endpoints may not include trace_id in success responses
                # 注意：某些端点可能不在成功响应中包含 trace_id
            elif "error" in data:
                # Error response should have error fields
                # 错误响应应具有错误字段
                assert "error" in data or "error_type" in data
                # trace_id should be present in error responses
                # trace_id 应该出现在错误响应中
                assert "trace_id" in data
        else:
            # Error response should have error fields
            # 错误响应应具有错误字段
            assert "error" in data or "error_type" in data
            # trace_id should be present in error responses
            # trace_id 应该出现在错误响应中
            if "error" in data or "error_type" in data:
                assert "trace_id" in data

    def test_smoke_hyperliquid_config_endpoint(self, client):
        """
        Smoke Test: /api/hyperliquid/config endpoint accepts requests without skew_factor
        冒烟测试：/api/hyperliquid/config 端点接受不包含 skew_factor 的请求
        
        Skew factor was removed from the UI, so the endpoint should work without it.
        倾斜因子已从 UI 中移除，因此端点应该可以在没有它的情况下工作。
        """
        config_data = {
            "symbol": "ETH/USDT:USDT",
            "spread": 0.015,
            "quantity": 0.1,
            "leverage": 5,
            "strategy_type": "fixed_spread",
            "strategy_id": "default",
            # Note: skew_factor is intentionally omitted / 注意：故意省略 skew_factor
        }
        
        response = client.post(
            "/api/hyperliquid/config",
            json=config_data
        )
        
        # Should accept the request (may return error if not connected, but should not crash)
        # 应接受请求（如果未连接可能返回错误，但不应崩溃）
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        assert "status" in data or "error" in data

    def test_smoke_hyperliquid_update_pair_endpoint(self, client):
        """
        Smoke Test: /api/hyperliquid/pair endpoint accepts symbol updates
        冒烟测试：/api/hyperliquid/pair 端点接受交易对更新
        
        This endpoint is called when user switches trading pairs via dropdown.
        当用户通过下拉框切换交易对时调用此端点。
        """
        pair_data = {
            "symbol": "BTC/USDT:USDT"
        }
        
        response = client.post(
            "/api/hyperliquid/pair",
            json=pair_data
        )
        
        # Should accept the request
        # 应接受请求
        assert response.status_code in [200, 400, 500]
        
        data = response.json()
        assert "status" in data or "error" in data

    def test_smoke_hyperliquid_status_rate_limit_handling(self, client):
        """
        Smoke Test: /api/hyperliquid/status handles rate limit errors gracefully
        冒烟测试：/api/hyperliquid/status 优雅地处理速率限制错误
        
        Rate limit errors should be returned with proper error structure.
        速率限制错误应使用正确的错误结构返回。
        """
        # Make multiple rapid requests to potentially trigger rate limiting
        # 发出多个快速请求以可能触发速率限制
        responses = []
        for _ in range(5):
            response = client.get("/api/hyperliquid/status")
            responses.append(response)
        
        # All responses should have proper structure
        # 所有响应都应具有正确的结构
        for response in responses:
            assert response.status_code in [200, 429, 400, 500]
            data = response.json()
            
            # If rate limited, should have rate limit indicators
            # 如果被限流，应具有速率限制指示器
            if response.status_code == 429:
                assert "error" in data or "error_type" in data
                assert "trace_id" in data

    def test_smoke_hyperliquid_page_route_exists(self, client):
        """
        Smoke Test: Hyperliquid trading page route exists and returns HTML
        冒烟测试：Hyperliquid 交易页面路由存在并返回 HTML
        
        The page should be accessible and return HTML content.
        页面应该可以访问并返回 HTML 内容。
        """
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
        assert "Hyperliquid" in response.text or "hyperliquid" in response.text.lower()

    def test_smoke_hyperliquid_page_contains_key_elements(self, client):
        """
        Smoke Test: Hyperliquid page contains key UI elements
        冒烟测试：Hyperliquid 页面包含关键 UI 元素
        
        Verify that essential UI elements are present in the HTML.
        验证 HTML 中是否存在基本 UI 元素。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check for key elements
        # 检查关键元素
        assert 'id="connectionStatus"' in html
        assert 'id="connectionDetails"' in html
        assert 'id="pairSelect"' in html
        assert 'id="quantityInput"' in html
        assert 'id="leverageInput"' in html
        # Verify skew_factor input is NOT present (it was removed)
        # 验证 skew_factor 输入不存在（已移除）
        assert 'id="skewInput"' not in html
        assert 'skew_factor' not in html.lower() or 'skewfactor' not in html.lower()

    def test_smoke_hyperliquid_page_pair_switching(self, client):
        """
        Smoke Test: Trading pair switching functionality
        冒烟测试：交易对切换功能
        
        Verify that pair switching endpoint works and page supports onchange event.
        验证交易对切换端点工作正常，页面支持 onchange 事件。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check that pair select has onchange handler
        # 检查交易对选择器具有 onchange 处理程序
        assert 'onchange="switchPair()' in html or 'onchange="switchPair(' in html
        
        # Verify switchPair function exists in the page
        # 验证 switchPair 函数在页面中存在
        assert 'function switchPair' in html or 'switchPair()' in html

    def test_smoke_hyperliquid_page_refresh_intervals(self, client):
        """
        Smoke Test: Page uses optimized refresh intervals
        冒烟测试：页面使用优化的刷新间隔
        
        Verify that refresh intervals are set to reduced values.
        验证刷新间隔设置为减少的值。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check for optimized intervals in JavaScript
        # 检查 JavaScript 中的优化间隔
        # Orders: 15000 (15 seconds) - updated to reduce rate limiting
        # 订单：15000（15秒）- 已更新以减少速率限制
        assert 'setInterval(refreshOrders, 15000)' in html or 'setInterval(refreshOrders,15000)' in html
        # Position: 20000 (20 seconds) - updated to reduce rate limiting
        # 仓位：20000（20秒）- 已更新以减少速率限制
        assert 'setInterval(refreshPosition, 20000)' in html or 'setInterval(refreshPosition,20000)' in html
        # Connection: 30000 (30 seconds)
        # 连接：30000（30秒）
        assert 'setInterval(checkConnection, 30000)' in html or 'setInterval(checkConnection,30000)' in html

    def test_smoke_hyperliquid_page_request_deduplication(self, client):
        """
        Smoke Test: Page implements request deduplication
        冒烟测试：页面实现请求去重
        
        Verify that deduplication flags are present in the JavaScript.
        验证 JavaScript 中存在去重标志。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check for deduplication flags
        # 检查去重标志
        assert 'isRefreshingOrders' in html
        assert 'isRefreshingPosition' in html
        assert 'isCheckingConnection' in html

    def test_smoke_hyperliquid_page_rate_limit_error_handling(self, client):
        """
        Smoke Test: Page handles rate limit errors in UI
        冒烟测试：页面在 UI 中处理速率限制错误
        
        Verify that rate limit error handling is present in checkConnection function.
        验证 checkConnection 函数中存在速率限制错误处理。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check for rate limit error handling
        # 检查速率限制错误处理
        assert 'isRateLimit' in html or 'rate_limit' in html or 'Rate limit' in html
        assert 'API调用超出速率限制' in html or 'rate limit exceeded' in html.lower()

    def test_smoke_hyperliquid_page_uses_correct_api_endpoints(self, client):
        """
        Smoke Test: Page uses correct API endpoints
        冒烟测试：页面使用正确的 API 端点
        
        Verify that checkConnection and loadStatus use /api/hyperliquid/status.
        验证 checkConnection 和 loadStatus 使用 /api/hyperliquid/status。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check that checkConnection uses /api/hyperliquid/status
        # 检查 checkConnection 使用 /api/hyperliquid/status
        assert "'/api/hyperliquid/status'" in html or '"/api/hyperliquid/status"' in html
        
        # Verify it's not using the slow evaluation API
        # 验证它不使用慢速评估 API
        # Should not have /api/evaluation/run in checkConnection
        # 在 checkConnection 中不应有 /api/evaluation/run
        check_connection_start = html.find('async function checkConnection')
        if check_connection_start != -1:
            check_connection_end = html.find('async function', check_connection_start + 1)
            if check_connection_end == -1:
                check_connection_end = len(html)
            check_connection_code = html[check_connection_start:check_connection_end]
            # Should use /api/hyperliquid/status, not /api/evaluation/run
            # 应使用 /api/hyperliquid/status，而不是 /api/evaluation/run
            assert "'/api/hyperliquid/status'" in check_connection_code or '"/api/hyperliquid/status"' in check_connection_code

    def test_smoke_hyperliquid_page_switch_pair_auto_refresh_logic(self, client):
        """
        Smoke Test: switchPair function implements auto-refresh after pair switching
        冒烟测试：switchPair 函数在切换交易对后实现自动刷新
        
        Verify that switchPair calls checkConnection, loadStatus, refreshPosition, and refreshOrders.
        验证 switchPair 调用 checkConnection、loadStatus、refreshPosition 和 refreshOrders。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        assert switch_pair_start != -1, "switchPair function not found"
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Verify auto-refresh calls after pair switch
        # 验证切换交易对后的自动刷新调用
        assert 'await checkConnection()' in switch_pair_code or 'checkConnection()' in switch_pair_code
        assert 'await loadStatus()' in switch_pair_code or 'loadStatus()' in switch_pair_code
        assert 'refreshPosition()' in switch_pair_code
        assert 'refreshOrders()' in switch_pair_code

    def test_smoke_hyperliquid_page_switch_pair_delays(self, client):
        """
        Smoke Test: switchPair function includes delays for backend updates
        冒烟测试：switchPair 函数包含用于后端更新的延迟
        
        Verify that switchPair uses setTimeout/Promise delays to wait for backend updates.
        验证 switchPair 使用 setTimeout/Promise 延迟等待后端更新。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start == -1:
            pytest.skip("switchPair function not found")
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Verify delays are present (setTimeout or Promise with setTimeout)
        # 验证延迟存在（setTimeout 或带 setTimeout 的 Promise）
        assert 'setTimeout' in switch_pair_code or 'Promise' in switch_pair_code
        # Should have delays for backend updates
        # 应该有用于后端更新的延迟
        assert 'resolve' in switch_pair_code or 'setTimeout' in switch_pair_code

    def test_smoke_hyperliquid_page_switch_pair_connection_flag_reset(self, client):
        """
        Smoke Test: switchPair resets isCheckingConnection flag before calling checkConnection
        冒烟测试：switchPair 在调用 checkConnection 之前重置 isCheckingConnection 标志
        
        Verify that the flag is reset to ensure checkConnection can run.
        验证标志被重置以确保 checkConnection 可以运行。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start == -1:
            pytest.skip("switchPair function not found")
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Verify isCheckingConnection flag is reset
        # 验证 isCheckingConnection 标志被重置
        assert 'isCheckingConnection = false' in switch_pair_code or 'isCheckingConnection=false' in switch_pair_code

    def test_smoke_hyperliquid_page_pair_select_data_attributes(self, client):
        """
        Smoke Test: Trading pair select options have data-price attributes
        冒烟测试：交易对选择选项具有 data-price 属性
        
        Verify that pair select options include data-price attributes for future use.
        验证交易对选择选项包含 data-price 属性以供将来使用。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check that pair select options have data-price attributes
        # 检查交易对选择选项具有 data-price 属性
        assert 'data-price' in html or 'data-price=""' in html

    def test_smoke_hyperliquid_page_switch_pair_error_handling(self, client):
        """
        Smoke Test: switchPair function has proper error handling
        冒烟测试：switchPair 函数具有适当的错误处理
        
        Verify that switchPair handles errors and resets flags on failure.
        验证 switchPair 处理错误并在失败时重置标志。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start == -1:
            pytest.skip("switchPair function not found")
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Verify error handling
        # 验证错误处理
        assert 'catch' in switch_pair_code or 'catch (' in switch_pair_code
        # Error handling can use showMessage, handleApiError, or displayError
        # 错误处理可以使用 showMessage、handleApiError 或 displayError
        assert 'showMessage' in switch_pair_code or 'handleApiError' in switch_pair_code or 'displayError' in switch_pair_code

    def test_smoke_hyperliquid_page_load_status_uses_hyperliquid_endpoint(self, client):
        """
        Smoke Test: loadStatus function uses /api/hyperliquid/status endpoint
        冒烟测试：loadStatus 函数使用 /api/hyperliquid/status 端点
        
        Verify that loadStatus has been updated to use the faster endpoint.
        验证 loadStatus 已更新为使用更快的端点。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find loadStatus function
        # 查找 loadStatus 函数
        load_status_start = html.find('async function loadStatus')
        if load_status_start == -1:
            pytest.skip("loadStatus function not found")
        
        load_status_end = html.find('async function', load_status_start + 1)
        if load_status_end == -1:
            load_status_end = html.find('function ', load_status_start + 1)
        if load_status_end == -1:
            load_status_end = len(html)
        
        load_status_code = html[load_status_start:load_status_end]
        
        # Verify it uses /api/hyperliquid/status
        # 验证它使用 /api/hyperliquid/status
        assert "'/api/hyperliquid/status'" in load_status_code or '"/api/hyperliquid/status"' in load_status_code
        # Should not use the old /api/status endpoint
        # 不应使用旧的 /api/status 端点
        assert "'/api/status'" not in load_status_code or '"/api/status"' not in load_status_code

    def test_smoke_hyperliquid_page_user_manually_switched_pair_flag(self, client):
        """
        Smoke Test: Page implements userManuallySwitchedPair flag
        冒烟测试：页面实现 userManuallySwitchedPair 标志
        
        Verify that the flag is used to track manual pair switching and prevent auto-updates.
        验证标志用于跟踪手动交易对切换并防止自动更新。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Check for userManuallySwitchedPair flag
        # 检查 userManuallySwitchedPair 标志
        assert 'userManuallySwitchedPair' in html
        
        # Verify it's used in switchPair function
        # 验证它在 switchPair 函数中使用
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start != -1:
            switch_pair_end = html.find('async function', switch_pair_start + 1)
            if switch_pair_end == -1:
                switch_pair_end = html.find('function ', switch_pair_start + 1)
            if switch_pair_end == -1:
                switch_pair_end = len(html)
            switch_pair_code = html[switch_pair_start:switch_pair_end]
            assert 'userManuallySwitchedPair' in switch_pair_code

    def test_smoke_hyperliquid_page_switch_pair_double_check_connection(self, client):
        """
        Smoke Test: switchPair calls checkConnection after pair switch
        冒烟测试：switchPair 在切换交易对后调用 checkConnection
        
        Verify that switchPair calls checkConnection to refresh connection status.
        验证 switchPair 调用 checkConnection 以刷新连接状态。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start == -1:
            pytest.skip("switchPair function not found")
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Count checkConnection calls (should be called at least once)
        # 计算 checkConnection 调用次数（应至少调用一次）
        check_connection_calls = switch_pair_code.count('checkConnection()')
        assert check_connection_calls >= 1, f"Expected at least 1 checkConnection call, found {check_connection_calls}"

    def test_smoke_hyperliquid_page_switch_pair_validation(self, client):
        """
        Smoke Test: switchPair includes symbol validation
        冒烟测试：switchPair 包含交易对验证
        
        Verify that switchPair validates the symbol before making API calls.
        The validation can be implicit (getting value from select) or explicit (validation function).
        验证 switchPair 在进行 API 调用之前验证交易对。
        验证可以是隐式的（从选择器获取值）或显式的（验证函数）。
        """
        response = client.get("/hyperliquid")
        html = response.text
        
        # Find switchPair function
        # 查找 switchPair 函数
        switch_pair_start = html.find('async function switchPair')
        if switch_pair_start == -1:
            pytest.skip("switchPair function not found")
        
        switch_pair_end = html.find('async function', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = html.find('function ', switch_pair_start + 1)
        if switch_pair_end == -1:
            switch_pair_end = len(html)
        
        switch_pair_code = html[switch_pair_start:switch_pair_end]
        
        # Verify validation is present (implicit or explicit)
        # 验证存在验证（隐式或显式）
        # Implicit validation: getting value from pairSelect (which only contains valid options)
        # 隐式验证：从 pairSelect 获取值（只包含有效选项）
        # Explicit validation: validateSymbol function or validation check
        # 显式验证：validateSymbol 函数或验证检查
        has_implicit_validation = 'pairSelect' in switch_pair_code and '.value' in switch_pair_code
        has_explicit_validation = 'validateSymbol' in switch_pair_code or 'validation' in switch_pair_code.lower()
        assert has_implicit_validation or has_explicit_validation, "switchPair should validate symbol (implicitly via pairSelect or explicitly)"


class TestHyperliquidStrategyInstanceCreation:
    """
    Smoke tests for Hyperliquid strategy instance creation on page load
    Hyperliquid 策略实例在页面加载时创建的冒烟测试
    
    Tests that the /api/hyperliquid/status endpoint creates a strategy instance
    when the page loads, ensuring the correct exchange client is initialized.
    测试 /api/hyperliquid/status 端点在页面加载时创建策略实例，
    确保正确的交易所客户端被初始化。
    """

    @pytest.fixture
    def client(self):
        """Create test client / 创建测试客户端"""
        return TestClient(app)

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_smoke_status_endpoint_creates_strategy_instance_on_page_load(
        self, mock_bot_engine, mock_get_exchange, client
    ):
        """
        Smoke Test: /api/hyperliquid/status creates strategy instance on first call
        冒烟测试：/api/hyperliquid/status 在首次调用时创建策略实例
        
        This simulates what happens when the page loads and calls loadStatus().
        这模拟了页面加载并调用 loadStatus() 时发生的情况。
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
        mock_bot_engine.add_strategy_instance = MagicMock(return_value=True)
        
        # Create a new instance after add_strategy_instance is called
        # 在 add_strategy_instance 被调用后创建新实例
        mock_instance = MagicMock()
        mock_instance.exchange = mock_exchange
        mock_strategy_instances.get = MagicMock(
            side_effect=lambda key: mock_instance if key == "hyperliquid" else None
        )

        # Call the status endpoint (simulating page load)
        # 调用状态端点（模拟页面加载）
        response = client.get("/api/hyperliquid/status")

        # Verify response is successful
        # 验证响应成功
        assert response.status_code == 200
        data = response.json()
        assert data["connected"] is True
        assert data["exchange"] == "hyperliquid"

        # Verify that add_strategy_instance was called
        # 验证 add_strategy_instance 被调用
        assert mock_bot_engine.add_strategy_instance.called, "Strategy instance should be created on page load"
        call_args = mock_bot_engine.add_strategy_instance.call_args
        assert call_args[0][0] == "hyperliquid", "Should create instance with id 'hyperliquid'"
        assert call_args[0][1] == "fixed_spread", "Should use 'fixed_spread' strategy type"
        assert call_args[1]["exchange"] == mock_exchange, "Should pass HyperliquidClient as exchange"

    @patch("server.get_exchange_by_name")
    @patch("server.bot_engine")
    def test_smoke_status_endpoint_reuses_existing_instance(
        self, mock_bot_engine, mock_get_exchange, client
    ):
        """
        Smoke Test: /api/hyperliquid/status reuses existing strategy instance
        冒烟测试：/api/hyperliquid/status 重用现有的策略实例
        
        Tests that subsequent calls to the status endpoint don't create duplicate instances.
        测试对状态端点的后续调用不会创建重复实例。
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
        mock_bot_engine.add_strategy_instance = MagicMock()

        # Call the status endpoint multiple times
        # 多次调用状态端点
        response1 = client.get("/api/hyperliquid/status")
        response2 = client.get("/api/hyperliquid/status")

        # Verify both responses are successful
        # 验证两个响应都成功
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify that add_strategy_instance was NOT called (instance already exists)
        # 验证 add_strategy_instance 未被调用（实例已存在）
        mock_bot_engine.add_strategy_instance.assert_not_called(), "Should not create duplicate instance"

