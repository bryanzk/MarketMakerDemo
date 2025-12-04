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

### `test_hyperliquid_orders_integration.py`
Integration tests for US-CORE-004-B: Hyperliquid Order Management  
US-CORE-004-B 集成测试：Hyperliquid 订单管理

**Coverage / 覆盖范围:**
- AC-10: OrderManager integration / OrderManager 集成
- Complete order sync flow / 完整订单同步流程
- StrategyInstance order management / StrategyInstance 订单管理
- Complete order lifecycle / 完整订单生命周期
- Order error handling / 订单错误处理

**Test Classes / 测试类:**
1. `TestHyperliquidOrderManagerIntegration` - OrderManager 集成测试
2. `TestHyperliquidStrategyInstanceOrderIntegration` - StrategyInstance 订单集成测试
3. `TestHyperliquidOrderWorkflowIntegration` - 订单工作流集成测试

**Run specific test / 运行特定测试:**
```bash
pytest tests/integration/test_hyperliquid_orders_integration.py -v
```

### `test_hyperliquid_llm_evaluation_integration.py`
Integration tests for US-API-004: Hyperliquid LLM Evaluation Support  
US-API-004 集成测试：Hyperliquid LLM 评估支持

**Coverage / 覆盖范围:**
- AC-1, AC-3: Complete evaluation flow with Hyperliquid / 使用 Hyperliquid 的完整评估流程
- AC-3, AC-4: Hyperliquid market data in LLM context / LLM 上下文中的 Hyperliquid 市场数据
- AC-2: Response format consistency for Hyperliquid / Hyperliquid 响应格式一致性
- AC-5: Error handling integration for Hyperliquid / Hyperliquid 错误处理集成
- MultiLLMEvaluator with HyperliquidClient integration / MultiLLMEvaluator 与 HyperliquidClient 集成
- AC-3: Apply LLM suggestions to Hyperliquid / 将 LLM 建议应用到 Hyperliquid

**Test Classes / 测试类:**
1. `TestHyperliquidLLMEvaluationAPIIntegration` - API 集成测试
2. `TestHyperliquidLLMEvaluatorIntegration` - MultiLLMEvaluator 集成测试
3. `TestHyperliquidLLMApplyIntegration` - 应用建议集成测试

**Run specific test / 运行特定测试:**
```bash
pytest tests/integration/test_hyperliquid_llm_evaluation_integration.py -v
```

### `test_hyperliquid_positions_integration.py`
Integration tests for US-CORE-004-C: Hyperliquid Position and Balance Tracking  
US-CORE-004-C 集成测试：Hyperliquid 仓位与余额追踪

**Coverage / 覆盖范围:**
- AC-2, AC-8: StrategyInstance position tracking integration / StrategyInstance 仓位追踪集成
- AC-3, AC-4: PnL calculation flow / 盈亏计算流程
- AC-5: Position history tracking / 仓位历史追踪
- AC-6: Margin information integration / 保证金信息集成
- AC-7: Multi-symbol position tracking / 多交易对仓位追踪
- AC-9: PerformanceTracker integration / PerformanceTracker 集成
- AC-10: Error handling integration / 错误处理集成
- Complete position tracking workflow / 完整仓位追踪工作流

**Test Classes / 测试类:**
1. `TestHyperliquidStrategyInstancePositionIntegration` - StrategyInstance 集成测试
2. `TestHyperliquidPerformanceTrackerIntegration` - PerformanceTracker 集成测试
3. `TestHyperliquidPositionWorkflowIntegration` - 工作流集成测试
4. `TestHyperliquidErrorHandlingIntegration` - 错误处理集成测试

**Run specific test / 运行特定测试:**
```bash
pytest tests/integration/test_hyperliquid_positions_integration.py -v
```

### `test_hyperliquid_trade_page_integration.py`
Integration tests for US-UI-004: Dedicated Hyperliquid Trading Page  
US-UI-004 集成测试：专用 Hyperliquid 交易页面

**Coverage / 覆盖范围:**
- AC-2: Strategy control API integration / 策略控制 API 集成
- AC-3: Position and balance data integration / 仓位与余额数据集成
- AC-4: LLM evaluation API integration / LLM 评估 API 集成
- AC-6: Real-time updates integration / 实时更新集成
- AC-10: Error handling integration / 错误处理集成
- Complete page workflow / 完整页面工作流
- API endpoint integration / API 端点集成

**Test Classes / 测试类:**
1. `TestHyperliquidPageAPIIntegration` - API 集成测试
2. `TestHyperliquidPageWorkflowIntegration` - 工作流集成测试
3. `TestHyperliquidPageErrorHandlingIntegration` - 错误处理集成测试
4. `TestHyperliquidPageRealTimeUpdatesIntegration` - 实时更新集成测试

**Run specific test / 运行特定测试:**
```bash
pytest tests/integration/test_hyperliquid_trade_page_integration.py -v
```

