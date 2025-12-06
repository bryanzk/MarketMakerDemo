# Exchange Failures Integration Tests / 交易所失败集成测试

Tests error handling for various exchange failure scenarios.
测试各种交易所失败场景的错误处理。

## Purpose / 目的

These tests verify that the HyperliquidClient correctly handles various failure scenarios:
- Network timeouts
- Connection errors
- Rate limit errors (429)
- Authentication errors (401)
- Server errors (500)

这些测试验证 HyperliquidClient 正确处理各种失败场景：
- 网络超时
- 连接错误
- 速率限制错误 (429)
- 认证错误 (401)
- 服务器错误 (500)

## Test Files / 测试文件

- `test_exchange_failures.py` - Tests exchange failure handling

## Running Tests / 运行测试

```bash
# Run all exchange failure tests / 运行所有交易所失败测试
pytest tests/integration/test_exchange_failures.py -v

# Run specific test class / 运行特定测试类
pytest tests/integration/test_exchange_failures.py::TestNetworkTimeoutHandling -v
```

## Test Coverage / 测试覆盖率

- ✅ Network timeout handling
- ✅ Connection error handling
- ✅ Rate limit (429) handling
- ✅ Authentication error (401) handling
- ✅ Server error (500) handling
- ✅ Error state tracking
- ✅ Connection status after error
- ✅ Error response context

## Test Results / 测试结果

**Last Run / 最近运行**: All 8 tests passed ✅

- TestNetworkTimeoutHandling: 2 tests passed
- TestRateLimitHandling: 1 test passed
- TestAuthenticationErrorHandling: 1 test passed
- TestServerErrorHandling: 1 test passed
- TestErrorRecovery: 2 tests passed
- TestErrorResponseFormat: 1 test passed

## Implementation Notes / 实现说明

These tests use `unittest.mock.patch` to mock `requests.post` calls. The HyperliquidClient's `_connect_and_authenticate` method makes two POST requests (to `/info` and `/exchange`), so tests must provide enough mock responses for the connection phase.

这些测试使用 `unittest.mock.patch` 来模拟 `requests.post` 调用。HyperliquidClient 的 `_connect_and_authenticate` 方法会进行两次 POST 请求（到 `/info` 和 `/exchange`），因此测试必须为连接阶段提供足够的 mock 响应。


