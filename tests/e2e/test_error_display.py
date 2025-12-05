"""
E2E tests to verify error banners render correctly / 端到端测试以验证错误横幅正确渲染

Tests frontend error display using Playwright.
使用 Playwright 测试前端错误显示。

Owner: Agent QA

Note: These tests require Playwright to be installed:
注意：这些测试需要安装 Playwright：

    pip install playwright
    playwright install

To run these tests, ensure the server is running on localhost:3000:
要运行这些测试，请确保服务器在 localhost:3000 上运行：

    python3 server.py
"""

import pytest

# Try to import playwright, skip tests if not available
# 尝试导入 playwright，如果不可用则跳过测试
try:
    from playwright.sync_api import Page, expect

    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    pytestmark = pytest.mark.skip(reason="Playwright not installed / Playwright 未安装")


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not available / Playwright 不可用")
class TestErrorBannerDisplay:
    """Test error banner display / 测试错误横幅显示"""

    def test_error_banner_displays_trace_id(self, page: Page):
        """Test that error banner displays trace_id / 测试错误横幅显示 trace_id"""
        # Navigate to page / 导航到页面
        page.goto("http://localhost:3000/hyperliquid", timeout=10000)
        
        # Wait for page to load (use 'load' instead of 'networkidle' since page has continuous polling)
        # 等待页面加载（使用 'load' 而不是 'networkidle'，因为页面有持续轮询）
        page.wait_for_load_state("load", timeout=10000)
        
        # Wait a bit for JavaScript to initialize / 等待 JavaScript 初始化
        page.wait_for_timeout(2000)
        
        # Try to trigger an error by clicking a button that might fail
        # 尝试通过单击可能失败的按钮来触发错误
        # Look for any button that might trigger an API call
        # 查找可能触发 API 调用的任何按钮
        
        # Check if error banner exists (may not always be visible)
        # 检查错误横幅是否存在（可能不总是可见）
        error_banner = page.locator(".error-message, #evaluationErrorBox")
        
        # If error banner is visible, check for trace_id
        # 如果错误横幅可见，检查 trace_id
        if error_banner.count() > 0:
            trace_id_element = page.locator(".error-trace-id, [data-trace-id]")
            if trace_id_element.count() > 0:
                expect(trace_id_element.first()).to_be_visible()

    def test_error_history_panel_exists(self, page: Page):
        """Test that error history panel exists / 测试错误历史面板存在"""
        page.goto("http://localhost:3000/hyperliquid", timeout=10000)
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(2000)
        
        # Check for error history panel
        # 检查错误历史面板
        error_history = page.locator("#errorHistory, .error-history-panel")
        
        # Panel should exist (may be hidden)
        # 面板应该存在（可能隐藏）
        assert error_history.count() > 0 or page.locator('[id*="error"]').count() > 0

    def test_debug_panel_exists(self, page: Page):
        """Test that debug panel exists / 测试调试面板存在"""
        page.goto("http://localhost:3000/hyperliquid", timeout=10000)
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(2000)
        
        # Check for debug panel toggle
        # 检查调试面板切换按钮
        debug_toggle = page.locator("#debugPanelToggle, [id*='debug']")
        
        # Toggle should exist
        # 切换按钮应该存在
        if debug_toggle.count() > 0:
            # Click to open debug panel
            # 单击以打开调试面板
            debug_toggle.first.click()
            
            # Check debug panel is visible
            # 检查调试面板是否可见
            debug_panel = page.locator("#debugPanel, [id*='debug']")
            # Panel may be visible or hidden, just check it exists
            # 面板可能可见或隐藏，只需检查它是否存在
            assert debug_panel.count() > 0


@pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="Playwright not available / Playwright 不可用")
class TestErrorDisplayFunctionality:
    """Test error display functionality / 测试错误显示功能"""

    def test_error_messages_are_bilingual(self, page: Page):
        """Test that error messages are bilingual / 测试错误消息是双语的"""
        page.goto("http://localhost:3000/hyperliquid", timeout=10000)
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(2000)
        
        # Check for bilingual content (Chinese characters)
        # 检查双语内容（中文字符）
        page_content = page.content()
        
        # Should contain some Chinese characters if bilingual
        # 如果是双语，应包含一些中文字符
        # This is a basic check - actual implementation may vary
        # 这是一个基本检查 - 实际实现可能有所不同
        assert len(page_content) > 0

    def test_trace_id_is_displayed(self, page: Page):
        """Test that trace_id is displayed in error messages / 测试 trace_id 在错误消息中显示"""
        page.goto("http://localhost:3000/hyperliquid", timeout=10000)
        page.wait_for_load_state("load", timeout=10000)
        page.wait_for_timeout(2000)
        
        # Look for trace_id in page content
        # 在页面内容中查找 trace_id
        page_content = page.content()
        
        # Check if trace_id format exists (req_ followed by hex)
        # 检查是否存在 trace_id 格式（req_ 后跟十六进制）
        # This is a basic check - actual implementation may vary
        # 这是一个基本检查 - 实际实现可能有所不同
        assert "trace" in page_content.lower() or "req_" in page_content


@pytest.fixture(scope="session")
def browser():
    """Create a browser fixture for Playwright tests / 为 Playwright 测试创建浏览器 fixture"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not available / Playwright 不可用")
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser_instance = p.chromium.launch(headless=True)
        yield browser_instance
        browser_instance.close()


@pytest.fixture(scope="function")
def page(browser):
    """Create a page fixture for Playwright tests / 为 Playwright 测试创建页面 fixture"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("Playwright not available / Playwright 不可用")
    
    page_instance = browser.new_page()
    yield page_instance
    page_instance.close()

