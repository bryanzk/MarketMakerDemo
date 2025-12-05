# Playwright Setup Guide / Playwright 安装指南

## Installation Status / 安装状态

✅ **Playwright 已成功安装**

- **Version / 版本**: 1.56.0
- **Browser / 浏览器**: Chromium (已安装)
- **Location / 位置**: `/Users/kezheng/Library/Caches/ms-playwright/`

## Installation Steps / 安装步骤

### 1. Install Playwright Package / 安装 Playwright 包

```bash
source .venv/bin/activate
pip install playwright
```

### 2. Install Browser / 安装浏览器

```bash
playwright install chromium
```

This installs:
- Chromium browser
- Chromium Headless Shell
- FFMPEG (for video recording)

这将安装：
- Chromium 浏览器
- Chromium Headless Shell
- FFMPEG（用于视频录制）

## Verification / 验证

### Check Installation / 检查安装

```bash
# Check Playwright version / 检查 Playwright 版本
playwright --version

# Test import / 测试导入
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright import successful')"

# Test browser launch / 测试浏览器启动
python -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); browser = p.chromium.launch(headless=True); print('✅ Browser launch successful'); browser.close(); p.stop()"
```

### Run E2E Tests / 运行 E2E 测试

```bash
# Collect tests (verify setup) / 收集测试（验证设置）
pytest tests/e2e/ --collect-only

# Run E2E tests (requires server running) / 运行 E2E 测试（需要服务器运行）
# First, start server: python3 server.py
# Then in another terminal:
pytest tests/e2e/ -v
```

## E2E Test Files / E2E 测试文件

- `tests/e2e/test_error_display.py` - Tests frontend error display

## Requirements / 要求

- Server must be running on `localhost:3000` before running E2E tests
- Tests use headless browser mode by default

运行 E2E 测试前，服务器必须在 `localhost:3000` 上运行
测试默认使用无头浏览器模式

## Troubleshooting / 故障排除

### Browser Not Found / 浏览器未找到

If you see "Browser not found" errors:

如果看到"浏览器未找到"错误：

```bash
# Reinstall browsers / 重新安装浏览器
playwright install chromium

# Or install all browsers / 或安装所有浏览器
playwright install
```

### Import Errors / 导入错误

If you see import errors:

如果看到导入错误：

```bash
# Reinstall Playwright / 重新安装 Playwright
pip uninstall playwright
pip install playwright
playwright install chromium
```

## Additional Resources / 额外资源

- [Playwright Documentation](https://playwright.dev/python/)
- [Playwright Python API](https://playwright.dev/python/docs/api/class-playwright)

