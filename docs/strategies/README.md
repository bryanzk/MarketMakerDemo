# Trading Strategies Documentation / 交易策略文档

This directory contains detailed documentation for all available trading strategies in the AlphaLoop Market Maker system.

本目录包含 AlphaLoop 做市商系统中所有可用交易策略的详细文档。

## Available Strategies / 可用策略

### 1. [Fixed Spread Strategy](fixed_spread_strategy.md)
- **Type**: Market Making / 做市
- **Complexity**: Low / 低
- **Best For**: Stable markets with predictable volatility / 波动性可预测的稳定市场
- **Description**: Places symmetric bid/ask orders around the mid-price with a fixed spread percentage.
- **描述**: 围绕中间价以固定价差百分比下对称的买卖订单。

### 2. [Funding Rate Skew Strategy](funding_rate_strategy.md) 🆕
- **Type**: Market Making + Arbitrage / 做市 + 套利
- **Complexity**: Medium / 中
- **Best For**: Capturing funding rate arbitrage opportunities / 捕获资金费率套利机会
- **Description**: Adjusts bid/ask quotes based on perpetual futures funding rates to earn funding payments.
- **描述**: 根据永续合约资金费率调整买卖报价以赚取资金费用。

## Strategy Selection Guide / 策略选择指南

| Market Condition | Recommended Strategy | Reason |
|-----------------|---------------------|--------|
| Low Volatility, Neutral Funding | Fixed Spread | Stable, predictable returns |
| High Positive Funding Rate | Funding Rate Skew | Earn funding by being short |
| High Negative Funding Rate | Funding Rate Skew | Earn funding by being long |
| High Volatility | Fixed Spread (wider) | Reduce inventory risk |

| 市场状况 | 推荐策略 | 原因 |
|---------|---------|------|
| 低波动性，中性资金费率 | Fixed Spread | 稳定、可预测的回报 |
| 高正资金费率 | Funding Rate Skew | 通过空头赚取资金费 |
| 高负资金费率 | Funding Rate Skew | 通过多头赚取资金费 |
| 高波动性 | Fixed Spread（更宽价差） | 降低库存风险 |

## Adding New Strategies / 添加新策略

For developers looking to implement new strategies, please refer to the [Strategy Development Guide](../strategy_development_guide.md).

开发者如需实现新策略，请参阅[策略开发指南](../strategy_development_guide.md)。
