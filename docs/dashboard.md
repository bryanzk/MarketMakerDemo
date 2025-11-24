# Dashboard & Monitoring Guide / Dashboard 与监控指南

The **Dashboard** provides a real-time view of the bot's performance, health, and operational metrics. It is designed to help traders and operators understand *how* the bot is making money and *where* risks might lie.
**Dashboard** 提供机器人性能、健康状况和运营指标的实时视图。它旨在帮助交易者和操作员了解机器人*如何*赚钱以及风险可能位于*何处*。

## 🖥️ Accessing the Dashboard / 访问 Dashboard

1.  Open the web interface (default: `http://localhost:3000`).
2.  Click the **"Dashboard"** button in the top navigation bar.
3.  Click **"Refresh Data"** to load the latest metrics.
1.  打开 Web 界面（默认：`http://localhost:3000`）。
2.  点击顶部导航栏中的 **"Dashboard"** 按钮。
3.  点击 **"Refresh Data"** 以加载最新指标。

---

## 📊 Metric Definitions / 指标定义

### 💼 Business Metrics / 业务指标

These metrics measure the financial success of the trading strategy.
这些指标衡量交易策略的财务成功。

| Metric / 指标 | Definition / 定义 | Interpretation / 解读 |
| :--- | :--- | :--- |
| **Realized PnL**<br>已实现盈亏 | The total profit or loss from closed positions.<br>平仓头寸的总盈亏。 | **Green**: Profitable.<br>**Red**: Loss-making.<br>**绿色**：盈利。<br>**红色**：亏损。 |
| **Win Rate**<br>胜率 | The percentage of trades that resulted in a positive PnL.<br>产生正盈亏的交易百分比。 | `> 50%` is generally good for market making, but depends on the profit/loss ratio.<br>`> 50%` 通常对做市商来说是好的，但取决于盈亏比。 |
| **Sharpe Ratio**<br>夏普比率 | A measure of risk-adjusted return. Calculated as `(Mean Returns / Std Dev of Returns)`.<br>风险调整后收益的衡量标准。计算公式为 `(平均收益 / 收益标准差)`。 | `> 1.0`: Good.<br>`> 2.0`: Excellent.<br>`< 0`: Taking risk for no return.<br>`> 1.0`：好。<br>`> 2.0`：优秀。<br>`< 0`：承担风险但无回报。 |
| **Max Drawdown**<br>最大回撤 | The maximum observed loss from a peak to a trough of a portfolio, before a new peak is attained.<br>在达到新峰值之前，投资组合从峰值到谷值的最大观察损失。 | Lower is better. High drawdown indicates high risk.<br>越低越好。高回撤表明高风险。 |

### ⚙️ Operational Metrics / 运营指标

These metrics measure the efficiency and health of the trading infrastructure.
这些指标衡量交易基础设施的效率和健康状况。

| Metric / 指标 | Definition / 定义 | Interpretation / 解读 |
| :--- | :--- | :--- |
| **Tick-to-Trade Latency**<br>Tick-to-Trade 延迟 | The time elapsed between receiving a market data update (tick) and placing an order.<br>从接收市场数据更新 (tick) 到下达订单之间经过的时间。 | Lower is better. High latency increases the risk of adverse selection.<br>越低越好。高延迟会增加逆向选择的风险。 |
| **Fill Rate**<br>成交率 | The percentage of placed orders that are actually executed (filled).<br>实际执行（成交）的已下达订单百分比。 | Low fill rate might indicate the spread is too wide or the bot is too slow.<br>低成交率可能表明点差太宽或机器人太慢。 |
| **Slippage**<br>滑点 | The difference between the expected price of a trade and the price at which the trade is executed.<br>交易的预期价格与交易执行价格之间的差异。 | Positive slippage (better price) is good. Negative slippage (worse price) eats into profits.<br>正滑点（更好的价格）是好的。负滑点（更差的价格）会侵蚀利润。 |

---

## 📈 Charts / 图表

### PnL Growth / 盈亏增长
A line chart showing the cumulative Realized PnL over time.
- **Upward Trend**: Consistent profitability.
- **Flat**: No trading activity or breakeven.
- **Downward Trend**: Strategy is losing money.

显示随时间推移的累计已实现盈亏的折线图。
- **上升趋势**：持续盈利。
- **平坦**：无交易活动或盈亏平衡。
- **下降趋势**：策略正在亏损。

### Trade Distribution / 交易分布
A doughnut chart showing the ratio of **Winning** vs **Losing** trades.
- Helps visualize the Win Rate.
- Even with a low win rate, a strategy can be profitable if winning trades are much larger than losing trades.

显示 **盈利** 与 **亏损** 交易比例的环形图。
- 帮助可视化胜率。
- 即使胜率较低，如果盈利交易远大于亏损交易，策略也可以盈利。

---

## ❓ Troubleshooting / 故障排除

**Q: Why are the charts empty? / 为什么图表是空的？**
A: The charts require closed trades to populate data. If the bot hasn't made any trades yet, the charts will be empty.
A: 图表需要已平仓的交易来填充数据。如果机器人尚未进行任何交易，图表将为空。

**Q: Why is "Tick-to-Trade Latency" N/A? / 为什么 "Tick-to-Trade Latency" 显示 N/A？**
A: This metric is calculated based on live trading events. It will populate after the first order is placed.
A: 此指标基于实时交易事件计算。它将在下达第一个订单后填充。
