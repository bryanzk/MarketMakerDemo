# Error Handling Guide / 错误处理指南

## Overview / 概述

The trading engine implements comprehensive error handling to ensure robust operation and provide clear feedback when issues occur. Errors are captured, logged, and displayed to users through strategy instance alerts.

交易引擎实现了全面的错误处理机制，确保系统稳定运行，并在出现问题时提供清晰的反馈。错误会被捕获、记录，并通过策略实例的警报显示给用户。

---

## Error Types / 错误类型

### 1. Insufficient Funds / 资金不足

**Error Type**: `insufficient_funds`

**When it occurs**: / 何时发生
- Account balance is too low to place an order / 账户余额不足以下单
- Margin is insufficient for leveraged positions / 杠杆仓位的保证金不足
- For sell orders: insufficient position size / 卖单：持仓数量不足

**Example Error Message**:
```
Insufficient balance to place sell order: binanceusdm {"code":-2019,"msg":"Margin is insufficient."}
```

**User Suggestion**:
- Check your account balance and margin / 检查账户余额和保证金
- Consider reducing order quantity or closing existing positions / 考虑减少订单数量或平仓现有仓位
- For sell orders, ensure you have sufficient position size / 对于卖单，确保有足够的持仓数量

### 2. Invalid Order / 无效订单

**Error Type**: `invalid_order`

**When it occurs**: / 何时发生
- Order parameters violate exchange rules / 订单参数违反交易所规则
- Price precision exceeds maximum allowed / 价格精度超过允许的最大值
- Quantity below minimum requirement / 数量低于最小要求

**User Suggestion**:
- Order parameters may be invalid / 订单参数可能无效
- Check price, quantity, and symbol settings / 检查价格、数量和交易对设置
- Verify order limits (min quantity, min notional) / 验证订单限制（最小数量、最小名义价值）

### 3. Exchange Error / 交易所错误

**Error Type**: `exchange_error`

**When it occurs**: / 何时发生
- Generic Binance API errors / 通用 Binance API 错误
- Exchange-side validation failures / 交易所端验证失败

**User Suggestion**:
- Exchange API error occurred / 交易所 API 错误
- This may be temporary - the system will retry in the next cycle / 这可能是临时问题，系统会在下一个周期重试
- If it persists, check Binance API status / 如果持续存在，请检查 Binance API 状态

### 4. Network Error / 网络错误

**Error Type**: `network_error`

**When it occurs**: / 何时发生
- Connection timeout / 连接超时
- Network interruption / 网络中断

**User Suggestion**:
- Check network connectivity / 检查网络连接
- The system will automatically retry / 系统会自动重试

### 5. Rate Limit / 频率限制

**Error Type**: `rate_limit`

**When it occurs**: / 何时发生
- Too many API requests in a short time / 短时间内 API 请求过多

**User Suggestion**:
- The system will pause briefly and retry / 系统会短暂暂停后重试
- Consider reducing trading frequency / 考虑降低交易频率

---

## Error Handling Flow / 错误处理流程

### 1. Error Capture / 错误捕获

When an order fails, the error is captured in `BinanceClient.last_order_error`:

```python
# In exchange.py
except InsufficientFunds as e:
    error_msg = f"Insufficient balance to place {order['side']} order: {str(e)}"
    self.last_order_error = {
        "type": "insufficient_funds",
        "message": error_msg,
        "symbol": self.symbol,
        "order": order,
        "details": {...}
    }
    continue  # Continue with other orders
```

### 2. Error Propagation / 错误传递

The error is then propagated to the strategy instance:

```python
# In main.py _run_strategy_instance_cycle
if hasattr(self.exchange, "last_order_error") and self.exchange.last_order_error:
    err = self.exchange.last_order_error
    error_type = err.get("type", "unknown")
    
    # Record in error history
    instance.error_history.append({
        "timestamp": time.time(),
        "type": error_type,
        "message": err.get("message", ""),
        "strategy_id": instance.strategy_id,
        ...
    })
    
    # Set alert for critical errors
    if error_type in ["insufficient_funds", "invalid_order", "exchange_error"]:
        instance.alert = {
            "type": "error",
            "message": error_msg,
            "suggestion": self._get_error_suggestion(error_type, err),
        }
```

### 3. Error Display / 错误显示

Errors are accessible through the status API:

```python
status = engine.get_status()
for strategy_id, instance_status in status["strategy_instances"].items():
    if instance_status.get("alert"):
        print(f"Alert: {instance_status['alert']}")
```

---

## Multi-Strategy Error Isolation / 多策略错误隔离

Each strategy instance maintains its own error history and alerts:

每个策略实例维护自己的错误历史和警报：

```python
# Strategy 1 has an error
engine.strategy_instances["default"].alert = {
    "type": "error",
    "message": "Insufficient balance...",
    "suggestion": "..."
}

# Strategy 2 continues normally
engine.strategy_instances["strategy_2"].alert = None
```

**Benefits** / 优势:
- Errors in one strategy don't affect others / 一个策略的错误不影响其他策略
- Independent error tracking / 独立的错误跟踪
- Per-strategy recovery / 每个策略独立恢复

---

## Error Recovery / 错误恢复

### Automatic Recovery / 自动恢复

1. **Network Errors**: System automatically retries in next cycle / 网络错误：系统在下一个周期自动重试
2. **Rate Limits**: System pauses and retries / 频率限制：系统暂停后重试
3. **Temporary Exchange Errors**: Retried automatically / 临时交易所错误：自动重试

### Manual Recovery / 手动恢复

For persistent errors like insufficient funds:

对于持续错误（如资金不足）：

1. **Check Account Balance** / 检查账户余额
   ```python
   account_data = exchange.fetch_account_data()
   print(f"Balance: {account_data['balance']}")
   print(f"Position: {account_data['position_amt']}")
   ```

2. **Adjust Strategy Parameters** / 调整策略参数
   ```python
   instance = engine.strategy_instances["default"]
   instance.strategy.quantity = 0.01  # Reduce quantity
   ```

3. **Close Positions** / 平仓
   - Close existing positions to free up margin / 平仓现有仓位以释放保证金

---

## Best Practices / 最佳实践

### 1. Monitor Alerts / 监控警报

Regularly check strategy instance alerts:

定期检查策略实例的警报：

```python
status = engine.get_status()
for strategy_id, instance_status in status["strategy_instances"].items():
    alert = instance_status.get("alert")
    if alert:
        logger.warning(f"Strategy {strategy_id}: {alert['message']}")
        logger.info(f"Suggestion: {alert['suggestion']}")
```

### 2. Error History Review / 错误历史审查

Review error history to identify patterns:

审查错误历史以识别模式：

```python
instance = engine.strategy_instances["default"]
for error in instance.error_history:
    if error["type"] == "insufficient_funds":
        # Analyze when this occurs
        print(f"Time: {error['timestamp']}, Order: {error.get('order')}")
```

### 3. Proactive Monitoring / 主动监控

- Set up alerts for critical errors / 为关键错误设置警报
- Monitor account balance regularly / 定期监控账户余额
- Track error frequency / 跟踪错误频率

---

## API Reference / API 参考

### StrategyInstance.alert

```python
{
    "type": "error" | "warning",
    "message": "Error description",
    "suggestion": "User-friendly suggestion"
}
```

### StrategyInstance.error_history

```python
[
    {
        "timestamp": float,
        "type": "insufficient_funds" | "invalid_order" | ...,
        "message": str,
        "symbol": str,
        "strategy_id": str,
        "strategy_type": str,
        "details": dict
    },
    ...
]
```

### AlphaLoop._get_error_suggestion()

```python
suggestion = engine._get_error_suggestion(error_type, error_details)
# Returns user-friendly suggestion string
```

---

## Troubleshooting / 故障排除

### Q: Why am I getting insufficient funds errors? / 为什么会出现资金不足错误？

**A**: Common causes / 常见原因：
1. Account balance is too low / 账户余额过低
2. Leverage requires more margin than available / 杠杆需要的保证金超过可用余额
3. Existing positions are using margin / 现有仓位占用了保证金
4. For sell orders: no position to sell / 卖单：没有可卖的仓位

**Solution** / 解决方案：
- Check `fetch_account_data()` for current balance / 检查 `fetch_account_data()` 获取当前余额
- Reduce order quantity / 减少订单数量
- Close some positions / 平仓部分仓位
- Increase account balance / 增加账户余额

### Q: How do I clear an alert? / 如何清除警报？

**A**: Alerts are automatically cleared when:
警报会在以下情况自动清除：
- The error condition is resolved / 错误条件已解决
- A successful order is placed / 成功下单
- The strategy instance is reset / 策略实例被重置

Manual clearing / 手动清除：
```python
instance.alert = None
```

### Q: Can I continue trading with errors? / 出现错误后还能继续交易吗？

**A**: Yes, the system continues processing other orders:
可以，系统会继续处理其他订单：
- Errors in one order don't stop other orders / 一个订单的错误不会阻止其他订单
- Each strategy instance operates independently / 每个策略实例独立运行
- Only the failed order is skipped / 只有失败的订单会被跳过

---

## Related Documentation / 相关文档

- [Architecture](./../architecture.md) - System architecture overview / 系统架构概览
- [Trading Strategy](./../trading_strategy.md) - Strategy implementation / 策略实现
- [Risk Management](./risk_indicators.md) - Risk control / 风险控制

