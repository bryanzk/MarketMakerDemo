# Hyperliquid Order Management Guide / Hyperliquid 订单管理指南

## Overview / 概述

This guide explains how to place, cancel, and query orders on Hyperliquid exchange using HyperliquidClient. All order management operations use the same interface as BinanceClient, ensuring seamless integration with existing trading strategies.

本指南介绍如何使用 HyperliquidClient 在 Hyperliquid 交易所上下单、取消和查询订单。所有订单管理操作使用与 BinanceClient 相同的接口，确保与现有交易策略无缝集成。

**Code Location / 代码位置**: `src/trading/hyperliquid_client.py#HyperliquidClient`

**Prerequisites / 前置条件**: This guide assumes you have already connected to Hyperliquid (see [Hyperliquid Connection Guide](hyperliquid_connection.md)).

**前置条件**: 本指南假设您已连接到 Hyperliquid（参见 [Hyperliquid 连接指南](hyperliquid_connection.md)）。

---

## Features / 功能特性

- ✅ **Limit Orders / 限价单**: Place buy/sell orders at specific prices
- ✅ **Market Orders / 市价单**: Execute orders immediately at market price
- ✅ **Order Cancellation / 订单取消**: Cancel individual or all open orders
- ✅ **Order Query / 订单查询**: Query order status, open orders, and order history
- ✅ **Error Handling / 错误处理**: Bilingual error messages with clear failure reasons
- ✅ **Order Idempotency / 订单幂等性**: Safe to retry order placement
- ✅ **Batch Operations / 批量操作**: Place or cancel multiple orders in one call

---

## Basic Usage / 基本使用

### Place Limit Order / 下限价单

Place a limit order at a specific price:

在指定价格下限价单：

```python
from src.trading.hyperliquid_client import HyperliquidClient

# Initialize client (assumes connection is already established)
# 初始化客户端（假设连接已建立）
client = HyperliquidClient()

# Place a limit buy order
# 下限价买单
orders = [
    {
        "side": "buy",
        "price": 3000.0,
        "quantity": 0.01,
        "type": "limit"
    }
]

placed_orders = client.place_orders(orders)

# Check result
# 检查结果
if placed_orders:
    print(f"Order placed: {placed_orders[0]['id']}")
    print(f"订单已下单：{placed_orders[0]['id']}")
```

### Place Market Order / 下市价单

Place a market order for immediate execution:

下市价单以立即执行：

```python
# Place a market sell order
# 下市价卖单
orders = [
    {
        "side": "sell",
        "quantity": 0.01,
        "type": "market"  # No price needed for market orders
    }
]

placed_orders = client.place_orders(orders)
```

### Cancel Order / 取消订单

Cancel a specific order by order ID:

通过订单 ID 取消特定订单：

```python
# Cancel a single order
# 取消单个订单
order_id = "12345"
client.cancel_orders([order_id])

print("Order cancelled successfully")
print("订单已成功取消")
```

### Cancel All Orders / 取消所有订单

Cancel all open orders at once:

一次性取消所有未成交订单：

```python
# Cancel all open orders
# 取消所有未成交订单
client.cancel_all_orders()

print("All orders cancelled")
print("所有订单已取消")
```

### Query Open Orders / 查询未成交订单

Get a list of all open orders:

获取所有未成交订单列表：

```python
# Fetch all open orders
# 获取所有未成交订单
open_orders = client.fetch_open_orders()

print(f"Open orders: {len(open_orders)}")
print(f"未成交订单：{len(open_orders)}")

for order in open_orders:
    print(f"Order ID: {order['id']}, Side: {order['side']}, Price: {order['price']}")
    print(f"订单 ID：{order['id']}，方向：{order['side']}，价格：{order['price']}")
```

---

## API Reference / API 参考

### `place_orders(orders: List[Dict]) -> List[Dict]`

Places a batch of orders on Hyperliquid.

在 Hyperliquid 上批量下单。

**Parameters / 参数**:
- `orders`: List of order dictionaries. Each order must contain:
  - `side`: `"buy"` or `"sell"` (required)
  - `quantity`: `float` (required) - Order quantity
  - `price`: `float` (required for limit orders) - Order price
  - `type`: `"limit"` or `"market"` (optional, default: `"limit"`)

**Returns / 返回**:
- List of created order dictionaries, each containing:
  - `id`: Order ID
  - `side`: Order side
  - `price`: Order price
  - `quantity`: Order quantity
  - `status`: Order status

**Example / 示例**:
```python
orders = [
    {"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"},
    {"side": "sell", "price": 3010.0, "quantity": 0.01, "type": "limit"}
]
placed = client.place_orders(orders)
```

### `cancel_orders(order_ids: List[str]) -> None`

Cancels one or more orders by their IDs.

通过订单 ID 取消一个或多个订单。

**Parameters / 参数**:
- `order_ids`: List of order ID strings to cancel

**Returns / 返回**:
- `None`

**Example / 示例**:
```python
client.cancel_orders(["order_123", "order_456"])
```

### `cancel_all_orders() -> None`

Cancels all open orders for the current symbol.

取消当前交易对的所有未成交订单。

**Returns / 返回**:
- `None`

**Example / 示例**:
```python
client.cancel_all_orders()
```

### `fetch_open_orders() -> List[Dict]`

Fetches all open orders for the current symbol.

获取当前交易对的所有未成交订单。

**Returns / 返回**:
- List of order dictionaries, each containing:
  - `id`: Order ID
  - `side`: `"buy"` or `"sell"`
  - `price`: Order price
  - `quantity`: Order quantity
  - `filled_quantity`: Filled quantity (if partially filled)
  - `status`: Order status

**Example / 示例**:
```python
open_orders = client.fetch_open_orders()
for order in open_orders:
    print(f"Order {order['id']}: {order['side']} {order['quantity']} @ {order['price']}")
```

---

## Order Types / 订单类型

### Limit Order / 限价单

A limit order is executed only at the specified price or better.

限价单仅在指定价格或更优价格执行。

**When to use / 何时使用**:
- You want to control the execution price
- 您想控制执行价格
- You're willing to wait for the price to reach your target
- 您愿意等待价格达到目标

**Example / 示例**:
```python
limit_order = {
    "side": "buy",
    "price": 3000.0,  # Required for limit orders
    "quantity": 0.01,
    "type": "limit"
}
```

### Market Order / 市价单

A market order is executed immediately at the current market price.

市价单立即以当前市场价格执行。

**When to use / 何时使用**:
- You need immediate execution
- 您需要立即执行
- Price is less important than speed
- 速度比价格更重要

**Example / 示例**:
```python
market_order = {
    "side": "sell",
    "quantity": 0.01,
    "type": "market"  # No price needed
}
```

---

## Error Handling / 错误处理

### Insufficient Balance / 余额不足

If you don't have enough balance to place an order:

如果您没有足够的余额下单：

```python
from src.trading.hyperliquid_client import InsufficientBalanceError

try:
    orders = [{"side": "buy", "price": 3000.0, "quantity": 1000.0, "type": "limit"}]
    placed = client.place_orders(orders)
except InsufficientBalanceError as e:
    print(f"Insufficient balance: {e.message}")
    print(f"余额不足：{e.message}")
```

**Error Message / 错误消息**:
```
Insufficient balance to place order. Please check your account balance.
余额不足，无法下单。请检查您的账户余额。
```

### Invalid Order / 无效订单

If order parameters are invalid:

如果订单参数无效：

```python
from src.trading.hyperliquid_client import InvalidOrderError

try:
    # Invalid: negative price
    # 无效：负价格
    orders = [{"side": "buy", "price": -100.0, "quantity": 0.01, "type": "limit"}]
    placed = client.place_orders(orders)
except InvalidOrderError as e:
    print(f"Invalid order: {e.message}")
    print(f"无效订单：{e.message}")
```

### Order Not Found / 订单未找到

If you try to cancel a non-existent order:

如果您尝试取消不存在的订单：

```python
# Order ID doesn't exist
# 订单 ID 不存在
try:
    client.cancel_orders(["non_existent_order_id"])
except Exception as e:
    print(f"Error: {e}")
    print(f"错误：{e}")
```

### Check Last Error / 检查最后错误

You can check the last order error without exception handling:

您可以在不处理异常的情况下检查最后的订单错误：

```python
orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
placed = client.place_orders(orders)

if not placed and client.last_order_error:
    error = client.last_order_error
    print(f"Error type: {error['type']}")
    print(f"Error message: {error['message']}")
    print(f"错误类型：{error['type']}")
    print(f"错误消息：{error['message']}")
```

---

## Integration Examples / 集成示例

### With OrderManager / 与 OrderManager 集成

HyperliquidClient works seamlessly with OrderManager:

HyperliquidClient 与 OrderManager 无缝协作：

```python
from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.order_manager import OrderManager

# Create client and order manager
# 创建客户端和订单管理器
client = HyperliquidClient()
order_manager = OrderManager()

# Fetch current orders
# 获取当前订单
current_orders = client.fetch_open_orders()

# Define target orders
# 定义目标订单
target_orders = [
    {"side": "buy", "price": 3000.0, "quantity": 0.01},
    {"side": "sell", "price": 3010.0, "quantity": 0.01},
]

# Sync orders (determine what to cancel and place)
# 同步订单（确定要取消和下单的内容）
to_cancel, to_place = order_manager.sync_orders(current_orders, target_orders)

# Execute changes
# 执行更改
if to_cancel:
    client.cancel_orders(to_cancel)
if to_place:
    client.place_orders(to_place)
```

### With StrategyInstance / 与 StrategyInstance 集成

HyperliquidClient can be used in StrategyInstance (future enhancement):

HyperliquidClient 可以在 StrategyInstance 中使用（未来增强）：

```python
from src.trading.strategy_instance import StrategyInstance
from src.trading.hyperliquid_client import HyperliquidClient

# Create strategy instance
# 创建策略实例
instance = StrategyInstance("my_strategy", "fixed_spread")

# Note: Currently StrategyInstance uses BinanceClient by default
# 注意：目前 StrategyInstance 默认使用 BinanceClient
# Future enhancement will support exchange selection
# 未来增强将支持交易所选择

# Use instance's order sync method
# 使用实例的订单同步方法
current_orders = []
target_orders = [
    {"side": "buy", "price": 3000.0, "quantity": 0.01},
]

to_cancel, to_place = instance.sync_orders(current_orders, target_orders)
```

---

## Best Practices / 最佳实践

### 1. Always Check Order Status / 始终检查订单状态

After placing orders, verify they were placed correctly:

下单后，验证订单是否正确下单：

```python
# Place orders
# 下单
placed_orders = client.place_orders(orders)

# Verify placement
# 验证下单
if placed_orders:
    print(f"Successfully placed {len(placed_orders)} orders")
    print(f"成功下单 {len(placed_orders)} 个订单")
    
    # Query open orders to confirm
    # 查询未成交订单以确认
    open_orders = client.fetch_open_orders()
    placed_ids = {o['id'] for o in placed_orders}
    open_ids = {o['id'] for o in open_orders}
    
    if placed_ids.issubset(open_ids):
        print("All orders confirmed in open orders list")
        print("所有订单已在未成交订单列表中确认")
else:
    print("No orders were placed. Check last_order_error for details.")
    print("未下单。检查 last_order_error 了解详情。")
```

### 2. Handle Errors Gracefully / 优雅处理错误

Always wrap order operations in try-except blocks:

始终在 try-except 块中包装订单操作：

```python
try:
    orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
    placed = client.place_orders(orders)
    
    if not placed:
        # Check for errors
        # 检查错误
        if client.last_order_error:
            error = client.last_order_error
            logger.error(f"Order placement failed: {error['message']}")
            logger.error(f"订单下单失败：{error['message']}")
            
except InsufficientBalanceError as e:
    logger.error(f"Insufficient balance: {e.message}")
    logger.error(f"余额不足：{e.message}")
except InvalidOrderError as e:
    logger.error(f"Invalid order: {e.message}")
    logger.error(f"无效订单：{e.message}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    logger.error(f"意外错误：{e}")
```

### 3. Use Batch Operations / 使用批量操作

Place or cancel multiple orders in one call for efficiency:

为效率起见，在一次调用中下单或取消多个订单：

```python
# Batch place orders
# 批量下单
orders = [
    {"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"},
    {"side": "sell", "price": 3010.0, "quantity": 0.01, "type": "limit"},
]
placed = client.place_orders(orders)  # Single API call / 单次 API 调用

# Batch cancel orders
# 批量取消订单
order_ids = ["order1", "order2", "order3"]
client.cancel_orders(order_ids)  # Single API call / 单次 API 调用
```

### 4. Monitor Order Status / 监控订单状态

Regularly check open orders to ensure they're still active:

定期检查未成交订单以确保它们仍然有效：

```python
import time

# Place order
# 下单
orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
placed = client.place_orders(orders)

if placed:
    order_id = placed[0]['id']
    
    # Monitor order status
    # 监控订单状态
    while True:
        open_orders = client.fetch_open_orders()
        order = next((o for o in open_orders if o['id'] == order_id), None)
        
        if order:
            print(f"Order {order_id} still open")
            print(f"订单 {order_id} 仍然未成交")
        else:
            print(f"Order {order_id} filled or cancelled")
            print(f"订单 {order_id} 已成交或已取消")
            break
        
        time.sleep(5)  # Check every 5 seconds / 每 5 秒检查一次
```

### 5. Order Idempotency / 订单幂等性

It's safe to retry order placement if you're unsure if it succeeded:

如果您不确定订单是否成功，可以安全地重试下单：

```python
def place_order_safely(client, order, max_retries=3):
    """Safely place order with retry logic / 使用重试逻辑安全下单"""
    for attempt in range(max_retries):
        try:
            placed = client.place_orders([order])
            if placed:
                return placed[0]
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)  # Wait before retry / 重试前等待
                continue
            else:
                raise
    return None

# Use it
# 使用它
order = {"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}
result = place_order_safely(client, order)
```

---

## Troubleshooting / 故障排除

### Issue: Orders Not Placed / 问题：订单未下单

**Symptoms / 症状**:
- `place_orders()` returns empty list
- `place_orders()` 返回空列表
- No error raised
- 未抛出错误

**Solutions / 解决方案**:
1. Check `last_order_error`:
   检查 `last_order_error`：
   ```python
   placed = client.place_orders(orders)
   if not placed and client.last_order_error:
       print(client.last_order_error['message'])
   ```

2. Verify order parameters:
   验证订单参数：
   ```python
   # Ensure all required fields are present
   # 确保所有必需字段都存在
   assert "side" in order
   assert "quantity" in order
   if order.get("type", "limit") == "limit":
       assert "price" in order
   ```

3. Check connection status:
   检查连接状态：
   ```python
   if not client.is_connected:
       raise RuntimeError("Not connected to Hyperliquid")
       # 未连接到 Hyperliquid
   ```

### Issue: Cannot Cancel Order / 问题：无法取消订单

**Symptoms / 症状**:
- Order cancellation fails silently
- 订单取消静默失败
- Order still appears in open orders
- 订单仍出现在未成交订单中

**Solutions / 解决方案**:
1. Verify order ID is correct:
   验证订单 ID 是否正确：
   ```python
   open_orders = client.fetch_open_orders()
   order_ids = [o['id'] for o in open_orders]
   
   if order_id not in order_ids:
       print(f"Order {order_id} not found in open orders")
       print(f"订单 {order_id} 在未成交订单中未找到")
   ```

2. Check if order was already filled:
   检查订单是否已成交：
   ```python
   # If order is not in open_orders, it may have been filled
   # 如果订单不在 open_orders 中，它可能已成交
   open_orders = client.fetch_open_orders()
   if order_id not in [o['id'] for o in open_orders]:
       print("Order may have been filled")
       print("订单可能已成交")
   ```

### Issue: Orders Execute at Wrong Price / 问题：订单以错误价格执行

**Symptoms / 症状**:
- Limit order executes at different price than specified
- 限价单以与指定价格不同的价格执行

**Solutions / 解决方案**:
1. Verify you're using limit orders:
   验证您使用的是限价单：
   ```python
   order = {
       "side": "buy",
       "price": 3000.0,  # Must specify price for limit orders
       "quantity": 0.01,
       "type": "limit"  # Explicitly set type
   }
   ```

2. Check market conditions:
   检查市场条件：
   - Limit orders execute at your price or better
   - 限价单在您的价格或更优价格执行
   - If market moves quickly, execution price may differ
   - 如果市场快速移动，执行价格可能不同

---

## Related Documentation / 相关文档

- **Connection Guide / 连接指南**: [Hyperliquid Connection Guide](hyperliquid_connection.md)
- **Specification / 规范**: `docs/specs/trading/CORE-004.md`
- **User Story / 用户故事**: `docs/stories/trading/US-CORE-004-B.md`
- **Interface Contract / 接口契约**: `contracts/trading.json#HyperliquidClient`
- **Unit Tests / 单元测试**: `tests/unit/trading/test_hyperliquid_orders.py`
- **Integration Tests / 集成测试**: `tests/integration/test_hyperliquid_orders_integration.py`
- **Smoke Tests / 冒烟测试**: `tests/smoke/test_hyperliquid_orders.py`

---

## Support / 支持

For issues or questions, please refer to:
如有问题或疑问，请参考：

- Project Issues: GitHub Issues
- Documentation: `docs/` directory
- Code: `src/trading/hyperliquid_client.py`

---

**Last Updated / 最后更新**: 2025-12-01  
**Owner / 负责人**: Agent QA  
**Feature / 功能**: US-CORE-004-B

