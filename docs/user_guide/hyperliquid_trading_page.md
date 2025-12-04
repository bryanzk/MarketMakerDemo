# Hyperliquid Trading Page Guide / Hyperliquid 交易页面指南

## Overview / 概述

This guide explains how to use the dedicated Hyperliquid Trading Page, a focused interface for all Hyperliquid trading activities including strategy control, LLM evaluation, position tracking, and order management. The page provides a seamless trading experience specifically designed for Hyperliquid exchange.

本指南介绍如何使用专用 Hyperliquid 交易页面，这是一个专注于所有 Hyperliquid 交易活动的界面，包括策略控制、LLM 评估、仓位追踪和订单管理。该页面为 Hyperliquid 交易所提供无缝的交易体验。

**Code Location / 代码位置**: 
- Page Template: `templates/HyperliquidTrade.html`
- API Routes: `server.py#hyperliquid_trade_page`, `/api/hyperliquid/*`
- Exchange Client: `src/trading/hyperliquid_client.py#HyperliquidClient`

**Prerequisites / 前置条件**: 
- Hyperliquid connection must be established (see [Hyperliquid Connection Guide](./hyperliquid_connection.md))
- Hyperliquid 连接必须已建立（参见 [Hyperliquid 连接指南](./hyperliquid_connection.md)）

---

## Features / 功能特性

- ✅ **Dedicated Interface / 专用界面**: Focused trading page exclusively for Hyperliquid
- ✅ **Strategy Control / 策略控制**: Configure Fixed Spread Strategy parameters (spread, quantity, leverage)
- ✅ **Position Tracking / 仓位追踪**: Real-time position and balance display
- ✅ **LLM Evaluation / LLM 评估**: Multi-LLM evaluation with Hyperliquid context
- ✅ **Order Management / 订单管理**: View and manage Hyperliquid orders
- ✅ **Real-time Updates / 实时更新**: Automatic data refresh without page reload
- ✅ **Bilingual Support / 双语支持**: All text in English and Chinese
- ✅ **Error Handling / 错误处理**: Clear error messages when connection fails

---

## Accessing the Page / 访问页面

### From Main Dashboard / 从主仪表盘

1. Navigate to the main dashboard at `http://localhost:8000/`
2. Click the **"⚡ Hyperliquid Trading"** button in the header
3. You will be redirected to `/hyperliquid`

1. 导航到主仪表盘 `http://localhost:8000/`
2. 点击标题中的 **"⚡ Hyperliquid Trading"** 按钮
3. 您将被重定向到 `/hyperliquid`

### Direct URL / 直接 URL

Access the page directly at:
直接访问页面：

```
http://localhost:8000/hyperliquid
```

### From LLM Trade Lab / 从 LLM 交易实验室

1. Navigate to `/evaluation` (LLM Trade Lab)
2. Click the **"⚡ Hyperliquid Trading"** link in the header
3. You will be redirected to `/hyperliquid`

1. 导航到 `/evaluation`（LLM 交易实验室）
2. 点击标题中的 **"⚡ Hyperliquid Trading"** 链接
3. 您将被重定向到 `/hyperliquid`

---

## Page Sections / 页面部分

### 1. Connection Status Panel / 连接状态面板

**Location / 位置**: Top of the page / 页面顶部

**Displays / 显示**:
- Exchange name: **Hyperliquid**
- Connection status (Connected / Disconnected)
- Current trading pair
- Connection error messages (if any)

**交易所名称**: **Hyperliquid**
- 连接状态（已连接 / 未连接）
- 当前交易对
- 连接错误消息（如果有）

**Usage / 使用**:
- Automatically checks connection status on page load
- Updates in real-time when connection changes
- Shows error messages if Hyperliquid is not connected

- 页面加载时自动检查连接状态
- 连接变化时实时更新
- 如果 Hyperliquid 未连接，显示错误消息

### 2. Position and Balance Panel / 仓位与余额面板

**Location / 位置**: Below connection status / 连接状态下方

**Displays / 显示**:
- **Total Balance / 总余额**: Total account value in USDT
- **Available Balance / 可用余额**: Available balance for trading
- **Position Amount / 仓位数量**: Current position size
- **Unrealized PnL / 未实现盈亏**: Unrealized profit/loss
- **Open Positions Table / 未平仓仓位表**: Table showing all open positions with:
  - Symbol / 交易对
  - Side / 方向 (LONG/SHORT)
  - Size / 数量
  - Entry Price / 入场价
  - Mark Price / 标记价
  - PnL / 盈亏

**Refresh Button / 刷新按钮**: Click **"🔄 Refresh"** to manually refresh position data

**刷新按钮**: 点击 **"🔄 Refresh"** 手动刷新仓位数据

**Usage / 使用**:
```javascript
// Position data is automatically refreshed every 30 seconds
// 仓位数据每 30 秒自动刷新
// Click "Refresh" button for manual refresh
// 点击"Refresh"按钮进行手动刷新
```

### 3. Strategy Control Panel / 策略控制面板

**Location / 位置**: Below position panel / 仓位面板下方

**Controls / 控件**:

#### Trading Pair Selection / 交易对选择
- **Dropdown / 下拉菜单**: Select from available Hyperliquid trading pairs
  - ETH/USDT:USDT
  - BTC/USDT:USDT
  - SOL/USDT:USDT
- **Switch Button / 切换按钮**: Click to switch to selected trading pair

#### Strategy Parameters / 策略参数

**Fixed Spread Strategy Parameters / 固定价差策略参数**:

| Parameter / 参数 | Description / 描述 | Range / 范围 | Default / 默认值 |
|----------------|------------------|-------------|----------------|
| **Spread (%) / 价差 (%)** | Bid-ask spread percentage / 买卖价差百分比 | 0.01 - 10.0 | 1.5 |
| **Quantity / 数量** | Order size / 订单大小 | 0.01+ | 0.1 |
| **Leverage / 杠杆** | Trading leverage / 交易杠杆 | 1 - 125 | 5 |

**Note / 注意**: Fixed Spread Strategy does **NOT** include Skew Factor. Only spread, quantity, and leverage are configurable.

**注意**: 固定价差策略**不**包含倾斜因子（Skew Factor）。仅价差、数量和杠杆可配置。

**Actions / 操作**:
- **💾 Save Strategy Config**: Save spread and quantity settings
- **⚡ Update Leverage**: Update leverage separately (can be changed independently)

- **💾 保存策略配置**: 保存价差和数量设置
- **⚡ 更新杠杆**: 单独更新杠杆（可以独立更改）

**Usage Example / 使用示例**:
1. Select trading pair: **ETH/USDT:USDT**
2. Set spread: **1.5%**
3. Set quantity: **0.1**
4. Set leverage: **5x**
5. Click **"💾 Save Strategy Config"** to save spread and quantity
6. Click **"⚡ Update Leverage"** to update leverage

### 4. LLM Evaluation Panel / LLM 评估面板

**Location / 位置**: Below strategy control panel / 策略控制面板下方

**Features / 功能**:
- **Multi-LLM Evaluation / 多模型评估**: Run evaluation with multiple LLM providers (Gemini, OpenAI, Claude)
- **Hyperliquid Context / Hyperliquid 上下文**: Evaluation uses Hyperliquid market data and exchange context
- **Progress Display / 进度显示**: Real-time progress for each LLM provider with detailed step indicators
- **Results Display / 结果显示**: View individual and aggregated LLM suggestions
- **Apply Suggestions / 应用建议**: Apply LLM suggestions to strategy configuration

**Progress Steps / 进度步骤**:
1. 📊 **Collecting Data / 收集数据**: Fetching market data from Hyperliquid
2. 📝 **Building Prompt / 整理 Prompt**: Constructing evaluation prompt
3. 🧠 **Inferring / 推理中**: LLM generating suggestions
4. 🔍 **Parsing & Validating / 解析并验证**: Validating LLM response
5. 🎲 **Simulating / 模拟中**: Running simulation (X/500 steps)
6. 📈 **Scoring / 打分中**: Calculating performance score
7. ✓ **Completed / 已完成**: Evaluation finished

**Usage / 使用**:
1. Click **"🚀 Run Evaluation"** to start evaluation
2. Watch progress for each LLM provider
3. Review individual and aggregated results
4. Click **"Apply Consensus"** or **"Apply [Provider Name]"** to apply suggestions
5. Suggestions will update strategy parameters (spread, quantity, leverage)

**Note / 注意**: 
- Evaluation always uses `exchange="hyperliquid"` parameter
- Market data is fetched from Hyperliquid exchange
- Suggestions are specific to Hyperliquid trading pairs

- 评估始终使用 `exchange="hyperliquid"` 参数
- 市场数据从 Hyperliquid 交易所获取
- 建议特定于 Hyperliquid 交易对

### 5. Order Management Panel / 订单管理面板

**Location / 位置**: Below LLM evaluation panel / LLM 评估面板下方

**Displays / 显示**:
- **Active Orders Table / 活跃订单表**: Table showing all open orders with:
  - Order ID / 订单 ID
  - Side / 方向 (BUY/SELL)
  - Price / 价格
  - Quantity / 数量
  - Status / 状态
  - Timestamp / 时间戳
  - Cancel Button / 取消按钮

**Actions / 操作**:
- **Refresh Orders / 刷新订单**: Click to refresh order list
- **Cancel Order / 取消订单**: Click cancel button next to each order

**Usage / 使用**:
1. Orders are automatically refreshed every 30 seconds
2. Click **"Refresh Orders"** for manual refresh
3. Click **"Cancel"** button to cancel a specific order
4. Order status updates in real-time

---

## Real-time Updates / 实时更新

The page automatically refreshes data without requiring manual page reload:

页面自动刷新数据，无需手动刷新页面：

- **Position Data / 仓位数据**: Refreshes every 30 seconds
- **Order Data / 订单数据**: Refreshes every 30 seconds
- **Connection Status / 连接状态**: Updates when connection changes
- **LLM Evaluation Progress / LLM 评估进度**: Updates in real-time during evaluation

- **仓位数据**: 每 30 秒刷新
- **订单数据**: 每 30 秒刷新
- **连接状态**: 连接变化时更新
- **LLM 评估进度**: 评估期间实时更新

---

## Navigation / 导航

### Navigation Links / 导航链接

The page includes navigation links in the header:

页面标题中包含导航链接：

- **← Back to Dashboard**: Returns to main dashboard (`/`)
- **⚡ Hyperliquid Trading**: Current page (highlighted)
- **🔎 Open LLM Trade Lab**: Navigate to LLM Trade Lab (`/evaluation`)

- **← 返回仪表盘**: 返回主仪表盘（`/`）
- **⚡ Hyperliquid Trading**: 当前页面（高亮）
- **🔎 Open LLM Trade Lab**: 导航到 LLM 交易实验室（`/evaluation`）

---

## Error Handling / 错误处理

### Connection Errors / 连接错误

**When Hyperliquid is not connected / 当 Hyperliquid 未连接时**:

- Connection status shows **"Disconnected"** in red
- Error message displayed: "Hyperliquid exchange not connected / Hyperliquid 交易所未连接"
- Trading features are disabled
- Position and order data cannot be loaded

- 连接状态显示红色 **"Disconnected"**
- 显示错误消息："Hyperliquid exchange not connected / Hyperliquid 交易所未连接"
- 交易功能被禁用
- 无法加载仓位和订单数据

**Solution / 解决方案**:
1. Check Hyperliquid API credentials in environment variables
2. Verify network connection
3. See [Hyperliquid Connection Guide](./hyperliquid_connection.md) for setup

1. 检查环境变量中的 Hyperliquid API 凭证
2. 验证网络连接
3. 查看 [Hyperliquid 连接指南](./hyperliquid_connection.md) 了解设置

### API Errors / API 错误

**When API calls fail / 当 API 调用失败时**:

- Error messages are displayed in both English and Chinese
- Error messages appear in red text
- Failed operations show specific error details

- 错误消息以英文和中文显示
- 错误消息以红色文本显示
- 失败的操作显示具体错误详情

**Common Errors / 常见错误**:
- "Failed to fetch position data / 获取仓位数据失败"
- "Failed to update leverage / 更新杠杆失败"
- "Failed to switch pair / 切换交易对失败"

---

## Best Practices / 最佳实践

### 1. Check Connection Before Trading / 交易前检查连接

Always verify that Hyperliquid is connected before using trading features:

在使用交易功能前，始终验证 Hyperliquid 已连接：

1. Check connection status in the header
2. Verify connection status panel shows "Connected"
3. Ensure position data loads successfully

1. 检查标题中的连接状态
2. 验证连接状态面板显示"Connected"
3. 确保仓位数据成功加载

### 2. Use LLM Evaluation for Parameter Tuning / 使用 LLM 评估进行参数调优

Before manually setting strategy parameters:

在手动设置策略参数之前：

1. Run LLM evaluation to get AI-powered suggestions
2. Review individual and aggregated results
3. Apply consensus or best-performing provider's suggestions
4. Fine-tune parameters based on results

1. 运行 LLM 评估以获取 AI 驱动的建议
2. 查看个人和聚合结果
3. 应用共识或表现最佳提供商的建议
4. 根据结果微调参数

### 3. Monitor Positions Regularly / 定期监控仓位

Keep an eye on your positions:

密切关注您的仓位：

1. Check position panel regularly
2. Monitor unrealized PnL
3. Review open positions table
4. Use refresh button if data seems stale

1. 定期检查仓位面板
2. 监控未实现盈亏
3. 查看未平仓仓位表
4. 如果数据看起来过时，使用刷新按钮

### 4. Manage Orders Actively / 主动管理订单

Monitor and manage your orders:

监控和管理您的订单：

1. Review active orders regularly
2. Cancel orders if market conditions change
3. Use refresh button to get latest order status
4. Check order execution status

1. 定期查看活跃订单
2. 如果市场条件变化，取消订单
3. 使用刷新按钮获取最新订单状态
4. 检查订单执行状态

---

## API Reference / API 参考

The page uses the following API endpoints:

页面使用以下 API 端点：

### GET `/api/hyperliquid/status`

Get Hyperliquid account status including positions, balance, and orders.

获取 Hyperliquid 账户状态，包括仓位、余额和订单。

**Response / 响应**:
```json
{
  "connected": true,
  "exchange": "hyperliquid",
  "symbol": "ETH/USDT:USDT",
  "balance": 10000.0,
  "available_balance": 5000.0,
  "position": 0.1,
  "unrealized_pnl": 10.0,
  "leverage": 5,
  "positions": [...],
  "orders": [...]
}
```

### POST `/api/hyperliquid/pair`

Update trading pair.

更新交易对。

**Request / 请求**:
```json
{
  "symbol": "BTC/USDT:USDT"
}
```

### POST `/api/hyperliquid/leverage`

Update leverage.

更新杠杆。

**Request / 请求**:
```json
5
```

### POST `/api/hyperliquid/config`

Update strategy configuration (spread and quantity).

更新策略配置（价差和数量）。

**Request / 请求**:
```json
{
  "spread": 1.5,
  "quantity": 0.1,
  "strategy_type": "fixed_spread"
}
```

### POST `/api/evaluation/run`

Run LLM evaluation with Hyperliquid context.

使用 Hyperliquid 上下文运行 LLM 评估。

**Request / 请求**:
```json
{
  "symbol": "ETH/USDT:USDT",
  "exchange": "hyperliquid",
  "simulation_steps": 500
}
```

### POST `/api/evaluation/apply`

Apply LLM evaluation suggestions.

应用 LLM 评估建议。

**Request / 请求**:
```json
{
  "source": "consensus",
  "exchange": "hyperliquid"
}
```

---

## Troubleshooting / 故障排除

### Issue: Page shows "Disconnected" / 问题：页面显示"Disconnected"

**Symptoms / 症状**:
- Connection status shows "Disconnected"
- Position data cannot be loaded
- Trading features are disabled

**Solutions / 解决方案**:
1. Check Hyperliquid API credentials: `HYPERLIQUID_API_KEY` and `HYPERLIQUID_API_SECRET`
2. Verify HyperliquidClient is initialized and connected
3. Check network connection
4. See [Hyperliquid Connection Guide](./hyperliquid_connection.md)

### Issue: Position data not updating / 问题：仓位数据未更新

**Symptoms / 症状**:
- Position panel shows stale data
- Refresh button doesn't update data

**Solutions / 解决方案**:
1. Check connection status
2. Verify Hyperliquid API is responding
3. Check browser console for errors
4. Try manual refresh

### Issue: LLM evaluation fails / 问题：LLM 评估失败

**Symptoms / 症状**:
- Evaluation shows error message
- Progress stops at a specific step

**Solutions / 解决方案**:
1. Check LLM API keys are configured
2. Verify Hyperliquid connection is active
3. Check market data is available
4. Review error message for specific issue

### Issue: Strategy config not saving / 问题：策略配置未保存

**Symptoms / 症状**:
- Clicking "Save Strategy Config" doesn't update values
- Error message appears

**Solutions / 解决方案**:
1. Verify Hyperliquid is connected
2. Check parameter values are valid (spread > 0, quantity > 0, leverage 1-125)
3. Check browser console for API errors
4. Try refreshing the page

---

## Related Documentation / 相关文档

- [Hyperliquid Connection Guide](./hyperliquid_connection.md) - Setting up Hyperliquid connection
- [Hyperliquid Orders Guide](./hyperliquid_orders.md) - Order management on Hyperliquid
- [Hyperliquid Positions Guide](./hyperliquid_positions.md) - Position tracking on Hyperliquid
- [Hyperliquid LLM Evaluation Guide](./hyperliquid_llm_evaluation.md) - LLM evaluation with Hyperliquid
- [Multi-LLM Evaluation Guide](./multi_llm_evaluation.md) - Multi-LLM evaluation framework
- [Hyperliquid 连接指南](./hyperliquid_connection.md) - 设置 Hyperliquid 连接
- [Hyperliquid 订单指南](./hyperliquid_orders.md) - Hyperliquid 订单管理
- [Hyperliquid 仓位指南](./hyperliquid_positions.md) - Hyperliquid 仓位追踪
- [Hyperliquid LLM 评估指南](./hyperliquid_llm_evaluation.md) - 使用 Hyperliquid 进行 LLM 评估
- [多 LLM 评估指南](./multi_llm_evaluation.md) - 多 LLM 评估框架

---

## Summary / 总结

The Hyperliquid Trading Page provides a comprehensive, focused interface for all Hyperliquid trading activities. Key features include:

Hyperliquid 交易页面为所有 Hyperliquid 交易活动提供全面的专用界面。主要功能包括：

1. ✅ Real-time position and balance tracking
2. ✅ Strategy control for Fixed Spread Strategy
3. ✅ Multi-LLM evaluation with Hyperliquid context
4. ✅ Order management and monitoring
5. ✅ Automatic data refresh
6. ✅ Bilingual support (English/Chinese)
7. ✅ Clear error handling
8. ✅ 实时仓位和余额追踪
9. ✅ 固定价差策略控制
10. ✅ 具有 Hyperliquid 上下文的多 LLM 评估
11. ✅ 订单管理和监控
12. ✅ 自动数据刷新
13. ✅ 双语支持（英文/中文）
14. ✅ 清晰的错误处理

The page is designed to provide a seamless trading experience specifically for Hyperliquid exchange, with all features integrated in one dedicated interface.

该页面专为 Hyperliquid 交易所设计，提供无缝的交易体验，所有功能都集成在一个专用界面中。

---

**Last Updated / 最后更新**: 2025-12-04  
**Owner / 负责人**: Agent QA  
**Feature / 功能**: US-UI-004

