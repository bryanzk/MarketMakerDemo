# AlphaLoop Prototype Walkthrough / AlphaLoop 原型演示

## Overview / 概述
We have successfully implemented a prototype of the **AlphaLoop** framework. This system demonstrates how autonomous agents collaborate to optimize trading strategies while respecting risk limits.
我们已成功实现 **AlphaLoop** 框架原型，展示了自主智能体如何在遵守风险约束的前提下协同优化交易策略。

### Key Improvements
1. **Structured Logging**: All agents now output machine-readable JSON logs.  
   **结构化日志**：所有智能体现在输出机器可读的 JSON 日志。
2. **Data Agent Enhancements**: Calculates `sharpe_ratio` and `slippage_bps` (mocked).  
   **数据智能体**：新增 `sharpe_ratio` 与 `slippage_bps`（模拟值）。
3. **Config Management**: Centralized risk limits in `config.py`.  
   **配置管理**：风险上限集中在 `config.py`。
4. **UI Improvements**: Added real-time “Stage” indicator and “Active Orders” list.  
   **界面优化**：新增实时“Stage”指示器与“Active Orders”列表。
5. **Bug Fixes**: Restored `orders` in API responses to prevent frontend crashes.  
   **缺陷修复**：API 恢复返回 `orders`，避免前端崩溃。

## 5. Pluggable Metrics Verification / 可插拔指标验证
We implemented a registry-based metrics system; `DataAgent` now loads metrics defined in `config.METRICS_CONFIG` at runtime.
我们实现了注册表驱动的指标系统，`DataAgent` 会在运行时加载 `config.METRICS_CONFIG` 中声明的指标。

### Verification Logs
```json
{"timestamp": "2025-11-22T15:36:00.993500Z", "level": "INFO", "logger": "DataAgent", "message": "Calculated Metrics", "extra_data": {"tick_to_trade_latency": 3.5, "slippage_bps": 0.5, "fill_rate": 0.85, "sharpe_ratio": 0.0}}
```
This confirms that metrics from infrastructure, execution, and strategy layers are being calculated and logged.
这证明基础设施、执行、策略各层的指标都已正确计算并记录。

## Components Implemented / 已实现的组件
1. **Market Simulator** (`simulation.py`): Generates synthetic market data and executes trades.  
   **市场模拟器**：生成合成市场数据并执行交易。
2. **Quant Agent** (`agents/quant.py`): Analyzes metrics (win rate) and proposes spread updates.  
   **量化智能体**：分析胜率等指标并提出价差调整。
3. **Risk Agent** (`agents/risk.py`): Enforces min/max spread constraints before deployment.  
   **风控智能体**：在部署前强制执行最小/最大价差的硬性约束。
4. **Orchestrator** (`agent_framework.py`): Runs the loop and coordinates agents.  
   **编排器**：驱动循环并协调各智能体。

## Verification Results / 验证结果

### 1. Initial State (Risk Rejection) / 初始状态（风控拒绝）
Initially, the strategy had a spread of `0.002%` (2e-05).
最初，策略的价差为 `0.002%` (2e-05)。

* **Quant Proposal**: Widen spread.  
  **量化提议**：扩大价差。
* **Risk Action**: **REJECTED** because the spread was below the 0.1% safety floor.  
  **风控行动**：**拒绝**，因为价差低于 0.1% 安全底线。
* **Outcome**: Unsafe parameters were blocked.  
  **结果**：成功阻止不安全配置上线。

### 2. Adjusted State (Successful Optimization) / 调整后状态（成功优化）
We updated the initial spread to `0.2%` (0.002).
我们将初始价差更新为 `0.2%` (0.002)。

* **Cycle 1**  
  **周期 1**
    * Performance: Win rate 0.0% (spread too tight, market flat).  
      性能：胜率 0.0%（价差过窄、市场波动不足）。
    * Quant Proposal: Widen to `0.0022` (+10%).  
      量化提议：扩大至 `0.0022`（+10%）。
    * Risk Action: **APPROVED**.  
      风控行动：**批准**。
    * Outcome: Config updated.  
      结果：策略配置更新。
* **Cycle 2**  
  **周期 2**
    * Quant Proposal: Widen to `0.0024`.  
      量化提议：扩大至 `0.0024`。
    * Risk Action: **APPROVED**.  
      风控行动：**批准**。
    * Outcome: Config updated again.  
      结果：策略再次更新。

### Console Output Log / 控制台输出日志
```text
=== Iteration 1 ===
--- Starting AlphaLoop Cycle ---
Starting simulation with spread: 0.002
Cycle Performance: PnL=0.0, WinRate=0.0%
[Quant] Analyzing... Win Rate: 0.0%, Current Spread: 0.002
[Quant] Win rate low. Proposing WIDER spread: 0.0022
[Risk] Validating proposal: Spread = 0.0022
[Risk] APPROVED.
Applying new config: {'spread': 0.0022}
```

## Conclusion / 结论
The prototype validates the core concept: **Segregation of Duties** works. The Quant Agent focuses on optimization, while the Risk Agent ensures safety. The system evolves autonomously.
原型验证了核心概念：**职责分离**有效；量化智能体专注优化，风控智能体确保安全，系统可自主演进。

## Troubleshooting / 故障排除
### Risk Alert Delay / 风控警报延迟
Users may notice a delay (e.g., 30 s) before a risk alert appears. This is expected when the strategy starts safe but adapts (widens spread) until crossing a limit.
用户可能观察到风控警报出现前有约 30 秒延迟；当策略以安全配置启动并逐步扩大价差直至触碰上限时，这是预期行为。

### Missing Orders / 订单丢失
Ensure `AlphaLoop.get_status()` returns the `orders` field; missing data previously caused a UI crash and has been fixed.
确保 `AlphaLoop.get_status()` 返回 `orders` 字段；缺失该字段曾导致前端崩溃，现已修复。
