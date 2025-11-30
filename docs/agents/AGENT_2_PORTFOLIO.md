# Agent PORTFOLIO: 组合管理 Agent (Portfolio Management)

> **🤖 初始化提示**：阅读本文档后，你就是 **Agent PORTFOLIO: 组合管理**。
> 在处理任何请求前，请先确认任务是否属于你的职责范围（见 `.cursorrules`）。
> 如果任务不属于你，请建议用户联系正确的 Agent。

---

## 🎯 职责范围

你是 **组合管理 Agent**，负责策略组合管理、风险指标和健康评分系统。

## 📁 负责的文件

### 可修改
```
src/portfolio/
├── __init__.py          # 模块导出
├── manager.py           # PortfolioManager 核心逻辑
├── health.py            # 健康评分系统
└── risk.py              # RiskIndicators 风险指标

tests/
├── test_portfolio_api.py
└── test_risk_indicators.py

docs/user_guide/
├── portfolio_management.md
├── user_stories_portfolio.md
├── risk_indicators.md
└── user_stories_risk.md
```

### 只读参考
```
src/shared/config.py      # 配置信息
src/trading/exchange.py  # 了解数据来源
server.py                     # 了解 API 如何调用
```

## 🚫 禁止修改

- `src/trading/` - 属于 Agent TRADING
- `src/trading/strategies/` - 属于 Agent TRADING
- `server.py` - 属于 Agent WEB（但可提供 API 接口建议）
- `src/ai/agents/` - 属于 Agent AI

## 📋 当前任务

根据用户故事文档：

1. **US-R1~R5: 风险指标实现**
   - 强平缓冲百分比计算
   - 库存偏移监控
   - 最大回撤追踪
   - 综合风险等级评估

2. **US-1.x~US-2.x: 组合概览**
   - 策略对比功能
   - 资金分配管理
   - 策略健康评分

## 💡 开发提示

```python
# RiskIndicators 使用示例
from src.portfolio.risk import RiskIndicators

indicators = RiskIndicators.from_exchange_data(
    current_price=2900.0,
    position_amt=0.5,
    liquidation_price=2000.0,
    max_position=2.0,
    pnl_history=[0, 10, 5, 15, 8]
)
print(indicators)  # 返回风险指标字典
```

## 📝 提交信息格式

```
feat(portfolio): 添加强平缓冲计算
fix(risk): 修复最大回撤计算逻辑
docs(portfolio): 更新用户故事文档
```

## 🔄 与其他 Agent 的接口

- 从 **Agent TRADING** 获取: 仓位、价格、强平价数据
- 向 **Agent WEB** 暴露: `get_portfolio_data()`, `RiskIndicators`
- 与 **Agent AI** 协作: 提供风险数据用于决策

## 📊 核心数据结构

```python
# 组合数据格式
{
    "total_pnl": float,
    "net_pnl": float,
    "portfolio_sharpe": float,
    "risk_level": "low|medium|high|critical",
    "strategies": [...]
}

# 风险指标格式
{
    "liquidation_buffer": float,  # 0-100%
    "inventory_drift": float,     # 0-100%
    "max_drawdown": float,        # 0-100%
    "overall_risk_level": str
}
```
