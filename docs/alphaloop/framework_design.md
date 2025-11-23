# Financial Agentic Framework: "AlphaLoop" / 金融智能体框架："AlphaLoop"

## 1. Introduction / 简介
This document outlines the design of the **AlphaLoop** agentic framework, which powers the **MarketMakerDemo** bot.
本文档概述了 **AlphaLoop** 智能体框架的设计，该框架驱动着 **MarketMakerDemo** 机器人。

The core philosophy is to model the software development and operational lifecycle of a trading system using specialized AI agents.
核心理念是使用专门的 AI 智能体对交易系统的软件开发和运营生命周期进行建模。This framework applies financial industry best practices (Segregation of Duties, Model Risk Management, CI/CD) to a multi-agent software development lifecycle. The goal is to create a self-optimizing system that converges on business objectives (e.g., Sharpe Ratio, PnL) while strictly adhering to risk and compliance constraints.

本框架将金融行业的最佳实践（职责分离、模型风险管理、CI/CD）应用于多智能体软件开发生命周期。其目标是创建一个自我优化的系统，在严格遵守风险和合规约束的同时，收敛于业务目标（如夏普比率、PnL）。

## 2. Core Philosophy / 核心理念
*   **Compliance as Code**: Risk and Compliance rules are immutable constraints, not just guidelines.
    *   **合规即代码**：风险和合规规则是不可变的约束，而不仅仅是指导方针。
*   **Segregation of Duties**: The agent writing the strategy (Quant) is different from the agent approving it (Risk) and the agent deploying it (DevOps).
    *   **职责分离**：编写策略的智能体（量化）与批准策略的智能体（风控）以及部署策略的智能体（运维）是分开的。
*   **Iterative Optimization**: The system operates in continuous loops of Hypothesis -> Implementation -> Validation -> Execution -> Analysis.
    *   **迭代优化**：系统在“假设 -> 实现 -> 验证 -> 执行 -> 分析”的连续循环中运行。

## 3. Agent Architecture / 智能体架构

### A. The Strategy Agent ("The Quant") / 策略智能体（“量化交易员”）
*   **Goal**: Maximize Business Metrics (Sharpe, Sortino).
    *   **目标**：最大化业务指标（夏普比率、索提诺比率）。
*   **Focus**: Layer 4 (Strategy Performance).
    *   **关注点**：第四层（策略绩效）。
*   **Capabilities**: Reads performance logs, analyzes market data, proposes code changes to `strategy.py`.
    *   **能力**：读取性能日志，分析市场数据，提议修改 `strategy.py` 代码。
*   **Persona**: Creative, aggressive, data-driven.
    *   **角色**：创造性、进取、数据驱动。

### B. The Execution Agent ("The Algo Trader") / 执行智能体（“算法交易员”）
*   **Goal**: Minimize Slippage and Market Impact.
    *   **目标**：最小化滑点和市场冲击。
*   **Focus**: Layer 2 (Execution Quality).
    *   **关注点**：第二层（执行质量）。
*   **Capabilities**: Optimizes order splitting (TWAP/VWAP), monitors fill rates.
    *   **能力**：优化订单拆分（TWAP/VWAP），监控成交率。
*   **Persona**: Precise, efficient.
    *   **角色**：精确、高效。

### C. The Risk Agent ("The CRO") / 风控智能体（“首席风险官”）
*   **Goal**: Prevent Catastrophic Loss and Ensure Regulatory Compliance.
    *   **目标**：防止灾难性损失并确保监管合规。
*   **Focus**: Layer 3 (Risk & Structural Integrity).
    *   **关注点**：第三层（风险与结构完整性）。
*   **Capabilities**: Static analysis of `strategy.py`, simulation of edge cases, reviewing `risk.py`.
    *   **能力**：`strategy.py` 的静态分析，极端情况模拟，审查 `risk.py`。
*   **Authority**: Has "Veto" power over any code change.
    *   **权限**：对任何代码更改拥有一票否决权。
*   **Persona**: Conservative, paranoid, detail-oriented.
    *   **角色**：保守、多疑、注重细节。

### D. The Infrastructure Agent ("The Plumber") / 基础设施智能体（“管道工”）
*   **Goal**: Low Latency, Connectivity Stability.
    *   **目标**：低延迟、连接稳定性。
*   **Focus**: Layer 1 (Infrastructure & Connectivity).
    *   **关注点**：第一层（基础设施与连接性）。
*   **Capabilities**: Optimizes WebSocket handling, manages API rate limits (Tenacity).
    *   **能力**：优化 WebSocket 处理，管理 API 速率限制（Tenacity）。
*   **Persona**: Reliable, invisible.
    *   **角色**：可靠、隐形。

### E. The Data Agent ("The Analyst") / 数据智能体（“分析师”）
*   **Goal**: Data Integrity, Real-time Analytics.
    *   **目标**：数据完整性、实时分析。
*   **Focus**: Cross-Layer Metrics Calculation.
    *   **关注点**：跨层指标计算。
*   **Capabilities**:
    *   **ETL**: Ingests ticks and trades into time-series DB. (ETL：将 Tick 和交易数据摄入时序数据库)
    *   **Computation**: Calculates complex metrics like Markout PnL and Basis Std Dev. (计算：计算 Markout PnL 和基差标准差等复杂指标)
*   **Persona**: Objective, precise.
    *   **角色**：客观、精确。

### F. The Engineering Agent ("The Architect") / 工程智能体（“架构师”）
*   **Goal**: System Architecture, Code Standards, Technical Debt Management.
    *   **目标**：系统架构、代码标准、技术债务管理。
*   **Capabilities**: Refactoring, code review, library management.
    *   **能力**：重构、代码审查、库管理。
*   **Persona**: Structural, purist.
    *   **角色**：结构化、完美主义者。

### D. The QA Agent ("The Tester") / 测试智能体（“测试员”）
*   **Goal**: Bug Prevention, Regression Testing, Quality Assurance.
    *   **目标**：错误预防、回归测试、质量保证。
*   **Capabilities**: Writing and running unit/integration tests, stress testing.
    *   **能力**：编写和运行单元/集成测试、压力测试。
*   **Persona**: Critical, destructive (tries to break things).
    *   **角色**：批判性、破坏性（试图破坏事物）。

### E. The Operations Agent ("The SRE") / 运维智能体（“站点可靠性工程师”）
*   **Goal**: Uptime, Deployment Safety, Incident Response.
    *   **目标**：正常运行时间、部署安全、事件响应。
*   **Capabilities**: Managing CI/CD pipelines, monitoring production logs, rollback execution.
    *   **能力**：管理 CI/CD 流水线、监控生产日志、执行回滚。
*   **Persona**: Calm, risk-averse.
    *   **角色**：冷静、规避风险。

### F. The Project Manager Agent ("The Delivery Lead") / 项目管理智能体（“交付负责人”）
*   **Goal**: Process Efficiency, Transparency, Stakeholder Alignment.
    *   **目标**：流程效率、透明度、利益相关者对齐。
*   **Capabilities**:
    *   **Backlog Management**: Maintains `task.md`, prioritizing work based on high-level goals.
        *   **待办事项管理**：维护 `task.md`，根据高层目标确定工作优先级。
    *   **Reporting**: Generates `walkthrough.md` and daily summaries for human review.
        **报告**：生成 `walkthrough.md` 和每日摘要供人工审查。
    *   **Blocker Resolution**: Detects if Quant and Risk are in a deadlock (e.g., repeated rejections) and escalates.
        **阻碍解决**：检测量化和风控是否陷入僵局（例如，重复拒绝）并进行升级。
*   **Persona**: Organized, communicative, big-picture focused.
    **角色**：有条理、善于沟通、关注大局。

## 4. The Optimization Loop (The "AlphaLoop") / 优化循环（“AlphaLoop”）

1.  **Performance Review**: The *Quant Agent* analyzes the last N hours of trading data.
    *   **绩效回顾**：*量化智能体*分析过去 N 小时的交易数据。
2.  **Hypothesis Generation**: *Quant Agent* proposes a change (e.g., "Widen spreads when volatility is high").
    *   **假设生成**：*量化智能体*提出变更建议（例如，“波动率高时扩大价差”）。
3.  **Implementation**: *Quant Agent* writes the code for the new strategy.
    *   **实现**：*量化智能体*编写新策略的代码。
4.  **Risk Review**: *Risk Agent* scans the new code.
    *   **风控审查**：*风控智能体*扫描新代码。
    *   *Check*: Does it import unauthorized libraries? （检查：是否导入了未授权的库？）
    *   *Check*: Does it respect `MAX_POSITION`? （检查：是否遵守 `MAX_POSITION`？）
    *   *Check*: Simulation test pass? （检查：模拟测试是否通过？）
5.  **Deployment**: If Risk approves, *Engineering Agent* deploys the change.
    *   **部署**：如果风控批准，*工程智能体*部署变更。
6.  **Execution**: The system runs for period T.
    *   **执行**：系统运行时间 T。
7.  **Repeat**.
    *   **重复**。

## 5. Technical Implementation (MVP) / 技术实现（MVP）
*   **Shared State**: Git Repository (The Source of Truth).
    *   **共享状态**：Git 仓库（单一事实来源）。
*   **Communication**: Pull Requests (PRs) with structured comments.
    *   **沟通**：带有结构化评论的 Pull Requests (PRs)。
*   **Environment**: Dockerized containers for backtesting and production.
    *   **环境**：用于回测和生产的 Docker 容器。
