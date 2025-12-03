# 🤖 Multi-Agent Development Guide / 多 Agent 开发指南

This document describes how to use multiple Cursor Chat sessions as independent Agents for parallel development.
本文档描述如何使用多个 Cursor Chat 会话作为独立的 Agent 进行并行开发。

---

## 📋 Agent Overview / Agent 概览

MarketMakerDemo uses a **9-Agent system** organized into three layers: Management, Development, and Quality.
MarketMakerDemo 使用 **9 个 Agent 系统**，分为三层：管理层、开发层和质量层。

### Management Layer / 管理层

| Agent | Role / 角色 | Responsibilities / 职责 | Documentation |
|-------|------------|------------------------|---------------|
| **[Agent PM](AGENT_PM.md)** | Project Manager / 项目管理 | Progress tracking, coordination, risk management / 进度跟踪、协调、风险管理 | `AGENT_PM.md` |
| **[Agent PO](AGENT_PO.md)** | Product Owner / 产品负责人 | Requirements, specifications, user stories / 需求、规范、用户故事 | `AGENT_PO.md` |
| **[Agent ARCH](AGENT_ARCH.md)** | Architect / 架构师 | Interface contracts, shared platform, module design / 接口契约、共享平台、模块设计 | `AGENT_ARCH.md` |

### Development Layer / 开发层

| Agent | Role / 角色 | Responsibilities / 职责 | Documentation |
|-------|------------|------------------------|---------------|
| **[Agent TRADING](AGENT_1_TRADING_ENGINE.md)** | Trading Engine / 交易引擎 | Exchange connection, order management, strategies / 交易所连接、订单管理、策略 | `AGENT_1_TRADING_ENGINE.md` |
| **[Agent PORTFOLIO](AGENT_2_PORTFOLIO.md)** | Portfolio Management / 组合管理 | Portfolio management, risk indicators, health monitoring / 组合管理、风险指标、健康监控 | `AGENT_2_PORTFOLIO.md` |
| **[Agent WEB](AGENT_3_WEB_API.md)** | Web/API / Web 与 API | FastAPI services, API routes, frontend templates / FastAPI 服务、API 路由、前端模板 | `AGENT_3_WEB_API.md` |
| **[Agent AI](AGENT_4_AI_AGENTS.md)** | AI/LLM / AI 评估层 | LLM integration, agents, evaluation framework / LLM 集成、智能体、评估框架 | `AGENT_4_AI_AGENTS.md` |

### Quality Layer / 质量层

| Agent | Role / 角色 | Responsibilities / 职责 | Documentation |
|-------|------------|------------------------|---------------|
| **[Agent QA](AGENT_5_DOCS_QA.md)** | Quality Assurance / 质量保证 | Integration tests, smoke tests, user docs, test review / 集成测试、冒烟测试、用户文档、测试审查 | `AGENT_5_DOCS_QA.md` |
| **[Agent REVIEW](AGENT_REVIEW.md)** | Code Reviewer / 代码审查 | Code quality, best practices, security review / 代码质量、最佳实践、安全审查 | `AGENT_REVIEW.md` |

---

## 🚀 Quick Start / 快速启动

### Step 1: Open Multiple Cursor Chat Sessions / 步骤 1：打开多个 Cursor Chat 会话

In Cursor, press `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux) to open Chat, then click `+` to create new chat sessions.
在 Cursor 中，按 `Cmd+L`（Mac）或 `Ctrl+L`（Windows/Linux）打开 Chat，然后点击 `+` 创建新的聊天会话。

### Step 2: Initialize Each Agent / 步骤 2：初始化每个 Agent

In each new Chat session, paste the following initialization prompt:
在每个新的 Chat 会话中，粘贴以下初始化提示：

```
请阅读文件 docs/agents/AGENT_XXX.md，了解你作为该 Agent 的职责和规范。
从现在开始，你只负责该文件中指定的模块。
在处理任何请求前，请先确认任务是否属于你的职责范围（见 .cursorrules）。
如果任务不属于你，请建议用户联系正确的 Agent。
```

Replace `AGENT_XXX` with the specific Agent document name:
将 `AGENT_XXX` 替换为特定的 Agent 文档名称：

- `AGENT_PM.md` - Project Manager
- `AGENT_PO.md` - Product Owner
- `AGENT_ARCH.md` - Architect
- `AGENT_1_TRADING_ENGINE.md` - Trading Engine (or `AGENT_TRADING.md`)
- `AGENT_2_PORTFOLIO.md` - Portfolio Management (or `AGENT_PORTFOLIO.md`)
- `AGENT_3_WEB_API.md` - Web/API (or `AGENT_WEB.md`)
- `AGENT_4_AI_AGENTS.md` - AI/LLM (or `AGENT_AI.md`)
- `AGENT_5_DOCS_QA.md` - Quality Assurance (or `AGENT_QA.md`)
- `AGENT_REVIEW.md` - Code Reviewer

### Step 3: Start Working / 步骤 3：开始工作

Each Agent can work independently on their assigned modules.
每个 Agent 可以独立处理其分配的模块。

---

## 📊 Agent Responsibility Matrix / Agent 职责矩阵

### Pipeline Steps / 流程步骤

| Step | Phase | Status Field | Responsible Agent | Artifact | Notes |
|------|------|-------------|-------------------|----------|------|
| 1 | Plan | `spec_defined` | Agent PO | `docs/specs/{module}/{feature}.md` | |
| 2 | Plan | `story_defined` | Agent PO | `docs/stories/{module}/US-{ID}.md` | |
| 3 | Plan | `ac_defined` | Agent PO | Acceptance criteria in story | |
| 4 | Plan | `plan_approved` | Human | 🛑 STOP GATE | **NEW** |
| 5 | Design | `contract_defined` | Agent ARCH | `contracts/{module}.json` | |
| 6 | Dev | `unit_test_written` | Dev Agent (按 owner) | `tests/unit/{module}/test_{feature}.py` | TDD: Red |
| 7 | Dev | `code_implemented` | Dev Agent (按 owner) | `src/{module}/...` | TDD: Green |
| 8 | Quality | `lint_passed` | Dev Agent + Tool | Linter 报告 | **NEW** |
| 9 | Quality | `security_check_passed` | Dev Agent + Tool | 安全扫描报告 | **NEW** |
| 10 | Review | `code_reviewed` | Agent REVIEW | `logs/reviews/{feature_id}.json` | |
| 11 | Test | `unit_test_passed` | Dev Agent (按 owner) | pytest 报告 | |
| 12 | Test | `smoke_test_passed` | Agent QA | `tests/smoke/` reports | |
| 13 | Test | `integration_passed` | Agent QA | `tests/integration/` reports | |
| 14 | Docs | `docs_updated` | Agent QA | `docs/user_guide/{module}/...` | |
| 15 | Ops | `progress_logged` | Agent PM | `status/roadmap.json` | |
| 16 | Ops | `ci_cd_passed` | Automated | GitHub Actions 结果 | |
| 17 | Ops | `release_approved` | Human | 🛑 STOP GATE | **NEW** |

### File Ownership / 文件所有权

| Directory/File | Owner Agent |
|----------------|-------------|
| `docs/specs/` | Agent PO |
| `docs/stories/` | Agent PO |
| `contracts/` | Agent ARCH |
| `src/shared/` | Agent ARCH |
| `src/trading/` | Agent TRADING |
| `src/portfolio/` | Agent PORTFOLIO |
| `src/web/` | Agent WEB |
| `src/ai/` | Agent AI |
| `tests/` | Agent QA (coordination) + Module Owners |
| `docs/user_guide/` | Agent QA |
| `logs/reviews/` | Agent REVIEW |
| `status/` | Agent PM |
| `docs/agents/` | Agent PM |

---

## ⚠️ Conflict Avoidance Rules / 冲突避免规则

### 🔴 EXCLUSIVE (Exclusive Ownership) / 独占所有权

Only the specified Agent can modify these files:
只有指定的 Agent 可以修改这些文件：

| File | Exclusive Owner |
|------|----------------|
| `docs/specs/` | Agent PO |
| `docs/stories/` | Agent PO |
| `contracts/` | Agent ARCH |
| `src/shared/` | Agent ARCH |
| `src/trading/` | Agent TRADING |
| `src/portfolio/` | Agent PORTFOLIO |
| `src/web/` | Agent WEB |
| `src/ai/` | Agent AI |
| `tests/smoke/` | Agent QA |
| `tests/integration/` | Agent QA |
| `docs/user_guide/` | Agent QA |
| `logs/reviews/` | Agent REVIEW |
| `status/` | Agent PM |
| `docs/agents/` | Agent PM |

### 🟡 COORDINATED (Requires Coordination) / 需协调

Modify these files only after coordination:
仅在协调后修改这些文件：

| File | Coordination Rule |
|------|------------------|
| `requirements.txt` | Request in `status/agent_requests.json` |
| `pyproject.toml` | Request in `status/agent_requests.json` |
| `.cursorrules` | Only Agent PM can modify |

### 🟢 SHARED-APPEND (Shared Append) / 共享追加

These files can be appended to, but follow specific rules:
可以追加这些文件，但需遵循特定规则：

| File | Rule |
|------|------|
| `status/roadmap.json` | Only modify `status.*` fields for your step |
| `status/agent_requests.json` | Only append new requests or update own requests |
| `logs/audit_trail.json` | Append-only, cannot modify history |

---

## 📝 Collaboration Protocol / 协作协议

### Cross-Agent Requests / 跨 Agent 请求

When you need another Agent's help, create a request in `status/agent_requests.json`:
当你需要其他 Agent 的帮助时，在 `status/agent_requests.json` 中创建请求：

```json
{
  "id": "REQ-001",
  "from": "Agent TRADING",
  "to": "Agent ARCH",
  "type": "INTERFACE",
  "priority": "HIGH",
  "feature": "CORE-001",
  "description": "需要在 contracts/trading.json 中添加 cancelOrder 接口",
  "status": "OPEN",
  "created": "2025-11-30T10:00:00Z"
}
```

**Request Types / 请求类型：**
- `INTERFACE` - Need to add/modify interface
- `CONFIG` - Need to modify shared configuration
- `BLOCKER` - Blocked, needs priority handling
- `REVIEW` - Need code review
- `CLARIFY` - Need requirement clarification

### Interface Change Notification / 接口变更通知

When modifying a public interface:
修改公共接口时：

1. Document the change in the Agent documentation
2. 在 Agent 文档中记录变更
2. Notify dependent Agents via `agent_requests.json`
3. 通过 `agent_requests.json` 通知依赖的 Agent
4. Update related documentation
5. 更新相关文档

### Shared Configuration Changes / 共享配置变更

When modifying shared configuration:
修改共享配置时：

1. Create a request in `status/agent_requests.json`
2. 在 `status/agent_requests.json` 中创建请求
2. Ensure backward compatibility
3. 确保向后兼容
4. Update all related tests
5. 更新所有相关测试

---

## 🔧 Common Commands / 常用命令

```bash
# Run all tests
pytest tests/ -v

# Run module-specific tests
pytest tests/unit/trading/ -v       # Agent TRADING
pytest tests/unit/portfolio/ -v     # Agent PORTFOLIO
pytest tests/unit/web/ -v           # Agent WEB
pytest tests/unit/ai/ -v            # Agent AI

# Run smoke tests
pytest tests/smoke/ -v               # Agent QA

# Run integration tests
pytest tests/integration/ -v        # Agent QA

# Start server
python server.py

# Check code style
flake8 src/

# Advance feature through pipeline
python scripts/advance_feature.py {feature_id} {next_step}

# Run audit check
python scripts/audit_check.py
```

---

## 💡 Best Practices / 最佳实践

1. **Before Starting Work / 开始工作前**
   - Pull latest code
   - 拉取最新代码
   - Read your Agent documentation
   - 阅读你的 Agent 文档
   - Check `.cursorrules` for your responsibilities
   - 检查 `.cursorrules` 了解你的职责

2. **Before Modifying / 修改前**
   - Confirm file belongs to your responsibility
   - 确认文件属于你的职责范围
   - Read related specifications and contracts
   - 阅读相关规范和契约
   - Check for dependencies
   - 检查依赖关系

3. **After Completing / 完成后**
   - Run relevant tests
   - 运行相关测试
   - Use automation scripts to advance features
   - 使用自动化脚本推进功能
   - Update documentation if needed
   - 如需要，更新文档

4. **When Committing / 提交时**
   - Use proper commit message format
   - 使用适当的提交信息格式
   - Reference feature ID if applicable
   - 如适用，引用功能 ID
   - Follow commit type conventions
   - 遵循提交类型约定

---

## 📞 Agent Communication / Agent 间通信

### Direct Communication / 直接通信

If you need another Agent's help:
如果你需要其他 Agent 的帮助：

```
@Agent ARCH: 请在 contracts/trading.json 中添加 cancelOrder 接口
@Agent QA: 请为 CORE-001 编写集成测试
@Agent PM: CORE-001 已完成，请更新进度
```

### Request Tracking / 请求跟踪

Record requests in:
在以下位置记录请求：

- `status/agent_requests.json` - Formal requests
- `status/agent_requests.json` - 正式请求
- Agent documentation - Informal notes
- Agent 文档 - 非正式注释

---

## 📚 Related Documents / 相关文档

- [Development Workflow](../development_workflow.md) - Complete 17-step pipeline
- [Modules Overview](../modules_overview.md) - Module structure and responsibilities
- [Development Protocol](../development_protocol.md) - Coding standards
- [Project Manifest](../../project_manifest.json) - Project structure map
- [Quick Start Guide](../quick_start.md) - Getting started guide

---

## 🎯 Agent Quick Reference / Agent 快速参考

| Agent | Pipeline Steps | Owned Directories |
|-------|---------------|-------------------|
| Agent PM | 12 | `status/`, `logs/`, `docs/agents/` |
| Agent PO | 1, 2, 3 | `docs/specs/`, `docs/stories/` |
| Agent ARCH | 4 | `contracts/`, `src/shared/` |
| Agent TRADING | 5, 6, 8 | `src/trading/` |
| Agent PORTFOLIO | 5, 6, 8 | `src/portfolio/` |
| Agent WEB | 5, 6, 8 | `src/web/` |
| Agent AI | 5, 6, 8 | `src/ai/` |
| Agent QA | 5, 9, 10, 11 | `tests/`, `docs/user_guide/` |
| Agent REVIEW | 7 | `logs/reviews/` |

---

**Last Updated / 最后更新:** 2025-11-30  
**Maintained by / 维护者:** Agent PM
