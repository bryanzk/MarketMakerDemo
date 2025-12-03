# Exchange Abstraction Layer / 交易所抽象层

## Overview / 概述

This document describes the exchange abstraction layer architecture that enables seamless integration of multiple exchange clients (Binance, Hyperliquid) while maintaining interface consistency.

本文档描述了交易所抽象层架构，该架构支持无缝集成多个交易所客户端（Binance、Hyperliquid），同时保持接口一致性。

**Owner / 负责人**: Agent ARCH  
**Last Updated / 最后更新**: 2025-12-01  
**Related Contract / 相关契约**: `contracts/trading.json`

---

## Architecture Diagram / 架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    Exchange Abstraction Layer                 │
│                      交易所抽象层                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ BinanceClient│              │HyperliquidCl │            │
│  │              │              │     ient      │            │
│  │ (CCXT-based) │              │ (REST API)    │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                              │                     │
│         └──────────┬───────────────────┘                     │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │  ExchangeClient    │                             │
│         │  Interface         │                             │
│         │  (Common Methods)   │                             │
│         └──────────┬──────────┘                             │
│                    │                                         │
│    ┌───────────────┼───────────────┐                        │
│    │               │               │                        │
│ ┌──▼──┐      ┌────▼────┐    ┌────▼────┐                  │
│ │Order│      │Performance│    │ Strategy │                  │
│ │Mgr  │      │  Tracker  │    │ Instance │                  │
│ └─────┘      └──────────┘    └──────────┘                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Principles / 设计原则

### 1. Interface Consistency / 接口一致性

**Principle / 原则**: All exchange clients must implement the same interface (`ExchangeClient`) to ensure seamless integration with existing code.

**原则**: 所有交易所客户端必须实现相同的接口（`ExchangeClient`），以确保与现有代码的无缝集成。

**Benefits / 好处**:
- Existing code (OrderManager, PerformanceTracker) works with any exchange client
- 现有代码（OrderManager、PerformanceTracker）可与任何交易所客户端一起工作
- Easy to add new exchanges without modifying business logic
- 易于添加新交易所，无需修改业务逻辑
- Consistent error handling across exchanges
- 跨交易所的一致错误处理

### 2. Implementation Flexibility / 实现灵活性

**Principle / 原则**: Each exchange client can use different underlying libraries (CCXT, REST API, etc.) as long as the interface is maintained.

**原则**: 每个交易所客户端可以使用不同的底层库（CCXT、REST API 等），只要保持接口一致。

**Examples / 示例**:
- `BinanceClient`: Uses CCXT library
- `HyperliquidClient`: Uses direct REST API calls

### 3. Error Mapping / 错误映射

**Principle / 原则**: Exchange-specific errors must be mapped to standard exceptions with bilingual error messages.

**原则**: 交易所特定错误必须映射到标准异常，并提供双语错误消息。

**Standard Exceptions / 标准异常**:
- `AuthenticationError` - Invalid API credentials
- `InsufficientFunds` - Not enough balance
- `InvalidOrder` - Invalid order parameters
- `OrderNotFound` - Order ID not found
- `NetworkError` - Connection/network issues
- `RateLimitExceeded` - API rate limit exceeded

---

## Interface Contract / 接口契约

### ExchangeClient Interface / ExchangeClient 接口

All exchange clients must implement the `ExchangeClient` interface defined in `contracts/trading.json`.

所有交易所客户端必须实现 `contracts/trading.json` 中定义的 `ExchangeClient` 接口。

**Key Methods / 关键方法**:

#### Connection & Configuration / 连接与配置
- `__init__(api_key, api_secret, testnet)` - Initialize client
- `set_symbol(symbol)` - Update trading symbol
- `get_leverage()` - Get current leverage
- `set_leverage(leverage)` - Set leverage
- `get_max_leverage()` - Get maximum leverage
- `get_symbol_limits()` - Get trading limits

#### Market Data / 市场数据
- `fetch_market_data()` - Get order book and mid price
- `fetch_funding_rate()` - Get funding rate
- `fetch_funding_rate_for_symbol(symbol)` - Get funding rate for specific symbol
- `fetch_bulk_funding_rates(symbols)` - Get funding rates for multiple symbols
- `fetch_ticker_stats()` - Get 24h ticker statistics

#### Account & Position / 账户与仓位
- `fetch_account_data()` - Get position and balance
- `fetch_account_balance()` - Get account balance
- `fetch_position(symbol)` - Get position for symbol
- `fetch_open_orders()` - Get all open orders

#### Order Management / 订单管理
- `place_orders(orders)` - Place batch of orders
- `cancel_orders(order_ids)` - Cancel multiple orders
- `cancel_all_orders()` - Cancel all open orders

#### PnL & Fees / 盈亏与费用
- `fetch_realized_pnl(start_time)` - Get realized PnL
- `fetch_commission(start_time)` - Get trading commission
- `fetch_pnl_and_fees(start_time)` - Get both PnL and fees

---

## Implementation Guidelines / 实现指南

### For New Exchange Clients / 对于新交易所客户端

When implementing a new exchange client (e.g., `HyperliquidClient`):

实现新交易所客户端时（例如 `HyperliquidClient`）：

1. **Extend ExchangeClient Interface / 扩展 ExchangeClient 接口**
   - Implement all methods defined in `contracts/trading.json#ExchangeClient`
   - 实现 `contracts/trading.json#ExchangeClient` 中定义的所有方法
   - Follow method signatures exactly
   - 严格遵循方法签名

2. **Error Mapping / 错误映射**
   - Map exchange-specific errors to standard exceptions
   - 将交易所特定错误映射到标准异常
   - Provide bilingual error messages (Chinese and English)
   - 提供双语错误消息（中文和英文）

3. **Data Format Normalization / 数据格式规范化**
   - Convert exchange-specific data formats to internal format
   - 将交易所特定数据格式转换为内部格式
   - Ensure consistency with existing clients
   - 确保与现有客户端的一致性

4. **Configuration / 配置**
   - Add exchange credentials to `src/shared/config.py`
   - 将交易所凭证添加到 `src/shared/config.py`
   - Support testnet/mainnet switching
   - 支持测试网/主网切换

5. **Testing / 测试**
   - Unit tests with mocked API responses
   - 使用模拟 API 响应进行单元测试
   - Integration tests with testnet
   - 使用测试网进行集成测试
   - Verify interface compliance
   - 验证接口合规性

---

## Current Implementations / 当前实现

### BinanceClient

**Location / 位置**: `src/trading/exchange.py#BinanceClient`

**Implementation / 实现**:
- Uses CCXT library (`ccxt.binanceusdm`)
- 使用 CCXT 库（`ccxt.binanceusdm`）
- Supports testnet via URL override
- 通过 URL 覆盖支持测试网
- Full interface implementation
- 完整接口实现

**Status / 状态**: ✅ **Implemented / 已实现**

---

### HyperliquidClient

**Location / 位置**: `src/trading/hyperliquid_client.py#HyperliquidClient` (to be created)

**Implementation / 实现**:
- Uses direct REST API calls
- 使用直接 REST API 调用
- Supports testnet/mainnet via configuration
- 通过配置支持测试网/主网
- Must implement full ExchangeClient interface
- 必须实现完整的 ExchangeClient 接口

**Status / 状态**: 📋 **Planned / 计划中** (CORE-004)

**Contract Reference / 契约参考**: `contracts/trading.json#HyperliquidClient`

---

## Integration Points / 集成点

### OrderManager Integration / OrderManager 集成

`OrderManager` uses exchange clients to place and cancel orders:

`OrderManager` 使用交易所客户端下单和取消订单：

```python
# Works with any ExchangeClient implementation
# 适用于任何 ExchangeClient 实现
order_manager = OrderManager(exchange_client)
order_manager.place_order(...)  # Uses exchange_client.place_orders()
```

**Requirement / 要求**: Exchange clients must implement `place_orders()` and `cancel_orders()` methods.

**要求**: 交易所客户端必须实现 `place_orders()` 和 `cancel_orders()` 方法。

---

### PerformanceTracker Integration / PerformanceTracker 集成

`PerformanceTracker` uses exchange clients to fetch positions and PnL:

`PerformanceTracker` 使用交易所客户端获取仓位和盈亏：

```python
# Works with any ExchangeClient implementation
# 适用于任何 ExchangeClient 实现
tracker = PerformanceTracker(exchange_client)
tracker.get_position()  # Uses exchange_client.fetch_position()
tracker.get_pnl()       # Uses exchange_client.fetch_realized_pnl()
```

**Requirement / 要求**: Exchange clients must implement `fetch_position()`, `fetch_account_data()`, and `fetch_realized_pnl()` methods.

**要求**: 交易所客户端必须实现 `fetch_position()`、`fetch_account_data()` 和 `fetch_realized_pnl()` 方法。

---

## Error Handling Strategy / 错误处理策略

### Standard Exception Hierarchy / 标准异常层次结构

```
ExchangeError (base)
├── AuthenticationError
├── InsufficientFunds
├── InvalidOrder
├── OrderNotFound
├── NetworkError
└── RateLimitExceeded
```

### Error Message Format / 错误消息格式

All error messages must be bilingual:

所有错误消息必须是双语的：

```python
{
    "error": "Insufficient balance to place order / 余额不足，无法下单",
    "code": "INSUFFICIENT_FUNDS",
    "details": {
        "required": 100.0,
        "available": 50.0,
        "symbol": "ETH/USDT:USDT"
    }
}
```

---

## Configuration Management / 配置管理

### Environment Variables / 环境变量

Exchange credentials are loaded from environment variables:

交易所凭证从环境变量加载：

```bash
# Binance
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret

# Hyperliquid
HYPERLIQUID_API_KEY=your_key
HYPERLIQUID_API_SECRET=your_secret
HYPERLIQUID_TESTNET=true  # or false for mainnet
```

### Configuration File / 配置文件

Configuration is managed in `src/shared/config.py`:

配置在 `src/shared/config.py` 中管理：

```python
# Binance
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Hyperliquid
HYPERLIQUID_API_KEY = os.getenv("HYPERLIQUID_API_KEY")
HYPERLIQUID_API_SECRET = os.getenv("HYPERLIQUID_API_SECRET")
HYPERLIQUID_TESTNET = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"
```

---

## Testing Strategy / 测试策略

### Unit Tests / 单元测试

- Mock exchange API responses
- 模拟交易所 API 响应
- Test all interface methods
- 测试所有接口方法
- Verify error mapping
- 验证错误映射

**Location / 位置**: `tests/unit/trading/test_*_client.py`

### Integration Tests / 集成测试

- Test with exchange testnet
- 使用交易所测试网进行测试
- Verify real API interactions
- 验证真实 API 交互
- Test error scenarios
- 测试错误场景

**Location / 位置**: `tests/integration/test_*_integration.py`

---

## Future Enhancements / 未来增强

### Potential Additions / 潜在添加

1. **Exchange Factory / 交易所工厂**
   - Factory pattern for creating exchange clients
   - 用于创建交易所客户端的工厂模式
   - Runtime exchange selection
   - 运行时交易所选择

2. **Connection Pooling / 连接池**
   - Reuse connections for better performance
   - 重用连接以提高性能

3. **Rate Limiting / 速率限制**
   - Centralized rate limiting across exchanges
   - 跨交易所的集中速率限制

4. **Health Monitoring / 健康监控**
   - Monitor connection health and API latency
   - 监控连接健康和 API 延迟

---

## Related Documents / 相关文档

- **Interface Contract / 接口契约**: `contracts/trading.json`
- **Specification / 规格说明**: `docs/specs/trading/CORE-004.md`
- **User Stories / 用户故事**:
  - `docs/stories/trading/US-CORE-004-A.md` (Connection)
  - `docs/stories/trading/US-CORE-004-B.md` (Orders)
  - `docs/stories/trading/US-CORE-004-C.md` (Positions)

---

## Owner / 负责人

**Agent**: Agent ARCH  
**Last Updated / 最后更新**: 2025-12-01

