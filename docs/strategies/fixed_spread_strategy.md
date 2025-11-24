# Fixed Spread Strategy / 固定价差策略

## Overview / 概述

The Fixed Spread Strategy is a classic market-making approach that places symmetric buy and sell orders around the current mid-price with a fixed percentage spread.

固定价差策略是一种经典的做市方法，围绕当前中间价以固定百分比价差下对称的买卖订单。

## How It Works / 工作原理

### Order Placement / 订单放置

```
Mid Price = (Best Bid + Best Ask) / 2
Bid Price = Mid Price × (1 - Spread / 2)
Ask Price = Mid Price × (1 + Spread / 2)
```

**Example / 示例:**
- Mid Price = $1000
- Spread = 0.2% (0.002)
- Bid = $1000 × 0.999 = $999
- Ask = $1000 × 1.001 = $1001

### Profit Mechanism / 盈利机制

The strategy earns the spread when both sides are filled:
- Buy at $999, Sell at $1001 → Profit = $2 per unit

当买卖双方都成交时，策略赚取价差：
- 以 $999 买入，以 $1001 卖出 → 每单位利润 = $2

## Parameters / 参数

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `spread` | float | 0.002 | 0.001 - 0.05 | Price spread as a decimal (0.002 = 0.2%) |
| `quantity` | float | 0.01 | Exchange limits | Order size in base currency |
| `leverage` | int | 1 | 1 - Max leverage | Position leverage multiplier |

| 参数 | 类型 | 默认值 | 范围 | 描述 |
|------|------|--------|------|------|
| `spread` | float | 0.002 | 0.001 - 0.05 | 价差（小数形式，0.002 = 0.2%） |
| `quantity` | float | 0.01 | 交易所限制 | 基础货币的订单大小 |
| `leverage` | int | 1 | 1 - 最大杠杆 | 仓位杠杆倍数 |

## Advantages / 优势

✅ **Simple & Predictable** / 简单且可预测
- Easy to understand and implement
- Predictable profit per round-trip
- 易于理解和实现
- 每轮交易利润可预测

✅ **Low Risk in Stable Markets** / 稳定市场中风险低
- Works well when volatility is low
- Minimal inventory risk if orders fill quickly
- 在波动性低时表现良好
- 如果订单快速成交，库存风险最小

✅ **Resource Efficient** / 资源高效
- Minimal computational requirements
- Low API call overhead
- 计算需求最小
- API 调用开销低

## Disadvantages / 劣势

❌ **Inventory Risk** / 库存风险
- Can accumulate unwanted positions in trending markets
- May require manual rebalancing
- 在趋势市场中可能累积不需要的仓位
- 可能需要手动再平衡

❌ **Ignores Market Conditions** / 忽略市场状况
- Does not adapt to funding rates or volatility changes
- May be suboptimal in certain market regimes
- 不适应资金费率或波动性变化
- 在某些市场状况下可能不是最优的

## Best Use Cases / 最佳使用场景

1. **Range-Bound Markets** / 区间震荡市场
   - Price oscillates within a predictable range
   - 价格在可预测范围内震荡

2. **High Liquidity** / 高流动性
   - Deep order books ensure quick fills
   - 深度订单簿确保快速成交

3. **Low Volatility** / 低波动性
   - Reduces risk of adverse price movements
   - 降低不利价格变动的风险

## Configuration Example / 配置示例

```python
# In alphaloop/core/config.py
STRATEGY_TYPE = "fixed_spread"
SPREAD_PCT = 0.002  # 0.2%
QUANTITY = 0.01     # 0.01 ETH
LEVERAGE = 1        # No leverage
```

## Risk Management / 风险管理

The `RiskAgent` enforces these limits:
- **Min Spread**: 0.1% (prevents too-tight spreads)
- **Max Spread**: 5.0% (prevents too-wide spreads)
- **Max Position**: Configurable inventory limit

`RiskAgent` 强制执行这些限制：
- **最小价差**: 0.1%（防止价差过窄）
- **最大价差**: 5.0%（防止价差过宽）
- **最大仓位**: 可配置的库存限制

## Performance Metrics / 性能指标

Monitor these KPIs to evaluate performance:
- **Sharpe Ratio**: Risk-adjusted returns
- **Fill Rate**: Percentage of orders filled
- **Inventory Turnover**: How quickly positions are closed
- **PnL per Round-Trip**: Average profit per buy-sell cycle

监控这些 KPI 以评估性能：
- **夏普比率**: 风险调整后的回报
- **成交率**: 订单成交百分比
- **库存周转**: 仓位关闭速度
- **每轮 PnL**: 每个买卖周期的平均利润

## Related Documentation / 相关文档

- [Strategy Development Guide](../strategy_development_guide.md)
- [Funding Rate Strategy](funding_rate_strategy.md) - Compare with adaptive approach
- [Trading Strategy Overview](../trading_strategy.md)
