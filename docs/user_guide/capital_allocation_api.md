# Capital Allocation API Reference / 资金分配 API 参考

## Overview / 概述

This document describes the API endpoints for managing capital allocation across multiple trading strategies.

本文档描述用于管理多个交易策略间资金分配的 API 端点。

---

## Endpoints / 端点

### 1. GET /api/portfolio/allocation

Get current capital allocation for all strategies.

获取所有策略的当前资金分配情况。

**Response / 响应**:
```json
{
  "total_capital": 10000.0,
  "min_allocation": 0.1,
  "max_allocation": 0.7,
  "auto_rebalance": false,
  "strategies": [
    {
      "strategy_id": "fixed_spread",
      "name": "Fixed Spread",
      "allocation": 0.6,
      "allocated_capital": 6000.0,
      "status": "live"
    },
    {
      "strategy_id": "funding_rate",
      "name": "Funding Rate",
      "allocation": 0.4,
      "allocated_capital": 4000.0,
      "status": "live"
    }
  ]
}
```

---

### 2. POST /api/portfolio/rebalance

Manually trigger capital rebalancing.

手动触发资金再平衡。

**Request Body / 请求体**:
```json
{
  "method": "composite",
  "weights": {
    "sharpe": 0.4,
    "roi": 0.3,
    "health": 0.3
  }
}
```

**Supported Methods / 支持的方法**:
- `"equal"`: Equal allocation / 等权重分配
- `"sharpe"`: Sharpe ratio weighted / 夏普比率加权
- `"health"`: Health score weighted / 健康度加权
- `"roi"`: ROI weighted / ROI 加权
- `"composite"`: Composite score (requires weights) / 综合评分（需要权重）
- `"risk_adjusted"`: Risk-adjusted allocation / 风险调整分配

**Response / 响应**:
```json
{
  "method": "composite",
  "new_allocations": {
    "fixed_spread": 0.55,
    "funding_rate": 0.45
  },
  "total_capital": 10000.0
}
```

---

### 3. PUT /api/portfolio/allocation/limits

Update allocation limits (min/max).

更新分配限制（最小/最大）。

**Request Body / 请求体**:
```json
{
  "min_allocation": 0.15,
  "max_allocation": 0.65
}
```

**Note / 注意**: Both fields are optional. Only provided fields will be updated.

两个字段都是可选的。只更新提供的字段。

**Response / 响应**:
```json
{
  "min_allocation": 0.15,
  "max_allocation": 0.65,
  "message": "Allocation limits updated successfully"
}
```

---

### 4. PUT /api/portfolio/strategy/{strategy_id}/allocation

Manually set allocation for a specific strategy.

手动设置特定策略的分配。

**Path Parameters / 路径参数**:
- `strategy_id`: Strategy identifier (e.g., "fixed_spread")

**Request Body / 请求体**:
```json
{
  "allocation": 0.7
}
```

**Response / 响应**:
```json
{
  "strategy_id": "fixed_spread",
  "old_allocation": 0.6,
  "new_allocation": 0.7,
  "allocated_capital": 7000.0,
  "all_strategies": {
    "fixed_spread": 0.7,
    "funding_rate": 0.3
  }
}
```

**Note / 注意**: After setting one strategy's allocation, all allocations are automatically normalized to sum to 100%.

设置一个策略的分配后，所有分配会自动归一化，总和为 100%。

---

### 5. GET /api/portfolio/strategy/{strategy_id}/allocation

Get allocation for a specific strategy.

获取特定策略的分配。

**Path Parameters / 路径参数**:
- `strategy_id`: Strategy identifier

**Response / 响应**:
```json
{
  "strategy_id": "fixed_spread",
  "name": "Fixed Spread",
  "allocation": 0.6,
  "allocated_capital": 6000.0,
  "total_capital": 10000.0
}
```

---

## Usage Examples / 使用示例

### Example 1: Check Current Allocation / 示例 1：查看当前分配

```bash
curl http://localhost:8000/api/portfolio/allocation
```

### Example 2: Rebalance Based on Sharpe Ratio / 示例 2：基于夏普比率再平衡

```bash
curl -X POST http://localhost:8000/api/portfolio/rebalance \
  -H "Content-Type: application/json" \
  -d '{"method": "sharpe"}'
```

### Example 3: Set Allocation Limits / 示例 3：设置分配限制

```bash
curl -X PUT http://localhost:8000/api/portfolio/allocation/limits \
  -H "Content-Type: application/json" \
  -d '{"min_allocation": 0.2, "max_allocation": 0.6}'
```

### Example 4: Manually Adjust Strategy Allocation / 示例 4：手动调整策略分配

```bash
curl -X PUT http://localhost:8000/api/portfolio/strategy/fixed_spread/allocation \
  -H "Content-Type: application/json" \
  -d '{"allocation": 0.7}'
```

### Example 5: Composite Rebalancing / 示例 5：综合评分再平衡

```bash
curl -X POST http://localhost:8000/api/portfolio/rebalance \
  -H "Content-Type: application/json" \
  -d '{
    "method": "composite",
    "weights": {
      "sharpe": 0.4,
      "roi": 0.3,
      "health": 0.3
    }
  }'
```

---

## Error Responses / 错误响应

### Strategy Not Found / 策略不存在

```json
{
  "error": "Strategy 'nonexistent' not found"
}
```

### Invalid Allocation Value / 无效的分配值

```json
{
  "error": "Allocation must be between 0 and 1"
}
```

---

## Integration with Frontend / 前端集成

These endpoints can be used to build a capital allocation management UI:

这些端点可用于构建资金分配管理界面：

1. **Display current allocations**: Use `GET /api/portfolio/allocation`
2. **Rebalance button**: Use `POST /api/portfolio/rebalance`
3. **Allocation slider/input**: Use `PUT /api/portfolio/strategy/{id}/allocation`
4. **Settings panel**: Use `PUT /api/portfolio/allocation/limits`

---

## Best Practices / 最佳实践

1. **Check allocation before rebalancing**: Always call `GET /api/portfolio/allocation` first
2. **Set reasonable limits**: Use `PUT /api/portfolio/allocation/limits` to prevent extreme allocations
3. **Monitor after rebalancing**: Check the new allocations and verify they meet your expectations
4. **Use composite method for balanced allocation**: The composite method considers multiple factors

1. **再平衡前检查分配**：先调用 `GET /api/portfolio/allocation`
2. **设置合理限制**：使用 `PUT /api/portfolio/allocation/limits` 防止极端分配
3. **再平衡后监控**：检查新分配并验证是否符合预期
4. **使用综合方法进行平衡分配**：综合方法考虑多个因素

---

## Update Log / 更新日志

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2024-01 | Initial API implementation |

