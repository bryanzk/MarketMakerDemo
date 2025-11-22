# Metrics Specification / 度量指标规范

## 1. Overview / 概述
This document defines the specific quantitative metrics to be implemented in the AlphaLoop trading system. These metrics serve as the "Health Bar" for each layer of the system.

本文档定义了将在 AlphaLoop 交易系统中实施的具体定量指标。这些指标充当系统每一层的“健康条”。

## 2. Layer 1: Infrastructure & Connectivity / 第一层：基础设施与连接性
**Owner**: Infrastructure Agent / **负责人**：基础设施智能体

| Metric / 指标 | Definition / 定义 | Why it Matters / 为什么重要 | Target / 目标 |
| :--- | :--- | :--- | :--- |
| **Tick-to-Trade Latency** | Time from receiving a tick to sending an order. <br> 从接收 Tick 到发送订单的时间。 | **Speed Kills**. If we are slow, we trade on old prices and lose money. <br> **速度至关重要**。如果我们慢了，我们就会按旧价格交易并亏损。 | < 5 ms |
| **WebSocket Sequence Gap** | Count of missing sequence IDs. <br> 丢失的序列号计数。 | **Blind Spots**. Missing data means we don't know the market state. <br> **盲点**。丢失数据意味着我们不知道市场状态。 | 0 |
| **API Weight Usage** | % of API limit consumed. <br> API 限制消耗百分比。 | **Banned**. If we hit 100%, the exchange bans us. <br> **被封禁**。如果我们达到 100%，交易所会封禁我们。 | < 50% |

## 3. Layer 2: Execution Quality / 第二层：执行质量
**Owner**: Execution Agent / **负责人**：执行智能体

| Metric / 指标 | Definition / 定义 | Why it Matters / 为什么重要 | Target / 目标 |
| :--- | :--- | :--- | :--- |
| **Slippage** | Diff between decision price and fill price. <br> 决策价格与成交价格的差异。 | **Hidden Cost**. High slippage eats up all your profits. <br> **隐性成本**。高滑点会吃掉你所有的利润。 | < 2 bps |
| **Fill Rate** | % of limit orders filled. <br> 限价单成交百分比。 | **Opportunity Cost**. If we don't fill, we don't trade. <br> **机会成本**。如果不成交，我们就无法交易。 | > 80% |

## 4. Layer 3: Risk & Structural Integrity / 第三层：风险与结构完整性
**Owner**: Risk Agent / **负责人**：风控智能体

| Metric / 指标 | Definition / 定义 | Formula / 公式 | Target / 目标 | Action Threshold / 触发阈值 |
| :--- | :--- | :--- | :--- | :--- |
| **Liquidation Buffer** | Distance to liquidation price. <br> 距离强平价格的距离。 | $\frac{|P_{mark} - P_{liq}|}{P_{mark}}$ | > 20% | < 10% (Deleverage/去杠杆) |
| **Basis Std Dev** | Volatility of the spot-perp basis. <br> 现货-永续基差的波动率。 | $\sigma(P_{perp} - P_{spot})$ | Low | > 2$\sigma$ (Pause Entry/暂停开仓) |
| **Funding Yield** | Annualized return from funding rates. <br> 资金费率年化收益。 | $\sum F_t \times 3 \times 365$ | > 10% | < 0% (Reduce Position/减仓) |

## 5. Layer 4: Strategy Performance / 第四层：策略绩效
**Owner**: Quant Agent / **负责人**：量化智能体

| Metric / 指标 | Definition / 定义 | Formula / 公式 | Target / 目标 | Action Threshold / 触发阈值 |
| :--- | :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | Risk-adjusted return. <br> 风险调整后收益。 | $\frac{R_p - R_f}{\sigma_p}$ | > 2.0 | < 1.0 (Retrain Model/重训模型) |
| **Sortino Ratio** | Downside risk-adjusted return. <br> 下行风险调整后收益。 | $\frac{R_p - R_f}{\sigma_{down}}$ | > 3.0 | < 1.5 (Review Strategy/审查策略) |
