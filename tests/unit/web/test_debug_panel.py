"""
Unit tests for Debug Panel Integration
调试面板集成单元测试

Tests for Phase 5: Frontend Debug Panel
测试 Phase 5: 前端调试面板

Owner: Agent QA
"""

import pytest
from fastapi.testclient import TestClient

import server


class TestDebugPanelIntegration:
    """
    Test Debug Panel Integration in HTML Templates
    测试 HTML 模板中的调试面板集成
    """

    def test_hyperliquid_trade_page_includes_debug_panel(self):
        """
        Test AC: HyperliquidTrade.html includes debug panel scripts and styles
        测试 AC: HyperliquidTrade.html 包含调试面板脚本和样式
        
        Given: I navigate to /hyperliquid
        When: The page loads
        Then: Debug panel JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for debug panel JavaScript / 检查调试面板 JavaScript
        assert "debug_panel.js" in html_content
        assert "/static/debug_panel.js" in html_content
        
        # Check for debug panel CSS / 检查调试面板 CSS
        assert "debug_panel.css" in html_content
        assert "/static/debug_panel.css" in html_content
        
        # Check for API diagnostics dependency / 检查 API 诊断依赖
        assert "api_diagnostics.js" in html_content
        assert "error_handler.js" in html_content

    def test_llm_trade_page_includes_debug_panel(self):
        """
        Test AC: LLMTrade.html includes debug panel scripts and styles
        测试 AC: LLMTrade.html 包含调试面板脚本和样式
        
        Given: I navigate to /evaluation
        When: The page loads
        Then: Debug panel JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/evaluation")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for debug panel JavaScript / 检查调试面板 JavaScript
        assert "debug_panel.js" in html_content
        assert "/static/debug_panel.js" in html_content
        
        # Check for debug panel CSS / 检查调试面板 CSS
        assert "debug_panel.css" in html_content
        assert "/static/debug_panel.css" in html_content

    def test_index_page_includes_debug_panel(self):
        """
        Test AC: index.html includes debug panel scripts and styles
        测试 AC: index.html 包含调试面板脚本和样式
        
        Given: I navigate to /
        When: The page loads
        Then: Debug panel JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for debug panel JavaScript / 检查调试面板 JavaScript
        assert "debug_panel.js" in html_content
        assert "/static/debug_panel.js" in html_content
        
        # Check for debug panel CSS / 检查调试面板 CSS
        assert "debug_panel.css" in html_content
        assert "/static/debug_panel.css" in html_content

    def test_debug_panel_static_files_accessible(self):
        """
        Test AC: Debug panel static files are accessible
        测试 AC: 调试面板静态文件可访问
        
        Given: Static files are mounted
        When: I request debug panel files
        Then: Files should be accessible
        """
        client = TestClient(server.app)
        
        # Test JavaScript file / 测试 JavaScript 文件
        js_response = client.get("/static/debug_panel.js")
        assert js_response.status_code == 200
        assert "DebugPanel" in js_response.text
        assert "class DebugPanel" in js_response.text
        
        # Test CSS file / 测试 CSS 文件
        css_response = client.get("/static/debug_panel.css")
        assert css_response.status_code == 200
        assert ".debug-panel" in css_response.text
        assert ".debug-panel-toggle" in css_response.text

    def test_debug_panel_requires_api_diagnostics(self):
        """
        Test AC: Debug panel requires apiDiagnostics to be available
        测试 AC: 调试面板需要 apiDiagnostics 可用
        
        Given: Debug panel JavaScript is loaded
        When: I check the code
        Then: It should reference window.apiDiagnostics
        """
        client = TestClient(server.app)
        response = client.get("/static/debug_panel.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for apiDiagnostics dependency / 检查 apiDiagnostics 依赖
        assert "apiDiagnostics" in js_content
        assert "window.apiDiagnostics" in js_content

    def test_debug_panel_has_filter_functionality(self):
        """
        Test AC: Debug panel has filter functionality
        测试 AC: 调试面板具有过滤功能
        
        Given: Debug panel JavaScript is loaded
        When: I check the code
        Then: It should have filter functionality (all/errors)
        """
        client = TestClient(server.app)
        response = client.get("/static/debug_panel.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for filter functionality / 检查过滤功能
        assert "filter" in js_content.lower()
        assert "errorsOnly" in js_content
        assert "getRecentCalls" in js_content

    def test_debug_panel_has_toggle_functionality(self):
        """
        Test AC: Debug panel has toggle functionality
        测试 AC: 调试面板具有切换功能
        
        Given: Debug panel JavaScript is loaded
        When: I check the code
        Then: It should have toggle/show/hide methods
        """
        client = TestClient(server.app)
        response = client.get("/static/debug_panel.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for toggle functionality / 检查切换功能
        assert "toggle" in js_content
        assert "show" in js_content
        assert "hide" in js_content
        assert "isVisible" in js_content

    def test_debug_panel_css_has_styles(self):
        """
        Test AC: Debug panel CSS has required styles
        测试 AC: 调试面板 CSS 具有所需样式
        
        Given: Debug panel CSS is loaded
        When: I check the styles
        Then: It should have panel, toggle button, and call item styles
        """
        client = TestClient(server.app)
        response = client.get("/static/debug_panel.css")
        
        assert response.status_code == 200
        css_content = response.text
        
        # Check for required CSS classes / 检查必需的 CSS 类
        assert ".debug-panel" in css_content
        assert ".debug-panel-toggle" in css_content
        assert ".debug-panel-header" in css_content
        assert ".debug-panel-content" in css_content
        assert ".debug-call-item" in css_content
        assert ".debug-call-header" in css_content

    def test_debug_panel_css_has_status_colors(self):
        """
        Test AC: Debug panel CSS has status-based color coding
        测试 AC: 调试面板 CSS 具有基于状态的颜色编码
        
        Given: Debug panel CSS is loaded
        When: I check the styles
        Then: It should have error, warning, and success styles
        """
        client = TestClient(server.app)
        response = client.get("/static/debug_panel.css")
        
        assert response.status_code == 200
        css_content = response.text
        
        # Check for status-based styles / 检查基于状态的样式
        assert ".status-error" in css_content or "error" in css_content.lower()
        assert ".status-warning" in css_content or "warning" in css_content.lower()
        assert ".status-success" in css_content or "success" in css_content.lower()

    def test_all_templates_have_consistent_debug_panel_integration(self):
        """
        Test AC: All templates have consistent debug panel integration
        测试 AC: 所有模板具有一致的调试面板集成
        
        Given: All HTML templates
        When: I check their debug panel integration
        Then: They should all include the same debug panel files
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
            
            # All templates should have debug panel / 所有模板都应该有调试面板
            assert "/static/debug_panel.js" in html_content, f"{template_name} missing debug_panel.js"
            assert "/static/debug_panel.css" in html_content, f"{template_name} missing debug_panel.css"
            
            # All templates should have dependencies / 所有模板都应该有依赖
            assert "/static/api_diagnostics.js" in html_content, f"{template_name} missing api_diagnostics.js"
            assert "/static/error_handler.js" in html_content, f"{template_name} missing error_handler.js"

