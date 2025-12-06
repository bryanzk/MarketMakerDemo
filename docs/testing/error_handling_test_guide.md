# Error Handling Module Testing Guide / 错误处理模块测试指南

## Overview / 概览

This guide explains how to test the error handling module, including unit tests, integration tests, and manual testing procedures.

本指南说明如何测试错误处理模块，包括单元测试、集成测试和手动测试程序。

## Quick Start / 快速开始

### Run All Error Handling Tests / 运行所有错误处理测试

```bash
# Set PYTHONPATH and run all error handling tests
# 设置 PYTHONPATH 并运行所有错误处理测试
cd /Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo
PYTHONPATH=. pytest tests/unit/shared/test_errors.py tests/unit/shared/test_error_mapper.py tests/unit/shared/test_tracing.py tests/unit/web/test_trace_id_middleware.py tests/unit/web/test_error_response_trace_id.py tests/unit/web/test_error_history_panel.py tests/unit/web/test_strategy_instance_errors.py -v
```

### Test Results Summary / 测试结果摘要

**Last Run / 最近运行**: All tests passed ✅

- **Error Response Tests / 错误响应测试**: 18 tests passed
- **Error Mapper Tests / 错误映射器测试**: 38 tests passed  
- **Tracing Tests / 追踪测试**: 12 tests passed
- **Trace ID Middleware Tests / Trace ID 中间件测试**: 8 tests passed
- **Error Response Trace ID Tests / 错误响应 Trace ID 测试**: 8 tests passed
- **Error History Panel Tests / 错误历史面板测试**: 20 tests passed
- **Strategy Instance Errors Tests / 策略实例错误测试**: 11 tests passed

**Total / 总计**: 115 tests passed ✅

## Test Categories / 测试类别

### 1. Unit Tests / 单元测试

#### Error Response Format Tests / 错误响应格式测试
**File**: `tests/unit/shared/test_errors.py`

Tests for:
- ErrorSeverity enum values
- ErrorType enum values  
- StandardErrorResponse creation and serialization
- Timestamp auto-generation
- Bilingual message support

测试内容：
- ErrorSeverity 枚举值
- ErrorType 枚举值
- StandardErrorResponse 创建和序列化
- 时间戳自动生成
- 双语消息支持

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/shared/test_errors.py -v
```

#### Error Mapper Tests / 错误映射器测试
**File**: `tests/unit/shared/test_error_mapper.py`

Tests for:
- Exception to error type mapping
- Error severity determination
- Bilingual message translation
- Error suggestions and remediation
- Trace ID handling

测试内容：
- 异常到错误类型映射
- 错误严重程度确定
- 双语消息翻译
- 错误建议和修复步骤
- Trace ID 处理

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/shared/test_error_mapper.py -v
```

#### Tracing Tests / 追踪测试
**File**: `tests/unit/shared/test_tracing.py`

Tests for:
- Trace ID generation and format
- Context variable isolation
- Request context creation
- Payload hashing

测试内容：
- Trace ID 生成和格式
- 上下文变量隔离
- 请求上下文创建
- 负载哈希

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/shared/test_tracing.py -v
```

### 2. Web/API Tests / Web/API 测试

#### Trace ID Middleware Tests / Trace ID 中间件测试
**File**: `tests/unit/web/test_trace_id_middleware.py`

Tests for:
- Trace ID in response headers
- Trace ID in response body
- Trace ID consistency
- Trace ID uniqueness per request

测试内容：
- 响应头中的 Trace ID
- 响应体中的 Trace ID
- Trace ID 一致性
- 每个请求的 Trace ID 唯一性

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/web/test_trace_id_middleware.py -v
```

#### Error Response Trace ID Tests / 错误响应 Trace ID 测试
**File**: `tests/unit/web/test_error_response_trace_id.py`

Tests for:
- Error responses include trace_id
- Success responses include trace_id
- Trace ID in error details
- create_error_response function

测试内容：
- 错误响应包含 trace_id
- 成功响应包含 trace_id
- 错误详情中的 Trace ID
- create_error_response 函数

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/web/test_error_response_trace_id.py -v
```

#### Error History Panel Tests / 错误历史面板测试
**File**: `tests/unit/web/test_error_history_panel.py`

Tests for:
- Error history panel integration in templates
- Auto-refresh functionality
- Trace ID display
- Bilingual support
- Error type display

测试内容：
- 模板中的错误历史面板集成
- 自动刷新功能
- Trace ID 显示
- 双语支持
- 错误类型显示

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/web/test_error_history_panel.py -v
```

#### Strategy Instance Errors Tests / 策略实例错误测试
**File**: `tests/unit/web/test_strategy_instance_errors.py`

Tests for:
- `/api/bot/status` includes errors field
- Global error history exposure
- Instance-specific error history
- Trace ID in error history entries
- Error history limits

测试内容：
- `/api/bot/status` 包含 errors 字段
- 全局错误历史暴露
- 实例特定错误历史
- 错误历史条目中的 Trace ID
- 错误历史限制

**Run / 运行**:
```bash
PYTHONPATH=. pytest tests/unit/web/test_strategy_instance_errors.py -v
```

## Quick Test Script / 快速测试脚本

A quick test script is available to test API endpoints:

**File**: `test_error_handling.py`

**Usage / 用法**:
```bash
# Start server first / 先启动服务器
python3 server.py

# In another terminal / 在另一个终端
python3 test_error_handling.py
```

This script tests:
- Error response format
- Trace ID in headers
- Bot status error information

此脚本测试：
- 错误响应格式
- 响应头中的 Trace ID
- Bot 状态错误信息

## Manual Testing / 手动测试

### 1. Test Error Response Format / 测试错误响应格式

```bash
# Start server / 启动服务器
python3 server.py

# Test API endpoint / 测试 API 端点
curl http://localhost:3000/api/hyperliquid/status

# Check response includes trace_id / 检查响应包含 trace_id
curl -v http://localhost:3000/api/hyperliquid/status | grep -i trace
```

### 2. Test Frontend Error Display / 测试前端错误显示

1. Open browser: `http://localhost:3000/hyperliquid`
2. Open Developer Tools (F12)
3. Test scenarios:
   - Trigger connection error → Check error message displays trace_id
   - Input invalid order parameters → Check validation errors
   - View error history panel → Check strategy instance errors
   - Open debug panel → Check API call records

测试场景：
- 触发连接错误 → 检查错误消息显示 trace_id
- 输入无效订单参数 → 检查验证错误
- 查看错误历史面板 → 检查策略实例错误
- 打开调试面板 → 检查 API 调用记录

### 3. Test Trace ID Correlation / 测试 Trace ID 关联

1. Trigger an error in browser, note the trace_id
2. Search for trace_id in server logs:
   ```bash
   grep "req_abc123" logs/*.log
   ```
3. Verify trace_id matches between frontend and backend

验证前端和后端的 trace_id 匹配

### 4. Test Error History / 测试错误历史

```bash
# Check /api/bot/status endpoint / 检查 /api/bot/status 端点
curl http://localhost:3000/api/bot/status | jq '.errors'
```

Expected response structure / 预期响应结构:
```json
{
  "errors": {
    "global_alert": "...",
    "global_error_history": [...],
    "instance_errors": {
      "instance_id": {
        "alert": "...",
        "error_history": [...]
      }
    }
  }
}
```

## Test Coverage / 测试覆盖率

Current test coverage / 当前测试覆盖率:

- ✅ Error response format standardization
- ✅ Trace ID generation and correlation
- ✅ Error mapper functionality
- ✅ Frontend error history panel
- ✅ Strategy instance error exposure
- ✅ Bilingual error messages
- ✅ Error suggestions and remediation

## Missing Tests / 缺失的测试

According to the improvement plan, the following tests are still needed:

根据改进计划，仍需要以下测试：

1. **Contract Tests / 契约测试**
   - File: `tests/contract/test_error_envelope.py` (to be created)
   - Tests error envelope structure for all endpoints

2. **Integration Tests / 集成测试**
   - File: `tests/integration/test_exchange_failures.py` (to be created)
   - Tests network timeout handling
   - Tests rate limit handling
   - Tests authentication failures

3. **E2E Tests / 端到端测试**
   - File: `tests/e2e/test_error_display.py` (to be created)
   - Tests error banner displays trace_id
   - Tests debug panel records failing calls

## Troubleshooting / 故障排除

### Import Errors / 导入错误

If you see `ModuleNotFoundError: No module named 'src'`:

如果看到 `ModuleNotFoundError: No module named 'src'`：

```bash
# Set PYTHONPATH before running tests / 运行测试前设置 PYTHONPATH
export PYTHONPATH=.
pytest tests/unit/... -v

# Or use inline / 或使用内联
PYTHONPATH=. pytest tests/unit/... -v
```

### Server Not Running / 服务器未运行

For API tests that require a running server:

对于需要运行服务器的 API 测试：

```bash
# Start server in background / 在后台启动服务器
python3 server.py &

# Run tests / 运行测试
PYTHONPATH=. pytest tests/unit/web/... -v
```

## Next Steps / 下一步

1. ✅ Run existing unit tests (completed)
2. ⏳ Create contract tests for error envelope structure
3. ⏳ Create integration tests for exchange failures
4. ⏳ Create E2E tests for error display
5. ⏳ Add test coverage reporting

## References / 参考

- [Error Handling Improvement Plan](../development/error_handling_improvement_plan.md)
- [Testing Documentation](../../tests/README.md)
- [Unit Tests README](../../tests/unit/README.md)


