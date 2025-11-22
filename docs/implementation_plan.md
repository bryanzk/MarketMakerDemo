# Implementation Plan - AlphaLoop Prototype / 实施计划 - AlphaLoop 原型

## Goal Description / 目标描述
Implement a prototype of the "AlphaLoop" framework within the existing `MarketMakerDemo` workspace. We will simulate the interaction between a **Strategy Agent** and a **Risk Agent** to optimize the `FixedSpreadStrategy`.

在现有的 `MarketMakerDemo` 工作区中实现 "AlphaLoop" 框架的原型。我们将模拟 **策略智能体** 和 **风控智能体** 之间的交互，以优化 `FixedSpreadStrategy`。

## User Review Required / 用户审查要求
> [!IMPORTANT]
> This plan involves creating new "Agent" scripts that will modify existing code (`strategy.py`).
> 此计划涉及创建新的“智能体”脚本，这些脚本将修改现有代码 (`strategy.py`)。

## Proposed Changes / 提议的变更

### Infrastructure / 基础设施
#### [NEW] [agent_framework.py](file:///Users/bamer/MarketMakerDemo/agent_framework.py)
*   Orchestrator script to run the loop.
    *   运行循环的编排脚本。
*   Defines the `Agent` base class and specific `StrategyAgent` and `RiskAgent` classes (mocked for this demo, or simple logic).
    *   定义 `Agent` 基类以及具体的 `StrategyAgent` 和 `RiskAgent` 类（在此演示中为模拟或简单逻辑）。

#### [NEW] [simulation.py](file:///Users/bamer/MarketMakerDemo/simulation.py)
*   A script to run a quick backtest/simulation of the current `strategy.py` and output performance metrics.
    *   运行当前 `strategy.py` 的快速回测/模拟并输出性能指标的脚本。

### Agents / 智能体
#### [NEW] [agents/quant.py](file:///Users/bamer/MarketMakerDemo/agents/quant.py)
*   Logic for the Quant Agent: Reads `performance.json`, decides to change `spread`.
    *   量化智能体的逻辑：读取 `performance.json`，决定更改 `spread`（价差）。

#### [NEW] [agents/risk.py](file:///Users/bamer/MarketMakerDemo/agents/risk.py)
*   Logic for the Risk Agent: Checks if `spread` is too low or high.
    *   风控智能体的逻辑：检查 `spread` 是否过低或过高。

## Verification Plan / 验证计划

### Automated Tests / 自动化测试
*   Run `python agent_framework.py` and observe:
    *   运行 `python agent_framework.py` 并观察：
    1.  Baseline simulation runs.
        *   基线模拟运行。
    2.  Quant Agent proposes a change (e.g., changing spread from 1% to 0.5%).
        *   量化智能体提议变更（例如，将价差从 1% 改为 0.5%）。
    3.  Risk Agent validates it.
        *   风控智能体进行验证。
    4.  Code is updated.
        *   代码已更新。
    5.  New simulation runs with different results.
        *   新的模拟运行并产生不同的结果。
