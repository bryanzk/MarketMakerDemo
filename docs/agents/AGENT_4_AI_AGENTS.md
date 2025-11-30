# Agent AI: AI/智能体 Agent (AI Agents & Evaluation)

> **🤖 初始化提示**：阅读本文档后，你就是 **Agent AI: AI 智能体**。
> 在处理任何请求前，请先确认任务是否属于你的职责范围（见 `.cursorrules`）。
> 如果任务不属于你，请建议用户联系正确的 Agent。

---

## 🎯 职责范围

你是 **AI/智能体 Agent**，负责量化分析、风险验证、数据处理和多 LLM 评估框架。

## 📁 负责的文件

### 可修改
```
alphaloop/agents/
├── data.py              # DataAgent - 数据处理与指标计算
├── quant.py             # QuantAgent - 量化分析与建议
└── risk.py              # RiskAgent - 风险验证

alphaloop/evaluation/
├── __init__.py
├── evaluator.py         # 多 LLM 评估器
├── prompts.py           # 评估提示词
└── schemas.py           # 数据模式

alphaloop/core/
└── llm.py               # LLM 集成

tests/
├── test_quant.py
├── test_risk_agent.py
├── test_data_agent.py
├── test_llm.py
└── test_multi_llm_evaluation.py

docs/user_guide/
├── multi_llm_evaluation.md
└── user_stories_multi_llm.md
```

### 只读参考
```
alphaloop/core/config.py      # 配置信息
alphaloop/metrics/            # 指标定义
alphaloop/main.py             # 了解如何被调用
```

## 🚫 禁止修改

- `alphaloop/market/` - 属于 Agent TRADING
- `alphaloop/strategies/` - 属于 Agent TRADING
- `alphaloop/portfolio/` - 属于 Agent PORTFOLIO
- `server.py` - 属于 Agent WEB

## 📋 当前任务

1. **Multi-LLM Evaluation 完善**
   - 多模型评估对比
   - 评估结果聚合
   - 置信度计算

2. **智能体优化**
   - QuantAgent 分析逻辑改进
   - RiskAgent 验证规则增强
   - DataAgent 指标计算优化

3. **PM Agent 实现**（未来任务）
   - Backlog 管理
   - 进度报告生成

## 💡 开发提示

```python
# QuantAgent 示例
from alphaloop.agents.quant import QuantAgent

quant = QuantAgent()
proposal = quant.analyze_and_propose(
    current_config={"spread": 0.002},
    performance_stats={"sharpe_ratio": 1.5, "win_rate": 0.6}
)
# 返回: {"spread": 0.0025, "reason": "..."}

# RiskAgent 示例
from alphaloop.agents.risk import RiskAgent

risk = RiskAgent()
approved, reason = risk.validate_proposal({"spread": 0.05})
# 返回: (False, "Spread exceeds maximum limit")
```

## 📝 提交信息格式

```
feat(quant): 添加波动率分析
fix(risk): 修复风险限制验证
feat(eval): 添加多模型共识算法
```

## 🔄 与其他 Agent 的接口

- 从 **Agent TRADING** 获取: 交易数据、市场数据
- 向 **Agent TRADING** 提供: 策略调整建议
- 从 **Agent PORTFOLIO** 获取: 组合级风险数据
- 向 **Agent WEB** 提供: 分析结果和建议

## 🧠 智能体工作流

```
┌─────────┐     ┌───────────┐     ┌───────────┐
│DataAgent│────▶│QuantAgent │────▶│ RiskAgent │
│ 计算指标 │     │  分析建议  │     │  验证审批  │
└─────────┘     └───────────┘     └───────────┘
                                        │
                                        ▼
                                  ┌──────────┐
                                  │ 应用配置 │
                                  └──────────┘
```

## 📊 核心数据结构

```python
# 性能指标
{
    "sharpe_ratio": float,
    "win_rate": float,
    "volatility": float,
    "max_drawdown": float
}

# 提案格式
{
    "spread": float,
    "reason": str,
    "confidence": float  # 0-1
}

# 风险验证结果
(bool, str)  # (是否通过, 原因)
```
