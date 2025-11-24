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

结果：机器人在空头一侧提供略优报价，当仓位持有跨过资金结算时，可以额外获得资金费率收入。

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

❌ **复杂度较高** – 依赖可靠且及时更新的资金费率数据。  
❌ **资金费率反转风险** – 当资金费率方向突然反转时，机器人可能落在需要支付资金费率的一侧。  
❌ **可能增加库存风险** – 由于价格倾斜，可能形成更大的净多或净空仓位。  

## Best Use Cases / 最佳使用场景

1. **Perpetual Futures Markets** / 永续合约市场  
   - **Perpetual futures** where funding rates are regularly posted.  
   - 资金费率按固定周期结算并持续公布的永续合约市场。  

2. **Stable Funding Direction** / 资金费率方向相对稳定  
   - Markets with a consistent positive or negative funding bias.  
   - 资金费率长期维持正向或负向，有利于持续捕获资金收益的市场。  

3. **High Liquidity** / 高流动性市场  
   - Deep order books to ensure orders are filled quickly even with skewed pricing.  
   - 订单簿深度充足，即使有价格倾斜也能快速成交的市场。  

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

`RiskAgent` 会强制执行以下限制：
- **最大 Skew**：0.5%（防止价格过度向一侧倾斜）  
- **最大仓位**：可配置的库存上限，用于控制整体风险敞口  
- **资金费率数据时效性**：如果资金费率数据超过 1 小时未更新，则回退到普通固定价差逻辑  

## Performance Metrics / 性能指标

Monitor these KPIs to evaluate performance:
- **Funding Capture Rate** – Percentage of funding intervals where the bot earned a payment.
- **Net PnL** – Includes spread profit + funding income.
- **Inventory Drift** – Net position change due to skew bias.
- **Fill Rate** – Order execution success on both sides.

监控这些 KPI 以评估资金费率策略表现：
- **资金捕获率（Funding Capture Rate）**：获得资金费率收入的结算周期占比  
- **净盈亏（Net PnL）**：同时包含价差收益与资金费率收益  
- **库存漂移（Inventory Drift）**：由于倾斜报价导致的净仓位变化趋势  
- **成交率（Fill Rate）**：双边挂单实际被成交的比例  

## Related Documentation / 相关文档

- [Strategy Development Guide](../strategy_development_guide.md)
- [Fixed Spread Strategy](fixed_spread_strategy.md)
- [Trading Strategy Overview](../trading_strategy.md)
