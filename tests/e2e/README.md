# End-to-End Tests / 端到端测试

E2E tests using Playwright for browser automation.
使用 Playwright 进行浏览器自动化的 E2E 测试。

## Prerequisites / 前置要求

Install Playwright:
安装 Playwright：

```bash
pip install playwright
playwright install
```

## Test Files / 测试文件

- `test_error_display.py` - Tests frontend error display and trace_id visibility

## Running Tests / 运行测试

**Important**: Ensure the server is running on `localhost:3000` before running E2E tests.

**重要**：运行 E2E 测试前，确保服务器在 `localhost:3000` 上运行。

```bash
# Start server / 启动服务器
python3 server.py

# In another terminal, run E2E tests / 在另一个终端，运行 E2E 测试
pytest tests/e2e/ -v
```

## Test Coverage / 测试覆盖率

- ✅ Error banner displays trace_id
- ✅ Error history panel exists
- ✅ Debug panel exists
- ✅ Bilingual error messages
- ✅ Trace ID visibility

## Note / 注意

These tests require Playwright and a running server. If Playwright is not installed, tests will be automatically skipped.

这些测试需要 Playwright 和运行中的服务器。如果未安装 Playwright，测试将自动跳过。

