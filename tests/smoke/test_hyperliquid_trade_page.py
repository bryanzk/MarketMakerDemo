"""
Smoke Test for US-UI-004: Dedicated Hyperliquid Trading Page
US-UI-004 冒烟测试：专用 Hyperliquid 交易页面

Smoke tests verify critical paths without full integration.
冒烟测试验证关键路径，无需完整集成。

Owner: Agent QA
"""

from unittest.mock import Mock, patch

import pytest
from fastapi.testclient import TestClient

import server


class TestHyperliquidTradePageSmoke:
    """
    Smoke tests for Hyperliquid Trading Page.
    Hyperliquid 交易页面的冒烟测试。
    
    These tests verify the critical path without full integration.
    这些测试验证关键路径，无需完整集成。
    """

    def test_smoke_page_route_exists(self):
        """
        Smoke Test: AC-1 - Hyperliquid page route exists and is accessible
        冒烟测试：AC-1 - Hyperliquid 页面路由存在且可访问
        
        This is the most critical path - if the page route doesn't exist, nothing works.
        这是最关键路径 - 如果页面路由不存在，所有功能都无法工作。
        """
        client = TestClient(server.app)
        
        # Test page route
        # 测试页面路由
        response = client.get("/hyperliquid")
        
        # Verify route exists and returns HTML
        # 验证路由存在并返回 HTML
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code} / 预期 200，得到 {response.status_code}"
        )
        assert "text/html" in response.headers.get("content-type", ""), (
            "Response should be HTML / 响应应该是 HTML"
        )

    def test_smoke_page_contains_hyperliquid_branding(self):
        """
        Smoke Test: AC-1 - Page contains Hyperliquid-specific branding
        冒烟测试：AC-1 - 页面包含 Hyperliquid 特定品牌
        
        Verifies that the page has Hyperliquid-specific content.
        验证页面具有 Hyperliquid 特定内容。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text.lower()
        
        # Check for Hyperliquid branding
        # 检查 Hyperliquid 品牌
        assert "hyperliquid" in html, (
            "Page should contain Hyperliquid branding / 页面应该包含 Hyperliquid 品牌"
        )
        assert "trading" in html or "交易" in response.text, (
            "Page should mention trading / 页面应该提到交易"
        )

    def test_smoke_page_contains_navigation(self):
        """
        Smoke Test: AC-7 - Page contains navigation links
        冒烟测试：AC-7 - 页面包含导航链接
        
        Verifies that navigation links are present.
        验证导航链接存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for navigation links
        # 检查导航链接
        assert 'href="/"' in html or 'href="' in html, (
            "Page should contain navigation links / 页面应该包含导航链接"
        )

    def test_smoke_page_contains_strategy_controls(self):
        """
        Smoke Test: AC-2 - Page contains strategy control panel
        冒烟测试：AC-2 - 页面包含策略控制面板
        
        Verifies that strategy control inputs are present.
        验证策略控制输入存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text.lower()
        
        # Check for strategy control elements
        # 检查策略控制元素
        # Note: Fixed Spread Strategy includes spread, quantity, leverage (NOT skew factor)
        # 注意：固定价差策略包括价差、数量、杠杆（不包括倾斜因子）
        assert (
            "spread" in html or "价差" in response.text
        ), "Page should contain spread control / 页面应该包含价差控制"
        assert (
            "quantity" in html or "数量" in response.text
        ), "Page should contain quantity control / 页面应该包含数量控制"
        assert (
            "leverage" in html or "杠杆" in response.text
        ), "Page should contain leverage control / 页面应该包含杠杆控制"

    def test_smoke_page_contains_position_panel(self):
        """
        Smoke Test: AC-3 - Page contains position and balance panel
        冒烟测试：AC-3 - 页面包含仓位与余额面板
        
        Verifies that position/balance display elements are present.
        验证仓位/余额显示元素存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text.lower()
        
        # Check for position/balance panel elements
        # 检查仓位/余额面板元素
        assert (
            "position" in html or "仓位" in response.text
        ), "Page should contain position panel / 页面应该包含仓位面板"
        assert (
            "balance" in html or "余额" in response.text
        ), "Page should contain balance panel / 页面应该包含余额面板"

    def test_smoke_page_contains_llm_evaluation_section(self):
        """
        Smoke Test: AC-4 - Page contains LLM evaluation section
        冒烟测试：AC-4 - 页面包含 LLM 评估部分
        
        Verifies that LLM evaluation UI elements are present.
        验证 LLM 评估 UI 元素存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text.lower()
        
        # Check for LLM evaluation elements
        # 检查 LLM 评估元素
        assert (
            "llm" in html or "evaluation" in html or "评估" in response.text
        ), "Page should contain LLM evaluation section / 页面应该包含 LLM 评估部分"

    def test_smoke_page_contains_connection_status(self):
        """
        Smoke Test: AC-9 - Page contains connection status display
        冒烟测试：AC-9 - 页面包含连接状态显示
        
        Verifies that connection status elements are present.
        验证连接状态元素存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for connection status elements
        # 检查连接状态元素
        assert (
            "connection" in html.lower()
            or "连接" in html
            or "status" in html.lower()
            or "状态" in html
        ), "Page should contain connection status / 页面应该包含连接状态"

    def test_smoke_page_contains_bilingual_text(self):
        """
        Smoke Test: AC-8 - Page contains bilingual text (English and Chinese)
        冒烟测试：AC-8 - 页面包含双语文本（英文和中文）
        
        Verifies that page has both English and Chinese text.
        验证页面同时包含英文和中文文本。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for bilingual content
        # 检查双语内容
        has_english = any(
            word in html.lower()
            for word in ["trading", "hyperliquid", "connection", "position", "balance"]
        )
        has_chinese = any(word in html for word in ["交易", "连接", "仓位", "余额", "页面"])
        
        assert has_english, "Page should contain English text / 页面应该包含英文文本"
        assert has_chinese, "Page should contain Chinese text / 页面应该包含中文文本"

    def test_smoke_page_contains_order_section(self):
        """
        Smoke Test: AC-5 - Page contains order management section
        冒烟测试：AC-5 - 页面包含订单管理部分
        
        Verifies that order management UI elements are present.
        验证订单管理 UI 元素存在。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text.lower()
        
        # Check for order management elements
        # 检查订单管理元素
        assert (
            "order" in html or "订单" in response.text
        ), "Page should contain order section / 页面应该包含订单部分"

    def test_smoke_page_structure_is_valid(self):
        """
        Smoke Test: Page structure is valid HTML
        冒烟测试：页面结构是有效的 HTML
        
        Verifies that the page has basic HTML structure.
        验证页面具有基本的 HTML 结构。
        """
        client = TestClient(server.app)
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200
        html = response.text
        
        # Check for basic HTML structure
        # 检查基本 HTML 结构
        assert "<html" in html.lower() or "<!doctype" in html.lower(), (
            "Page should have HTML structure / 页面应该有 HTML 结构"
        )
        assert "<head" in html.lower(), "Page should have head section / 页面应该有 head 部分"
        assert "<body" in html.lower() or "<div" in html.lower(), (
            "Page should have body/content section / 页面应该有 body/内容部分"
        )

    @patch("server.get_exchange_by_name")
    def test_smoke_page_loads_without_errors(self, mock_get_exchange):
        """
        Smoke Test: Page loads without critical errors
        冒烟测试：页面加载无严重错误
        
        Verifies that the page can be loaded without raising exceptions.
        验证页面可以在不引发异常的情况下加载。
        """
        # Mock exchange to avoid connection errors
        # 模拟交易所以避免连接错误
        mock_get_exchange.return_value = None
        
        client = TestClient(server.app)
        
        # Page should load even if exchange is not connected
        # 即使交易所未连接，页面也应该加载
        response = client.get("/hyperliquid")
        
        assert response.status_code == 200, (
            f"Page should load successfully, got {response.status_code} / "
            f"页面应该成功加载，得到 {response.status_code}"
        )

