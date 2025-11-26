# Portfolio Management User Guide / 组合管理用户指南

## 概述

本指南介绍如何使用 AlphaLoop 的**组合管理**功能来监控和管理多个交易策略。组合管理视图让您可以在一个页面上看到所有策略的整体表现，并进行策略间的对比分析。

---

## 1. Portfolio Overview / 组合概览

### 1.1 功能说明

Portfolio Overview 位于页面顶部，提供所有运行中策略的汇总视图。

![Portfolio Overview](../images/portfolio_overview.png)

### 1.2 核心指标

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| **Total PnL** | 所有策略的总盈亏 | Σ(各策略 Realized PnL)，从会话起始时间计算 |
| **Trading Fees** | 已缴纳的交易手续费 | 从 Binance 获取，从会话起始时间累计 |
| **Net PnL** | 净盈亏（扣除手续费后） | Total PnL - Trading Fees |
| **Portfolio Sharpe** | 组合风险调整后收益 | 基于组合整体收益率计算 |
| **Active Strategies** | 正在运行的策略数量 | 状态为 LIVE 的策略计数 |
| **Portfolio Risk** | 整体风险等级 | 基于最大回撤和仓位综合评估 |

### 1.3 使用场景

**场景 A：日常监控**
> 作为交易员，我每天早上打开仪表盘，首先查看 Portfolio Overview 了解整体盈亏情况，确认所有策略是否正常运行。

**场景 B：风险预警**
> 当 Portfolio Risk 显示为 "High" 或 "Critical" 时，我需要立即查看各策略详情，决定是否需要暂停某些策略。

**场景 C：绩效汇报**
> 月末需要汇报整体交易绩效时，Portfolio Overview 提供了一目了然的汇总数据。

### 1.4 操作指南

1. **查看组合概览**
   - 打开 AlphaLoop 仪表盘
   - Portfolio Overview 自动显示在页面顶部
   - 数据每 5 秒自动刷新
   - 显示会话起始时间（默认：今天 9:00 AM UTC+8）

2. **理解风险等级**
   - 🟢 **Low**：所有指标正常，无需操作
   - 🟡 **Medium**：部分指标接近阈值，建议关注
   - 🔴 **High**：存在风险，建议审查策略配置
   - ⚫ **Critical**：严重风险，建议立即暂停策略

---

## 2. Strategy Comparison Table / 策略对比表

### 2.1 功能说明

策略对比表以表格形式展示所有策略的关键指标，支持快速对比和管理操作。

### 2.2 表格列说明

| 列名 | 说明 | 示例值 |
|------|------|--------|
| **Strategy** | 策略名称 | Fixed Spread |
| **Status** | 运行状态 | 🟢 LIVE / 🟡 PAPER / 🔴 PAUSED |
| **PnL** | 该策略的已实现盈亏 | +$156.78 |
| **Sharpe** | 该策略的夏普比率 | 2.1 |
| **Health** | 策略健康度评分 (0-100) | 85 |
| **Allocation** | 分配给该策略的资金比例 | 60% |
| **ROI** | 投资回报率 | 2.6% |
| **Actions** | 操作按钮 | [暂停] [详情] |

### 2.3 策略状态说明

| 状态 | 图标 | 说明 |
|------|------|------|
| **LIVE** | 🟢 | 策略正在实盘运行 |
| **PAPER** | 🟡 | 策略在模拟模式运行 |
| **PAUSED** | 🔴 | 策略已暂停，不下单 |
| **STOPPED** | ⚫ | 策略已停止 |

### 2.4 健康度评分 / Health Score

健康度是一个 0-100 的综合评分，基于以下因素计算：
Health score is a comprehensive 0-100 rating based on the following factors:

- **盈利能力 / Profitability** (权重 40% / Weight 40%)：基于 PnL 正负和大小
  - 公式 / Formula: `min(100, max(0, 50 + pnl / 100))`
  - PnL = 0 → 50分, PnL = 5000 → 100分, PnL = -5000 → 0分
  
- **风险调整收益 / Risk-Adjusted Return** (权重 30% / Weight 30%)：基于 Sharpe Ratio
  - 公式 / Formula: `min(100, max(0, sharpe * 40))`
  - Sharpe = 0 → 0分, Sharpe = 2.5 → 100分, Sharpe < 0 → 0分
  
- **执行质量 / Execution Quality** (权重 20% / Weight 20%)：基于 Fill Rate 和 Slippage
  - 公式 / Formula: `max(0, min(100, fill_rate * 100 - slippage * 10))`
  - Fill Rate = 1.0, Slippage = 0 → 100分
  
- **稳定性 / Stability** (权重 10% / Weight 10%)：基于 Max Drawdown
  - 公式 / Formula: `max(0, min(100, 100 - max_drawdown * 1000))`
  - Max Drawdown = 0 → 100分, Max Drawdown = 0.1 → 0分

**最终评分保证 / Final Score Guarantee:**
- 所有子项评分均限制在 0-100 范围内
- 最终健康度评分通过 `max(0, min(100, health))` 确保始终在 0-100 范围内
- All sub-scores are clamped to 0-100 range
- Final health score is guaranteed to be in 0-100 range via `max(0, min(100, health))`

| 评分范围 / Score Range | 状态 / Status | 建议操作 / Recommended Action |
|----------------------|--------------|------------------------------|
| 80-100 | 优秀 / Excellent | 可考虑增加资金分配 / Consider increasing allocation |
| 60-79 | 良好 / Good | 保持现状 / Maintain current state |
| 40-59 | 一般 / Fair | 需要关注和优化 / Needs attention and optimization |
| 0-39 | 较差 / Poor | 建议暂停或调整 / Recommend pausing or adjusting |

### 2.5 使用场景

**场景 A：策略对比决策**
> 我有两个策略同时运行，想知道哪个表现更好。通过对比表，我可以快速看到各策略的 Sharpe、PnL 和健康度，决定是否调整资金分配。

**场景 B：问题策略定位**
> 当 Portfolio 整体表现下滑时，我需要快速找出是哪个策略拖累了整体收益。对比表按 PnL 排序，问题策略一目了然。

**场景 C：新策略评估**
> 新上线一个策略后，我在对比表中可以与成熟策略进行对比，评估新策略的表现是否达标。

### 2.6 操作指南

1. **查看策略对比**
   - 策略对比表位于 Portfolio Overview 下方
   - 点击表头可按该列排序（Strategy, PnL, Sharpe, Health, ROI）
   - 第一次点击降序排列，再次点击升序排列
   - 当前排序列显示排序图标（▼ 降序，▲ 升序）
   - 默认按 PnL 降序排列

2. **暂停策略**
   - 点击策略行的 [Pause] 按钮
   - 弹出确认对话框："确定要暂停策略 'xxx' 吗？"
   - 确认后策略状态变为 PAUSED
   - 暂停期间策略不会下新订单
   - 暂停后按钮变为 [Resume]

3. **恢复策略**
   - 点击已暂停策略行的 [Resume] 按钮
   - 策略状态恢复为 LIVE
   - 恢复后可以继续下单

4. **查看策略详情**
   - 点击策略行的 [Details] 按钮
   - 自动跳转到该策略的专属 Tab 页
   - Fixed Spread 策略 → Trade Tab
   - Funding Rate 策略 → Funding Tab

5. **手动刷新数据**
   - 点击策略对比表右上角的 [🔄 Refresh] 按钮
   - 立即获取最新的组合数据和策略状态

---

## 3. 常见问题

### Q1: Portfolio Sharpe 与单个策略 Sharpe 的关系？
Portfolio Sharpe 是基于组合整体收益率计算的，不是各策略 Sharpe 的简单平均。低相关性的策略组合可以获得更高的 Portfolio Sharpe。

### Q2: 策略健康度多久更新一次？
健康度每 5 秒更新一次，基于最近的交易数据计算。组合概览和策略对比表也每 5 秒自动刷新。

### Q5: Trading Fees 和 Net PnL 的区别？
- **Trading Fees**：支付给交易所的手续费总额（从会话起始时间累计）
- **Net PnL**：扣除手续费后的净盈亏 = Total PnL - Trading Fees
- 这两个指标帮助您了解真实的交易收益

### Q3: 如何调整策略资金分配？
目前资金分配在策略配置中设定。未来版本将支持在对比表中直接调整分配比例。

### Q4: 暂停策略后会发生什么？
暂停后，策略的现有订单会被取消，不会再下新订单。但历史数据和统计会保留。


---

## 4. 快捷键

| 快捷键 | 功能 |
|--------|------|
| `R` | 刷新所有数据 |
| `1` | 切换到 Fixed Spread Tab |
| `2` | 切换到 Funding Rate Tab |
| `3` | 切换到 Dashboard Tab |

---

## 5. API 参考

如果您需要通过 API 获取组合数据，请参考：

```bash
# 获取组合概览
GET /api/portfolio

# 响应示例
{
  "total_pnl": 234.56,
  "commission": 5.00,
  "net_pnl": 229.56,
  "portfolio_sharpe": 2.3,
  "active_count": 2,
  "total_count": 2,
  "risk_level": "low",
  "total_capital": 10000.0,
  "available_balance": 9500.0,
  "session_start_time": 1701234000000,
  "strategies": [
    {
      "id": "fixed_spread",
      "name": "Fixed Spread",
      "status": "live",
      "pnl": 156.78,
      "sharpe": 2.1,
      "health": 85,
      "allocation": 0.6,
      "roi": 0.026
    },
    {
      "id": "funding_rate",
      "name": "Funding Rate",
      "status": "live",
      "pnl": 77.78,
      "sharpe": 2.5,
      "health": 88,
      "allocation": 0.4,
      "roi": 0.019
    }
  ]
}

# 暂停策略
POST /api/strategy/{strategy_id}/pause

# 恢复策略
POST /api/strategy/{strategy_id}/resume
```

---

## 6. 多策略实例隔离运行 / Multi-Strategy Instance Isolation

### 6.1 功能说明

AlphaLoop 支持多个策略实例同时运行，每个策略实例拥有：
- **独立的状态管理**：订单历史、错误历史、活跃订单
- **独立的参数配置**：Spread、Quantity、Leverage 等
- **独立的订单管理**：每个策略实例有独立的 OrderManager
- **隔离的执行环境**：策略之间互不干扰

### 6.2 策略实例类型

| 策略类型 | 说明 | 默认实例 ID |
|---------|------|------------|
| **Fixed Spread** | 固定价差策略 | `fixed_spread` |
| **Funding Rate** | 资金费率倾斜策略 | `funding_rate` |
| **Custom** | 自定义策略实例 | 用户定义 |

### 6.3 使用场景

**场景 A：策略对比测试**
> 我想同时运行两个不同参数的 Fixed Spread 策略，对比哪个参数组合表现更好。通过创建两个策略实例，我可以独立监控每个实例的表现。

**场景 B：风险分散**
> 我将资金分配给多个策略实例，降低单一策略的风险。即使某个策略表现不佳，其他策略仍可继续盈利。

**场景 C：渐进式部署**
> 新策略上线时，我先创建一个新实例进行小规模测试，确认表现良好后再增加资金分配。

### 6.4 技术实现

- 后端：`alphaloop/main.py` 中的 `AlphaLoop` 类管理多个 `StrategyInstance`
- 前端：通过 `/api/portfolio` 获取所有策略实例的状态和表现
- 隔离机制：每个策略实例有独立的 `order_manager` 和状态追踪

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1 | 2024-12 | 添加 Trading Fees 和 Net PnL 显示；完善排序功能；添加恢复策略功能；多策略实例隔离运行支持 |
| v1.0 | 2024-01 | 初始版本：Portfolio Overview + 策略对比表 |


