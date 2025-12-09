# LLM 推理过程深度解析 / Deep Dive into LLM Reasoning Process

## 概述 / Overview

本文档详细解释 LLM 如何基于市场数据进行分析和推理，生成具体的策略参数建议。

This document explains in detail how LLMs analyze market data and reason to generate specific strategy parameter recommendations.

---

## 一、LLM 推理的认知架构 / Cognitive Architecture of LLM Reasoning

### 1.1 信息处理流程 / Information Processing Flow

```
输入数据 (Input Data)
    ↓
数据理解 (Data Comprehension)
    ↓
模式识别 (Pattern Recognition)
    ↓
关联分析 (Correlation Analysis)
    ↓
参数推导 (Parameter Derivation)
    ↓
置信度评估 (Confidence Assessment)
    ↓
输出建议 (Output Recommendation)
```

### 1.2 LLM 的知识基础 / LLM's Knowledge Base

LLM 在推理时依赖以下知识：

1. **量化交易原理 / Quantitative Trading Principles**:
   - 做市策略的基本机制
   - 价差、数量、杠杆的相互关系
   - 风险与收益的权衡

2. **市场微观结构 / Market Microstructure**:
   - 价差与流动性的关系
   - 波动率对策略的影响
   - 资金费率的作用机制

3. **风险管理原则 / Risk Management Principles**:
   - 杠杆与波动率的关系
   - 仓位管理与资金管理
   - 止损与风险控制

---

## 二、市场数据解读 / Market Data Interpretation

### 2.1 数据输入结构 / Input Data Structure

LLM 接收以下结构化数据：

```python
MarketContext {
    # 价格数据 / Price Data
    symbol: "ETHUSDT"
    mid_price: 2500.0
    best_bid: 2499.5
    best_ask: 2500.5
    spread_bps: 4.0
    
    # 波动率 / Volatility
    volatility_24h: 0.035  # 3.5%
    volatility_1h: 0.012    # 1.2%
    
    # 资金费率 / Funding Rate
    funding_rate: 0.0001   # 0.01%
    funding_rate_trend: "rising"
    
    # 持仓信息 / Position
    current_position: 0.0
    position_side: "neutral"
    unrealized_pnl: 0.0
    current_leverage: 1.0
    
    # 账户状态 / Account
    available_balance: 10000.0
    
    # 历史绩效 / Performance
    win_rate: 0.52
    sharpe_ratio: 1.20
    recent_pnl: 100.0
}
```

### 2.2 LLM 的数据理解过程 / LLM's Data Comprehension Process

#### Step 1: 市场状态识别 / Market State Identification

LLM 首先识别当前市场状态：

**低波动市场 / Low Volatility Market**:
- 24h 波动率 < 5%
- 1h 波动率 < 2%
- 市场价差 < 10 bps
- **判断**: 适合做市策略，风险较低

**高波动市场 / High Volatility Market**:
- 24h 波动率 > 10%
- 1h 波动率 > 5%
- 市场价差 > 20 bps
- **判断**: 需要更保守的参数，价差要更大

**趋势市场 / Trending Market**:
- 资金费率趋势明显（rising/falling）
- 持仓方向与趋势一致
- **判断**: 可能需要调整 skew_factor 或降低杠杆

#### Step 2: 风险水平评估 / Risk Level Assessment

LLM 评估整体风险水平：

**低风险场景 / Low Risk Scenario**:
- 波动率低 + 价差小 + 无持仓 + 低杠杆
- **策略**: 可以更激进，价差更小，数量更大

**中风险场景 / Medium Risk Scenario**:
- 波动率中等 + 有持仓 + 中等杠杆
- **策略**: 平衡参数，适度保守

**高风险场景 / High Risk Scenario**:
- 波动率高 + 大持仓 + 高杠杆
- **策略**: 非常保守，价差大，数量小，降低杠杆

---

## 三、参数推导逻辑 / Parameter Derivation Logic

### 3.1 价差 (Spread) 推导 / Spread Derivation

#### 推理公式 / Reasoning Formula

```
基础价差 = 市场价差 × 安全系数
安全系数 = f(波动率, 资金费率, 历史绩效)

如果 波动率低:
    安全系数 = 1.5 - 2.0  (价差略大于市场价差)
如果 波动率高:
    安全系数 = 2.5 - 4.0  (价差显著大于市场价差)
```

#### 实际推理示例 / Real Reasoning Example

**场景 1: 低波动市场**
```
市场数据:
- 市场价差: 4 bps
- 24h 波动率: 3.5%
- 1h 波动率: 1.2%

LLM 推理:
"Market spread is currently ~4 bps (0.04%) with low-to-moderate 
short-term volatility (1h vol 1.2%, 24h vol 3.5%). A FixedSpread 
market making strategy fits low-to-moderate volatility environments. 
We want a spread wide enough to cover taker fees, inventory risk, 
and short-term volatility, but tight enough to get filled."

推导结果:
- 建议价差: 8-12 bps (0.0008 - 0.0012)
- 理由: 略大于市场价差，覆盖成本和风险，但仍保持竞争力
```

**场景 2: 高波动市场**
```
市场数据:
- 市场价差: 20 bps
- 24h 波动率: 15%
- 1h 波动率: 8%

LLM 推理:
"High volatility detected (1h vol 8%, 24h vol 15%). Market spread 
is already wide at 20 bps, indicating high uncertainty. We need 
to set spread even wider to protect against adverse price movements 
and reduce inventory risk."

推导结果:
- 建议价差: 30-50 bps (0.003 - 0.005)
- 理由: 显著大于市场价差，充分覆盖波动风险
```

#### 价差决策树 / Spread Decision Tree

```
市场价差 (Market Spread)
    ├─ < 5 bps (极窄)
    │   └─ 建议: 8-12 bps (2-3倍市场价差)
    │
    ├─ 5-15 bps (正常)
    │   └─ 建议: 12-20 bps (1.5-2倍市场价差)
    │
    └─ > 15 bps (较宽)
        └─ 建议: 20-40 bps (1.3-2倍市场价差)

波动率调整 (Volatility Adjustment)
    ├─ 1h 波动率 < 2%
    │   └─ 价差 -20% (更激进)
    │
    ├─ 1h 波动率 2-5%
    │   └─ 价差不变
    │
    └─ 1h 波动率 > 5%
        └─ 价差 +30% (更保守)
```

### 3.2 数量 (Quantity) 推导 / Quantity Derivation

#### 推理公式 / Reasoning Formula

```
基础数量 = 可用余额 × 风险系数 / 资产价格
风险系数 = f(波动率, 杠杆, 历史绩效, 当前持仓)

如果 账户余额 = $10,000, 资产价格 = $2,500:
    保守策略: 0.1 - 0.2 ETH ($250 - $500 名义价值)
    中等策略: 0.3 - 0.5 ETH ($750 - $1,250 名义价值)
    激进策略: 0.5 - 1.0 ETH ($1,250 - $2,500 名义价值)
```

#### 实际推理示例 / Real Reasoning Example

**场景 1: 小账户 + 低波动**
```
市场数据:
- 可用余额: $10,000
- ETH 价格: $2,500
- 波动率: 低
- 当前持仓: 0

LLM 推理:
"With $10,000 equity and ETH at $2,500, 0.2 ETH per side is ~$500 
notional per order. At 2x leverage, that's $1,000 notional exposure 
per side when both bid and ask are filled (10% of equity). This is 
small enough to limit drawdowns from short-term moves while still 
meaningful for PnL generation."

推导结果:
- 建议数量: 0.2 - 0.4 ETH
- 理由: 平衡风险与收益，10-20% 资金使用率
```

**场景 2: 大账户 + 高波动**
```
市场数据:
- 可用余额: $100,000
- ETH 价格: $2,500
- 波动率: 高
- 当前持仓: 有持仓

LLM 推理:
"High volatility environment requires conservative position sizing. 
With existing position and high volatility, we should reduce quantity 
to minimize inventory risk and potential drawdowns."

推导结果:
- 建议数量: 0.1 - 0.2 ETH
- 理由: 降低风险，即使账户更大也要保守
```

#### 数量决策树 / Quantity Decision Tree

```
账户余额 (Account Balance)
    ├─ < $5,000 (小账户)
    │   └─ 数量: 0.05 - 0.15 ETH
    │
    ├─ $5,000 - $50,000 (中等账户)
    │   └─ 数量: 0.2 - 0.5 ETH
    │
    └─ > $50,000 (大账户)
        └─ 数量: 0.3 - 1.0 ETH (但受波动率限制)

波动率调整 (Volatility Adjustment)
    ├─ 低波动 (< 5%)
    │   └─ 数量 +50% (更激进)
    │
    ├─ 中波动 (5-10%)
    │   └─ 数量不变
    │
    └─ 高波动 (> 10%)
        └─ 数量 -50% (更保守)

持仓调整 (Position Adjustment)
    ├─ 无持仓 (neutral)
    │   └─ 数量不变
    │
    ├─ 小持仓 (< 20% 账户)
    │   └─ 数量 -20%
    │
    └─ 大持仓 (> 20% 账户)
        └─ 数量 -50% (降低风险)
```

### 3.3 杠杆 (Leverage) 推导 / Leverage Derivation

#### 推理公式 / Reasoning Formula

```
基础杠杆 = f(波动率, 资金费率, 历史绩效, 当前杠杆)

如果 波动率低 + 资金费率有利:
    杠杆 = 2-3x (适度杠杆)
如果 波动率高 + 资金费率不利:
    杠杆 = 1-1.5x (保守杠杆)
如果 波动率极高:
    杠杆 = 1x (无杠杆)
```

#### 实际推理示例 / Real Reasoning Example

**场景 1: 低波动 + 有利资金费率**
```
市场数据:
- 波动率: 低 (3.5%)
- 资金费率: 0.01% (rising)
- 当前杠杆: 1x
- 持仓: neutral

LLM 推理:
"2x is sufficient to slightly amplify returns while keeping risk low, 
given neutral starting position and modest size. Funding rate is positive 
and rising (0.01%), which marginally favors being net long, but since 
this is a symmetric market making strategy with small inventory, funding 
impact is minor. Higher leverage is unnecessary and would mainly add tail 
risk without significantly improving market making edge."

推导结果:
- 建议杠杆: 2.0x
- 理由: 适度放大收益，风险可控
```

**场景 2: 高波动 + 不利资金费率**
```
市场数据:
- 波动率: 高 (15%)
- 资金费率: -0.05% (falling)
- 当前杠杆: 3x
- 持仓: long

LLM 推理:
"High volatility (15%) combined with negative funding rate trend 
suggests increased risk. Current leverage of 3x is too high for this 
environment. We should reduce leverage to 1-1.5x to minimize liquidation 
risk and drawdowns."

推导结果:
- 建议杠杆: 1.0 - 1.5x
- 理由: 降低风险，避免爆仓
```

#### 杠杆决策树 / Leverage Decision Tree

```
波动率 (Volatility)
    ├─ < 5% (低波动)
    │   └─ 杠杆: 2-3x
    │
    ├─ 5-10% (中波动)
    │   └─ 杠杆: 1.5-2x
    │
    └─ > 10% (高波动)
        └─ 杠杆: 1-1.5x

资金费率调整 (Funding Rate Adjustment)
    ├─ 资金费率 > 0.02% (有利)
    │   └─ 杠杆 +0.5x (适度增加)
    │
    ├─ 资金费率 -0.02% to 0.02% (中性)
    │   └─ 杠杆不变
    │
    └─ 资金费率 < -0.02% (不利)
        └─ 杠杆 -0.5x (适度减少)

历史绩效调整 (Performance Adjustment)
    ├─ Sharpe > 1.5 (优秀)
    │   └─ 杠杆 +0.5x (适度增加)
    │
    ├─ Sharpe 0.5-1.5 (良好)
    │   └─ 杠杆不变
    │
    └─ Sharpe < 0.5 (较差)
        └─ 杠杆 -0.5x (适度减少)
```

### 3.4 置信度 (Confidence) 评估 / Confidence Assessment

#### 评估因素 / Assessment Factors

LLM 评估置信度时考虑以下因素：

1. **市场数据清晰度 / Market Data Clarity**:
   - 数据是否完整
   - 信号是否一致
   - 是否有矛盾指标

2. **策略匹配度 / Strategy Fit**:
   - FixedSpread 策略是否适合当前市场
   - 市场条件是否明确支持该策略

3. **历史绩效一致性 / Historical Performance Consistency**:
   - 历史绩效是否稳定
   - 近期表现是否与历史一致

#### 置信度评分标准 / Confidence Scoring Criteria

```
高置信度 (0.8 - 1.0):
- 市场信号明确且一致
- 波动率稳定
- 策略与市场条件高度匹配
- 历史绩效稳定

中置信度 (0.5 - 0.8):
- 市场信号部分明确
- 波动率中等
- 策略与市场条件基本匹配
- 历史绩效一般

低置信度 (0.0 - 0.5):
- 市场信号模糊或矛盾
- 波动率极高或极低
- 策略与市场条件匹配度低
- 历史绩效不稳定
```

#### 实际推理示例 / Real Reasoning Example

**高置信度场景**:
```
市场数据:
- 波动率: 稳定 (3.5%)
- 价差: 稳定 (4 bps)
- 资金费率: 稳定上升
- 历史绩效: Sharpe 1.2, 胜率 52%

LLM 推理:
"Market conditions are clear and stable. Low volatility, tight spread, 
and stable funding rate trend all support FixedSpread strategy. Historical 
performance (Sharpe 1.2, win rate 52%) is consistent and positive. High 
confidence in this recommendation."

置信度: 0.82 (82%)
```

**低置信度场景**:
```
市场数据:
- 波动率: 极高 (20%)
- 价差: 波动大 (5-30 bps)
- 资金费率: 快速变化
- 历史绩效: Sharpe 0.3, 胜率 40%

LLM 推理:
"Market conditions are highly uncertain. Extreme volatility, unstable 
spread, and rapidly changing funding rate suggest high risk. Historical 
performance is poor (Sharpe 0.3). FixedSpread may not be optimal in this 
environment. Lower confidence in recommendation."

置信度: 0.45 (45%)
```

---

## 四、完整推理示例 / Complete Reasoning Example

### 4.1 实际 LLM 响应分析 / Real LLM Response Analysis

以下是一个完整的 LLM 响应示例（来自 OpenAI gpt-5.1）：

```json
{
  "recommended_strategy": "FixedSpread",
  "spread": 0.0009,
  "skew_factor": 0,
  "quantity": 0.2,
  "leverage": 2.0,
  "reasoning": "Market is relatively calm (24h vol 3.5%, 1h vol 1.2%) with a tight current spread of ~4 bps (0.04%) between 2499.5 and 2500.5. A FixedSpread market making strategy fits low-to-moderate volatility environments. We want a spread wide enough to cover taker fees, inventory risk, and short-term volatility, but tight enough to get filled. Given neutral starting position, small account ($10k), and historical Sharpe ~1.2, a moderately conservative configuration is appropriate.\n\n1) Spread: I recommend quoting at ~9 bps (0.09%) around mid, slightly wider than the current 4 bps. This gives room to absorb short-term 1h volatility and typical fee drag while still being competitive. At $2,500, 0.09% ≈ $2.25 total spread; this is reasonable for a low-leverage, low-inventory strategy and should yield positive expectancy if fills are balanced.\n\n2) Quantity: With $10,000 equity and ETH at $2,500, 0.2 ETH per side is ~$500 notional per order. At 2x leverage, that's $1,000 notional exposure per side when both bid and ask are filled (10% of equity). This is small enough to limit drawdowns from short-term moves while still meaningful for PnL generation. It also keeps liquidation risk negligible at low leverage.\n\n3) Leverage: 2x is sufficient to slightly amplify returns while keeping risk low, given neutral starting position and modest size. Funding rate is positive and rising (0.01%), which marginally favors being net long, but since this is a symmetric market making strategy with small inventory, funding impact is minor. Higher leverage is unnecessary and would mainly add tail risk without significantly improving market making edge.\n\n4) Skew: With no existing position and only mildly positive funding, I recommend no initial skew (skew_factor = 0). As inventory accumulates in live trading, a dynamic skew could be introduced, but the simulation constraint is a simple FixedSpread strategy; starting neutral is appropriate.\n\nOverall, this configuration targets stable, low-risk market making returns with modest capital usage and minimal liquidation risk, aligned with the current low-volatility and tight-spread environment.",
  "confidence": 0.78,
  "risk_level": "low",
  "expected_return": 0.04
}
```

### 4.2 推理过程分解 / Reasoning Process Breakdown

#### Step 1: 市场状态识别
```
输入: 24h vol 3.5%, 1h vol 1.2%, spread 4 bps
分析: "Market is relatively calm"
结论: 低波动市场，适合做市策略
```

#### Step 2: 价差推导
```
输入: 市场价差 4 bps, 波动率低
分析: "slightly wider than the current 4 bps"
计算: 9 bps (0.09%) = 4 bps × 2.25
理由: "gives room to absorb short-term 1h volatility and typical fee drag"
```

#### Step 3: 数量推导
```
输入: 账户 $10,000, ETH 价格 $2,500
分析: "0.2 ETH per side is ~$500 notional per order"
计算: $500 / $2,500 = 0.2 ETH
理由: "small enough to limit drawdowns while still meaningful for PnL"
```

#### Step 4: 杠杆推导
```
输入: 波动率低, 资金费率上升, 无持仓
分析: "2x is sufficient to slightly amplify returns while keeping risk low"
计算: 2.0x
理由: "Higher leverage is unnecessary and would mainly add tail risk"
```

#### Step 5: 置信度评估
```
输入: 市场清晰, 策略匹配, 历史绩效良好
分析: "moderately conservative configuration is appropriate"
计算: 0.78 (78%)
理由: 市场条件明确，但账户较小，需要适度保守
```

---

## 五、不同 LLM 的推理差异 / Reasoning Differences Across LLMs

### 5.1 推理风格对比 / Reasoning Style Comparison

| LLM | 推理特点 | 参数倾向 | 置信度范围 |
|-----|---------|---------|-----------|
| **Claude** | 详细分析，多因素考虑 | 中等保守 | 0.75 - 0.85 |
| **Gemini** | 简洁直接，关注关键指标 | 偏保守 | 0.70 - 0.85 |
| **OpenAI** | 平衡分析，强调风险收益比 | 中等激进 | 0.70 - 0.80 |

### 5.2 实际案例对比 / Real Case Comparison

**相同市场数据下的不同建议**:

| 参数 | Claude | Gemini | OpenAI |
|------|--------|--------|--------|
| Spread | 8 bps | 15 bps | 9 bps |
| Quantity | 0.80 | 0.20 | 0.40 |
| Leverage | 2.0x | 1.0x | 2.0x |
| Confidence | 82% | 82% | 78% |

**推理差异分析**:
- **Claude**: 更关注数量，建议更大的 quantity (0.80)
- **Gemini**: 更保守，建议更大的 spread (15 bps) 和更小的 quantity (0.20)
- **OpenAI**: 平衡策略，参数居中

---

## 六、推理质量评估 / Reasoning Quality Assessment

### 6.1 优秀推理的特征 / Characteristics of Good Reasoning

1. **逻辑清晰 / Clear Logic**:
   - 推理步骤明确
   - 因果关系清楚
   - 结论有依据

2. **数据驱动 / Data-Driven**:
   - 基于提供的市场数据
   - 不依赖外部假设
   - 计算过程可追溯

3. **风险意识 / Risk Awareness**:
   - 考虑多种风险因素
   - 平衡风险与收益
   - 提供风险等级评估

4. **参数协调 / Parameter Coherence**:
   - 参数之间相互协调
   - 不存在矛盾
   - 整体策略一致

### 6.2 常见推理问题 / Common Reasoning Issues

1. **过度依赖单一指标**:
   - 只关注波动率，忽略其他因素
   - 只关注价差，忽略资金费率

2. **参数不协调**:
   - 高杠杆 + 高数量 + 高波动率（风险过高）
   - 低价差 + 高波动率（容易被套）

3. **缺乏风险考虑**:
   - 只考虑收益，忽略风险
   - 杠杆过高，不考虑爆仓风险

---

## 七、总结 / Summary

### 7.1 关键要点 / Key Points

1. **LLM 推理是多步骤过程**:
   - 数据理解 → 模式识别 → 参数推导 → 置信度评估

2. **推理基于市场数据**:
   - 波动率、价差、资金费率是核心输入
   - 历史绩效、账户状态影响参数选择

3. **参数相互关联**:
   - 价差、数量、杠杆需要协调
   - 不能孤立考虑单个参数

4. **置信度反映不确定性**:
   - 高置信度：市场清晰，策略匹配
   - 低置信度：市场模糊，需要谨慎

### 7.2 优化建议 / Optimization Suggestions

1. **增强 Prompt**:
   - 提供更多参数指导
   - 明确参数范围和建议公式

2. **改进推理质量**:
   - 要求 LLM 提供详细推理过程
   - 验证参数协调性

3. **多 LLM 共识**:
   - 利用多个 LLM 的不同视角
   - 通过共识提高建议质量

---

## 参考资料 / References

- `src/ai/evaluation/prompts.py` - Prompt 模板
- `src/ai/evaluation/evaluator.py` - 评估器实现
- `src/ai/evaluation/schemas.py` - 数据结构定义
- `docs/framework/llm_evaluation_algorithm_explanation.md` - 算法说明

