"""
Unit tests for Client-Side Validation
客户端验证单元测试

Tests for Phase 6: Client-Side Validation
测试 Phase 6: 客户端验证

Owner: Agent QA
"""

import pytest
from fastapi.testclient import TestClient

import server


class TestValidationIntegration:
    """
    Test Validation Integration in HTML Templates
    测试 HTML 模板中的验证集成
    """

    def test_hyperliquid_trade_page_includes_validation(self):
        """
        Test AC: HyperliquidTrade.html includes validation scripts and styles
        测试 AC: HyperliquidTrade.html 包含验证脚本和样式
        
        Given: I navigate to /hyperliquid
        When: The page loads
        Then: Validation JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for validation JavaScript / 检查验证 JavaScript
        assert "validation.js" in html_content
        assert "/static/validation.js" in html_content
        
        # Check for validation CSS / 检查验证 CSS
        assert "validation.css" in html_content
        assert "/static/validation.css" in html_content

    def test_llm_trade_page_includes_validation(self):
        """
        Test AC: LLMTrade.html includes validation scripts and styles
        测试 AC: LLMTrade.html 包含验证脚本和样式
        
        Given: I navigate to /evaluation
        When: The page loads
        Then: Validation JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/evaluation")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for validation JavaScript / 检查验证 JavaScript
        assert "validation.js" in html_content
        assert "/static/validation.js" in html_content
        
        # Check for validation CSS / 检查验证 CSS
        assert "validation.css" in html_content
        assert "/static/validation.css" in html_content

    def test_index_page_includes_validation(self):
        """
        Test AC: index.html includes validation scripts and styles
        测试 AC: index.html 包含验证脚本和样式
        
        Given: I navigate to /
        When: The page loads
        Then: Validation JavaScript and CSS should be included
        """
        client = TestClient(server.app)
        response = client.get("/")
        
        assert response.status_code == 200
        html_content = response.text
        
        # Check for validation JavaScript / 检查验证 JavaScript
        assert "validation.js" in html_content
        assert "/static/validation.js" in html_content
        
        # Check for validation CSS / 检查验证 CSS
        assert "validation.css" in html_content
        assert "/static/validation.css" in html_content

    def test_validation_static_files_accessible(self):
        """
        Test AC: Validation static files are accessible
        测试 AC: 验证静态文件可访问
        
        Given: Static files are mounted
        When: I request validation files
        Then: Files should be accessible
        """
        client = TestClient(server.app)
        
        # Test JavaScript file / 测试 JavaScript 文件
        js_response = client.get("/static/validation.js")
        assert js_response.status_code == 200
        assert "OrderValidator" in js_response.text
        assert "class OrderValidator" in js_response.text
        
        # Test CSS file / 测试 CSS 文件
        css_response = client.get("/static/validation.css")
        assert css_response.status_code == 200
        assert ".validation-errors" in css_response.text
        assert ".field-error" in css_response.text

    def test_validation_has_symbol_validation(self):
        """
        Test AC: Validation has symbol validation function
        测试 AC: 验证具有交易对验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validateSymbol function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for symbol validation / 检查交易对验证
        assert "validateSymbol" in js_content
        assert "symbol" in js_content.lower()

    def test_validation_has_quantity_validation(self):
        """
        Test AC: Validation has quantity validation function
        测试 AC: 验证具有数量验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validateQuantity function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for quantity validation / 检查数量验证
        assert "validateQuantity" in js_content
        assert "quantity" in js_content.lower()

    def test_validation_has_price_validation(self):
        """
        Test AC: Validation has price validation function
        测试 AC: 验证具有价格验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validatePrice function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for price validation / 检查价格验证
        assert "validatePrice" in js_content
        assert "price" in js_content.lower()

    def test_validation_has_leverage_validation(self):
        """
        Test AC: Validation has leverage validation function
        测试 AC: 验证具有杠杆验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validateLeverage function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for leverage validation / 检查杠杆验证
        assert "validateLeverage" in js_content
        assert "leverage" in js_content.lower()

    def test_validation_has_spread_validation(self):
        """
        Test AC: Validation has spread validation function
        测试 AC: 验证具有价差验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validateSpread function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for spread validation / 检查价差验证
        assert "validateSpread" in js_content
        assert "spread" in js_content.lower()

    def test_validation_has_order_validation(self):
        """
        Test AC: Validation has order validation function
        测试 AC: 验证具有订单验证函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have validateOrder function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for order validation / 检查订单验证
        assert "validateOrder" in js_content

    def test_validation_has_error_display(self):
        """
        Test AC: Validation has error display function
        测试 AC: 验证具有错误显示函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have displayErrors function
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for error display / 检查错误显示
        assert "displayErrors" in js_content or "displayValidationErrors" in js_content

    def test_validation_css_has_error_styles(self):
        """
        Test AC: Validation CSS has error styles
        测试 AC: 验证 CSS 具有错误样式
        
        Given: Validation CSS is loaded
        When: I check the styles
        Then: It should have validation error styles
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.css")
        
        assert response.status_code == 200
        css_content = response.text
        
        # Check for required CSS classes / 检查必需的 CSS 类
        assert ".validation-errors" in css_content
        assert ".field-error" in css_content
        assert ".field-success" in css_content

    def test_validation_has_bilingual_support(self):
        """
        Test AC: Validation has bilingual error messages
        测试 AC: 验证具有双语错误消息
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should have English and Chinese messages
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for bilingual support / 检查双语支持
        assert "message" in js_content
        assert "en" in js_content.lower() or "english" in js_content.lower()
        assert "zh" in js_content.lower() or "chinese" in js_content.lower()

    def test_all_templates_have_consistent_validation_integration(self):
        """
        Test AC: All templates have consistent validation integration
        测试 AC: 所有模板具有一致的验证集成
        
        Given: All HTML templates
        When: I check their validation integration
        Then: They should all include the same validation files
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
            
            # All templates should have validation / 所有模板都应该有验证
            assert "/static/validation.js" in html_content, f"{template_name} missing validation.js"
            assert "/static/validation.css" in html_content, f"{template_name} missing validation.css"

    def test_validation_has_global_functions(self):
        """
        Test AC: Validation exposes global functions
        测试 AC: 验证暴露全局函数
        
        Given: Validation JavaScript is loaded
        When: I check the code
        Then: It should expose global validation functions
        """
        client = TestClient(server.app)
        response = client.get("/static/validation.js")
        
        assert response.status_code == 200
        js_content = response.text
        
        # Check for global functions / 检查全局函数
        assert "window.orderValidator" in js_content
        assert "window.validateSymbol" in js_content
        assert "window.validateQuantity" in js_content
        assert "window.validatePrice" in js_content
        assert "window.validateLeverage" in js_content
        assert "window.validateSpread" in js_content
        assert "window.validateOrder" in js_content

