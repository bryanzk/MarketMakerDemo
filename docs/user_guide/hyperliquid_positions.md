# Hyperliquid Position and Balance Tracking Guide / Hyperliquid 仓位与余额追踪指南

## Overview / 概述

This guide explains how to track positions, balances, and PnL on Hyperliquid exchange using HyperliquidClient. All position tracking operations use the same interface as BinanceClient, ensuring seamless integration with existing trading strategies and performance tracking systems.

本指南介绍如何使用 HyperliquidClient 在 Hyperliquid 交易所上追踪仓位、余额和盈亏。所有仓位追踪操作使用与 BinanceClient 相同的接口，确保与现有交易策略和性能追踪系统无缝集成。

**Code Location / 代码位置**: 
- Position Methods: `src/trading/hyperliquid_client.py#HyperliquidClient`
- Performance Tracker: `src/trading/performance.py#PerformanceTracker`

**Prerequisites / 前置条件**: This guide assumes you have already connected to Hyperliquid (see [Hyperliquid Connection Guide](hyperliquid_connection.md)).

**前置条件**: 本指南假设您已连接到 Hyperliquid（参见 [Hyperliquid 连接指南](hyperliquid_connection.md)）。

---

## Features / 功能特性

- ✅ **Balance Tracking / 余额追踪**: Fetch total balance, available balance, and margin information
- ✅ **Position Tracking / 仓位追踪**: Track open positions with entry price, mark price, and unrealized PnL
- ✅ **PnL Calculation / 盈亏计算**: Calculate unrealized and realized PnL automatically
- ✅ **Position History / 仓位历史**: Query historical positions (both open and closed)
- ✅ **Margin Information / 保证金信息**: Monitor margin used, available margin, and margin ratio
- ✅ **Multi-Symbol Support / 多交易对支持**: Track positions across multiple trading pairs
- ✅ **Real-time Updates / 实时更新**: Refresh position data with latest market prices
- ✅ **Performance Integration / 性能集成**: Integrate with PerformanceTracker for metrics calculation

---

## Basic Usage / 基本使用

### Fetch Account Balance / 获取账户余额

Get your account balance and margin information:

获取您的账户余额和保证金信息：

```python
from src.trading.hyperliquid_client import HyperliquidClient

# Initialize client (assumes connection is already established)
# 初始化客户端（假设连接已建立）
client = HyperliquidClient()

# Fetch balance
# 获取余额
balance = client.fetch_balance()

if balance:
    print(f"Total Balance: {balance['total']} USDT")
    print(f"Available Balance: {balance['available']} USDT")
    print(f"Margin Used: {balance['margin_used']} USDT")
    print(f"Margin Available: {balance['margin_available']} USDT")
    print(f"Margin Ratio: {balance['margin_ratio']}%")
    print(f"总余额: {balance['total']} USDT")
    print(f"可用余额: {balance['available']} USDT")
    print(f"已用保证金: {balance['margin_used']} USDT")
    print(f"可用保证金: {balance['margin_available']} USDT")
    print(f"保证金比率: {balance['margin_ratio']}%")
```

**Response Format / 响应格式**:
```python
{
    "total": 10000.0,           # Total account value in USDT
    "available": 5000.0,        # Available balance in USDT
    "margin_used": 2000.0,      # Margin used for positions
    "margin_available": 5000.0, # Available margin
    "margin_ratio": 20.0,       # Margin ratio as percentage (0-100)
    "liquidation_price": 0.0    # Liquidation price (if requested)
}
```

### Fetch All Positions / 获取所有仓位

Get all open positions across all trading pairs:

获取所有交易对的所有未平仓仓位：

```python
# Fetch all positions
# 获取所有仓位
positions = client.fetch_positions()

for position in positions:
    print(f"Symbol: {position['symbol']}")
    print(f"Side: {position['side']}")  # LONG, SHORT, or NONE
    print(f"Size: {position['size']}")
    print(f"Entry Price: {position['entry_price']}")
    print(f"Mark Price: {position['mark_price']}")
    print(f"Unrealized PnL: {position['unrealized_pnl']} USDT")
    print(f"Liquidation Price: {position['liquidation_price']}")
    print("---")
```

**Response Format / 响应格式**:
```python
[
    {
        "symbol": "ETH/USDT:USDT",
        "side": "LONG",
        "size": 0.1,
        "entry_price": 3000.0,
        "mark_price": 3100.0,
        "unrealized_pnl": 10.0,
        "liquidation_price": 2500.0,
        "timestamp": 1234567890000
    }
]
```

### Fetch Position for Specific Symbol / 获取特定交易对的仓位

Get position for a specific trading pair:

获取特定交易对的仓位：

```python
# Set symbol first
# 先设置交易对
client.set_symbol("ETH/USDT:USDT")

# Fetch position for current symbol
# 获取当前交易对的仓位
position = client.fetch_position("ETH/USDT:USDT")

if position:
    print(f"Position Size: {position['size']}")
    print(f"Entry Price: {position['entry_price']}")
    print(f"Current Mark Price: {position['mark_price']}")
    print(f"Unrealized PnL: {position['unrealized_pnl']} USDT")
else:
    print("No open position for this symbol")
    print("此交易对没有未平仓仓位")
```

### Fetch Account Data / 获取账户数据

Get combined account data (balance + position):

获取组合账户数据（余额 + 仓位）：

```python
# Fetch account data (includes balance and position)
# 获取账户数据（包含余额和仓位）
account_data = client.fetch_account_data()

if account_data:
    print(f"Position Amount: {account_data['position_amt']}")
    print(f"Entry Price: {account_data['entry_price']}")
    print(f"Total Balance: {account_data['balance']} USDT")
    print(f"Available Balance: {account_data['available_balance']} USDT")
    print(f"Liquidation Price: {account_data['liquidation_price']}")
```

**Response Format / 响应格式**:
```python
{
    "position_amt": 0.1,          # Position size (positive for long, negative for short)
    "entry_price": 3000.0,        # Average entry price
    "balance": 10000.0,           # Total balance in USDT
    "available_balance": 5000.0,  # Available balance in USDT
    "liquidation_price": 2500.0   # Liquidation price
}
```

---

## Advanced Usage / 高级使用

### Fetch Position History / 获取仓位历史

Get historical positions (both open and closed):

获取历史仓位（包括未平仓和已平仓）：

```python
# Fetch position history
# 获取仓位历史
history = client.fetch_position_history(limit=100)

for position in history:
    print(f"Symbol: {position['symbol']}")
    print(f"Status: {position.get('status', 'unknown')}")  # 'open' or 'closed'
    print(f"Entry Price: {position['entry_price']}")
    if position.get('close_price'):
        print(f"Close Price: {position['close_price']}")
        print(f"Realized PnL: {position.get('realized_pnl', 0)} USDT")
    print(f"Timestamp: {position['timestamp']}")
    print("---")
```

**Parameters / 参数**:
- `limit` (optional): Maximum number of positions to return (default: 100)
- `start_time` (optional): Start timestamp in milliseconds
- `symbol` (optional): Filter by specific symbol

### Fetch Realized PnL / 获取已实现盈亏

Get total realized PnL from closed positions:

获取已平仓仓位的总已实现盈亏：

```python
# Fetch realized PnL
# 获取已实现盈亏
realized_pnl = client.fetch_realized_pnl()

print(f"Total Realized PnL: {realized_pnl} USDT")
print(f"总已实现盈亏: {realized_pnl} USDT")

# Fetch realized PnL since a specific time
# 获取自特定时间以来的已实现盈亏
from datetime import datetime, timezone
start_time = int(datetime(2025, 1, 1, tzinfo=timezone.utc).timestamp() * 1000)
realized_pnl_since = client.fetch_realized_pnl(start_time=start_time)
print(f"Realized PnL since 2025-01-01: {realized_pnl_since} USDT")
```

### Fetch Balance with Liquidation Price / 获取带清算价格的余额

Get balance information including liquidation price:

获取包含清算价格的余额信息：

```python
# Fetch balance with liquidation price
# 获取带清算价格的余额
balance = client.fetch_balance(include_liquidation_price=True)

if balance and balance.get('liquidation_price', 0) > 0:
    print(f"Liquidation Price: {balance['liquidation_price']}")
    print(f"清算价格: {balance['liquidation_price']}")
```

**Note / 注意**: Including liquidation price requires an additional API call to fetch positions, so use `include_liquidation_price=True` only when needed.

**注意**: 包含清算价格需要额外的 API 调用来获取仓位，因此仅在需要时使用 `include_liquidation_price=True`。

---

## PnL Calculation / 盈亏计算

### Unrealized PnL / 未实现盈亏

Unrealized PnL is automatically calculated and included in position data:

未实现盈亏会自动计算并包含在仓位数据中：

```python
position = client.fetch_position("ETH/USDT:USDT")

if position:
    # Unrealized PnL is already calculated
    # 未实现盈亏已经计算
    unrealized_pnl = position['unrealized_pnl']
    
    # Formula: (mark_price - entry_price) × size × side_multiplier
    # 公式: (标记价格 - 开仓价格) × 数量 × 方向乘数
    # For LONG: side_multiplier = 1
    # For SHORT: side_multiplier = -1
    print(f"Unrealized PnL: {unrealized_pnl} USDT")
```

### Realized PnL / 已实现盈亏

Realized PnL is calculated from closed positions:

已实现盈亏从已平仓仓位计算：

```python
# Fetch realized PnL
# 获取已实现盈亏
realized_pnl = client.fetch_realized_pnl()

# Realized PnL is the sum of all closed position PnL
# 已实现盈亏是所有已平仓仓位盈亏的总和
print(f"Total Realized PnL: {realized_pnl} USDT")
```

---

## Margin Information / 保证金信息

### Margin Ratio / 保证金比率

Monitor your margin ratio to manage risk:

监控您的保证金比率以管理风险：

```python
balance = client.fetch_balance()

if balance:
    margin_ratio = balance['margin_ratio']
    
    if margin_ratio > 80:
        print("⚠️ Warning: High margin ratio! Consider reducing position size.")
        print("⚠️ 警告：保证金比率过高！考虑减少仓位大小。")
    elif margin_ratio > 50:
        print("⚠️ Caution: Margin ratio is moderate.")
        print("⚠️ 注意：保证金比率适中。")
    else:
        print("✅ Margin ratio is healthy.")
        print("✅ 保证金比率健康。")
```

### Margin Available / 可用保证金

Check available margin before placing new orders:

在下新订单前检查可用保证金：

```python
balance = client.fetch_balance()

if balance:
    margin_available = balance['margin_available']
    margin_used = balance['margin_used']
    
    print(f"Margin Used: {margin_used} USDT")
    print(f"Margin Available: {margin_available} USDT")
    print(f"已用保证金: {margin_used} USDT")
    print(f"可用保证金: {margin_available} USDT")
    
    # Check if you have enough margin for a new position
    # 检查是否有足够的保证金开新仓位
    required_margin = 1000.0  # Example: 1000 USDT
    if margin_available >= required_margin:
        print("✅ Sufficient margin available")
        print("✅ 有足够的可用保证金")
    else:
        print("❌ Insufficient margin")
        print("❌ 保证金不足")
```

---

## Multi-Symbol Position Tracking / 多交易对仓位追踪

Track positions across multiple trading pairs:

追踪多个交易对的仓位：

```python
# Fetch all positions
# 获取所有仓位
positions = client.fetch_positions()

# Group positions by symbol
# 按交易对分组仓位
positions_by_symbol = {}
for position in positions:
    symbol = position['symbol']
    if symbol not in positions_by_symbol:
        positions_by_symbol[symbol] = []
    positions_by_symbol[symbol].append(position)

# Display summary
# 显示摘要
print(f"Total Open Positions: {len(positions)}")
print(f"Trading Pairs: {len(positions_by_symbol)}")
print(f"总未平仓仓位: {len(positions)}")
print(f"交易对数量: {len(positions_by_symbol)}")

for symbol, pos_list in positions_by_symbol.items():
    total_pnl = sum(p['unrealized_pnl'] for p in pos_list)
    print(f"\n{symbol}:")
    print(f"  Positions: {len(pos_list)}")
    print(f"  Total Unrealized PnL: {total_pnl} USDT")
```

---

## Position Updates / 仓位更新

Refresh position data to get latest market prices:

刷新仓位数据以获取最新市场价格：

```python
import time

# Initial position fetch
# 初始仓位获取
position1 = client.fetch_position("ETH/USDT:USDT")

if position1:
    print(f"Initial Mark Price: {position1['mark_price']}")
    print(f"Initial Unrealized PnL: {position1['unrealized_pnl']} USDT")
    
    # Wait for market to move
    # 等待市场变动
    time.sleep(5)
    
    # Refresh position
    # 刷新仓位
    position2 = client.fetch_position("ETH/USDT:USDT")
    
    if position2:
        print(f"Updated Mark Price: {position2['mark_price']}")
        print(f"Updated Unrealized PnL: {position2['unrealized_pnl']} USDT")
        
        # Check if PnL changed
        # 检查盈亏是否变化
        pnl_change = position2['unrealized_pnl'] - position1['unrealized_pnl']
        print(f"PnL Change: {pnl_change} USDT")
```

---

## Integration with PerformanceTracker / 与 PerformanceTracker 集成

Use HyperliquidClient with PerformanceTracker for automated performance tracking:

将 HyperliquidClient 与 PerformanceTracker 一起使用，实现自动化性能追踪：

```python
from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.performance import PerformanceTracker

# Initialize client and tracker
# 初始化客户端和追踪器
client = HyperliquidClient()
client.set_symbol("ETH/USDT:USDT")
tracker = PerformanceTracker()

# Fetch position and update tracker
# 获取仓位并更新追踪器
account_data = client.fetch_account_data()
if account_data:
    position_amt = account_data['position_amt']
    # Get current price from market data
    # 从市场数据获取当前价格
    market_data = client.fetch_market_data()
    current_price = market_data.get('mid_price', 0)
    
    # Update tracker with position
    # 使用仓位更新追踪器
    tracker.update_position(position_amt, current_price)

# Get performance stats
# 获取性能统计
stats = tracker.get_stats()
print(f"Realized PnL: {stats['realized_pnl']} USDT")
print(f"Total Trades: {stats['total_trades']}")
print(f"Win Rate: {stats['win_rate']}%")
print(f"已实现盈亏: {stats['realized_pnl']} USDT")
print(f"总交易数: {stats['total_trades']}")
print(f"胜率: {stats['win_rate']}%")
```

---

## Error Handling / 错误处理

### Handle Connection Errors / 处理连接错误

```python
try:
    balance = client.fetch_balance()
    if balance:
        print(f"Balance: {balance['total']} USDT")
    else:
        print("Failed to fetch balance")
        print("获取余额失败")
except ConnectionError as e:
    print(f"Connection error: {e}")
    print(f"连接错误: {e}")
    # Error message is bilingual
    # 错误消息是双语的
except Exception as e:
    print(f"Unexpected error: {e}")
    print(f"意外错误: {e}")
```

### Handle API Failures / 处理 API 失败

```python
try:
    positions = client.fetch_positions()
    if not positions:
        print("No open positions")
        print("没有未平仓仓位")
except ConnectionError as e:
    # API call failed - check network or API status
    # API 调用失败 - 检查网络或 API 状态
    error_msg = str(e)
    if "network" in error_msg.lower() or "网络" in error_msg:
        print("Network error - check your connection")
        print("网络错误 - 检查您的连接")
    else:
        print(f"API error: {e}")
        print(f"API 错误: {e}")
```

---

## Best Practices / 最佳实践

### 1. Regular Position Monitoring / 定期仓位监控

Monitor positions regularly to track performance:

定期监控仓位以追踪性能：

```python
import time
from datetime import datetime

def monitor_positions(client, interval_seconds=60):
    """Monitor positions at regular intervals"""
    """定期监控仓位"""
    while True:
        positions = client.fetch_positions()
        if positions:
            total_unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
            print(f"[{datetime.now()}] Total Unrealized PnL: {total_unrealized_pnl} USDT")
        else:
            print(f"[{datetime.now()}] No open positions")
        time.sleep(interval_seconds)

# Usage / 使用
# monitor_positions(client)
```

### 2. Risk Management / 风险管理

Check margin ratio before increasing positions:

在增加仓位前检查保证金比率：

```python
def check_margin_before_trade(client, required_margin):
    """Check if there's enough margin before placing a trade"""
    """在下单前检查是否有足够的保证金"""
    balance = client.fetch_balance()
    if not balance:
        return False, "Failed to fetch balance"
    
    margin_available = balance['margin_available']
    margin_ratio = balance['margin_ratio']
    
    if margin_ratio > 80:
        return False, "Margin ratio too high (>80%)"
    
    if margin_available < required_margin:
        return False, f"Insufficient margin. Available: {margin_available}, Required: {required_margin}"
    
    return True, "OK"

# Usage / 使用
can_trade, message = check_margin_before_trade(client, required_margin=1000.0)
if not can_trade:
    print(f"⚠️ Cannot trade: {message}")
    print(f"⚠️ 无法交易: {message}")
```

### 3. Position Summary / 仓位摘要

Create a position summary function:

创建仓位摘要函数：

```python
def get_position_summary(client):
    """Get a summary of all positions"""
    """获取所有仓位的摘要"""
    positions = client.fetch_positions()
    balance = client.fetch_balance()
    
    if not positions:
        return {
            "total_positions": 0,
            "total_unrealized_pnl": 0.0,
            "balance": balance['total'] if balance else 0.0,
        }
    
    total_unrealized_pnl = sum(p['unrealized_pnl'] for p in positions)
    total_size = sum(abs(p['size']) for p in positions)
    
    return {
        "total_positions": len(positions),
        "total_size": total_size,
        "total_unrealized_pnl": total_unrealized_pnl,
        "balance": balance['total'] if balance else 0.0,
        "margin_ratio": balance['margin_ratio'] if balance else 0.0,
    }

# Usage / 使用
summary = get_position_summary(client)
print(f"Positions: {summary['total_positions']}")
print(f"Total Unrealized PnL: {summary['total_unrealized_pnl']} USDT")
print(f"Balance: {summary['balance']} USDT")
print(f"Margin Ratio: {summary['margin_ratio']}%")
```

---

## API Reference / API 参考

### `fetch_balance(include_liquidation_price=False)`

Fetch account balance and margin information.

获取账户余额和保证金信息。

**Parameters / 参数**:
- `include_liquidation_price` (bool): Whether to include liquidation price (default: False)

**Returns / 返回**:
```python
{
    "total": float,              # Total account value in USDT
    "available": float,          # Available balance in USDT
    "margin_used": float,        # Margin used for positions
    "margin_available": float,   # Available margin
    "margin_ratio": float,       # Margin ratio as percentage (0-100)
    "liquidation_price": float   # Liquidation price (0.0 if not fetched)
}
```

### `fetch_positions()`

Fetch all open positions across all trading pairs.

获取所有交易对的所有未平仓仓位。

**Returns / 返回**: List of position dictionaries

### `fetch_position(symbol=None)`

Fetch position for a specific trading pair.

获取特定交易对的仓位。

**Parameters / 参数**:
- `symbol` (str, optional): Trading pair symbol. If None, uses client's current symbol.

**Returns / 返回**: Position dictionary or None if no position

### `fetch_account_data()`

Fetch combined account data (balance + position).

获取组合账户数据（余额 + 仓位）。

**Returns / 返回**:
```python
{
    "position_amt": float,        # Position size
    "entry_price": float,        # Average entry price
    "balance": float,            # Total balance in USDT
    "available_balance": float, # Available balance in USDT
    "liquidation_price": float   # Liquidation price
}
```

### `fetch_position_history(limit=100, start_time=None, symbol=None)`

Fetch position history (both open and closed positions).

获取仓位历史（包括未平仓和已平仓仓位）。

**Parameters / 参数**:
- `limit` (int): Maximum number of positions to return (default: 100)
- `start_time` (int, optional): Start timestamp in milliseconds
- `symbol` (str, optional): Filter by specific symbol

**Returns / 返回**: List of historical position dictionaries

### `fetch_realized_pnl(start_time=None)`

Fetch total realized PnL from closed positions.

获取已平仓仓位的总已实现盈亏。

**Parameters / 参数**:
- `start_time` (int, optional): Start timestamp in milliseconds

**Returns / 返回**: float - Total realized PnL in USDT

---

## Troubleshooting / 故障排除

### Issue: Balance returns None / 问题：余额返回 None

**Symptoms / 症状**:
- `fetch_balance()` returns None
- `fetch_balance()` 返回 None

**Solutions / 解决方案**:
1. Verify HyperliquidClient is connected: `client.is_connected`
2. Check API credentials are correct
3. Verify network connection
4. 验证 HyperliquidClient 已连接：`client.is_connected`
5. 检查 API 凭证是否正确
6. 验证网络连接

### Issue: Position data not updating / 问题：仓位数据未更新

**Symptoms / 症状**:
- Position mark price and unrealized PnL don't change
- 仓位标记价格和未实现盈亏不变化

**Solutions / 解决方案**:
1. Call `fetch_position()` again to refresh data
2. Check if market is moving (position data reflects current market prices)
3. Verify API is returning latest data
4. 再次调用 `fetch_position()` 刷新数据
5. 检查市场是否在变动（仓位数据反映当前市场价格）
6. 验证 API 返回最新数据

### Issue: Realized PnL is 0 / 问题：已实现盈亏为 0

**Symptoms / 症状**:
- `fetch_realized_pnl()` returns 0.0 even after closing positions
- `fetch_realized_pnl()` 即使在平仓后也返回 0.0

**Solutions / 解决方案**:
1. Verify positions were actually closed (check position history)
2. Check if `start_time` parameter is filtering out closed positions
3. Realized PnL is calculated from closed positions with `closedPnl` field
4. 验证仓位是否实际已平仓（检查仓位历史）
5. 检查 `start_time` 参数是否过滤掉了已平仓仓位
6. 已实现盈亏从带有 `closedPnl` 字段的已平仓仓位计算

---

## Related Documentation / 相关文档

- [Hyperliquid Trading Page Guide](./hyperliquid_trading_page.md) - Dedicated Hyperliquid trading interface
- [Hyperliquid Connection Guide](./hyperliquid_connection.md) - Setting up Hyperliquid connection
- [Hyperliquid Orders Guide](./hyperliquid_orders.md) - Order management on Hyperliquid
- [Hyperliquid LLM Evaluation Guide](./hyperliquid_llm_evaluation.md) - LLM evaluation with Hyperliquid
- [Portfolio Management Guide](./portfolio_management.md) - Portfolio-level position tracking
- [Hyperliquid 连接指南](./hyperliquid_connection.md) - 设置 Hyperliquid 连接
- [Hyperliquid 订单指南](./hyperliquid_orders.md) - Hyperliquid 订单管理
- [Hyperliquid LLM 评估指南](./hyperliquid_llm_evaluation.md) - 使用 Hyperliquid 进行 LLM 评估
- [组合管理指南](./portfolio_management.md) - 组合级别的仓位追踪

---

## Summary / 总结

The Hyperliquid Position and Balance Tracking system provides comprehensive tools for monitoring your trading positions and account status on Hyperliquid exchange. Key features include:

Hyperliquid 仓位与余额追踪系统提供了在 Hyperliquid 交易所上监控交易仓位和账户状态的全面工具。主要功能包括：

1. ✅ Real-time balance and margin monitoring
2. ✅ Multi-symbol position tracking
3. ✅ Automatic PnL calculation (unrealized and realized)
4. ✅ Position history and performance tracking
5. ✅ Integration with PerformanceTracker
6. ✅ 实时余额和保证金监控
7. ✅ 多交易对仓位追踪
8. ✅ 自动盈亏计算（未实现和已实现）
9. ✅ 仓位历史和性能追踪
10. ✅ 与 PerformanceTracker 集成

All methods use the same interface as BinanceClient, ensuring seamless integration with existing trading strategies.

所有方法使用与 BinanceClient 相同的接口，确保与现有交易策略无缝集成。

