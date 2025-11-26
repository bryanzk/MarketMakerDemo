# Risk Indicators User Guide / 风险指标用户指南

## Overview / 概述

This guide introduces AlphaLoop's **risk monitoring indicators**, helping you understand trading risk status in real-time and take timely action to prevent significant losses.

本指南介绍 AlphaLoop 的**风险监控指标**，帮助您实时了解交易风险状况，及时采取行动防止重大亏损。

---

## 1. Liquidation Buffer / 强平缓冲

### 1.1 Feature Description / 功能说明

Liquidation Buffer shows the safe distance between the current price and the forced liquidation price, serving as **the first line of defense against liquidation**.

Liquidation Buffer（强平缓冲）显示当前价格距离强制平仓价格的安全距离，是**防止爆仓的第一道防线**。

### 1.2 Calculation Formula / 计算公式

```
For long positions / 对于多头仓位:
Liquidation Buffer = (Current Price - Liquidation Price) / Current Price × 100%

For short positions / 对于空头仓位:
Liquidation Buffer = (Liquidation Price - Current Price) / Current Price × 100%
```

### 1.3 Risk Levels / 风险等级

| Buffer Value / 缓冲值 | Status / 状态 | Color / 颜色 | Recommended Action / 建议操作 |
|--------|------|------|----------|
| > 20% | Safe / 安全 | 🟢 Green / 绿色 | Normal operation / 正常运行 |
| 10% - 20% | Warning / 警告 | 🟡 Yellow / 黄色 | Monitor market volatility / 关注市场波动 |
| 5% - 10% | Danger / 危险 | 🟠 Orange / 橙色 | Consider reducing position / 考虑减仓 |
| < 5% | Critical / 紧急 | 🔴 Red / 红色 | Reduce immediately or add margin / 立即减仓或补充保证金 |

### 1.4 Use Cases / 使用场景

**Scenario A: Daily Monitoring / 场景 A：日常监控**
> Check Liquidation Buffer first when opening the dashboard. If below 10%, immediately evaluate whether to reduce position.
> 每次打开仪表盘，首先检查 Liquidation Buffer。如果低于 10%，需要立即评估是否需要减仓。

**Scenario B: Extreme Market Conditions / 场景 B：极端行情**
> During violent market fluctuations (e.g., major news releases), Liquidation Buffer may drop rapidly. The system will alert when below threshold.
> 市场剧烈波动时（如重大新闻发布），Liquidation Buffer 可能快速下降。系统会在低于阈值时发出预警。

**Scenario C: Leverage Adjustment / 场景 C：杠杆调整**
> Increasing leverage reduces Liquidation Buffer. Check if current buffer is sufficient before adjusting leverage.
> 增加杠杆会降低 Liquidation Buffer。在调整杠杆前，先检查当前缓冲是否充足。

### 1.5 Alert Mechanism / 预警机制

- **< 10%**: Dashboard shows yellow warning / Dashboard 显示黄色警告
- **< 5%**: Dashboard shows red warning + blinking / Dashboard 显示红色警告 + 闪烁提示
- **< 3%**: Recommend auto-pause strategy (configurable) / 建议自动暂停策略（可配置）

---

## 2. Inventory Drift / 库存偏移

### 2.1 Feature Description / 功能说明

Inventory Drift measures the **directional risk** of market maker positions. An ideal market maker should keep net position close to zero.

Inventory Drift（库存偏移）衡量做市商持仓的**方向性风险**。理想的做市商应保持净持仓接近零。

### 2.2 Calculation Formula / 计算公式

```
Inventory Drift = Net Position / Max Allowed Position × 100%

Net Position / 净持仓 = Long Position - Short Position (for hedged mode)
                      = Current Position Amount (for one-way mode)
```

### 2.3 Risk Levels / 风险等级

| Drift Value / 偏移值 | Status / 状态 | Color / 颜色 | Meaning / 含义 |
|--------|------|------|------|
| -20% ~ +20% | Balanced / 平衡 | 🟢 Green / 绿色 | Healthy inventory / 库存健康 |
| -50% ~ -20% or +20% ~ +50% | Offset / 偏移 | 🟡 Yellow / 黄色 | Directional exposure / 存在方向性敞口 |
| -80% ~ -50% or +50% ~ +80% | Severe / 严重偏移 | 🟠 Orange / 橙色 | Need to adjust quotes / 需要调整报价 |
| < -80% or > +80% | Extreme / 极端偏移 | 🔴 Red / 红色 | Pause market making or reverse / 暂停做市或反向操作 |

### 2.4 Use Cases / 使用场景

**Scenario A: Market Making Strategy Monitoring / 场景 A：做市策略监控**
> As a market maker, I need to maintain inventory balance. When Inventory Drift > 50%, it means I hold too many long positions and need to adjust bid/ask quotes to attract more sell orders.
> 作为做市商，我需要保持库存平衡。当 Inventory Drift > 50% 时，表示我持有过多多头仓位，需要调整 bid/ask 报价以吸引更多卖单。

**Scenario B: Trending Market / 场景 B：趋势市场**
> In a one-sided trending market, inventory tends to accumulate drift. Consider pausing market making or increasing spread.
> 在单边趋势市场中，库存容易积累偏移。此时需要考虑暂停做市或加大价差。

**Scenario C: Strategy Comparison / 场景 C：策略对比**
> Inventory drift of different strategies reflects their hedging efficiency. Strategies with smaller drift are usually more stable.
> 不同策略的库存偏移可以反映其对冲效率。偏移小的策略通常更稳定。

### 2.5 Drift Direction Explanation / 偏移方向说明

| Direction / 方向 | Meaning / 含义 | Risk / 风险 |
|------|------|------|
| **Positive (+) / 正偏移** | Net long position / 净多头仓位 | Loss when price falls / 价格下跌时亏损 |
| **Negative (-) / 负偏移** | Net short position / 净空头仓位 | Loss when price rises / 价格上涨时亏损 |

---

## 3. Max Drawdown / 最大回撤

### 3.1 Feature Description / 功能说明

Max Drawdown measures the **maximum loss from peak to trough** of a strategy, a core metric for evaluating strategy risk.

Max Drawdown（最大回撤）衡量策略从峰值到谷底的**最大亏损幅度**，是评估策略风险的核心指标。

### 3.2 Calculation Formula / 计算公式

```
Max Drawdown = (Peak Value - Trough Value) / Peak Value × 100%

Strategy-level Drawdown / 策略级回撤 = Max drawdown of individual strategy
Portfolio-level Drawdown / 组合级回撤 = Max drawdown of all strategies combined
```

### 3.3 Risk Levels / 风险等级

| Drawdown Value / 回撤值 | Status / 状态 | Color / 颜色 | Recommended Action / 建议操作 |
|--------|------|------|----------|
| < 5% | Excellent / 优秀 | 🟢 Green / 绿色 | Strategy running well / 策略运行良好 |
| 5% - 10% | Normal / 正常 | 🟡 Yellow / 黄色 | Normal fluctuation range / 正常波动范围 |
| 10% - 20% | Warning / 警告 | 🟠 Orange / 橙色 | Check strategy parameters / 检查策略参数 |
| > 20% | Danger / 危险 | 🔴 Red / 红色 | Consider pausing strategy / 考虑暂停策略 |

### 3.4 Use Cases / 使用场景

**Scenario A: Strategy Evaluation / 场景 A：策略评估**
> Check Max Drawdown one week after a new strategy goes live. If it exceeds 10%, analyze whether it's due to market conditions or strategy issues.
> 新策略上线一周后，检查其 Max Drawdown。如果超过 10%，需要分析是市场原因还是策略问题。

**Scenario B: Capital Allocation Decision / 场景 B：资金分配决策**
> Strategies with smaller drawdown can be allocated more capital. E.g., Strategy A has 5% drawdown, Strategy B has 15% - reduce allocation to Strategy B.
> 回撤小的策略可以分配更多资金。例如：策略A回撤5%、策略B回撤15%，应减少策略B的资金分配。

**Scenario C: Stop Loss Setting / 场景 C：止损设置**
> Set automatic stop-loss rules: automatically pause strategy when drawdown exceeds 15%.
> 可以设置自动止损规则：当策略回撤超过15%时，自动暂停该策略。

### 3.5 Strategy-level vs Portfolio-level Drawdown / 策略级 vs 组合级回撤

| Type / 类型 | Description / 说明 | Purpose / 用途 |
|------|------|------|
| **Strategy-level / 策略级回撤** | Drawdown of individual strategy / 单个策略的回撤 | Identify problem strategies / 识别问题策略 |
| **Portfolio-level / 组合级回撤** | All strategies combined / 所有策略合计 | Overall risk control / 整体风险控制 |

> 💡 Low-correlation strategy portfolios can reduce portfolio-level drawdown / 低相关性的策略组合可以降低组合级回撤

---

## 4. Risk Dashboard Layout / Risk Dashboard 布局

### 4.1 Risk Indicator Cards / 风险指标卡片

```
┌─────────────────────────────────────────────────────────────────┐
│ ⚠️ Risk Indicators                                              │
│ ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│ │ Liquidation      │ │ Inventory        │ │ Max Drawdown     │ │
│ │ Buffer           │ │ Drift            │ │                  │ │
│ │                  │ │                  │ │                  │ │
│ │   15.2%          │ │   +32.5%         │ │   -4.8%          │ │
│ │   ⚠️ Warning     │ │   🟡 Offset      │ │   🟢 Good        │ │
│ └──────────────────┘ └──────────────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 Strategy-level Risk Table / 策略级风险表

| Strategy / 策略 | Liq Buffer | Inv Drift | Max DD | Risk Level / 风险等级 |
|----------|------------|-----------|--------|------------|
| Fixed Spread | 18.5% 🟢 | +12% 🟢 | -3.2% 🟢 | Low / 低 |
| Funding Rate | 12.3% 🟡 | +45% 🟡 | -8.1% 🟡 | Medium / 中 |

---

## 5. API Reference / API 参考

### 5.1 Get Risk Indicators / 获取风险指标

```bash
GET /api/risk-indicators

# Response Example / 响应示例
{
  "liquidation_buffer": 15.2,
  "liquidation_buffer_status": "warning",
  "inventory_drift": 32.5,
  "inventory_drift_status": "offset",
  "max_drawdown": -4.8,
  "max_drawdown_status": "good",
  "overall_risk_level": "medium",
  "strategies": [
    {
      "id": "fixed_spread",
      "liquidation_buffer": 18.5,
      "inventory_drift": 12.0,
      "max_drawdown": -3.2,
      "risk_level": "low"
    },
    {
      "id": "funding_rate",
      "liquidation_buffer": 12.3,
      "inventory_drift": 45.0,
      "max_drawdown": -8.1,
      "risk_level": "medium"
    }
  ]
}
```

---

## 6. FAQ / 常见问题

### Q1: What does Liquidation Buffer showing N/A mean? / Liquidation Buffer 显示 N/A 是什么意思？
It means there's no position currently, or the liquidation price cannot be obtained from the exchange.
表示当前没有持仓，或无法从交易所获取强平价格。

### Q2: What does a negative Inventory Drift represent? / Inventory Drift 为负数代表什么？
It indicates a net short position. For example, -30% means 30% short direction drift.
表示净空头仓位。例如 -30% 表示空头方向偏移 30%。

### Q3: How often are these indicators updated? / 这些指标多久更新一次？
By default, they update every 3 seconds. The refresh frequency can be adjusted in settings.
默认每 3 秒更新一次，可在设置中调整刷新频率。

### Q4: How to set risk threshold alerts? / 如何设置风险阈值预警？
Currently using default thresholds. Future versions will support custom threshold configuration.
目前使用默认阈值，未来版本将支持自定义阈值配置。

---

## Changelog / 更新日志

| Version / 版本 | Date / 日期 | Changes / 更新内容 |
|------|------|----------|
| v1.0 | 2024-01 | Initial version: Three major risk indicators / 初始版本：三大风险指标 |
| v1.1 | 2025-11 | Bilingual documentation / 双语文档更新 |
