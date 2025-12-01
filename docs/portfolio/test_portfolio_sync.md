# Portfolio Sync Tests / 组合同步测试

## Overview / 概述

This document describes the unit tests for `_sync_portfolio_with_bot()` function, which synchronizes portfolio manager with multiple strategy instances.

本文档描述了对 `_sync_portfolio_with_bot()` 函数的单元测试，该函数用于同步组合管理器与多个策略实例。

---

## Test File / 测试文件

**Location / 位置**: `tests/test_portfolio_sync.py`

## Test Coverage / 测试覆盖

### 1. Basic Sync Tests / 基本同步测试

#### `test_sync_single_strategy_instance`
- Tests syncing a single strategy instance
- Verifies status is updated to LIVE
- Verifies metrics are updated from exchange

- 测试同步单个策略实例
- 验证状态更新为 LIVE
- 验证从 exchange 更新指标

#### `test_sync_multiple_strategy_instances`
- Tests syncing multiple strategy instances simultaneously
- Verifies each instance's data is isolated
- Verifies all strategies are updated correctly

- 测试同时同步多个策略实例
- 验证每个实例的数据是隔离的
- 验证所有策略都正确更新

### 2. Status Management Tests / 状态管理测试

#### `test_sync_preserves_paused_status`
- Tests that PAUSED status is preserved when instance is running
- Ensures API-set status takes precedence over running state

- 测试当实例运行时保留 PAUSED 状态
- 确保 API 设置的状态优先于运行状态

#### `test_sync_stopped_instance`
- Tests syncing a stopped instance
- Verifies status is updated to STOPPED when instance is not running

- 测试同步停止的实例
- 验证当实例未运行时状态更新为 STOPPED

### 3. Data Source Tests / 数据源测试

#### `test_sync_fallback_to_shared_data`
- Tests fallback to shared DataAgent when instance exchange is unavailable
- Verifies graceful degradation

- 测试当实例 exchange 不可用时回退到共享 DataAgent
- 验证优雅降级

#### `test_sync_calculates_metrics_from_order_history`
- Tests calculating metrics from instance's order history
- Verifies fill_rate and total_trades are calculated correctly

- 测试从实例的订单历史计算指标
- 验证 fill_rate 和 total_trades 计算正确

### 4. Error Handling Tests / 错误处理测试

#### `test_sync_handles_exchange_error_gracefully`
- Tests graceful handling of exchange errors
- Verifies fallback to shared data when exchange fails
- Ensures no exceptions are raised

- 测试优雅处理 exchange 错误
- 验证当 exchange 失败时回退到共享数据
- 确保不抛出异常

#### `test_sync_unknown_strategy_type`
- Tests handling of unknown strategy types
- Verifies existing strategies are not affected

- 测试处理未知策略类型
- 验证现有策略不受影响

### 5. Backward Compatibility Tests / 向后兼容测试

#### `test_sync_legacy_mode`
- Tests backward compatibility with legacy single-strategy mode
- Verifies function works when strategy_instances is empty

- 测试与旧版单策略模式的向后兼容
- 验证当 strategy_instances 为空时函数仍能工作

### 6. Additional Tests / 附加测试

#### `test_sync_updates_total_capital`
- Tests that total capital is updated from exchange balance

- 测试从 exchange 余额更新总资金

#### `test_sync_records_pnl_snapshot`
- Tests that PnL snapshot is recorded for portfolio Sharpe calculation

- 测试记录 PnL 快照用于组合 Sharpe 计算

---

## Running Tests / 运行测试

### Run All Portfolio Sync Tests / 运行所有组合同步测试

```bash
pytest tests/test_portfolio_sync.py -v
```

### Run Specific Test / 运行特定测试

```bash
pytest tests/test_portfolio_sync.py::TestPortfolioSync::test_sync_multiple_strategy_instances -v
```

### Run with Coverage / 运行并查看覆盖率

```bash
pytest tests/test_portfolio_sync.py --cov=server --cov-report=html
```

---

## Test Fixtures / 测试 Fixtures

### `portfolio_manager`
- Creates a PortfolioManager instance with two registered strategies
- Returns: PortfolioManager instance

- 创建包含两个注册策略的 PortfolioManager 实例
- 返回：PortfolioManager 实例

### `mock_strategy_instance`
- Creates a mock StrategyInstance with exchange and order history
- Returns: MagicMock instance configured as StrategyInstance

- 创建带有 exchange 和订单历史的模拟 StrategyInstance
- 返回：配置为 StrategyInstance 的 MagicMock 实例

### `mock_bot_engine`
- Creates a mock bot_engine with strategy_instances
- Returns: MagicMock instance configured as AlphaLoop

- 创建带有 strategy_instances 的模拟 bot_engine
- 返回：配置为 AlphaLoop 的 MagicMock 实例

---

## Key Testing Patterns / 关键测试模式

### 1. Patching Server Module / 补丁 Server 模块

```python
with patch.object(server, "get_default_exchange", return_value=instance.exchange):
    with patch.object(server, "bot_engine", bot):
        with patch.object(server, "portfolio_manager", portfolio_manager):
            server._sync_portfolio_with_bot()
```

### 2. Verifying Status Updates / 验证状态更新

```python
strategy = portfolio_manager.strategies["fixed_spread"]
assert strategy.status == StrategyStatus.LIVE
```

### 3. Verifying Metrics Updates / 验证指标更新

```python
assert strategy.pnl == 100.0
assert strategy.sharpe == 2.0
assert strategy.fill_rate == 0.85
```

---

## Expected Behavior / 预期行为

### Success Cases / 成功情况

1. ✅ Multiple instances sync independently
2. ✅ Status reflects instance running state
3. ✅ Metrics are calculated per instance
4. ✅ Errors are handled gracefully

1. ✅ 多个实例独立同步
2. ✅ 状态反映实例运行状态
3. ✅ 按实例计算指标
4. ✅ 优雅处理错误

### Edge Cases / 边界情况

1. ✅ PAUSED status is preserved
2. ✅ Unknown strategy types are skipped
3. ✅ Exchange errors trigger fallback
4. ✅ Legacy mode still works

1. ✅ 保留 PAUSED 状态
2. ✅ 跳过未知策略类型
3. ✅ Exchange 错误触发回退
4. ✅ 旧版模式仍能工作

---

## Future Test Additions / 未来测试添加

1. **Performance Tests**: Test sync performance with many instances
2. **Concurrency Tests**: Test concurrent sync operations
3. **Data Consistency Tests**: Verify data consistency across syncs
4. **Integration Tests**: Test with real exchange connections (mocked)

1. **性能测试**：测试多个实例的同步性能
2. **并发测试**：测试并发同步操作
3. **数据一致性测试**：验证跨同步的数据一致性
4. **集成测试**：使用真实 exchange 连接（模拟）进行测试

---

## Update Log / 更新日志

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2024-01 | Initial test suite for multi-strategy sync |






