# Funding Rate Skew Strategy / 资金费率倾斜策略

## Overview / 概述

The Funding Rate Skew Strategy is an advanced market‑making approach that adjusts order prices based on the perpetual futures funding rate. By positioning the bot on the side of the market that receives funding, it can earn additional income while still providing liquidity.

Funding Rate Skew 策略是一种高级做市方法，根据永续合约的资金费率调整订单价格。通过将机器人放在能够获得资金费率的一侧，既提供流动性，又能赚取额外收益。

## How It Works / 工作原理

1. **Fetch Funding Rate** – The exchange API provides a periodic funding rate (e.g., every 8 hours).
2. **Determine Skew Direction** –
   - Positive funding → Long positions pay, short positions receive. The bot should bias **short** (sell) orders.
   - Negative funding → Long positions receive, short positions pay. The bot should bias **long** (buy) orders.
3. **Adjust Prices** – Apply a small offset (`skew_pct`) to the normal spread on the funded side.

### Example / 示例

- Mid price = $10,000
- Base spread = 0.2 % (0.002)
- Funding rate = +0.03 % (positive)
- Skew = 0.05 % (0.0005)

```
Bid = Mid × (1 - (spread/2) - skew)   # more aggressive sell side
Ask = Mid × (1 + (spread/2))          # normal buy side
```

Result: The bot offers a slightly better price for short positions, earning the funding payment when the position is held through the funding interval.

## Parameters / 参数

| Parameter   | Type   | Default | Range          | Description |
|-------------|--------|---------|----------------|-------------|
| `spread`    | float  | 0.002   | 0.001‑0.05    | Base spread as a decimal |
| `skew_pct`  | float  | 0.0005  | 0.0001‑0.01   | Additional price offset for funded side |
| `quantity`  | float  | 0.01    | Exchange limits | Order size in base currency |
| `leverage`  | int    | 1       | 1‑max leverage | Position leverage |

| 参数       | 类型   | 默认值 | 范围          | 描述 |
|------------|--------|--------|----------------|------|
| `spread`   | float  | 0.002  | 0.001‑0.05    | 基础价差（小数） |
| `skew_pct` | float  | 0.0005 | 0.0001‑0.01   | 资金费率侧的额外价格偏移 |
| `quantity` | float  | 0.01   | 交易所限制      | 基础货币的订单大小 |
| `leverage` | int    | 1      | 1‑最大杠杆      | 仓位杠杆 |

## Advantages / 优势

✅ **Earn Funding Income** – Captures funding payments on the side of the market that receives them.
✅ **Still Provides Liquidity** – Maintains a market‑making presence on both sides.
✅ **Dynamic Adaptation** – Responds automatically to funding rate changes.

✅ **赚取资金费用** – 在能够获得资金费率的一侧捕获收益。
✅ **仍提供流动性** – 双向做市保持市场深度。
✅ **动态适应** – 自动响应资金费率变化。

## Disadvantages / 劣势

❌ **Complexity** – Requires reliable funding rate data and timely updates.
❌ **Risk of Funding Rate Reversal** – If the rate flips, the bot may be on the paying side.
❌ **Potential Increased Inventory** – Skewed orders can lead to larger net positions.

## Best Use Cases / 最佳使用场景

1. **Perpetual Futures Markets** – Where funding rates are regularly posted.
2. **Stable Funding Direction** – Markets with consistent positive or negative rates.
3. **High Liquidity** – To ensure orders are filled quickly despite skew.

## Configuration Example / 配置示例

```python
# In alphaloop/core/config.py
STRATEGY_TYPE = "funding_rate_skew"
SPREAD_PCT = 0.002      # 0.2% base spread
SKEW_PCT = 0.0005       # 0.05% funding skew
QUANTITY = 0.01
LEVERAGE = 1
```

## Risk Management / 风险管理

The `RiskAgent` enforces:
- **Max Skew**: 0.5 % (prevents extreme price bias)
- **Max Position**: Configurable inventory cap
- **Funding Rate Staleness**: If funding data is older than 1 hour, revert to normal spread.

## Performance Metrics / 性能指标

- **Funding Capture Rate** – Percentage of funding intervals where the bot earned a payment.
- **Net PnL** – Includes spread profit + funding income.
- **Inventory Drift** – Net position change due to skew bias.
- **Fill Rate** – Order execution success on both sides.

## Related Documentation / 相关文档

- [Strategy Development Guide](../strategy_development_guide.md)
- [Fixed Spread Strategy](fixed_spread_strategy.md)
- [Trading Strategy Overview](../trading_strategy.md)
