# TODO: Multi-Strategy LLM Evaluation Framework Improvements
# TODO: 多策略 LLM 评估框架改进项

**Last Updated / 最后更新**: 2025-11-30  
**Owner / 负责人**: Agent PO  
**Status / 状态**: Open / 待处理

---

## 🎯 Overview / 概述

This document tracks improvement suggestions and action items for the Multi-Strategy LLM Evaluation Framework.
本文档追踪多策略 LLM 评估框架的改进建议和行动项。

---

## 📋 Action Items / 行动项

### 1. UI/UX: Remove Skew Factor from Fixed Spread Control Panel
### 1. UI/UX: 从固定价差控制面板移除倾斜因子

**Priority / 优先级**: Medium / 中等  
**Owner / 负责人**: Agent WEB  
**Category / 类别**: UI/UX Improvement / UI/UX 改进

#### Problem / 问题

Currently, the `LLMTrade.html` Fixed Spread Strategy Control Panel displays a "Skew Factor" input field, but:
当前 `LLMTrade.html` 的固定价差策略控制面板显示"倾斜因子"输入框，但：

- `FixedSpreadStrategy` does not use `skew_factor` parameter
- `FixedSpreadStrategy` 不使用 `skew_factor` 参数
- The parameter is only used by `FundingRateStrategy`
- 该参数仅由 `FundingRateStrategy` 使用
- Users may be confused by this irrelevant control
- 用户可能被这个无关的控制项困惑

**Evidence / 证据**:
- `alphaloop/strategies/strategy.py`: `FixedSpreadStrategy` has no `skew_factor` attribute
- `alphaloop/evaluation/evaluator.py:271`: Comment states "skew_factor is not used for FixedSpread strategy"
- `alphaloop/strategies/funding.py`: `FundingRateStrategy` uses `skew_factor`

#### Solution / 解决方案

**Short-term (Current State) / 短期方案（当前状态）**:
- Remove the Skew Factor input field from Fixed Spread Control Panel
- 从固定价差控制面板移除倾斜因子输入框
- File: `templates/LLMTrade.html` (lines 238-241)
- 文件: `templates/LLMTrade.html` (第 238-241 行)

**Long-term (Multi-Strategy Support) / 长期方案（多策略支持）**:
- Implement dynamic parameter display based on selected strategy type
- 根据选择的策略类型动态显示参数
- Show `skew_factor` only when `FundingRateStrategy` is selected
- 仅在选择 `FundingRateStrategy` 时显示 `skew_factor`

#### Implementation Steps / 实施步骤

1. **Remove static Skew Factor input (Phase 1) / 移除静态倾斜因子输入（阶段1）**
   ```html
   <!-- Remove or comment out -->
   <div>
       <label>Skew Factor / 倾斜因子</label>
       <input type="number" id="skewInput" step="5" value="120">
   </div>
   ```

2. **Update JavaScript (Phase 1) / 更新 JavaScript（阶段1）**
   - Remove `skewInput` references from `updateConfig()` function
   - 从 `updateConfig()` 函数中移除 `skewInput` 引用
   - Remove from `loadStatus()` if applicable
   - 如适用，从 `loadStatus()` 中移除

3. **Add strategy selector (Phase 2) / 添加策略选择器（阶段2）**
   ```html
   <div>
       <label>Strategy Type / 策略类型</label>
       <select id="strategyTypeSelect">
           <option value="FixedSpread">Fixed Spread</option>
           <option value="FundingRate">Funding Rate</option>
       </select>
   </div>
   ```

4. **Implement dynamic controls (Phase 2) / 实现动态控制（阶段2）**
   ```javascript
   function updateStrategyControls(strategyType) {
       const skewControl = document.getElementById('skewFactorControl');
       if (strategyType === 'FixedSpread') {
           skewControl.style.display = 'none';
       } else if (strategyType === 'FundingRate') {
           skewControl.style.display = 'block';
       }
   }
   ```

#### Acceptance Criteria / 验收标准

- [ ] Skew Factor input removed from Fixed Spread panel (Phase 1)
- [ ] 倾斜因子输入从固定价差面板移除（阶段1）
- [ ] No JavaScript errors when saving Fixed Spread config
- [ ] 保存固定价差配置时无 JavaScript 错误
- [ ] Strategy selector added (Phase 2)
- [ ] 策略选择器已添加（阶段2）
- [ ] Parameters display dynamically based on strategy type (Phase 2)
- [ ] 参数根据策略类型动态显示（阶段2）

#### Related Files / 相关文件

- `templates/LLMTrade.html` - UI template
- `server.py` - Backend API endpoints
- `alphaloop/strategies/strategy.py` - FixedSpreadStrategy implementation
- `alphaloop/strategies/funding.py` - FundingRateStrategy implementation

---

### 2. Architecture: Plugin-Based Strategy Evaluation Framework
### 2. 架构: 基于插件的策略评估框架

**Priority / 优先级**: High / 高  
**Owner / 负责人**: Agent AI (with Agent ARCH)  
**Category / 类别**: Architecture Refactoring / 架构重构

#### Problem / 问题

Current `MultiLLMEvaluator` is hardcoded for `FixedSpreadStrategy` only:
当前 `MultiLLMEvaluator` 仅硬编码支持 `FixedSpreadStrategy`：

- Cannot evaluate other strategies (FundingRate, Grid, etc.)
- 无法评估其他策略（FundingRate、Grid 等）
- Strategy-specific logic is embedded in evaluator
- 策略特定逻辑嵌入在评估器中
- Adding new strategies requires modifying core evaluator code
- 添加新策略需要修改核心评估器代码

#### Solution / 解决方案

Implement plugin-based architecture with:
实现基于插件的架构，包含：

1. **BaseStrategyAdvisor Interface / 基础策略顾问接口**
   - `generate_prompt()` - Strategy-specific prompt generation
   - `parse_response()` - Parse LLM response to StrategyProposal
   - `validate_parameters()` - Validate proposed parameters

2. **BaseStrategySimulator Interface / 基础策略模拟器接口**
   - `run_simulation()` - Run backtesting with proposed parameters

3. **StrategyRegistry / 策略注册表**
   - Register advisors and simulators
   - 注册顾问和模拟器
   - Retrieve by strategy name
   - 按策略名称检索

#### Implementation Steps / 实施步骤

1. Create `src/ai/evaluation/advisors/base.py`
2. Create `src/ai/evaluation/simulators/base.py`
3. Create `src/ai/evaluation/registry.py`
4. Refactor `evaluator.py` to use registry
5. Implement `FixedSpreadAdvisor` and `FixedSpreadSimulator`
6. Implement `FundingRateAdvisor` and `FundingRateSimulator`

#### Acceptance Criteria / 验收标准

- [ ] Base interfaces defined and documented
- [ ] 基础接口已定义并文档化
- [ ] StrategyRegistry implemented
- [ ] StrategyRegistry 已实现
- [ ] FixedSpread refactored to use plugin architecture
- [ ] FixedSpread 已重构为使用插件架构
- [ ] FundingRate can be added without modifying core evaluator
- [ ] FundingRate 可在不修改核心评估器的情况下添加

#### Related Files / 相关文件

- `alphaloop/evaluation/evaluator.py` - Core evaluator (needs refactoring)
- `docs/specs/ai/LLM-001.md` - Specification document (to be created)

---

### 3. Documentation: Strategy Parameter Specifications
### 3. 文档: 策略参数规格

**Priority / 优先级**: High / 高  
**Owner / 负责人**: Agent PO  
**Category / 类别**: Documentation / 文档

#### Problem / 问题

Parameter ranges and validation rules are scattered across code:
参数范围和验证规则分散在代码中：

- No centralized specification of valid parameter ranges
- 没有集中的有效参数范围规格
- LLM prompts may suggest invalid parameters
- LLM 提示可能建议无效参数
- UI controls lack validation guidance
- UI 控件缺乏验证指导

#### Solution / 解决方案

Create comprehensive parameter specification document:
创建全面的参数规格文档：

- Define valid ranges for each strategy type
- 定义每种策略类型的有效范围
- Document parameter relationships and constraints
- 文档化参数关系和约束
- Provide examples for each strategy
- 为每种策略提供示例

#### Implementation Steps / 实施步骤

1. Create `docs/specs/ai/LLM-001.md` with:
   - Parameter schema for FixedSpread
   - Parameter schema for FundingRate
   - Validation rules
   - Example configurations

#### Acceptance Criteria / 验收标准

- [ ] Parameter specifications documented for FixedSpread
- [ ] FixedSpread 的参数规格已文档化
- [ ] Parameter specifications documented for FundingRate
- [ ] FundingRate 的参数规格已文档化
- [ ] Validation rules clearly defined
- [ ] 验证规则已明确定义
- [ ] Examples provided for each strategy
- [ ] 为每种策略提供了示例

### 4. Integration: Real Trading Data for LLM Evaluation
### 4. 集成: 实盘交易数据用于 LLM 评估

**Priority / 优先级**: High / 高  
**Owner / 负责人**: Agent AI (with Agent TRADING)  
**Category / 类别**: Feature Enhancement / 功能增强

#### Problem / 问题

Current evaluation framework only uses simulated data to assess LLM proposals:
当前评估框架仅使用模拟数据来评估 LLM 建议：

- Simulation results may not reflect real market conditions
- 模拟结果可能无法反映真实市场条件
- No way to validate LLM suggestions against actual trading performance
- 无法用实际交易表现验证 LLM 建议
- Cannot track which proposals were applied and their real-world outcomes
- 无法追踪哪些建议被应用了以及它们的实际结果
- Missing feedback loop to improve LLM recommendations
- 缺少改进 LLM 推荐的反馈循环

**Current State / 当前状态**:
- `MultiLLMEvaluator._run_simulation()` uses `StrategySimulator` with synthetic market data
- `MultiLLMEvaluator._run_simulation()` 使用 `StrategySimulator` 和合成市场数据
- Real trading data exists in `PerformanceTracker`, `DataAgent`, and `/api/performance` endpoint
- 实盘交易数据存在于 `PerformanceTracker`、`DataAgent` 和 `/api/performance` 端点中
- No connection between evaluation results and real trading outcomes
- 评估结果与实际交易结果之间没有连接

#### Solution / 解决方案

Implement a dual-mode evaluation system:
实现双模式评估系统：

1. **Simulation Mode (Current) / 模拟模式（当前）**
   - Fast evaluation using synthetic data
   - 使用合成数据快速评估
   - Suitable for initial proposal comparison
   - 适用于初始建议比较

2. **Real Data Mode (New) / 实盘数据模式（新增）**
   - Backtest LLM proposals against historical real trading data
   - 使用历史实盘交易数据回测 LLM 建议
   - Track applied proposals and their actual performance
   - 追踪已应用的建议及其实际表现
   - Build feedback loop for LLM improvement
   - 构建 LLM 改进的反馈循环

#### Implementation Steps / 实施步骤

**Phase 1: Real Data Backtesting / 阶段1: 实盘数据回测**

1. **Extend EvaluationResult Schema / 扩展 EvaluationResult 模式**
   ```python
   @dataclass
   class EvaluationResult:
       # ... existing fields ...
       real_data_backtest: Optional[RealDataResult] = None  # New field
       evaluation_mode: str = "simulation"  # "simulation" | "real_data" | "both"
   ```

2. **Create RealDataBacktester / 创建实盘数据回测器**
   ```python
   class RealDataBacktester:
       def backtest_proposal(
           self,
           proposal: StrategyProposal,
           historical_trades: List[Trade],
           historical_prices: List[PriceData]
       ) -> RealDataResult:
           """Run proposal against real historical data"""
   ```

3. **Integrate with DataAgent / 与 DataAgent 集成**
   - Access `bot_engine.data.trade_history` for historical trades
   - Access `bot_engine.data.price_history` for historical prices
   - Filter by time window (e.g., last 24 hours, last week)

**Phase 2: Proposal Tracking / 阶段2: 建议追踪**

4. **Create ProposalTracker / 创建建议追踪器**
   ```python
   class ProposalTracker:
       def record_applied_proposal(
           self,
           proposal: StrategyProposal,
           evaluation_result: EvaluationResult,
           applied_at: datetime
       ):
           """Record when a proposal is applied to real trading"""
       
       def track_performance(
           self,
           proposal_id: str,
           time_window: timedelta
       ) -> RealPerformanceMetrics:
           """Track actual performance of applied proposal"""
   ```

5. **Extend EvaluationResult with Tracking / 扩展 EvaluationResult 支持追踪**
   ```python
   @dataclass
   class EvaluationResult:
       # ... existing fields ...
       proposal_id: str = ""  # Unique ID for tracking
       applied_to_real_trading: bool = False
       real_trading_performance: Optional[RealPerformanceMetrics] = None
   ```

**Phase 3: Feedback Loop / 阶段3: 反馈循环**

6. **Compare Simulation vs Real Performance / 对比模拟与实盘表现**
   ```python
   def compare_simulation_vs_real(
       self,
       simulation_result: SimulationResult,
       real_performance: RealPerformanceMetrics
   ) -> ComparisonReport:
       """Compare predicted vs actual performance"""
       return {
           "pnl_accuracy": real_performance.pnl / simulation_result.realized_pnl,
           "sharpe_accuracy": real_performance.sharpe / simulation_result.sharpe_ratio,
           "win_rate_accuracy": real_performance.win_rate / simulation_result.win_rate,
       }
   ```

7. **Update LLM Prompt with Historical Performance / 使用历史表现更新 LLM 提示**
   - Include past proposal performance in MarketContext
   - 在 MarketContext 中包含过去建议的表现
   - Help LLMs learn from previous mistakes
   - 帮助 LLM 从过去的错误中学习

#### Data Flow / 数据流

```
┌─────────────────────────────────────────────────────────────────┐
│                    Real Data Evaluation Flow                    │
│                        实盘数据评估流程                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. LLM generates proposal                                      │
│     LLM 生成建议                                                │
│         │                                                       │
│         ▼                                                       │
│  2. Run simulation (fast, synthetic data)                      │
│     运行模拟（快速，合成数据）                                    │
│         │                                                       │
│         ▼                                                       │
│  3. Run real data backtest (slower, historical)            │
│     运行实盘数据回测（较慢，历史数据）                            │
│         │                                                       │
│         ▼                                                       │
│  4. Compare simulation vs real data results                    │
│     对比模拟与实盘数据结果                                        │
│         │                                                       │
│         ▼                                                       │
│  5. User applies proposal → Record in ProposalTracker         │
│     用户应用建议 → 记录到 ProposalTracker                        │
│         │                                                       │
│         ▼                                                       │
│  6. Track real trading performance over time                  │
│     随时间追踪实盘交易表现                                        │
│         │                                                       │
│         ▼                                                       │
│  7. Feed performance data back to LLM context                  │
│     将表现数据反馈给 LLM 上下文                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

#### Acceptance Criteria / 验收标准

- [ ] `RealDataBacktester` implemented and tested
- [ ] RealDataBacktester 已实现并测试
- [ ] Evaluation API supports `evaluation_mode` parameter
- [ ] 评估 API 支持 `evaluation_mode` 参数
- [ ] `ProposalTracker` records applied proposals
- [ ] ProposalTracker 记录已应用的建议
- [ ] Real trading performance can be queried by `proposal_id`
- [ ] 可以通过 `proposal_id` 查询实盘交易表现
- [ ] Comparison report shows simulation vs real accuracy
- [ ] 对比报告显示模拟与实盘的准确性
- [ ] Historical performance included in LLM MarketContext
- [ ] 历史表现包含在 LLM MarketContext 中

#### API Changes / API 变更

**POST `/api/evaluation/run` - Extended Request / 扩展请求**:
```json
{
    "symbol": "ETHUSDT",
    "simulation_steps": 500,
    "evaluation_mode": "both",  // "simulation" | "real_data" | "both"
    "real_data_window_hours": 24  // Optional: hours of historical data
}
```

**Response - Extended / 扩展响应**:
```json
{
    "individual_results": [
        {
            "provider_name": "Gemini",
            "proposal": {...},
            "simulation": {...},
            "real_data_backtest": {  // New field
                "realized_pnl": 150.0,
                "sharpe_ratio": 1.8,
                "win_rate": 0.55,
                "data_points_used": 1200
            },
            "comparison": {  // New field
                "pnl_accuracy": 0.83,  // real / simulation
                "sharpe_accuracy": 0.86,
                "win_rate_accuracy": 0.95
            }
        }
    ]
}
```

**New Endpoint: GET `/api/evaluation/tracked-proposals` / 新端点**:
```json
{
    "proposals": [
        {
            "proposal_id": "prop-2025-11-30-001",
            "applied_at": "2025-11-30T10:00:00Z",
            "provider_name": "Gemini",
            "simulation_pnl": 180.0,
            "real_pnl": 165.0,
            "accuracy": 0.92,
            "status": "tracking"  // "tracking" | "completed"
        }
    ]
}
```

#### Related Files / 相关文件

- `alphaloop/evaluation/evaluator.py` - Core evaluator (needs extension)
- `alphaloop/evaluation/schemas.py` - Data models (needs extension)
- `alphaloop/market/performance.py` - PerformanceTracker (data source)
- `alphaloop/agents/data.py` - DataAgent (data source)
- `server.py` - API endpoints (needs extension)
- `alphaloop/evaluation/backtester.py` - New file (to be created)
- `alphaloop/evaluation/tracker.py` - New file (to be created)

---

## 📊 Status Tracking / 状态追踪

| Item / 项目 | Priority / 优先级 | Status / 状态 | Assigned To / 分配给 | Target Date / 目标日期 |
|------------|------------------|--------------|---------------------|---------------------|
| UI: Remove Skew Factor | Medium | Open | Agent WEB | TBD |
| Architecture: Plugin Framework | High | Open | Agent AI + ARCH | TBD |
| Docs: Parameter Specs | High | Open | Agent PO | TBD |
| Integration: Real Data Evaluation | High | Open | Agent AI + TRADING | TBD |

---

## 🔗 Related Documents / 相关文档

- `docs/framework/evaluation_framework.md` - High-level architecture
- `docs/specs/ai/LLM-001.md` - Feature specification (to be created)
- `templates/LLMTrade.html` - UI implementation
- `alphaloop/evaluation/evaluator.py` - Current evaluator implementation

---

## 📝 Notes / 备注

- This TODO list will be updated as new issues are discovered
- 此 TODO 列表将在发现新问题时更新
- Items may be moved to separate feature specifications as they mature
- 项目成熟后可能会移至单独的功能规格文档
- Priority levels: High (blocks other work), Medium (improves UX), Low (nice to have)
- 优先级：高（阻塞其他工作）、中（改善用户体验）、低（锦上添花）

---

**Document Version / 文档版本**: 1.0  
**Created / 创建日期**: 2025-11-30  
**Last Reviewed / 最后审查**: 2025-11-30

