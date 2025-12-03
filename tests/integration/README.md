# Integration Tests / 集成测试

This directory contains integration tests that verify cross-module interactions.  
此目录包含验证跨模块交互的集成测试。

## Owner / 负责人

This directory is owned by **Agent QA**.  
此目录由 **Agent QA** 负责。

## Running Tests / 运行测试

```bash
# Run all integration tests / 运行所有集成测试
pytest tests/integration/ -v
```

## Test Categories / 测试类别

- API integration tests / API 集成测试
- Module interaction tests / 模块交互测试
- End-to-end workflow tests / 端到端工作流测试

## Test Files / 测试文件

### `test_hyperliquid_integration.py`
Integration tests for US-CORE-004-A: Hyperliquid Connection and Authentication  
US-CORE-004-A 集成测试：Hyperliquid 连接与认证

**Coverage / 覆盖范围:**
- HyperliquidClient with StrategyInstance integration / HyperliquidClient 与 StrategyInstance 集成
- Complete data refresh flow / 完整数据刷新流程
- Order management flow / 订单管理流程
- Interface compatibility with BinanceClient / 与 BinanceClient 的接口兼容性
- Error handling integration / 错误处理集成

**Test Classes / 测试类:**
1. `TestHyperliquidStrategyInstanceIntegration` - StrategyInstance 集成测试
2. `TestHyperliquidInterfaceCompatibility` - 接口兼容性测试
3. `TestHyperliquidErrorHandlingIntegration` - 错误处理集成测试

**Run specific test / 运行特定测试:**
```bash
pytest tests/integration/test_hyperliquid_integration.py -v
```

