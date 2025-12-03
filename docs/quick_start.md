# Quick Start Guide / 快速入门指南

This guide helps new team members understand MarketMakerDemo in 5 minutes.
本指南帮助新团队成员在 5 分钟内了解 MarketMakerDemo。

---

## 🎯 What is MarketMakerDemo? / 什么是 MarketMakerDemo?

**MarketMakerDemo** is an autonomous market making bot that uses AI agents to optimize trading strategies in real-time.
**MarketMakerDemo** 是一个自主做市机器人，使用 AI 智能体实时优化交易策略。

**Key Concept / 核心概念：**
- Traditional bots: Static logic, manual tuning
- 传统机器人：静态逻辑，手动调优
- MarketMakerDemo: Self-optimizing with AI agents
- MarketMakerDemo：使用 AI 智能体自我优化

---

## 📋 Project Structure at a Glance / 项目结构一览

### 6 Core Modules / 6 个核心模块

| Module | Owner | Purpose |
|--------|-------|---------|
| **Shared** | Agent ARCH | Common utilities (config, logging, metrics) |
| **Trading** | Agent TRADING | Exchange connection, orders, strategies |
| **Portfolio** | Agent PORTFOLIO | Capital allocation, risk management |
| **AI** | Agent AI | LLM evaluation, strategy optimization |
| **Web** | Agent WEB | REST API, user interface |
| **QA** | Agent QA | Testing, documentation |

**📖 Full Details:** [Modules Overview](modules_overview.md)

---

## 🔄 Development Workflow / 开发流程

Every feature follows a **17-step pipeline** (7 phases with 2 human approval gates):
每个功能都遵循 **17 步流程**（7 个阶段，包含 2 个人工批准门禁）：

```
Spec → Story → AC → Contract → Test → Code → Review → Unit → Smoke → Integration → Docs → Progress → CI/CD
```

**Key Rules / 关键规则：**
1. ✅ **TDD**: Write tests BEFORE code (Step 5 before Step 6)
2. ✅ **TDD**：在编写代码之前编写测试（步骤 5 在步骤 6 之前）
3. ✅ **No Skipping**: Follow steps in order
4. ✅ **禁止跳步**：按顺序执行步骤
5. ✅ **Automation**: Use `advance_feature.py` instead of manual JSON edits
6. ✅ **自动化**：使用 `advance_feature.py` 而不是手动编辑 JSON

**📖 Full Details:** [Development Workflow](development_workflow.md)

---

## 🚀 Getting Started / 快速开始

### Step 1: Understand Your Role / 步骤 1：了解您的角色

**Check which Agent you are / 检查您是哪个 Agent：**
- Read `docs/agents/AGENT_X_XXX.md` for your responsibilities
- 阅读 `docs/agents/AGENT_X_XXX.md` 了解您的职责
- Each Agent owns specific modules and files
- 每个 Agent 拥有特定的模块和文件

### Step 2: Find Your Module / 步骤 2：找到您的模块

**Check module ownership / 检查模块所有权：**
```bash
cat project_manifest.json | grep -A 5 "owner_agent"
```

**Read your module card / 阅读您的模块卡片：**
```bash
cat docs/modules/{your_module}.json
```

### Step 3: Understand the Workflow / 步骤 3：理解工作流程

**Read the development workflow / 阅读开发流程：**
- [Development Workflow](development_workflow.md) - Complete guide
- [Development Workflow](development_workflow.md) - 完整指南

**Key steps for developers / 开发者的关键步骤：**
1. Read spec (`docs/specs/{module}/{feature}.md`)
2. Read story (`docs/stories/{module}/US-{ID}.md`)
3. Check contract (`contracts/{module}.json`)
4. Write tests (`tests/unit/{module}/test_{feature}.py`)
5. Implement code (`src/{module}/...`)
6. Use automation: `python scripts/advance_feature.py {feature_id} {next_step}`

### Step 4: Use Automation / 步骤 4：使用自动化

**Instead of manually editing JSON files, use:**
**不要手动编辑 JSON 文件，使用：**

```bash
# Advance a feature to the next step
python scripts/advance_feature.py CORE-001 story_defined

# With full context
python scripts/advance_feature.py CORE-001 code_implemented \
  --pr "#123" \
  --branch "feature/CORE-001" \
  --author "Agent TRADING" \
  --notes "Implementation complete"
```

**What it does / 它做什么：**
- ✅ Updates module JSON
- ✅ Syncs roadmap
- ✅ Adds progress event
- ✅ Runs audit check

---

## 📁 Key Directories / 关键目录

```
MarketMakerDemo/
├── src/                    # Source code (organized by module)
│   ├── shared/            # Shared platform
│   ├── trading/           # Trading engine
│   ├── portfolio/         # Portfolio & risk
│   ├── ai/                # AI & evaluation
│   └── web/               # Web & API
├── tests/                 # Tests (unit, smoke, integration)
├── docs/                  # Documentation
│   ├── modules/          # Module cards (JSON)
│   ├── specs/            # Specifications
│   ├── stories/          # User stories
│   └── user_guide/       # User documentation
├── contracts/            # Interface contracts
├── status/               # Roadmap & progress tracking
└── scripts/              # Automation scripts
```

---

## 🔑 Key Files / 关键文件

### For Understanding the Project / 用于理解项目

| File | Purpose |
|------|---------|
| `project_manifest.json` | Complete project structure and module definitions |
| `docs/modules/{module}.json` | Detailed module information and features |
| `status/roadmap.json` | Feature status tracking |
| `docs/progress/progress_index.json` | Event log of feature progress |

### For Development / 用于开发

| File | Purpose |
|------|---------|
| `docs/development_workflow.md` | Complete workflow guide |
| `docs/modules_overview.md` | Module responsibilities and dependencies |
| `scripts/advance_feature.py` | Automation tool for feature advancement |
| `scripts/audit_check.py` | Validation script for JSON consistency |

---

## ⚠️ Important Rules / 重要规则

### 1. Agent Ownership / Agent 所有权
- ✅ Only modify files in your module
- ✅ 只修改您模块中的文件
- ❌ Don't modify files outside your responsibility
- ❌ 不要修改您职责范围之外的文件

### 2. TDD Principle / TDD 原则
- ✅ Write tests FIRST (Step 5)
- ✅ 先编写测试（步骤 5）
- ✅ Then implement code (Step 6)
- ✅ 然后实现代码（步骤 6）

### 3. No Skipping Steps / 禁止跳步
- ❌ Cannot write code before tests
- ❌ 不能在测试之前编写代码
- ❌ Cannot review before implementation
- ❌ 不能在实现之前审查

### 4. Use Automation / 使用自动化
- ✅ Use `advance_feature.py` instead of manual JSON edits
- ✅ 使用 `advance_feature.py` 而不是手动编辑 JSON
- ✅ Run `audit_check.py` after changes
- ✅ 更改后运行 `audit_check.py`

---

## 📚 Reading Order / 阅读顺序

### For New Team Members / 对于新团队成员

1. **[Quick Start](quick_start.md)** ← You are here
   - **[快速入门](quick_start.md)** ← 您在这里

2. **[Development Workflow](development_workflow.md)**
   - Understand the 17-step pipeline
   - 理解 17 步流程

3. **[Modules Overview](modules_overview.md)**
   - Learn about all 6 modules
   - 了解所有 6 个模块

4. **[Your Agent Documentation](agents/README.md)**
   - Find your specific responsibilities
   - 找到您的具体职责

5. **[Development Protocol](development_protocol.md)**
   - Coding standards and best practices
   - 编码标准和最佳实践

### For Understanding the System / 用于理解系统

1. **[System Flow](system_flow.md)**
   - How the bot works end-to-end
   - 机器人如何端到端工作

2. **[Architecture](architecture.md)**
   - High-level system design
   - 高层系统设计

3. **[Framework Design](framework/framework_design.md)**
   - AlphaLoop framework details
   - AlphaLoop 框架详情

---

## 🛠️ Common Tasks / 常见任务

### Starting a New Feature / 开始新功能

```bash
# 1. Read the spec
cat docs/specs/{module}/{feature}.md

# 2. Read the story
cat docs/stories/{module}/US-{feature}.md

# 3. Check the contract
cat contracts/{module}.json

# 4. Write tests
# Edit tests/unit/{module}/test_{feature}.py

# 5. Implement code
# Edit src/{module}/...

# 6. Advance the feature
python scripts/advance_feature.py {feature_id} code_implemented
```

### Running Tests / 运行测试

```bash
# Unit tests
pytest tests/unit/{module}/

# All tests
pytest tests/

# With coverage
pytest --cov=src tests/
```

### Validating JSON Files / 验证 JSON 文件

```bash
# Run audit check
python scripts/audit_check.py
```

---

## 🆘 Need Help? / 需要帮助？

### Documentation / 文档
- [Development Workflow](development_workflow.md) - Workflow details
- [Modules Overview](modules_overview.md) - Module information
- [Development Protocol](development_protocol.md) - Standards
- [Feature Automation Guide](development_protocol_feature_automation.md) - Automation

### Key Contacts / 关键联系人
- **Agent PM** - Project management, roadmap
- **Agent PO** - Requirements, specifications
- **Agent ARCH** - Architecture, contracts
- **Module Owners** - Code implementation
- **Agent QA** - Testing, documentation

---

## ✅ Checklist for New Developers / 新开发者清单

- [ ] Read this Quick Start guide
- [ ] 阅读本快速入门指南
- [ ] Read [Development Workflow](development_workflow.md)
- [ ] 阅读 [开发流程](development_workflow.md)
- [ ] Read [Modules Overview](modules_overview.md)
- [ ] 阅读 [模块概览](modules_overview.md)
- [ ] Identify your Agent role
- [ ] 识别您的 Agent 角色
- [ ] Read your Agent documentation
- [ ] 阅读您的 Agent 文档
- [ ] Understand your module ownership
- [ ] 了解您的模块所有权
- [ ] Set up development environment
- [ ] 设置开发环境
- [ ] Run tests to verify setup
- [ ] 运行测试以验证设置
- [ ] Try the automation script
- [ ] 尝试自动化脚本

---

**Last Updated / 最后更新:** 2025-11-30  
**Maintained by / 维护者:** Agent PM


