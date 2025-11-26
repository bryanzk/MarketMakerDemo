# 多 LLM 策略评估系统用户指南

## 概述

多 LLM 策略评估系统允许交易员同时使用 **Gemini、OpenAI、Claude** 三家大语言模型分析相同的市场数据，获取不同的策略建议，并通过模拟交易比较各模型的表现，帮助交易员做出更明智的决策。

## 为什么需要多 LLM 评估？

| 痛点 | 解决方案 |
|-----|---------|
| 单一模型可能有偏见 | 三个模型交叉验证 |
| 不知道哪个模型更适合 | 通过模拟交易量化比较 |
| 决策缺乏信心 | 多数共识增强信心 |
| 参数调优困难 | AI 建议 + 模拟验证 |

## 功能特性

### 1. 多模型并行评估
- 同时调用 Gemini、OpenAI、Claude
- 统一的输入数据格式
- 并行处理，快速获取结果

### 2. 策略参数建议
每个模型会建议：
- **策略类型**：FixedSpread 或 FundingRate
- **价差 (spread)**：0.5% - 3%
- **倾斜因子 (skew_factor)**：50 - 200
- **交易数量 (quantity)**：0.05 - 0.5
- **杠杆倍数 (leverage)**：1x - 5x
- **置信度 (confidence)**：模型对建议的信心

### 3. 模拟交易验证
对每个模型的建议运行 500 步模拟交易：
- 计算 PnL（盈亏）
- 计算胜率
- 计算夏普比率
- 记录交易历史

### 4. 结果排名与对比
根据综合评分排名：
- PnL 权重：40%
- 夏普比率权重：30%
- 胜率权重：20%
- 置信度权重：10%

## 使用方式

### 方式一：命令行工具

```bash
# 运行多 LLM 评估
python -m alphaloop.evaluation.cli --symbol ETHUSDT

# 指定模拟步数
python -m alphaloop.evaluation.cli --symbol ETHUSDT --steps 1000

# 只使用特定模型
python -m alphaloop.evaluation.cli --symbol ETHUSDT --providers gemini,openai
```

### 方式二：Python API

```python
from alphaloop.evaluation import MultiLLMEvaluator, MarketContext
from alphaloop.core.llm import create_all_providers

# 1. 准备市场数据
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

# 2. 创建评估器
providers = create_all_providers()
evaluator = MultiLLMEvaluator(providers=providers, simulation_steps=500)

# 3. 运行评估
results = evaluator.evaluate(context)

# 4. 查看结果
print(MultiLLMEvaluator.generate_comparison_table(results))

# 5. 获取最佳建议
best = MultiLLMEvaluator.get_best_proposal(results)
print(f"推荐使用 {best.provider_name} 的建议")
```

### 方式三：Web Dashboard

访问 `http://localhost:8000/evaluation` 查看可视化界面：

1. 点击「开始评估」按钮
2. 等待三个模型返回结果（约 5-10 秒）
3. 查看对比表格和排名
4. 点击「应用最佳策略」一键使用

## 输出示例

### 对比表格

```
------------------------------------------------------------------------------------------------------------------------
 Rank |         Provider          |   Strategy   |  Spread  |  Skew  |  Conf  |    PnL     | WinRate |  Sharpe | Score  | Latency
------------------------------------------------------------------------------------------------------------------------
  1   |   Claude (claude-sonnet-4-20250514)   |  FundingRate |  0.0100  |  150   | 92.0%  |   $200.00  |  60.0%  |   2.50  |  92.0  |  1850ms
  2   |   Gemini (gemini-1.5-pro) |  FundingRate |  0.0120  |  120   | 85.0%  |   $180.00  |  58.0%  |   2.10  |  85.0  |  1250ms
  3   |   OpenAI (gpt-4o)         |  FixedSpread |  0.0150  |  100   | 78.0%  |   $120.00  |  52.0%  |   1.50  |  72.0  |  980ms
------------------------------------------------------------------------------------------------------------------------
```

### 最佳建议详情

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
  "reasoning": "当前资金费率为正且呈上升趋势，建议采用资金费率策略做空偏向，可赚取资金费用。较小的价差可增加成交率，较高的倾斜因子可放大资金费率收益。",
  "confidence": 0.92,
  "simulation_results": {
    "pnl": 200.00,
    "win_rate": 0.60,
    "sharpe_ratio": 2.50
  }
}
```

## 配置说明

### 环境变量

```bash
# .env 文件
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 配置文件

```python
# alphaloop/core/config.py
MULTI_LLM_CONFIG = {
    "simulation_steps": 500,      # 模拟步数
    "parallel": True,             # 是否并行调用
    "timeout_seconds": 30,        # 单个模型超时时间
    "scoring_weights": {
        "pnl": 0.40,
        "sharpe": 0.30,
        "win_rate": 0.20,
        "confidence": 0.10,
    }
}
```

## 最佳实践

### 1. 何时使用多 LLM 评估

✅ **推荐使用场景：**
- 市场状态不明朗时
- 调整策略参数前
- 每日开盘前的策略审查
- 重大行情变化后

❌ **不推荐使用场景：**
- 紧急行情需要快速决策
- API 额度有限时
- 网络不稳定时

### 2. 解读评估结果

| 情况 | 建议操作 |
|-----|---------|
| 三个模型一致 | 高信心执行 |
| 两个模型一致 | 参考多数意见 |
| 三个模型分歧 | 保守操作或等待 |
| 最高分 < 60 | 暂不操作 |

### 3. 结合风控使用

所有建议都会经过 `RiskAgent` 验证：
- 检查参数是否在安全范围
- 验证杠杆是否合规
- 确认不会触发风控警报

## 常见问题

### Q: 为什么某个模型没有返回结果？
A: 可能原因：
1. API Key 未配置
2. 网络超时
3. API 额度耗尽

### Q: 模拟结果和实盘差异大怎么办？
A: 模拟器使用简化的市场模型，建议：
1. 小仓位先测试
2. 逐步调整参数
3. 记录实盘结果对比

### Q: 如何降低 API 成本？
A: 建议：
1. 减少评估频率（每小时一次）
2. 使用更便宜的模型版本
3. 只在关键时刻使用

## 下一步

- 查看 [用户故事](./user_stories_multi_llm.md) 了解具体使用场景
- 查看 [API 文档](../api_reference.md) 了解详细接口
- 查看 [策略开发指南](../strategy_development_guide.md) 自定义策略

