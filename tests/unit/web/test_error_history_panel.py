"""
Unit tests for Error History Panel
错误历史面板单元测试

Tests for Phase 8: Add Error History Display
测试 Phase 8: 添加错误历史显示

Owner: Agent QA
"""

import pytest
from fastapi.testclient import TestClient

import server


class TestErrorHistoryPanelIntegration:
    """
    Test Error History Panel Integration in HTML Templates
    测试 HTML 模板中的错误历史面板集成
    """

    def test_hyperliquid_trade_page_includes_error_history(self):
        """
        Test AC: HyperliquidTrade.html includes error history scripts and styles
        测试 AC: HyperliquidTrade.html 包含错误历史脚本和样式
        
        Given: I navigate to /hyperliquid
        When: The page loads
        Then: Error history JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for error history JavaScript / 检查错误历史 JavaScript
        assert "error_history.js" in html_content
        assert "/static/error_history.js" in html_content
        
        # Check for error history CSS / 检查错误历史 CSS
        assert "error_history.css" in html_content
        assert "/static/error_history.css" in html_content
        
        # Check for error history panel container / 检查错误历史面板容器
        assert 'id="errorHistoryPanel"' in html_content

    def test_llm_trade_page_includes_error_history(self):
        """
        Test AC: LLMTrade.html includes error history scripts and styles
        测试 AC: LLMTrade.html 包含错误历史脚本和样式
        
        Given: I navigate to /evaluation
        When: The page loads
        Then: Error history JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/evaluation")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for error history JavaScript / 检查错误历史 JavaScript
        assert "error_history.js" in html_content
        assert "/static/error_history.js" in html_content
        
        # Check for error history CSS / 检查错误历史 CSS
        assert "error_history.css" in html_content
        assert "/static/error_history.css" in html_content
        
        # Check for error history panel container / 检查错误历史面板容器
        assert 'id="errorHistoryPanel"' in html_content

    def test_index_page_includes_error_history(self):
        """
        Test AC: index.html includes error history scripts and styles
        测试 AC: index.html 包含错误历史脚本和样式
        
        Given: I navigate to /
        When: The page loads
        Then: Error history JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for error history JavaScript / 检查错误历史 JavaScript
        assert "error_history.js" in html_content
        assert "/static/error_history.js" in html_content
        
        # Check for error history CSS / 检查错误历史 CSS
        assert "error_history.css" in html_content
        assert "/static/error_history.css" in html_content
        
        # Check for error history panel container / 检查错误历史面板容器
        assert 'id="errorHistoryPanel"' in html_content

    def test_error_history_static_files_accessible(self):
        """
        Test AC: Error history static files are accessible
        测试 AC: 错误历史静态文件可访问
        
        Given: Static files are mounted
        When: I request error history files
        Then: Files should be accessible
        """
        client = TestClient(server.app)
        
        # Test JavaScript file / 测试 JavaScript 文件
        js_response = client.get("/static/error_history.js")
        assert js_response.status_code == 200
        assert "ErrorHistoryPanel" in js_response.text
        assert "class ErrorHistoryPanel" in js_response.text
        
        # Test CSS file / 测试 CSS 文件
        css_response = client.get("/static/error_history.css")
        assert css_response.status_code == 200
        assert ".error-history-panel" in css_response.text
        assert ".error-item" in css_response.text

    def test_error_history_has_auto_refresh_functionality(self):
        """
        Test AC: Error history has auto-refresh functionality
        测试 AC: 错误历史具有自动刷新功能
        
        Given: Error history JavaScript is loaded
        When: I check the code
        Then: It should have auto-refresh functionality
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for auto-refresh functionality / 检查自动刷新功能
        assert "autoRefresh" in js_content
        assert "refreshInterval" in js_content
        assert "startAutoRefresh" in js_content
        assert "stopAutoRefresh" in js_content

    def test_error_history_displays_trace_id(self):
        """
        Test AC: Error history displays trace_id
        测试 AC: 错误历史显示 trace_id
        
        Given: Error history JavaScript is loaded
        When: I check the code
        Then: It should have trace_id display functionality
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for trace_id display / 检查 trace_id 显示
        assert "trace_id" in js_content or "traceId" in js_content
        assert "showTraceId" in js_content

    def test_error_history_has_refresh_button(self):
        """
        Test AC: Error history has refresh button
        测试 AC: 错误历史具有刷新按钮
        
        Given: Error history JavaScript is loaded
        When: I check the code
        Then: It should have refresh button functionality
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for refresh button / 检查刷新按钮
        assert "errorHistoryRefresh" in js_content
        assert "refresh" in js_content.lower()

    def test_error_history_has_toggle_auto_refresh(self):
        """
        Test AC: Error history has toggle auto-refresh button
        测试 AC: 错误历史具有切换自动刷新按钮
        
        Given: Error history JavaScript is loaded
        When: I check the code
        Then: It should have toggle auto-refresh functionality
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for toggle auto-refresh / 检查切换自动刷新
        assert "errorHistoryToggle" in js_content
        assert "toggleAutoRefresh" in js_content

    def test_error_history_css_has_styles(self):
        """
        Test AC: Error history CSS has required styles
        测试 AC: 错误历史 CSS 具有必需的样式
        
        Given: Error history CSS is loaded
        When: I check the styles
        Then: It should have error history styles
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.css")
        
        assert response.status_code == 200
        css_content = response.text
        
        # Check for required CSS classes / 检查必需的 CSS 类
        assert ".error-history-panel" in css_content
        assert ".error-history-header" in css_content
        assert ".error-history-content" in css_content
        assert ".error-item" in css_content
        assert ".error-alert" in css_content

    def test_error_history_css_has_error_type_styles(self):
        """
        Test AC: Error history CSS has error type styles
        测试 AC: 错误历史 CSS 具有错误类型样式
        
        Given: Error history CSS is loaded
        When: I check the styles
        Then: It should have error type color coding
        """
        client = TestClient(server.app)
        response = client.get("/static/error_history.css")
        
        assert response.status_code == 200
        css_content = response.text
        
        # Check for error type styles / 检查错误类型样式
        assert "error-type-" in css_content or "error_type" in css_content.lower()
        assert "insufficient_funds" in css_content or "insufficient-funds" in css_content

    def test_all_templates_have_consistent_error_history_integration(self):
        """
        Test AC: All templates have consistent error history integration
        测试 AC: 所有模板具有一致的错误历史集成
        
        Given: All HTML templates
        When: I check their error history integration
        Then: They should all include the same error history files
        """
        client = TestClient(server.app)
        
        templates = [
            ("/", "index.html"),
            ("/evaluation", "LLMTrade.html"),
            ("/hyperliquid", "HyperliquidTrade.html"),
        ]
        
        for route, template_name in templates:
            response = client.get(route)
            assert response.status_code == 200
            html_content = response.text
            
            # All templates should have error history / 所有模板都应该有错误历史
            assert "/static/error_history.js" in html_content, f"{template_name} missing error_history.js"
            assert "/static/error_history.css" in html_content, f"{template_name} missing error_history.css"
            assert 'id="errorHistoryPanel"' in html_content, f"{template_name} missing errorHistoryPanel container"

    def test_error_history_initializes_on_page_load(self):
        """
        Test AC: Error history initializes on page load
        测试 AC: 错误历史在页面加载时初始化
        
        Given: HTML templates include error history
        When: I check the initialization code
        Then: ErrorHistoryPanel should be initialized on DOMContentLoaded
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for initialization code / 检查初始化代码
        assert "ErrorHistoryPanel" in html_content
        assert "new ErrorHistoryPanel" in html_content
        assert "DOMContentLoaded" in html_content or "addEventListener" in html_content

