# Contract Tests / 契约测试

Tests that verify API contracts and response formats.
验证 API 契约和响应格式的测试。

## Purpose / 目的

Contract tests ensure that all API endpoints follow the standard error response format defined in the error handling improvement plan.

契约测试确保所有 API 端点遵循错误处理改进计划中定义的标准错误响应格式。

## Test Files / 测试文件

- `test_error_envelope.py` - Tests error response envelope structure

## Running Tests / 运行测试

```bash
# Run all contract tests / 运行所有契约测试
pytest tests/contract/ -v

# Run specific test file / 运行特定测试文件
pytest tests/contract/test_error_envelope.py -v
```

## Test Coverage / 测试覆盖率

- ✅ Error response required fields
- ✅ Success response trace_id
- ✅ Trace ID in headers
- ✅ Trace ID in body
- ✅ Bilingual messages
- ✅ Timestamp
- ✅ Error type
- ✅ Endpoint-specific format checks

