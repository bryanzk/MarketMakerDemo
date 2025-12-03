# Development Workflow / 开发流程

This document provides a clear, step-by-step guide to the 17-step development pipeline used in MarketMakerDemo.
本文档提供了 MarketMakerDemo 项目中使用的 17 步开发流程的清晰分步指南。

---

## 📋 Overview / 概览

Every feature in MarketMakerDemo follows a **17-step pipeline** from specification to production deployment. The workflow is divided into 7 phases with 2 human approval gates (Steps 4, 17). Each step has a responsible Agent and produces specific artifacts.
MarketMakerDemo 中的每个功能都遵循从规范到生产部署的 **17 步流程**。流程分为 7 个阶段，包含 2 个人工批准门禁（步骤 4, 17）。每个步骤都有负责的 Agent 并产生特定的产物。

### Quick Reference / 快速参考

```
Plan: Spec → Story → AC → [APPROVAL] → Design: Contract → 
Dev: Test(Red) → Code(Green) → Quality: Lint → Security → 
Review → Test: Unit → Smoke → Integration → 
Docs: Docs → Progress → CI/CD → [RELEASE]
```

### Phase Organization / 阶段划分

1. **Phase 1: Plan (规划)** - Steps 1-4 - 需求定义和批准 / Requirements definition and approval
2. **Phase 2: Design (设计)** - Step 5 - 接口契约定义 / Interface contract definition
3. **Phase 3: Dev (开发 - TDD)** - Steps 6-7 - 测试驱动开发 / Test-driven development
4. **Phase 4: Quality (静态质量)** - Steps 8-9 - 代码格式检查和安全检查 / Code formatting and security check
5. **Phase 5: Review (审查)** - Step 10 - 代码审查 / Code review
6. **Phase 6: Test (动态测试)** - Steps 11-13 - 单元测试、冒烟测试、集成测试 / Unit, smoke, and integration tests
7. **Phase 7: Docs & Ops (文档与交付)** - Steps 14-17 - 文档更新、进度记录、CI/CD 检查、发布批准 / Documentation, progress logging, CI/CD checks, release approval

---

## 🔄 The 17-Step Pipeline / 17 步流程

### Step 1: Spec Defined / 规范定义
**Agent:** Agent PO  
**Artifact:** `docs/specs/{module}/{feature}.md`  
**Status Field:** `spec_defined`

**What happens / 发生什么：**
- Product Owner writes a detailed specification document
- 产品负责人编写详细的规范文档
- Defines what the feature should do, why it's needed, and success criteria
- 定义功能应该做什么、为什么需要它以及成功标准

**Example / 示例：**
```markdown
# CORE-001: Exchange Connection
## Purpose
Provide reliable Binance API connectivity...

## Success Criteria
- Connection retry logic works
- Credentials are secure
```

---

### Step 2: Story Defined / 用户故事定义
**Agent:** Agent PO  
**Artifact:** `docs/stories/{module}/US-{ID}.md`  
**Status Field:** `story_defined`

**What happens / 发生什么：**
- User story written in "As a... I want... So that..." format
- 以"作为...我想要...以便..."格式编写用户故事
- Includes personas and use cases
- 包括角色和使用场景

**Example / 示例：**
```markdown
# US-CORE-001
As a trading bot operator,
I want the system to automatically reconnect to Binance when connection drops,
So that trading can continue without manual intervention.
```

---

### Step 3: Acceptance Criteria Defined / 验收标准定义
**Agent:** Agent PO  
**Artifact:** Inside story document  
**Status Field:** `ac_defined`

**What happens / 发生什么：**
- Detailed acceptance criteria added to the user story
- 在用户故事中添加详细的验收标准
- Each criterion is testable and measurable
- 每个标准都是可测试和可衡量的

**Example / 示例：**
```markdown
## Acceptance Criteria
- [ ] Connection retries up to 3 times with exponential backoff
- [ ] Credentials are stored in environment variables, not code
- [ ] Health check endpoint returns connection status
```

---

### Step 4: Plan Approved / 计划批准 🛑 STOP GATE
**Agent:** Human  
**Artifact:** Approval confirmation / 批准确认  
**Status Field:** `plan_approved`

**What happens / 发生什么：**
- Human reviewer approves the plan (spec, story, AC)
- 人工审查员批准计划（规范、用户故事、验收标准）
- This is a **STOP GATE** - development cannot proceed without approval
- 这是一个**停止门禁** - 未经批准，开发无法继续进行

**Approval Criteria / 批准标准：**
- ✅ Specification is complete and clear
- ✅ 规范完整且清晰
- ✅ User story follows format and includes personas
- ✅ 用户故事遵循格式并包含角色
- ✅ Acceptance criteria are testable and measurable
- ✅ 验收标准可测试且可衡量

---

### Step 5: Contract Defined / 接口契约定义
**Agent:** Agent ARCH  
**Artifact:** `contracts/{module}.json`  
**Status Field:** `contract_defined`

**What happens / 发生什么：**
- Architect defines the public API interface
- 架构师定义公共 API 接口
- Specifies function signatures, data types, and error handling
- 指定函数签名、数据类型和错误处理

**Example / 示例：**
```json
{
  "ExchangeClient": {
    "connect": {
      "params": ["api_key", "api_secret"],
      "returns": "ConnectionStatus",
      "errors": ["ConnectionError", "AuthError"]
    }
  }
}
```

---

### Step 5: Unit Test Written / 单元测试编写
**Agent:** Module Owner (TRADING/PORTFOLIO/WEB/AI)  
**Artifact:** `tests/unit/{module}/test_{feature}.py`  
**Status Field:** `unit_test_written`

**What happens / 发生什么：**
- Developer writes unit tests **BEFORE** writing code (TDD)
- 开发者在编写代码**之前**编写单元测试（TDD）
- Tests will fail initially (red phase)
- 测试最初会失败（红色阶段）

**Example / 示例：**
```python
def test_exchange_connection():
    client = ExchangeClient()
    status = client.connect(api_key, api_secret)
    assert status.is_connected == True
```

---

### Step 6: Code Implemented / 代码实现
**Agent:** Module Owner  
**Artifact:** `src/{module}/...`  
**Status Field:** `code_implemented`

**What happens / 发生什么：**
- Developer implements the feature to make tests pass (green phase)
- 开发者实现功能以使测试通过（绿色阶段）
- Code must follow the contract defined in Step 5
- 代码必须遵循步骤 5 中定义的契约

**Example / 示例：**
```python
class ExchangeClient:
    def connect(self, api_key: str, api_secret: str) -> ConnectionStatus:
        # Implementation here
        pass
```

---

### Step 8: Lint Passed / 代码格式检查通过
**Agent:** Dev Agent + Tool  
**Artifact:** Linter report / Linter 报告  
**Status Field:** `lint_passed`

**What happens / 发生什么：**
- Code formatting and style checks are performed
- 执行代码格式和风格检查
- Uses tools like flake8, black, isort
- 使用 flake8、black、isort 等工具

**Command / 命令：**
```bash
flake8 src/{module}/
black --check src/{module}/
isort --check src/{module}/
```

**Requirements / 要求：**
- ✅ All linting errors must be fixed
- ✅ 必须修复所有 linting 错误
- ✅ Code follows PEP 8 style guide
- ✅ 代码遵循 PEP 8 风格指南

---

### Step 9: Security Check Passed / 安全检查通过
**Agent:** Dev Agent + Tool  
**Artifact:** Security scan report / 安全扫描报告  
**Status Field:** `security_check_passed`

**What happens / 发生什么：**
- Security vulnerability scanning is performed
- 执行安全漏洞扫描
- Checks for common security issues (SQL injection, XSS, etc.)
- 检查常见安全问题（SQL 注入、XSS 等）

**Command / 命令：**
```bash
bandit -r src/{module}/
safety check
```

**Requirements / 要求：**
- ✅ No critical or high-severity vulnerabilities
- ✅ 无严重或高危漏洞
- ✅ All security issues must be addressed
- ✅ 必须解决所有安全问题

---

### Step 10: Code Reviewed / 代码审查
**Agent:** Agent REVIEW  
**Artifact:** `logs/reviews/{feature}.json`  
**Status Field:** `code_reviewed`

**What happens / 发生什么：**
- Code reviewer checks for quality, security, and best practices
- 代码审查员检查质量、安全性和最佳实践
- Review results logged in JSON format
- 审查结果以 JSON 格式记录

**Example / 示例：**
```json
{
  "feature_id": "CORE-001",
  "reviewer": "Agent REVIEW",
  "status": "approved",
  "issues": [],
  "suggestions": ["Add type hints"]
}
```

---

### Step 11: Unit Test Passed / 单元测试通过
**Agent:** Module Owner  
**Artifact:** pytest reports  
**Status Field:** `unit_test_passed`

**What happens / 发生什么：**
- All unit tests must pass
- 所有单元测试必须通过
- Coverage should meet project standards
- 覆盖率应达到项目标准

**Command / 命令：**
```bash
pytest tests/unit/{module}/test_{feature}.py --cov=src/{module}
```

---

### Step 12: Smoke Test Passed / 冒烟测试通过
**Agent:** Agent QA  
**Artifact:** `tests/smoke/` reports  
**Status Field:** `smoke_test_passed`

**What happens / 发生什么：**
- Quick sanity checks to ensure basic functionality works
- 快速健全性检查以确保基本功能正常工作
- Tests critical paths without full integration
- 测试关键路径，无需完整集成

**Example / 示例：**
```python
def test_smoke_exchange_connection():
    # Quick test: can we connect?
    client = ExchangeClient()
    assert client.connect() is not None
```

---

### Step 13: Integration Test Passed / 集成测试通过
**Agent:** Agent QA  
**Artifact:** `tests/integration/` reports  
**Status Field:** `integration_passed`

**What happens / 发生什么：**
- Full integration tests with real dependencies
- 使用真实依赖的完整集成测试
- Tests module interactions and end-to-end flows
- 测试模块交互和端到端流程

**Example / 示例：**
```python
def test_integration_trading_flow():
    # Test: Exchange → Order Manager → Portfolio
    exchange = ExchangeClient()
    order_mgr = OrderManager(exchange)
    portfolio = PortfolioManager()
    # ... full flow test
```

---

### Step 14: Docs Updated / 文档更新
**Agent:** Agent QA  
**Artifact:** `docs/user_guide/{module}/...`  
**Status Field:** `docs_updated`

**What happens / 发生什么：**
- User-facing documentation written or updated
- 编写或更新面向用户的文档
- Includes usage examples and API reference
- 包括使用示例和 API 参考

**Example / 示例：**
```markdown
# Exchange Connection Guide
## Usage
```python
from src.trading.exchange import ExchangeClient
client = ExchangeClient()
client.connect(api_key, api_secret)
```
```

---

### Step 15: Progress Logged / 进度记录
**Agent:** Agent PM  
**Artifact:** `status/roadmap.json`  
**Status Field:** `progress_logged`

**What happens / 发生什么：**
- Project Manager updates the roadmap
- 项目经理更新路线图
- Adds event to progress index
- 在进度索引中添加事件

**Automation / 自动化：**
```bash
python scripts/advance_feature.py CORE-001 progress_logged
```

---

### Step 16: CI/CD Passed / CI/CD 通过
**Agent:** Automated  
**Artifact:** GitHub Actions results / GitHub Actions 结果  
**Status Field:** `ci_cd_passed`

**What happens / 发生什么：**
- Automated CI/CD pipeline runs all checks
- 自动化 CI/CD 管道运行所有检查
- All automated checks must pass
- 所有自动化检查必须通过

**Checks / 检查：**
- ✅ Linting (flake8, black, isort)
- ✅ Security scanning
- ✅ Unit tests
- ✅ Integration tests
- ✅ Code coverage

---

### Step 17: Release Approved / 发布批准 🛑 STOP GATE
**Agent:** Human  
**Artifact:** Release approval confirmation / 发布批准确认  
**Status Field:** `release_approved`

**What happens / 发生什么：**
- Human reviewer approves the feature for release
- 人工审查员批准功能发布
- This is a **STOP GATE** - feature cannot be released without approval
- 这是一个**停止门禁** - 未经批准，功能无法发布

**Approval Criteria / 批准标准：**
- ✅ All tests pass
- ✅ 所有测试通过
- ✅ Documentation is complete
- ✅ 文档完整
- ✅ Code review is approved
- ✅ 代码审查已批准
- ✅ CI/CD pipeline passed
- ✅ CI/CD 管道通过

---

## 🚀 Automation / 自动化

### Using `advance_feature.py` / 使用 `advance_feature.py`

Instead of manually editing JSON files, use the automation script:
无需手动编辑 JSON 文件，使用自动化脚本：

```bash
# Basic usage
python scripts/advance_feature.py CORE-001 story_defined

# With full context
python scripts/advance_feature.py CORE-001 code_implemented \
  --pr "#123" \
  --branch "feature/CORE-001" \
  --author "Agent TRADING" \
  --notes "Implementation complete"
```

**What it does / 它做什么：**
1. Updates `docs/modules/{module}.json` → `current_step`
2. Syncs `status/roadmap.json`
3. Adds event to `docs/progress/progress_index.json`
4. Runs `scripts/audit_check.py` to validate

---

## 📊 Pipeline Visualization / 流程可视化

```
┌─────────────────────────────────────────────────────────────────┐
│                   17-Step Development Pipeline                   │
│                     17 步开发流程                                │
│          (7 Phases with 2 Human Approval Gates)                 │
│          (7 个阶段，包含 2 个人工批准门禁)                      │
└─────────────────────────────────────────────────────────────────┘

Phase 1: Plan (规划)
Step 1: Spec Defined (Agent PO)
   ↓
Step 2: Story Defined (Agent PO)
   ↓
Step 3: AC Defined (Agent PO)
   ↓
Step 4: Plan Approved (Human) 🛑 STOP GATE
   ↓
Phase 2: Design (设计)
Step 5: Contract Defined (Agent ARCH)
   ↓
Phase 3: Dev (开发 - TDD)
Step 6: Unit Test Written (Dev Agent) ← TDD: Red - Write tests first
   ↓
Step 7: Code Implemented (Dev Agent) ← TDD: Green - Make tests pass
   ↓
Phase 4: Quality (静态质量)
Step 8: Lint Passed (Dev Agent + Tool)
   ↓
Step 9: Security Check Passed (Dev Agent + Tool)
   ↓
Phase 5: Review (审查)
Step 10: Code Reviewed (Agent REVIEW)
   ↓
Phase 6: Test (动态测试)
Step 11: Unit Test Passed (Dev Agent)
   ↓
Step 12: Smoke Test Passed (Agent QA)
   ↓
Step 13: Integration Passed (Agent QA)
   ↓
Phase 7: Docs & Ops (文档与交付)
Step 14: Docs Updated (Agent QA)
   ↓
Step 15: Progress Logged (Agent PM)
   ↓
Step 16: CI/CD Passed (Automated)
   ↓
Step 17: Release Approved (Human) 🛑 STOP GATE
   ↓
✅ Feature Complete / 功能完成
```

---

## ⚠️ Important Rules / 重要规则

### 1. No Skipping Steps / 禁止跳步
- ❌ Cannot write code before tests (Step 7 before Step 6)
- ❌ 不能在测试之前编写代码（步骤 7 在步骤 6 之前）
- ❌ Cannot review before implementation (Step 10 before Step 7)
- ❌ 不能在实现之前审查（步骤 10 在步骤 7 之前）
- ❌ Cannot proceed without plan approval (Step 5 before Step 4)
- ❌ 未经计划批准不能继续（步骤 5 在步骤 4 之前）
- ❌ Cannot release without approval (Step 17 is required)
- ❌ 未经批准不能发布（步骤 17 是必需的）

### 2. TDD Principle / TDD 原则
- **Always write tests first** (Step 6 - Red Phase)
- **始终先编写测试**（步骤 6 - 红色阶段）
- Then implement code to pass tests (Step 7 - Green Phase)
- 然后实现代码以使测试通过（步骤 7 - 绿色阶段）

### 3. Human Approval Gates / 人工批准门禁
- **Step 4: Plan Approved** - Must be approved before design phase
- **步骤 4：计划批准** - 必须在设计阶段之前获得批准
- **Step 17: Release Approved** - Must be approved before release
- **步骤 17：发布批准** - 必须在发布之前获得批准

### 4. Agent Responsibilities / Agent 职责
- Each step has a specific responsible Agent
- 每个步骤都有特定的负责 Agent
- Do not modify files outside your responsibility
- 不要修改您职责范围之外的文件

---

## 📚 Related Documents / 相关文档

- [Development Protocol](development_protocol.md) - Detailed standards
- [Feature Automation Guide](development_protocol_feature_automation.md) - Automation scripts
- [Module Overview](modules_overview.md) - Module responsibilities
- [Project Manifest](../project_manifest.json) - Complete project structure

---

## 🎯 Quick Start for New Developers / 新开发者快速开始

1. **Read the spec** (`docs/specs/{module}/{feature}.md`)
   - **阅读规范** (`docs/specs/{module}/{feature}.md`)

2. **Read the story** (`docs/stories/{module}/US-{ID}.md`)
   - **阅读用户故事** (`docs/stories/{module}/US-{ID}.md`)

3. **Check the contract** (`contracts/{module}.json`)
   - **检查契约** (`contracts/{module}.json`)

4. **Write tests** (`tests/unit/{module}/test_{feature}.py`)
   - **编写测试** (`tests/unit/{module}/test_{feature}.py`)

5. **Implement code** (`src/{module}/...`)
   - **实现代码** (`src/{module}/...`)

6. **Use automation** to advance the feature:
   - **使用自动化**推进功能：
   ```bash
   python scripts/advance_feature.py {feature_id} {next_step}
   ```

---

**Last Updated / 最后更新:** 2025-12-01  
**Maintained by / 维护者:** Agent PM


