# Capital Allocation Strategies / 资金分配策略

## Overview / 概述

When running multiple trading strategies simultaneously, deciding how to allocate capital among them is crucial for portfolio performance. This guide explains different allocation strategies and how to use them in AlphaLoop.

当同时运行多个交易策略时，如何在不同策略间分配资金对组合表现至关重要。本指南介绍不同的资金分配策略及其在 AlphaLoop 中的使用方法。

---

## 1. Allocation Strategies / 分配策略

### 1.1 Equal Allocation / 等权重分配

**Description / 描述**: Distribute capital equally among all active strategies.

将所有活跃策略平均分配资金。

**Use Case / 适用场景**:
- Starting with multiple strategies (no historical performance data)
- When strategies have similar expected returns and risks
- Conservative approach for diversification

- 刚开始运行多个策略（无历史表现数据）
- 策略预期收益和风险相似时
- 保守的分散化方法

**Example / 示例**:
```python
# 2 strategies → 50% each
# 3 strategies → 33.3% each
```

**Pros / 优点**:
- Simple and easy to understand
- No bias toward any strategy
- Good for initial setup

- 简单易懂
- 不偏向任何策略
- 适合初始设置

**Cons / 缺点**:
- Doesn't optimize for performance
- May allocate too much to underperforming strategies

- 不优化表现
- 可能给表现差的策略分配过多资金

---

### 1.2 Performance-Based Allocation / 基于表现的分配

**Description / 描述**: Allocate more capital to strategies with better historical performance (higher Sharpe, ROI, or health score).

根据历史表现（更高的 Sharpe、ROI 或健康度）给表现更好的策略分配更多资金。

**Use Case / 适用场景**:
- After running strategies for a period (have performance data)
- Want to maximize returns by favoring winners
- Strategies have different performance levels

- 策略运行一段时间后（有表现数据）
- 希望通过偏向赢家来最大化收益
- 策略表现差异明显时

**Example / 示例**:
```python
# Strategy A: Sharpe 2.5, Health 90 → 70% allocation
# Strategy B: Sharpe 1.2, Health 60 → 30% allocation
```

**Calculation Methods / 计算方法**:

1. **Sharpe Ratio Weighted / 夏普比率加权**
   ```python
   allocation[i] = sharpe[i] / sum(all_sharpe)
   ```

2. **Health Score Weighted / 健康度加权**
   ```python
   allocation[i] = health[i] / sum(all_health)
   ```

3. **Composite Score / 综合评分**
   ```python
   score = 0.4 * normalized_sharpe + 0.3 * normalized_roi + 0.3 * normalized_health
   allocation[i] = score[i] / sum(all_scores)
   ```

**Pros / 优点**:
- Optimizes for better returns
- Automatically adjusts based on performance
- Rewards successful strategies

- 优化收益
- 基于表现自动调整
- 奖励成功策略

**Cons / 缺点**:
- May over-concentrate in one strategy (higher risk)
- Past performance doesn't guarantee future results
- Can amplify losses if top strategy fails

- 可能过度集中在单一策略（风险更高）
- 历史表现不保证未来结果
- 如果顶级策略失败，损失会被放大

---

### 1.3 Risk-Adjusted Allocation / 风险调整分配

**Description / 描述**: Allocate capital inversely proportional to risk (lower risk → more capital).

根据风险反向分配资金（风险越低 → 资金越多）。

**Use Case / 适用场景**:
- Prioritize capital preservation
- Strategies have different risk profiles
- Want to minimize portfolio volatility

- 优先考虑资金保护
- 策略风险特征不同
- 希望最小化组合波动

**Risk Metrics / 风险指标**:
- Max Drawdown (最大回撤)
- Volatility (波动率)
- Position Size (仓位大小)

**Example / 示例**:
```python
# Strategy A: Max Drawdown 5% → 60% allocation
# Strategy B: Max Drawdown 15% → 40% allocation
```

**Calculation / 计算**:
```python
risk_score = max_drawdown + volatility + position_risk
inverse_risk = 1 / (risk_score + 0.01)  # Add small value to avoid division by zero
allocation[i] = inverse_risk[i] / sum(all_inverse_risk)
```

**Pros / 优点**:
- Reduces portfolio risk
- Protects capital
- More stable returns

- 降低组合风险
- 保护资金
- 更稳定的收益

**Cons / 缺点**:
- May under-allocate to high-return strategies
- Lower overall returns potential

- 可能给高收益策略分配不足
- 整体收益潜力较低

---

### 1.4 Kelly Criterion / 凯利公式

**Description / 描述**: Use Kelly Criterion to optimize allocation based on win rate and average win/loss ratio.

使用凯利公式根据胜率和平均盈亏比优化分配。

**Use Case / 适用场景**:
- Strategies have clear win/loss statistics
- Want mathematically optimal allocation
- Comfortable with higher risk

- 策略有清晰的盈亏统计
- 希望数学上最优的分配
- 能承受较高风险

**Formula / 公式**:
```python
kelly_fraction = (win_rate * avg_win - (1 - win_rate) * avg_loss) / avg_win
allocation = min(kelly_fraction, max_allocation)  # Cap at max (e.g., 50%)
```

**Example / 示例**:
```python
# Strategy A: Win Rate 60%, Avg Win $10, Avg Loss $5
# Kelly = (0.6 * 10 - 0.4 * 5) / 10 = 0.4 → 40% allocation
```

**Pros / 优点**:
- Mathematically optimal for long-term growth
- Maximizes expected log utility
- Accounts for both win rate and risk

- 长期增长数学上最优
- 最大化期望对数效用
- 同时考虑胜率和风险

**Cons / 缺点**:
- Can suggest very high allocations (risky)
- Requires accurate win/loss statistics
- Sensitive to estimation errors

- 可能建议非常高的分配（风险高）
- 需要准确的盈亏统计
- 对估计误差敏感

---

### 1.5 Minimum Variance Allocation / 最小方差分配

**Description / 描述**: Allocate to minimize portfolio variance (volatility) while maintaining target returns.

分配资金以最小化组合方差（波动率），同时保持目标收益。

**Use Case / 适用场景**:
- Multiple strategies with different correlations
- Want to reduce portfolio volatility
- Have return targets

- 多个策略相关性不同
- 希望降低组合波动
- 有收益目标

**Calculation / 计算**:
Uses mean-variance optimization (requires covariance matrix of strategy returns).

使用均值-方差优化（需要策略收益的协方差矩阵）。

**Pros / 优点**:
- Minimizes portfolio risk
- Accounts for correlation between strategies
- Optimal for risk-averse investors

- 最小化组合风险
- 考虑策略间相关性
- 适合风险厌恶投资者

**Cons / 缺点**:
- Complex to implement
- Requires historical return data
- May underperform in trending markets

- 实现复杂
- 需要历史收益数据
- 在趋势市场中可能表现不佳

---

## 2. Implementation in AlphaLoop / 在 AlphaLoop 中的实现

### 2.1 Manual Allocation / 手动分配

Set allocation when registering strategies:

注册策略时设置分配：

```python
from alphaloop.portfolio.manager import PortfolioManager, StrategyStatus

portfolio = PortfolioManager(total_capital=10000.0)

# Equal allocation
portfolio.register_strategy("strategy_1", "Strategy 1", allocation=0.5)
portfolio.register_strategy("strategy_2", "Strategy 2", allocation=0.5)

# Custom allocation
portfolio.register_strategy("strategy_1", "Strategy 1", allocation=0.7)
portfolio.register_strategy("strategy_2", "Strategy 2", allocation=0.3)
```

### 2.2 Dynamic Allocation / 动态分配

Use `rebalance_allocations()` method to automatically adjust based on performance:

使用 `rebalance_allocations()` 方法根据表现自动调整：

```python
# Rebalance based on Sharpe ratio
portfolio.rebalance_allocations(method="sharpe")

# Rebalance based on health score
portfolio.rebalance_allocations(method="health")

# Rebalance based on composite score
portfolio.rebalance_allocations(method="composite", 
                                weights={"sharpe": 0.4, "roi": 0.3, "health": 0.3})
```

### 2.3 Allocation Constraints / 分配约束

Set minimum and maximum allocation limits:

设置最小和最大分配限制：

```python
# Ensure no strategy gets less than 10% or more than 70%
portfolio.set_allocation_limits(min_allocation=0.1, max_allocation=0.7)
portfolio.rebalance_allocations(method="sharpe")
```

---

## 3. Best Practices / 最佳实践

### 3.1 Start Conservative / 从保守开始

- Begin with equal allocation
- Monitor performance for at least 1-2 weeks
- Gradually adjust based on data

- 从等权重分配开始
- 至少监控 1-2 周表现
- 根据数据逐步调整

### 3.2 Set Limits / 设置限制

- Never allocate more than 50-60% to a single strategy
- Maintain minimum 10-20% per strategy for diversification
- Use stop-loss rules for underperforming strategies

- 单个策略不超过 50-60%
- 每个策略至少保持 10-20% 以分散风险
- 对表现差的策略使用止损规则

### 3.3 Regular Rebalancing / 定期再平衡

- Rebalance weekly or monthly (not too frequently)
- Avoid overreacting to short-term fluctuations
- Consider transaction costs

- 每周或每月再平衡（不要太频繁）
- 避免对短期波动过度反应
- 考虑交易成本

### 3.4 Monitor Correlation / 监控相关性

- If strategies are highly correlated, diversification benefits are limited
- Prefer strategies with low or negative correlation
- Adjust allocation if correlation changes

- 如果策略高度相关，分散化收益有限
- 偏好低相关或负相关策略
- 相关性变化时调整分配

---

## 4. Example Scenarios / 示例场景

### Scenario 1: Two Strategies, Similar Performance / 两个策略，表现相似

**Initial Setup / 初始设置**:
- Fixed Spread: 50%
- Funding Rate: 50%

**After 1 Month / 1个月后**:
- Fixed Spread: Sharpe 2.1, Health 85
- Funding Rate: Sharpe 2.3, Health 88

**Action / 行动**: Slight rebalance to 45% / 55% (favor Funding Rate)

轻微再平衡至 45% / 55%（偏向 Funding Rate）

### Scenario 2: One Strategy Underperforming / 一个策略表现不佳

**Initial Setup / 初始设置**:
- Strategy A: 50%
- Strategy B: 50%

**After 2 Weeks / 2周后**:
- Strategy A: Sharpe 2.5, Health 90
- Strategy B: Sharpe 0.8, Health 45

**Action / 行动**: 
- Reduce Strategy B to 20% (minimum)
- Increase Strategy A to 80%
- Consider pausing Strategy B if health < 40

- 将 Strategy B 降至 20%（最小值）
- 将 Strategy A 增至 80%
- 如果健康度 < 40，考虑暂停 Strategy B

### Scenario 3: High Correlation / 高相关性

**Observation / 观察**: Both strategies move together (correlation > 0.7)

两个策略同步移动（相关性 > 0.7）

**Action / 行动**: 
- Reduce total allocation to these strategies
- Add a third uncorrelated strategy
- Or focus on the better-performing one

- 减少这些策略的总分配
- 添加第三个不相关策略
- 或专注于表现更好的那个

---

## 5. API Reference / API 参考

See `alphaloop/portfolio/manager.py` for full API documentation.

完整 API 文档请参考 `alphaloop/portfolio/manager.py`。

### Key Methods / 关键方法

- `register_strategy()`: Register a strategy with initial allocation
- `rebalance_allocations()`: Rebalance based on performance
- `set_allocation_limits()`: Set min/max allocation constraints
- `get_allocation_for_strategy()`: Get current allocation for a strategy
- `update_strategy_metrics()`: Update performance metrics (triggers auto-rebalance if enabled)

---

## 6. Recommendations / 推荐方案

### For Beginners / 初学者

1. **Start with equal allocation** (50/50 for 2 strategies)
2. **Monitor for 2-4 weeks** before making changes
3. **Use health-based rebalancing** (simpler than Sharpe)

1. **从等权重分配开始**（2 个策略 50/50）
2. **监控 2-4 周**后再调整
3. **使用基于健康度的再平衡**（比 Sharpe 更简单）

### For Advanced Users / 高级用户

1. **Use composite score** (Sharpe + ROI + Health)
2. **Set allocation limits** (min 15%, max 60%)
3. **Rebalance monthly** based on rolling 30-day performance
4. **Monitor correlation** and adjust accordingly

1. **使用综合评分**（Sharpe + ROI + Health）
2. **设置分配限制**（最小 15%，最大 60%）
3. **每月再平衡**，基于滚动 30 天表现
4. **监控相关性**并相应调整

---

## Update Log / 更新日志

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2024-01 | Initial version: Manual and dynamic allocation strategies |

