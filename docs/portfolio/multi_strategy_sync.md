# Portfolio Manager Multi-Strategy Sync / 组合管理器多策略同步

## Overview / 概述

This document describes the changes made to `_sync_portfolio_with_bot()` function in `server.py` to support the new multi-strategy instance architecture.

本文档描述了对 `server.py` 中 `_sync_portfolio_with_bot()` 函数的修改，以支持新的多策略实例架构。

---

## Changes / 变更

### Before / 之前

The original `_sync_portfolio_with_bot()` function only supported a single active strategy:

原始的 `_sync_portfolio_with_bot()` 函数只支持单个活跃策略：

- Used `bot_engine.strategy` (single strategy reference)
- Determined active strategy by checking strategy type
- Updated only one strategy's metrics in portfolio_manager
- Used shared `bot_engine.data` for all metrics

- 使用 `bot_engine.strategy`（单一策略引用）
- 通过检查策略类型确定活跃策略
- 只更新一个策略的指标到 portfolio_manager
- 使用共享的 `bot_engine.data` 获取所有指标

### After / 之后

The updated function now supports multiple strategy instances:

更新后的函数现在支持多个策略实例：

- Iterates through all `bot_engine.strategy_instances`
- Updates each strategy instance's metrics separately
- Uses each instance's own exchange connection for PnL data
- Maintains backward compatibility with legacy single-strategy mode

- 遍历所有 `bot_engine.strategy_instances`
- 单独更新每个策略实例的指标
- 使用每个实例自己的 exchange 连接获取 PnL 数据
- 保持与旧版单策略模式的向后兼容

---

## Implementation Details / 实现细节

### 1. Strategy Instance Mapping / 策略实例映射

```python
strategy_type_to_id = {
    "fixed_spread": "fixed_spread",
    "funding_rate": "funding_rate",
}
```

Maps strategy types to portfolio_manager strategy IDs.

将策略类型映射到 portfolio_manager 的策略 ID。

### 2. Status Synchronization / 状态同步

```python
if instance.running:
    if strategy.status != StrategyStatus.PAUSED:
        strategy.status = StrategyStatus.LIVE
elif strategy.status == StrategyStatus.LIVE:
    if not instance.running:
        strategy.status = StrategyStatus.STOPPED
```

Updates strategy status based on instance's `running` state, while preserving `PAUSED` status set via API.

根据实例的 `running` 状态更新策略状态，同时保留通过 API 设置的 `PAUSED` 状态。

### 3. PnL Data Fetching / PnL 数据获取

```python
if instance.use_real_exchange and instance.exchange is not None:
    try:
        pnl_data = instance.exchange.fetch_pnl_and_fees(start_time=start_time_ms)
        realized_pnl = pnl_data.get("realized_pnl", 0.0)
    except Exception as e:
        logger.debug(f"Error fetching PnL for {instance_id}: {e}")
```

Each strategy instance uses its own exchange connection to fetch PnL data, ensuring data isolation.

每个策略实例使用自己的 exchange 连接获取 PnL 数据，确保数据隔离。

### 4. Metrics Calculation / 指标计算

The function attempts to calculate metrics from multiple sources:

函数尝试从多个来源计算指标：

1. **Primary**: From instance's exchange and order history
2. **Fallback**: From shared `bot_engine.data` (filtered by strategy_id/strategy_type)
3. **Legacy**: Uses shared data if no instance-specific data available

1. **主要**：从实例的 exchange 和订单历史
2. **回退**：从共享的 `bot_engine.data`（按 strategy_id/strategy_type 过滤）
3. **旧版**：如果没有实例特定数据，使用共享数据

### 5. Backward Compatibility / 向后兼容

The function includes a fallback path for legacy single-strategy mode:

函数包含旧版单策略模式的回退路径：

```python
else:
    # Fallback: Legacy single-strategy mode
    current_strategy_type = type(bot_engine.strategy).__name__
    # ... legacy logic ...
```

This ensures the function works even if `strategy_instances` is not available.

这确保即使 `strategy_instances` 不可用，函数也能正常工作。

---

## Key Features / 关键特性

### 1. Per-Instance Data Isolation / 每个实例的数据隔离

- Each strategy instance has its own exchange connection
- PnL data is fetched separately for each instance
- Metrics are calculated per instance

- 每个策略实例有自己的 exchange 连接
- 为每个实例单独获取 PnL 数据
- 按实例计算指标

### 2. Status Management / 状态管理

- Strategy status reflects instance's `running` state
- `PAUSED` status is preserved (set via API)
- `LIVE` status is set when instance is running
- `STOPPED` status is set when instance is not running

- 策略状态反映实例的 `running` 状态
- 保留 `PAUSED` 状态（通过 API 设置）
- 实例运行时设置为 `LIVE` 状态
- 实例未运行时设置为 `STOPPED` 状态

### 3. Error Handling / 错误处理

- Graceful fallback if instance exchange is unavailable
- Logs errors at debug level without breaking the sync
- Continues processing other instances if one fails

- 如果实例 exchange 不可用，优雅回退
- 在调试级别记录错误，不中断同步
- 如果一个实例失败，继续处理其他实例

---

## Usage / 使用

The function is automatically called by portfolio-related API endpoints:

函数由组合相关的 API 端点自动调用：

- `GET /api/portfolio` - Before returning portfolio data
- `GET /api/portfolio/allocation` - Before returning allocation data
- `POST /api/portfolio/rebalance` - Before rebalancing

---

## Testing / 测试

To test the multi-strategy sync:

测试多策略同步：

1. Create multiple strategy instances with different types
2. Start/stop instances independently
3. Verify portfolio_manager reflects correct status and metrics for each strategy
4. Check that PnL data is correctly isolated per instance

1. 创建多个不同类型的策略实例
2. 独立启动/停止实例
3. 验证 portfolio_manager 正确反映每个策略的状态和指标
4. 检查 PnL 数据是否正确按实例隔离

---

## Future Improvements / 未来改进

1. **Per-Instance DataAgent**: Each strategy instance could have its own DataAgent for better metrics calculation
2. **Trade History Tracking**: Track trades per instance for more accurate metrics
3. **Performance Optimization**: Cache metrics to avoid repeated calculations

1. **每个实例的 DataAgent**：每个策略实例可以有自己的 DataAgent 以更好地计算指标
2. **交易历史跟踪**：按实例跟踪交易以获得更准确的指标
3. **性能优化**：缓存指标以避免重复计算

---

## Update Log / 更新日志

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2024-01 | Initial multi-strategy instance support |

