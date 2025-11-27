# Capital Allocation Examples / 资金分配示例

## Overview / 概述

This document provides practical examples of how to use the capital allocation features in AlphaLoop's PortfolioManager.

本文档提供在 AlphaLoop 的 PortfolioManager 中使用资金分配功能的实际示例。

---

## Example 1: Manual Equal Allocation / 示例 1：手动等权重分配

**Scenario / 场景**: Starting with 2 strategies, want equal allocation.

从 2 个策略开始，希望等权重分配。

```python
from alphaloop.portfolio.manager import PortfolioManager, StrategyStatus

# Initialize portfolio manager
portfolio = PortfolioManager(total_capital=10000.0)

# Register strategies with equal allocation
portfolio.register_strategy(
    strategy_id="fixed_spread",
    name="Fixed Spread",
    allocation=0.5,  # 50%
    status=StrategyStatus.LIVE,
)

portfolio.register_strategy(
    strategy_id="funding_rate",
    name="Funding Rate",
    allocation=0.5,  # 50%
    status=StrategyStatus.LIVE,
)

# Check allocations
print(f"Fixed Spread: {portfolio.get_allocation_for_strategy('fixed_spread'):.1%}")
print(f"Funding Rate: {portfolio.get_allocation_for_strategy('funding_rate'):.1%}")
# Output: Fixed Spread: 50.0%
#         Funding Rate: 50.0%
```

---

## Example 2: Performance-Based Rebalancing / 示例 2：基于表现的再平衡

**Scenario / 场景**: After running for 2 weeks, rebalance based on Sharpe ratio.

运行 2 周后，基于夏普比率再平衡。

```python
# Update strategy metrics (simulated data)
portfolio.update_strategy_metrics(
    strategy_id="fixed_spread",
    pnl=150.0,
    sharpe=2.1,
    health=85,
)

portfolio.update_strategy_metrics(
    strategy_id="funding_rate",
    pnl=200.0,
    sharpe=2.5,  # Better Sharpe
    health=88,
)

# Rebalance based on Sharpe ratio
new_allocations = portfolio.rebalance_allocations(method="sharpe")

print("New allocations after rebalancing:")
for strategy_id, allocation in new_allocations.items():
    print(f"  {strategy_id}: {allocation:.1%}")

# Output:
#   fixed_spread: 45.7%  (Sharpe 2.1)
#   funding_rate: 54.3%  (Sharpe 2.5)
```

---

## Example 3: Composite Score Allocation / 示例 3：综合评分分配

**Scenario / 场景**: Use composite score (Sharpe + ROI + Health) for allocation.

使用综合评分（Sharpe + ROI + Health）进行分配。

```python
# Update metrics
portfolio.update_strategy_metrics(
    strategy_id="fixed_spread",
    pnl=150.0,
    sharpe=2.1,
    health=85,
    max_drawdown=0.05,
)

portfolio.update_strategy_metrics(
    strategy_id="funding_rate",
    pnl=200.0,
    sharpe=2.5,
    health=88,
    max_drawdown=0.03,
)

# Rebalance using composite score
new_allocations = portfolio.rebalance_allocations(
    method="composite",
    weights={"sharpe": 0.4, "roi": 0.3, "health": 0.3}
)

print("Composite score allocations:")
for strategy_id, allocation in new_allocations.items():
    print(f"  {strategy_id}: {allocation:.1%}")
```

---

## Example 4: Risk-Adjusted Allocation / 示例 4：风险调整分配

**Scenario / 场景**: Allocate more to lower-risk strategies.

给低风险策略分配更多资金。

```python
# Update metrics with different risk profiles
portfolio.update_strategy_metrics(
    strategy_id="fixed_spread",
    pnl=100.0,
    sharpe=1.8,
    health=75,
    max_drawdown=0.15,  # Higher risk
)

portfolio.update_strategy_metrics(
    strategy_id="funding_rate",
    pnl=120.0,
    sharpe=2.0,
    health=80,
    max_drawdown=0.05,  # Lower risk
)

# Rebalance based on risk (inverse risk weighting)
new_allocations = portfolio.rebalance_allocations(method="risk_adjusted")

print("Risk-adjusted allocations:")
for strategy_id, allocation in new_allocations.items():
    strategy = portfolio.strategies[strategy_id]
    print(f"  {strategy_id}: {allocation:.1%} (Drawdown: {strategy.max_drawdown:.1%})")

# Output:
#   fixed_spread: 25.0%  (Drawdown: 15.0%)
#   funding_rate: 75.0%  (Drawdown: 5.0%)
```

---

## Example 5: Setting Allocation Limits / 示例 5：设置分配限制

**Scenario / 场景**: Ensure no strategy gets less than 20% or more than 60%.

确保没有策略少于 20% 或超过 60%。

```python
# Set allocation limits
portfolio.set_allocation_limits(min_allocation=0.2, max_allocation=0.6)

# Update metrics
portfolio.update_strategy_metrics(
    strategy_id="fixed_spread",
    pnl=50.0,
    sharpe=1.5,
    health=70,
)

portfolio.update_strategy_metrics(
    strategy_id="funding_rate",
    pnl=300.0,
    sharpe=3.0,  # Much better
    health=95,
)

# Rebalance (will respect limits)
new_allocations = portfolio.rebalance_allocations(method="sharpe")

print("Allocations with limits (20%-60%):")
for strategy_id, allocation in new_allocations.items():
    print(f"  {strategy_id}: {allocation:.1%}")

# Output:
#   fixed_spread: 20.0%  (min limit)
#   funding_rate: 60.0%  (max limit)
```

---

## Example 6: Auto-Rebalancing / 示例 6：自动再平衡

**Scenario / 场景**: Automatically rebalance when metrics are updated.

更新指标时自动再平衡。

```python
# Initialize with auto-rebalance enabled
portfolio = PortfolioManager(
    total_capital=10000.0,
    min_allocation=0.15,
    max_allocation=0.65,
    auto_rebalance=True,  # Enable auto-rebalance
)

portfolio.register_strategy("fixed_spread", "Fixed Spread", allocation=0.5)
portfolio.register_strategy("funding_rate", "Funding Rate", allocation=0.5)

# Set both to LIVE
portfolio.set_strategy_status("fixed_spread", StrategyStatus.LIVE)
portfolio.set_strategy_status("funding_rate", StrategyStatus.LIVE)

# Update metrics - this will trigger automatic rebalancing
portfolio.update_strategy_metrics(
    strategy_id="fixed_spread",
    pnl=100.0,
    sharpe=2.0,
    health=80,
)

portfolio.update_strategy_metrics(
    strategy_id="funding_rate",
    pnl=150.0,
    sharpe=2.5,
    health=85,
)

# Check allocations (automatically adjusted)
print("Auto-rebalanced allocations:")
for strategy_id in ["fixed_spread", "funding_rate"]:
    alloc = portfolio.get_allocation_for_strategy(strategy_id)
    print(f"  {strategy_id}: {alloc:.1%}")
```

---

## Example 7: Three Strategies / 示例 7：三个策略

**Scenario / 场景**: Managing 3 strategies with different allocation methods.

管理 3 个策略，使用不同的分配方法。

```python
portfolio = PortfolioManager(total_capital=15000.0)

# Register 3 strategies
portfolio.register_strategy("strategy_a", "Strategy A", allocation=0.33)
portfolio.register_strategy("strategy_b", "Strategy B", allocation=0.33)
portfolio.register_strategy("strategy_c", "Strategy C", allocation=0.34)

# Set all to LIVE
for sid in ["strategy_a", "strategy_b", "strategy_c"]:
    portfolio.set_strategy_status(sid, StrategyStatus.LIVE)

# Update metrics
portfolio.update_strategy_metrics("strategy_a", pnl=200.0, sharpe=2.2, health=85)
portfolio.update_strategy_metrics("strategy_b", pnl=150.0, sharpe=1.8, health=70)
portfolio.update_strategy_metrics("strategy_c", pnl=250.0, sharpe=2.5, health=90)

# Rebalance based on health
new_allocations = portfolio.rebalance_allocations(method="health")

print("Health-based allocations for 3 strategies:")
for strategy_id, allocation in sorted(new_allocations.items()):
    strategy = portfolio.strategies[strategy_id]
    print(f"  {strategy_id}: {allocation:.1%} (Health: {strategy.health})")

# Output:
#   strategy_a: 34.7%  (Health: 85)
#   strategy_b: 28.6%  (Health: 70)
#   strategy_c: 36.7%  (Health: 90)
```

---

## Example 8: Gradual Rebalancing / 示例 8：渐进式再平衡

**Scenario / 场景**: Gradually shift allocation over time instead of sudden changes.

随时间逐步调整分配，而不是突然改变。

```python
def gradual_rebalance(
    portfolio: PortfolioManager,
    target_allocations: Dict[str, float],
    step_size: float = 0.05,
) -> Dict[str, float]:
    """
    Gradually adjust allocations toward target.
    
    Args:
        portfolio: PortfolioManager instance
        target_allocations: Target allocation dict
        step_size: Maximum change per step (0-1)
    
    Returns:
        New allocations after gradual adjustment
    """
    current_allocations = {
        sid: portfolio.get_allocation_for_strategy(sid)
        for sid in target_allocations.keys()
    }
    
    new_allocations = {}
    for sid, target in target_allocations.items():
        current = current_allocations.get(sid, 0.0)
        diff = target - current
        
        # Limit change to step_size
        if abs(diff) > step_size:
            change = step_size if diff > 0 else -step_size
            new_allocations[sid] = current + change
        else:
            new_allocations[sid] = target
    
    # Apply new allocations
    for sid, alloc in new_allocations.items():
        portfolio.strategies[sid].allocation = alloc
    
    # Renormalize
    portfolio._normalize_allocations()
    
    return {sid: portfolio.get_allocation_for_strategy(sid) 
            for sid in new_allocations.keys()}

# Usage
portfolio = PortfolioManager(total_capital=10000.0)
portfolio.register_strategy("fixed_spread", "Fixed Spread", allocation=0.5)
portfolio.register_strategy("funding_rate", "Funding Rate", allocation=0.5)

# Calculate target allocations
target = portfolio.rebalance_allocations(method="sharpe")

# Apply gradually (5% max change per step)
new = gradual_rebalance(portfolio, target, step_size=0.05)
print(f"Gradual rebalance: {new}")
```

---

## Best Practices Summary / 最佳实践总结

1. **Start with equal allocation** when you have no performance data
2. **Set reasonable limits** (min 10-20%, max 50-70%)
3. **Rebalance monthly** or when performance diverges significantly
4. **Use composite score** for balanced allocation (not just Sharpe)
5. **Monitor correlation** between strategies
6. **Use gradual rebalancing** to avoid sudden large changes

1. **从等权重分配开始**（无表现数据时）
2. **设置合理限制**（最小 10-20%，最大 50-70%）
3. **每月再平衡**或表现显著分化时
4. **使用综合评分**进行平衡分配（不只是 Sharpe）
5. **监控策略间相关性**
6. **使用渐进式再平衡**避免突然大幅变化

---

## API Quick Reference / API 快速参考

```python
# Initialize
portfolio = PortfolioManager(
    total_capital=10000.0,
    min_allocation=0.1,
    max_allocation=0.7,
    auto_rebalance=False,
)

# Register strategy
portfolio.register_strategy(
    strategy_id="strategy_1",
    name="Strategy 1",
    allocation=0.5,
    status=StrategyStatus.LIVE,
)

# Update metrics
portfolio.update_strategy_metrics(
    strategy_id="strategy_1",
    pnl=100.0,
    sharpe=2.0,
    health=80,
)

# Rebalance
new_allocations = portfolio.rebalance_allocations(
    method="composite",  # or "sharpe", "health", "roi", "risk_adjusted", "equal"
    weights={"sharpe": 0.4, "roi": 0.3, "health": 0.3},
)

# Get allocation
allocation = portfolio.get_allocation_for_strategy("strategy_1")

# Set limits
portfolio.set_allocation_limits(min_allocation=0.15, max_allocation=0.65)
```

