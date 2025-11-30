# Architecture Change: Per-Instance Exchange Connections / 架构变更：每个实例独立的交易所连接

## Overview / 概述

This document describes the architectural change where each strategy instance now maintains its own exchange connection, ensuring complete isolation between strategies.

本文档描述了架构变更：每个策略实例现在维护自己的交易所连接，确保策略之间的完全隔离。

---

## Change Summary / 变更摘要

### Before / 之前

- **Shared Exchange**: All strategy instances shared a single `BinanceClient` connection at the `AlphaLoop` level
- **共享交易所**：所有策略实例在 `AlphaLoop` 级别共享一个 `BinanceClient` 连接

```python
class AlphaLoop:
    def __init__(self):
        self.exchange = BinanceClient()  # Shared by all strategies
        self.strategy_instances = {...}
```

### After / 之后

- **Per-Instance Exchange**: Each `StrategyInstance` has its own `BinanceClient` connection
- **每个实例独立的交易所**：每个 `StrategyInstance` 都有自己的 `BinanceClient` 连接

```python
class StrategyInstance:
    def __init__(self, strategy_id, strategy_type, symbol=None):
        self.exchange = BinanceClient()  # Own connection
        self.symbol = symbol or SYMBOL
        # ... other instance-specific state
```

---

## Benefits / 优势

### 1. Complete Isolation / 完全隔离

- **Independent Connections**: Each strategy can have different API credentials if needed
- **独立连接**：如果需要，每个策略可以使用不同的 API 凭证

- **Separate Error Handling**: Errors in one strategy's exchange don't affect others
- **独立错误处理**：一个策略的交易所错误不影响其他策略

- **Independent Rate Limits**: Each connection has its own rate limit tracking
- **独立频率限制**：每个连接有自己的频率限制跟踪

### 2. Per-Strategy Symbol Support / 每个策略支持不同交易对

- Each strategy instance can trade different symbols
- 每个策略实例可以交易不同的交易对

```python
# Strategy 1 trades ETH/USDT
instance1 = StrategyInstance("strategy_1", "fixed_spread", symbol="ETH/USDT:USDT")

# Strategy 2 trades BTC/USDT
instance2 = StrategyInstance("strategy_2", "funding_rate", symbol="BTC/USDT:USDT")
```

### 3. Independent Data Refresh / 独立数据刷新

- Each strategy instance refreshes its own market data
- 每个策略实例刷新自己的市场数据

- No shared cache conflicts
- 没有共享缓存冲突

- Strategies can operate on different timeframes
- 策略可以在不同的时间框架下运行

### 4. Better Resource Management / 更好的资源管理

- Failed connections in one strategy don't affect others
- 一个策略的连接失败不影响其他策略

- Can selectively enable/disable strategies
- 可以选择性地启用/禁用策略

---

## Implementation Details / 实现细节

### StrategyInstance Changes / StrategyInstance 变更

```python
class StrategyInstance:
    def __init__(self, strategy_id: str, strategy_type: str = "fixed_spread", symbol: str = None):
        # ... strategy initialization ...
        
        # Independent exchange connection
        self.exchange = None
        self.use_real_exchange = False
        try:
            self.exchange = BinanceClient()
            if self.symbol != SYMBOL:
                self.exchange.set_symbol(self.symbol)
            self.use_real_exchange = True
        except Exception as e:
            logger.error(f"Strategy instance '{strategy_id}' failed to connect: {e}")
            self.use_real_exchange = False
        
        # Instance-specific data cache
        self.latest_market_data = None
        self.latest_funding_rate = 0.0
        self.latest_account_data = None
    
    def refresh_data(self):
        """Refresh data using this instance's exchange."""
        if not self.use_real_exchange or not self.exchange:
            return False
        # ... fetch and cache data ...
    
    def set_symbol(self, symbol: str):
        """Update symbol for this instance's exchange."""
        if self.exchange:
            return self.exchange.set_symbol(symbol)
        return False
```

### AlphaLoop Changes / AlphaLoop 变更

```python
class AlphaLoop:
    def __init__(self):
        # No shared exchange anymore
        # 不再有共享的交易所
        self.strategy_instances = {}
        # ... other initialization ...
    
    def _run_strategy_instance_cycle(self, instance: StrategyInstance):
        """Run cycle using instance's own exchange."""
        # Each instance refreshes its own data
        if not instance.refresh_data():
            instance.alert = {...}
            return
        
        # Use instance's cached data
        market_data = instance.latest_market_data
        funding_rate = instance.latest_funding_rate
        
        # Use instance's exchange for orders
        all_orders = instance.exchange.fetch_open_orders()
        # ... rest of cycle logic ...
```

---

## Migration Guide / 迁移指南

### For Existing Code / 对于现有代码

If you have code that accesses `engine.exchange`:

如果你有访问 `engine.exchange` 的代码：

**Before / 之前**:
```python
engine = AlphaLoop()
engine.exchange.set_symbol("BTC/USDT:USDT")
```

**After / 之后**:
```python
engine = AlphaLoop()
# Access default instance
default_instance = engine.strategy_instances["default"]
default_instance.set_symbol("BTC/USDT:USDT")

# Or use helper method
engine.set_symbol("BTC/USDT:USDT", strategy_id="default")
```

### For New Code / 对于新代码

Always access exchange through strategy instances:

始终通过策略实例访问交易所：

```python
# Get instance
instance = engine.strategy_instances["strategy_id"]

# Access exchange
instance.exchange.fetch_market_data()
instance.exchange.place_orders(orders)

# Or use instance methods
instance.refresh_data()
instance.set_symbol("BTC/USDT:USDT")
```

---

## API Changes / API 变更

### Removed / 已移除

- `AlphaLoop.exchange` - No longer exists
- `AlphaLoop.use_real_exchange` - No longer exists
- `AlphaLoop.refresh_data()` - Moved to `StrategyInstance.refresh_data()`
- `AlphaLoop.latest_market_data` - Moved to `StrategyInstance.latest_market_data`
- `AlphaLoop.latest_funding_rate` - Moved to `StrategyInstance.latest_funding_rate`
- `AlphaLoop.latest_account_data` - Moved to `StrategyInstance.latest_account_data`

### Added / 新增

- `StrategyInstance.exchange` - Instance's own exchange connection
- `StrategyInstance.use_real_exchange` - Instance's exchange status
- `StrategyInstance.refresh_data()` - Refresh data for this instance
- `StrategyInstance.set_symbol(symbol)` - Set symbol for this instance
- `StrategyInstance.latest_market_data` - Instance's cached market data
- `StrategyInstance.latest_funding_rate` - Instance's cached funding rate
- `StrategyInstance.latest_account_data` - Instance's cached account data

### Modified / 已修改

- `AlphaLoop.set_symbol(symbol, strategy_id)` - Now requires strategy_id parameter
- `AlphaLoop.get_status()` - Returns aggregated data from all instances
- `AlphaLoop._run_strategy_instance_cycle(instance)` - No longer takes market_data/funding_rate parameters

---

## Testing / 测试

All existing tests have been updated to work with the new architecture:

所有现有测试已更新以适配新架构：

- Tests now mock `src.trading.strategy_instance.BinanceClient` instead of `src.trading.engine.BinanceClient`
- 测试现在 mock `src.trading.strategy_instance.BinanceClient` 而不是 `src.trading.engine.BinanceClient`

- Each test verifies instance-specific behavior
- 每个测试验证实例特定的行为

**Test Results**: ✅ All 17 tests passing
**测试结果**：✅ 所有 17 个测试通过

---

## Performance Considerations / 性能考虑

### Connection Overhead / 连接开销

- **Multiple Connections**: Each strategy instance creates its own connection
- **多个连接**：每个策略实例创建自己的连接

- **Impact**: Minimal - CCXT connections are lightweight
- **影响**：最小 - CCXT 连接是轻量级的

- **Benefit**: Better isolation and fault tolerance
- **优势**：更好的隔离和容错能力

### Rate Limits / 频率限制

- Each connection has independent rate limit tracking
- 每个连接有独立的频率限制跟踪

- Strategies can operate at different frequencies
- 策略可以以不同的频率运行

- No shared rate limit conflicts
- 没有共享频率限制冲突

---

## Best Practices / 最佳实践

### 1. Symbol Management / 交易对管理

```python
# Create instances with different symbols
engine.add_strategy_instance("eth_strategy", "fixed_spread")
engine.set_symbol("ETH/USDT:USDT", "eth_strategy")

engine.add_strategy_instance("btc_strategy", "funding_rate")
engine.set_symbol("BTC/USDT:USDT", "btc_strategy")
```

### 2. Error Handling / 错误处理

```python
# Check each instance's exchange status
for strategy_id, instance in engine.strategy_instances.items():
    if not instance.use_real_exchange:
        logger.warning(f"Strategy '{strategy_id}' is in simulation mode")
    
    if instance.alert:
        logger.error(f"Strategy '{strategy_id}' alert: {instance.alert}")
```

### 3. Resource Cleanup / 资源清理

```python
# When removing a strategy, its exchange connection is automatically cleaned up
engine.remove_strategy_instance("strategy_id")
# The instance's exchange connection is no longer used
```

---

## Related Documentation / 相关文档

- [Architecture](./architecture.md) - Overall system architecture
- [Multi-Strategy Guide](./user_guide/multi_llm_evaluation.md) - Multi-strategy usage
- [Error Handling Guide](./user_guide/error_handling.md) - Error handling with per-instance exchanges

---

## Changelog / 变更日志

**Date**: 2025-11-26
**Version**: Architecture v2.0

### Changes / 变更

1. ✅ Moved exchange connection from `AlphaLoop` to `StrategyInstance`
2. ✅ Added `refresh_data()` method to `StrategyInstance`
3. ✅ Added `set_symbol()` method to `StrategyInstance`
4. ✅ Updated `_run_strategy_instance_cycle()` to use instance's exchange
5. ✅ Updated all tests to mock `StrategyInstance` exchange
6. ✅ Updated `get_status()` to aggregate from instances
7. ✅ Removed shared exchange and data cache from `AlphaLoop`

### Breaking Changes / 破坏性变更

- `AlphaLoop.exchange` - **REMOVED** - Use `instance.exchange` instead
- `AlphaLoop.refresh_data()` - **REMOVED** - Use `instance.refresh_data()` instead
- `AlphaLoop.set_symbol(symbol)` - **MODIFIED** - Now requires `strategy_id` parameter

