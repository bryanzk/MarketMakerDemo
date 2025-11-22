# Agent Business Workflows / 智能体业务流程

## 1. Overview / 概述
This document details the step-by-step interactions between agents for specific business scenarios. It maps the lifecycle of a task from inception to production.

本文档详细说明了特定业务场景下智能体之间的一步步交互。它映射着任务从开始到生产的生命周期。

### Scenario A: The "New Idea" Flow / 场景 A：“新想法”流程
**Story**: A human stakeholder wants a new "Mean Reversion" strategy.
**故事**：人类利益相关者想要一个新的“均值回归”策略。

**Steps / 步骤**:
1.  **Human** tells **PM**: "I want this."
2.  **PM** asks **Quant**: "Design it."
3.  **Quant** writes the logic.
4.  **Risk** checks: "Is it safe?" (Crucial Step!)
5.  **Eng** builds it.
6.  **QA** tests it.
7.  **Ops** deploys it.

```mermaid
sequenceDiagram
    participant Human as Human Stakeholder/人类
    participant PM as PM Agent/项目经理
    participant Quant as Quant Agent/量化
    participant Risk as Risk Agent/风控
    participant Eng as Eng Agent/工程
    participant QA as QA Agent/测试
    participant Ops as Ops Agent/运维

    Human->>PM: Request "Mean Reversion Strategy" (请求“均值回归策略”)
    PM->>Quant: Assign Task: Design Logic (分配任务：设计逻辑)
    Quant->>PM: Submit Specification (提交规格说明)
    PM->>Risk: Request Review (请求审查)
    
    alt Risk Rejects (风控拒绝)
        Risk-->>PM: Reject (Too risky) (拒绝 - 风险过高)
        PM->>Quant: Revise Strategy (修改策略)
    else Risk Approves (风控批准)
        Risk->>PM: Approve (批准)
        PM->>Eng: Assign Task: Implement Code (分配任务：实现代码)
        Eng->>QA: Submit for Testing (提交测试)
        
        alt QA Fails (测试失败)
            QA-->>Eng: Bug Found (发现 Bug)
            Eng->>QA: Fix & Resubmit (修复并重新提交)
        else QA Passes (测试通过)
            QA->>Ops: Ready for Deployment (准备部署)
            Ops->>Ops: Deploy to Staging (部署到预发)
            Ops->>Ops: Deploy to Production (部署到生产)
            Ops-->>PM: Deployment Complete (部署完成)
            PM-->>Human: Feature Live (功能已上线)
        end
    end
```

### Scenario B: The "Self-Optimization" Loop / 场景 B：“自我优化”循环
**Story**: The system is running. The Quant Agent notices we are losing money because the spread is too tight.
**故事**：系统正在运行。量化智能体注意到我们因为价差太窄而亏损。

**Steps / 步骤**:
1.  **Quant** reads the data (from Data Agent).
2.  **Quant** thinks: "If I widen the spread, we make more."
3.  **Quant** asks **Risk**: "Can I change spread to 0.5%?"
4.  **Risk** checks limits: "Yes, 0.5% is safe."
5.  **Ops** updates the live system.

```mermaid
sequenceDiagram
    participant Quant as Quant Agent/量化
    participant Risk as Risk Agent/风控
    participant Ops as Ops Agent/运维
    participant Prod as Production/生产环境

    Quant->>Prod: Read Performance Logs (读取性能日志)
    Quant->>Quant: Analyze & Generate Hypothesis (分析并生成假设)
    Note right of Quant: e.g., "Widen spread by 10%" (例如，“扩大价差 10%”)
    
    Quant->>Risk: Propose Config Change (提议配置更改)
    
    alt Risk Rejects (风控拒绝)
        Risk-->>Quant: Deny (Violates Limits) (拒绝 - 违反限制)
        Note right of Risk: Loop Ends (循环结束)
    else Risk Approves (风控批准)
        Risk->>Ops: Approve Change (批准更改)
        Ops->>Prod: Hot Reload Config (热重载配置)
        Prod-->>Quant: New Data Generated (生成新数据)
    end
```

## 4. Scenario C: Production Incident Response / 场景 C：生产事故响应
**Trigger**: Production PnL drops below safety threshold.
**触发器**：生产环境 PnL 跌破安全阈值。

```mermaid
sequenceDiagram
    participant Prod as Production/生产环境
    participant Ops as Ops Agent/运维
    participant PM as PM Agent/项目经理
    participant Eng as Eng Agent/工程
    participant Risk as Risk Agent/风控

    Prod->>Ops: Alert: PnL Critical Drop (报警：PnL以此下跌)
    Ops->>Prod: EXECUTE EMERGENCY STOP (执行紧急停止)
    Ops->>PM: Report Incident (报告事故)
    
    PM->>Risk: Request Incident Review (请求事故审查)
    PM->>Eng: Assign: Root Cause Analysis (分配：根本原因分析)
    
    Eng->>PM: Report: Logic Bug Found (报告：发现逻辑 Bug)
    PM->>Eng: Assign: Fix (分配：修复)
    
    Note over Eng, Ops: Follows Standard Deployment Flow (Scenario A) (遵循标准部署流程 - 场景 A)
```
