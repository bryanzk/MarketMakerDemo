# Multi-LLM Strategy Evaluation System User Guide / 多 LLM 策略评估系统用户指南

## Overview / 概述

The Multi-LLM Strategy Evaluation System allows traders to simultaneously use **Gemini, OpenAI, and Claude** to analyze the same market data, obtain different strategy recommendations, compare model performance through simulated trading, and help traders make more informed decisions.

多 LLM 策略评估系统允许交易员同时使用 **Gemini、OpenAI、Claude** 三家大语言模型分析相同的市场数据，获取不同的策略建议，并通过模拟交易比较各模型的表现，帮助交易员做出更明智的决策。

---

## Why Multi-LLM Evaluation? / 为什么需要多 LLM 评估？

| Pain Point / 痛点 | Solution / 解决方案 |
|-----|---------|
| Single model may have bias / 单一模型可能有偏见 | Cross-validation with three models / 三个模型交叉验证 |
| Unknown which model fits better / 不知道哪个模型更适合 | Quantitative comparison via simulation / 通过模拟交易量化比较 |
| Lack of decision confidence / 决策缺乏信心 | Majority consensus builds confidence / 多数共识增强信心 |
| Difficult parameter tuning / 参数调优困难 | AI suggestions + simulation validation / AI 建议 + 模拟验证 |

---

## Features / 功能特性

### 1. Multi-Model Parallel Evaluation / 多模型并行评估
- Simultaneously call Gemini, OpenAI, Claude / 同时调用 Gemini、OpenAI、Claude
- Unified input data format / 统一的输入数据格式
- Parallel processing for fast results / 并行处理，快速获取结果

### 2. Strategy Parameter Suggestions / 策略参数建议

Each model will suggest: / 每个模型会建议：
- **Strategy Type / 策略类型**：FixedSpread or FundingRate
- **Spread / 价差**：0.5% - 3%
- **Skew Factor / 倾斜因子**：50 - 200
- **Quantity / 交易数量**：0.05 - 0.5
- **Leverage / 杠杆倍数**：1x - 5x
- **Confidence / 置信度**：Model's confidence in suggestion / 模型对建议的信心

### 3. Simulation Trading Validation / 模拟交易验证

Run 500-step simulation for each model's suggestion: / 对每个模型的建议运行 500 步模拟交易：
- Calculate PnL / 计算 PnL（盈亏）
- Calculate Win Rate / 计算胜率
- Calculate Sharpe Ratio / 计算夏普比率
- Record Trade History / 记录交易历史

### 4. Result Ranking and Comparison / 结果排名与对比

Ranking based on composite score: / 根据综合评分排名：
- PnL Weight / PnL 权重：40%
- Sharpe Ratio Weight / 夏普比率权重：30%
- Win Rate Weight / 胜率权重：20%
- Confidence Weight / 置信度权重：10%

---

## Usage / 使用方式

### Method 1: Command Line Tool / 方式一：命令行工具

```bash
# Run multi-LLM evaluation / 运行多 LLM 评估
python -m alphaloop.evaluation.cli --symbol ETHUSDT

# Specify simulation steps / 指定模拟步数
python -m alphaloop.evaluation.cli --symbol ETHUSDT --steps 1000

# Use specific models only / 只使用特定模型
python -m alphaloop.evaluation.cli --symbol ETHUSDT --providers gemini,openai
```

### Method 2: Python API / 方式二：Python API

```python
from alphaloop.evaluation import MultiLLMEvaluator, MarketContext
from alphaloop.core.llm import create_all_providers

# 1. Prepare market data / 准备市场数据
context = MarketContext(
    symbol="ETHUSDT",
    mid_price=2500.0,
    best_bid=2499.5,
    best_ask=2500.5,
    spread_bps=4.0,
    volatility_24h=0.035,
    volatility_1h=0.012,
    funding_rate=0.0001,
    funding_rate_trend="rising",
)

# 2. Create evaluator / 创建评估器
providers = create_all_providers()
evaluator = MultiLLMEvaluator(providers=providers, simulation_steps=500)

# 3. Run evaluation / 运行评估
results = evaluator.evaluate(context)

# 4. View results / 查看结果
print(MultiLLMEvaluator.generate_comparison_table(results))

# 5. Get best proposal / 获取最佳建议
best = MultiLLMEvaluator.get_best_proposal(results)
print(f"Recommended: {best.provider_name} / 推荐使用 {best.provider_name} 的建议")
```

### Method 3: Web Dashboard / 方式三：Web Dashboard

Visit `http://localhost:8000/evaluation` for the visualization interface: / 访问 `http://localhost:8000/evaluation` 查看可视化界面：

1. Click "Start Evaluation" button / 点击「开始评估」按钮
2. Wait for three models to return results (about 5-10 seconds) / 等待三个模型返回结果（约 5-10 秒）
3. View comparison table and rankings / 查看对比表格和排名
4. Click "Apply Best Strategy" to use with one click / 点击「应用最佳策略」一键使用

---

## Output Examples / 输出示例

### Comparison Table / 对比表格

```
------------------------------------------------------------------------------------------------------------------------
| Rank |         Provider          |   Strategy   |  Spread  |  Skew  |  Conf  |    PnL     | WinRate |  Sharpe | Score  | Latency
------------------------------------------------------------------------------------------------------------------------
|  1   |   Claude (claude-sonnet-4-20250514)   |  FundingRate |  0.0100  |  150   | 92.0%  |   $200.00  |  60.0%  |   2.50  |  92.0  |  1850ms
|  2   |   Gemini (gemini-1.5-pro) |  FundingRate |  0.0120  |  120   | 85.0%  |   $180.00  |  58.0%  |   2.10  |  85.0  |  1250ms
|  3   |   OpenAI (gpt-4o)         |  FixedSpread |  0.0150  |  100   | 78.0%  |   $120.00  |  52.0%  |   1.50  |  72.0  |  980ms
------------------------------------------------------------------------------------------------------------------------
```

### Best Proposal Details / 最佳建议详情

```json
{
  "provider": "Claude (claude-sonnet-4-20250514)",
  "recommended_strategy": "FundingRate",
  "parameters": {
    "spread": 0.010,
    "skew_factor": 150,
    "quantity": 0.15,
    "leverage": 2.5
  },
  "reasoning": "Current funding rate is positive and rising, suggesting a funding rate strategy with short bias to earn funding fees. Smaller spread increases fill rate, higher skew factor amplifies funding rate returns. / 当前资金费率为正且呈上升趋势，建议采用资金费率策略做空偏向，可赚取资金费用。较小的价差可增加成交率，较高的倾斜因子可放大资金费率收益。",
  "confidence": 0.92,
  "simulation_results": {
    "pnl": 200.00,
    "win_rate": 0.60,
    "sharpe_ratio": 2.50
  }
}
```

---

## Configuration / 配置说明

### Environment Variables / 环境变量

```bash
# .env file / .env 文件
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### Configuration File / 配置文件

```python
# alphaloop/core/config.py
MULTI_LLM_CONFIG = {
    "simulation_steps": 500,      # Simulation steps / 模拟步数
    "parallel": True,             # Enable parallel calls / 是否并行调用
    "timeout_seconds": 30,        # Single model timeout / 单个模型超时时间
    "scoring_weights": {
        "pnl": 0.40,
        "sharpe": 0.30,
        "win_rate": 0.20,
        "confidence": 0.10,
    }
}
```

---

## Best Practices / 最佳实践

### 1. When to Use Multi-LLM Evaluation / 何时使用多 LLM 评估

✅ **Recommended Scenarios / 推荐使用场景：**
- When market conditions are unclear / 市场状态不明朗时
- Before adjusting strategy parameters / 调整策略参数前
- Daily pre-market strategy review / 每日开盘前的策略审查
- After significant market changes / 重大行情变化后

❌ **Not Recommended Scenarios / 不推荐使用场景：**
- Urgent situations requiring quick decisions / 紧急行情需要快速决策
- When API quota is limited / API 额度有限时
- When network is unstable / 网络不稳定时

### 2. Interpreting Evaluation Results / 解读评估结果

| Situation / 情况 | Recommended Action / 建议操作 |
|-----|---------|
| Three models agree / 三个模型一致 | Execute with high confidence / 高信心执行 |
| Two models agree / 两个模型一致 | Follow majority opinion / 参考多数意见 |
| Three models disagree / 三个模型分歧 | Act conservatively or wait / 保守操作或等待 |
| Highest score < 60 | Do not act for now / 暂不操作 |

### 3. Combining with Risk Control / 结合风控使用

All suggestions are validated by `RiskAgent`: / 所有建议都会经过 `RiskAgent` 验证：
- Check if parameters are within safe range / 检查参数是否在安全范围
- Verify leverage compliance / 验证杠杆是否合规
- Confirm no risk alerts will be triggered / 确认不会触发风控警报

---

## FAQ / 常见问题

### Q: Why did a model not return results? / 为什么某个模型没有返回结果？
A: Possible reasons: / 可能原因：
1. API Key not configured / API Key 未配置
2. Network timeout / 网络超时
3. API quota exhausted / API 额度耗尽

### Q: What if simulation results differ significantly from live trading? / 模拟结果和实盘差异大怎么办？
A: The simulator uses a simplified market model. Suggestions: / 模拟器使用简化的市场模型，建议：
1. Test with small positions first / 小仓位先测试
2. Gradually adjust parameters / 逐步调整参数
3. Record live results for comparison / 记录实盘结果对比

### Q: How to reduce API costs? / 如何降低 API 成本？
A: Suggestions: / 建议：
1. Reduce evaluation frequency (once per hour) / 减少评估频率（每小时一次）
2. Use cheaper model versions / 使用更便宜的模型版本
3. Only use at critical moments / 只在关键时刻使用

---

## Next Steps / 下一步

- See [User Stories](./user_stories_multi_llm.md) for specific use cases / 查看 [用户故事](./user_stories_multi_llm.md) 了解具体使用场景
- See [API Reference](../api_reference.md) for detailed interfaces / 查看 [API 文档](../api_reference.md) 了解详细接口
- See [Strategy Development Guide](../strategy_development_guide.md) for custom strategies / 查看 [策略开发指南](../strategy_development_guide.md) 自定义策略
