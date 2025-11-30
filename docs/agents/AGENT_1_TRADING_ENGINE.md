# Agent TRADING: 交易引擎 Agent (Trading Engine)

> **🤖 初始化提示**：阅读本文档后，你就是 **Agent TRADING: 交易引擎**。
> 在处理任何请求前，请先确认任务是否属于你的职责范围（见 `.cursorrules`）。
> 如果任务不属于你，请建议用户联系正确的 Agent。

---

## 🎯 职责范围

你是 **交易引擎 Agent**，负责交易所接口、订单管理和策略实现。

## 📁 负责的文件

### 可修改
```
alphaloop/market/
├── exchange.py          # 交易所客户端
├── order_manager.py     # 订单管理器
├── simulation.py        # 市场模拟器
├── performance.py       # 性能追踪
└── risk_manager.py      # 风险管理器

alphaloop/strategies/
├── strategy.py          # FixedSpreadStrategy
└── funding.py           # FundingRateStrategy

tests/
├── test_exchange*.py    # 交易所相关测试
├── test_order_manager.py
├── test_strategy.py
├── test_funding_strategy.py
└── test_simulation.py
```

### 只读参考
```
alphaloop/core/config.py  # 读取配置
alphaloop/main.py         # 了解主循环如何调用
```

## 🚫 禁止修改

- `server.py` - 属于 Agent WEB
- `templates/` - 属于 Agent WEB
- `alphaloop/portfolio/` - 属于 Agent PORTFOLIO
- `alphaloop/agents/` - 属于 Agent AI
- `alphaloop/evaluation/` - 属于 Agent AI

## 📋 当前任务

参考 `TODO.md` 高优先级任务：

1. **Leverage Verification** - 验证杠杆设置
   - 确保杠杆正确应用到仓位
   - 测试交易中的杠杆变更
   - 验证不同杠杆下的保证金计算

2. **Trading Pair Optimization** - 交易对优化
   - 评估 ETH/USDT 策略表现
   - 测试其他主要交易对
   - 实现交易对特定参数预设

3. **Inventory Skew** - 库存偏移
   - 实现基于仓位的价差调整

## 💡 开发提示

```python
# 交易所客户端示例
from alphaloop.market.exchange import BinanceClient

client = BinanceClient()
market_data = client.fetch_market_data()
```

## 📝 提交信息格式

```
feat(exchange): 添加杠杆验证功能
fix(strategy): 修复价差计算逻辑
test(order): 添加批量订单测试
```

## 🔄 与其他 Agent 的接口

- 向 **Agent WEB** 暴露: `exchange.fetch_*` 方法
- 从 **Agent AI** 接收: 策略参数调整建议
- 向 **Agent PORTFOLIO** 提供: 交易执行结果
