# Multi-LLM Strategy Evaluation User Stories / 多 LLM 策略评估用户故事

## Overview / 概述

This document describes user stories for the Multi-LLM Strategy Evaluation System, guiding development and testing.

本文档描述了多 LLM 策略评估系统的用户故事，用于指导开发和测试。

---

## US-ML-001: Trader Gets Multi-Model Strategy Suggestions / 交易员获取多模型策略建议

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** get strategy suggestions from Gemini, OpenAI, and Claude simultaneously / 同时获取 Gemini、OpenAI、Claude 三个模型的策略建议  
**So that** I can compare different AI perspectives and make more informed trading decisions / 我可以比较不同 AI 的观点，做出更明智的交易决策

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Get strategy suggestions from three models / 获取三个模型的策略建议
  Given I have configured API Keys for all three LLMs / 我已配置好三个 LLM 的 API Key
  And current market data is ready / 当前市场数据已准备就绪
  When I call MultiLLMEvaluator.evaluate(context) / 我调用 MultiLLMEvaluator.evaluate(context)
  Then I should receive 3 evaluation results / 我应该收到 3 个评估结果
  And each result contains strategy type, parameter suggestions, confidence / 每个结果包含策略类型、参数建议、置信度
  And each result contains model name identifier / 每个结果包含模型名称标识

Scenario: Return available results when some model APIs fail / 部分模型 API 失败时仍返回可用结果
  Given I have configured Gemini and OpenAI API Keys / 我已配置好 Gemini 和 OpenAI 的 API Key
  And Claude API Key is not configured or invalid / Claude API Key 未配置或无效
  When I call MultiLLMEvaluator.evaluate(context) / 我调用 MultiLLMEvaluator.evaluate(context)
  Then I should receive at least 2 successful evaluation results / 我应该收到至少 2 个成功的评估结果
  And failed model results are marked as parse_success=False / 失败的模型结果标记为 parse_success=False

Scenario: Parse JSON response returned by LLM / 解析 LLM 返回的 JSON 响应
  Given LLM returned JSON containing strategy suggestions / LLM 返回了包含策略建议的 JSON
  When evaluator parses the response / 评估器解析响应时
  Then should correctly extract spread, skew_factor, confidence fields / 应该正确提取 spread、skew_factor、confidence 等字段
  And if JSON format is incorrect, use default values and mark parse failure / 如果 JSON 格式错误，应该使用默认值并标记解析失败
```

### Technical Notes / 技术备注

- Use `concurrent.futures.ThreadPoolExecutor` for parallel calls / 使用 `concurrent.futures.ThreadPoolExecutor` 并行调用
- Each model call is independent / 每个模型调用独立，互不影响
- Timeout setting: 30 seconds / 超时设置：30 秒

---

## US-ML-002: Trader Compares Simulated Performance of Model Suggestions / 交易员比较模型建议的模拟表现

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** run simulated trading for each model's strategy suggestions / 对每个模型的策略建议运行模拟交易  
**So that** I can quantitatively compare which model's suggestions perform best / 我可以量化比较哪个模型的建议表现最好

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Run simulation for each suggestion / 为每个建议运行模拟交易
  Given I have obtained 3 model strategy suggestions / 我已获取 3 个模型的策略建议
  When evaluator runs simulation / 评估器运行模拟时
  Then each suggestion should have corresponding simulation results / 每个建议都应该有对应的模拟结果
  And simulation results include PnL, win rate, Sharpe ratio / 模拟结果包含 PnL、胜率、夏普比率
  And simulation uses same market conditions (price, volatility, funding rate) / 模拟使用相同的市场条件

Scenario: Simulation uses suggested parameters / 模拟使用建议的参数
  Given Gemini suggests spread=0.012, skew_factor=120 / Gemini 建议 spread=0.012, skew_factor=120
  When running simulation for Gemini suggestion / 为 Gemini 建议运行模拟时
  Then simulator should use spread=0.012, skew_factor=120 / 模拟器应该使用 spread=0.012, skew_factor=120
  And should not use other models' parameters / 不应该使用其他模型的参数

Scenario: Configurable simulation steps / 可配置模拟步数
  Given I set simulation_steps=1000 / 我设置 simulation_steps=1000
  When running evaluation / 运行评估时
  Then each simulation should run 1000 steps / 每个模拟应该运行 1000 步
  And result's simulation_steps field should be 1000 / 结果中 simulation_steps 字段为 1000
```

### Technical Notes / 技术备注

- Simulator needs to support dynamic parameter setting / 模拟器需要支持动态参数设置
- Each model's simulation runs independently with same random seed for fairness / 每个模型的模拟独立运行，使用相同的随机种子保证公平
- Simulation results are recorded in `SimulationResult` object / 模拟结果记录在 `SimulationResult` 对象中

---

## US-ML-003: Trader Gets Ranked Results / 交易员获取排名结果

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** see results ranked by composite score / 看到按综合评分排名的结果  
**So that** I can quickly identify the best strategy suggestion / 我可以快速识别最佳策略建议

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Rank by composite score / 按综合评分排名
  Given all three models returned valid evaluation results / 三个模型都返回了有效的评估结果
  When calculating ranking / 计算排名时
  Then results should be sorted by score descending / 结果应该按 score 降序排列
  And first place has rank=1, second has rank=2, etc. / 第一名的 rank=1，第二名的 rank=2，依此类推
  And scoring formula is: PnL*0.4 + Sharpe*0.3 + WinRate*0.2 + Confidence*0.1 / 评分公式为: PnL*0.4 + Sharpe*0.3 + WinRate*0.2 + Confidence*0.1

Scenario: Get best proposal / 获取最佳建议
  Given evaluation results are ranked / 评估结果已排名
  When calling get_best_proposal(results) / 调用 get_best_proposal(results)
  Then should return result with rank=1 / 应该返回 rank=1 的结果
  And that result's score is highest among all / 该结果的 score 是所有结果中最高的

Scenario: Parse-failed results rank last / 解析失败的结果排名靠后
  Given one model's response failed to parse / 有一个模型的响应解析失败
  When calculating ranking / 计算排名时
  Then that model's score should be 0 / 该模型的 score 应该为 0
  And that model's rank should be last / 该模型的 rank 应该是最后一名
```

### Technical Notes / 技术备注

- Scores normalized to 0-100 range / 评分归一化到 0-100 范围
- Parse-failed results get score of 0 / 解析失败的结果得分为 0
- Use stable sort for consistency / 使用稳定排序保证一致性

---

## US-ML-004: Trader Views Comparison Table / 交易员查看对比表格

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** see a formatted comparison table / 看到格式化的对比表格  
**So that** I can compare each model's suggestions and results at a glance / 我可以一目了然地比较各模型的建议和结果

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Generate comparison table / 生成对比表格
  Given there are 3 evaluation results / 有 3 个评估结果
  When calling generate_comparison_table(results) / 调用 generate_comparison_table(results)
  Then should return formatted string table / 应该返回格式化的字符串表格
  And table includes rank, model name, strategy, parameters, PnL, win rate, Sharpe, score / 表格包含排名、模型名、策略、参数、PnL、胜率、夏普、评分
  And table displays in rank order / 表格按排名顺序显示

Scenario: Table shows key metrics / 表格显示关键指标
  Given Claude's PnL=$200, win rate=60%, Sharpe=2.5 / Claude 的 PnL=$200, 胜率=60%, 夏普=2.5
  When generating table / 生成表格时
  Then Claude row should show "$200.00" / Claude 行应该显示 "$200.00"
  And show "60.0%" / 显示 "60.0%"
  And show "2.50" / 显示 "2.50"

Scenario: Table shows latency info / 表格显示延迟信息
  Given Gemini response latency is 1250ms / Gemini 响应延迟 1250ms
  When generating table / 生成表格时
  Then Gemini row's Latency column should show "1250ms" / Gemini 行的 Latency 列应该显示 "1250ms"
```

### Technical Notes / 技术备注

- Use fixed-width format for alignment / 使用固定宽度格式保证对齐
- Number formatting: PnL with currency symbol, percentages with %, decimals to 2 places / 数值格式化：PnL 带货币符号，百分比带 %，小数保留 2 位
- Support export to JSON format / 支持导出为 JSON 格式

---

## US-ML-005: Trader Views Suggestion Reasoning / 交易员查看建议理由

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** understand the reasoning behind each model's suggestions / 了解每个模型给出建议的理由  
**So that** I can understand the AI's thought process and evaluate its reasonableness / 我可以理解 AI 的思考过程并评估其合理性

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Suggestion includes reasoning / 建议包含理由说明
  Given LLM returned a reasoning field / LLM 返回了 reasoning 字段
  When parsing response / 解析响应时
  Then StrategyProposal.reasoning should contain reasoning text / StrategyProposal.reasoning 应该包含理由文本
  And reasoning should explain why the strategy and parameters were chosen / 理由应该解释为什么选择该策略和参数

Scenario: Suggestion includes risk level / 建议包含风险等级
  Given LLM returned a risk_level field / LLM 返回了 risk_level 字段
  When parsing response / 解析响应时
  Then StrategyProposal.risk_level should be "low", "medium", or "high" / StrategyProposal.risk_level 应该是 "low"、"medium" 或 "high"

Scenario: Suggestion includes expected return / 建议包含预期收益
  Given LLM returned an expected_return field / LLM 返回了 expected_return 字段
  When parsing response / 解析响应时
  Then StrategyProposal.expected_return should be a float / StrategyProposal.expected_return 应该是浮点数
```

### Technical Notes / 技术备注

- Reasoning field can be in Chinese or English / reasoning 字段可以是中文或英文
- Frontend needs to support expand/collapse for long text / 前端需要支持展开/折叠长文本
- Consider adding sentiment analysis to judge optimistic/pessimistic reasoning / 考虑添加情感分析判断理由的乐观/悲观程度

---

## US-ML-006: System Measures LLM Response Latency / 系统测量 LLM 响应延迟

### Story Description / 故事描述

**As a** system administrator / 系统管理员  
**I want to** know each LLM's response time / 知道每个 LLM 的响应时间  
**So that** I can monitor API performance and optimize experience / 我可以监控 API 性能并优化体验

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Record each model's response latency / 记录每个模型的响应延迟
  When calling LLM API / 调用 LLM API 时
  Then should record time from request sent to response received / 应该记录从发送请求到收到响应的时间
  And time is stored in milliseconds in latency_ms field / 时间以毫秒为单位存储在 latency_ms 字段

Scenario: Latency included in results / 延迟包含在结果中
  Given OpenAI response took 980ms / OpenAI 响应用时 980ms
  When evaluation completes / 评估完成时
  Then OpenAI's EvaluationResult.latency_ms should be approximately 980 / OpenAI 的 EvaluationResult.latency_ms 应该约等于 980

Scenario: Timeout handling / 超时处理
  Given a model response exceeds 30 seconds / 某个模型响应超过 30 秒
  When waiting for response / 等待响应时
  Then should return timeout error / 应该返回超时错误
  And that model's result is marked as failed / 该模型的结果标记为失败
```

### Technical Notes / 技术备注

- Use `time.time()` or `time.perf_counter()` for measurement / 使用 `time.time()` 或 `time.perf_counter()` 测量
- Timeout using `concurrent.futures` timeout parameter / 超时使用 `concurrent.futures` 的 timeout 参数
- Log latency for subsequent analysis / 日志记录延迟便于后续分析

---

## US-ML-007: Trader Applies Best Strategy / 交易员应用最佳策略

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** apply the #1 ranked strategy suggestion with one click / 一键应用排名第一的策略建议  
**So that** I can quickly convert AI suggestions into actual trading parameters / 我可以快速将 AI 建议转化为实际交易参数

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Apply best strategy parameters / 应用最佳策略参数
  Given Claude is the #1 ranked suggestion / Claude 是排名第一的建议
  And Claude suggests spread=0.010, skew_factor=150 / Claude 建议 spread=0.010, skew_factor=150
  When I call apply strategy function / 我调用应用策略功能
  Then current strategy's spread should update to 0.010 / 当前策略的 spread 应该更新为 0.010
  And skew_factor should update to 150 / skew_factor 应该更新为 150

Scenario: Risk control validation before applying / 应用前经过风控验证
  Given best suggestion's spread=0.001 (too small) / 最佳建议的 spread=0.001（过小）
  When attempting to apply strategy / 尝试应用策略时
  Then RiskAgent should reject the parameters / RiskAgent 应该拒绝该参数
  And return rejection reason / 返回拒绝原因
  And current strategy parameters remain unchanged / 当前策略参数不变

Scenario: Log strategy changes / 记录策略变更日志
  Given strategy parameters were successfully updated / 策略参数被成功更新
  When application completes / 应用完成时
  Then should record change log / 应该记录变更日志
  And log includes before/after parameter values / 日志包含变更前后的参数值
  And log includes suggestion source (which model) / 日志包含建议来源（哪个模型）
```

### Technical Notes / 技术备注

- Integrate with existing QuantAgent and RiskAgent / 与现有的 QuantAgent 和 RiskAgent 集成
- Support rollback to previous parameters / 支持回滚到之前的参数
- Optional manual confirmation step / 可选的人工确认步骤

---

## US-ML-008: Trader Views Historical Evaluation Records / 交易员查看历史评估记录

### Story Description / 故事描述

**As a** cryptocurrency trader / 一名加密货币交易员  
**I want to** view historical evaluation records / 查看历史评估记录  
**So that** I can analyze which model performs better long-term / 我可以分析哪个模型长期表现更好

### Acceptance Criteria / 验收标准

```gherkin
Scenario: Save evaluation records / 保存评估记录
  Given I completed a multi-model evaluation / 我完成了一次多模型评估
  When evaluation ends / 评估结束时
  Then results should be saved to history / 结果应该被保存到历史记录
  And record includes timestamp, market state, all models' suggestions and results / 记录包含时间戳、市场状态、所有模型的建议和结果

Scenario: Query historical records / 查询历史记录
  Given I want to view evaluations from past 7 days / 我想查看过去 7 天的评估
  When I call history query API / 我调用历史查询 API
  Then should return all evaluation records from past 7 days / 应该返回过去 7 天的所有评估记录
  And sorted by time descending / 按时间倒序排列

Scenario: Model performance statistics / 统计模型表现
  Given I have 30 days of evaluation history / 我有 30 天的评估历史
  When I request model performance statistics / 我请求模型表现统计
  Then should return each model's average rank / 应该返回每个模型的平均排名
  And return each model's win count (times ranked #1) / 返回每个模型的胜出次数（排名第一的次数）
```

### Technical Notes / 技术备注

- Use SQLite or JSON file for history storage / 使用 SQLite 或 JSON 文件存储历史
- Support filtering by time range, symbol / 支持按时间范围、币种筛选
- Provide visualization charts (future feature) / 提供可视化图表（后续功能）

---

## Priority Matrix / 优先级矩阵

| User Story / 用户故事 | Priority / 优先级 | Complexity / 复杂度 | MVP |
|---------|-------|-------|-----|
| US-ML-001 | P0 | Medium / 中 | ✅ |
| US-ML-002 | P0 | Medium / 中 | ✅ |
| US-ML-003 | P0 | Low / 低 | ✅ |
| US-ML-004 | P0 | Low / 低 | ✅ |
| US-ML-005 | P1 | Low / 低 | ✅ |
| US-ML-006 | P1 | Low / 低 | ✅ |
| US-ML-007 | P1 | Medium / 中 | ❌ |
| US-ML-008 | P2 | High / 高 | ❌ |

---

## Next Steps / 下一步

These user stories will guide test case writing. See [Test Cases](../../tests/test_multi_llm_evaluation.py).

这些用户故事将指导测试用例的编写，详见 [测试用例文档](../../tests/test_multi_llm_evaluation.py)。
