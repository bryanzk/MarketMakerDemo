# MarketMakerDemo / 做市商演示

![CI Status](https://github.com/bryanzk/MarketMakerDemo/actions/workflows/ci.yml/badge.svg)
## 📄 Project Baseline

The project baseline overview is documented in [Project Baseline](docs/project_baseline.md).

## 🤖 Introduction / 简介
**MarketMakerDemo** is an autonomous, self-optimizing market making bot designed for crypto markets. Unlike traditional bots with static logic, this system continuously analyzes its own performance and adapts its strategy in real-time.
**MarketMakerDemo** 是一个专为加密市场设计的自主、自我优化的做市商机器人。与具有静态逻辑的传统机器人不同，该系统持续分析自身性能并实时调整策略。

It is powered by **AlphaLoop**, an agentic framework where specialized AI agents (Quant, Risk, Operations) collaborate to manage the trading business.
它由 **AlphaLoop** 驱动，这是一个智能体框架，专门的 AI 智能体（量化、风控、运营）在此协作管理交易业务。

> **Code Location / 代码位置**: The `AlphaLoop` class is implemented in [`src/trading/engine.py`](src/trading/engine.py).
> **代码位置**：`AlphaLoop` 类实现在 [`src/trading/engine.py`](src/trading/engine.py) 中。

### 🏛️ Project Organization / 项目组织

This project follows an **Agent-First Architecture** with a **9-Agent system** organized into three layers:
本项目遵循**智能体优先架构**，采用**9-Agent 体系**，分为三层：

**Management Layer / 管理层**
- **Agent PM** - Project management, progress tracking, coordination
- **Agent PO** - Product owner, requirements, specifications, user stories
- **Agent ARCH** - System architect, interface contracts, shared platform

**Development Layer / 开发层**
- **Agent TRADING** - Trading engine, exchange connectivity, order management
- **Agent PORTFOLIO** - Portfolio management, risk indicators, capital allocation
- **Agent WEB** - Web API, FastAPI services, user interface
- **Agent AI** - LLM integration, AI agents, evaluation framework

**Quality Layer / 质量层**
- **Agent QA** - Quality assurance, testing, documentation
- **Agent REVIEW** - Code review, quality checks, security

See [Agent Documentation](docs/agents/README.md) for details.
详见 [Agent 文档](docs/agents/README.md)。

### 📦 Module Structure / 模块结构

The project is organized into **6 core modules**:
项目组织为**6 个核心模块**：

| Module | Owner | Purpose |
|--------|-------|---------|
| **shared** | Agent ARCH | Common utilities (config, logging, metrics) |
| **trading** | Agent TRADING | Exchange connection, orders, strategies |
| **portfolio** | Agent PORTFOLIO | Capital allocation, risk management |
| **ai** | Agent AI | LLM evaluation, strategy optimization |
| **web** | Agent WEB | REST API, user interface |
| **qa** | Agent QA | Testing, documentation |

See [Modules Overview](docs/modules_overview.md) for detailed information.
详见 [模块概览](docs/modules_overview.md)。

---

## 🧠 Powered by AlphaLoop / 由 AlphaLoop 驱动
This bot is not just a script; it's a digital organization.
这个机器人不仅仅是一个脚本；它是一个数字组织。

**Implementation / 实现位置**: The `AlphaLoop` class is defined in [`src/trading/engine.py`](src/trading/engine.py). It orchestrates multiple strategy instances and coordinates AI agents (Data, Quant, Risk) to manage the trading business.
**实现位置**：`AlphaLoop` 类定义在 [`src/trading/engine.py`](src/trading/engine.py) 中。它协调多个策略实例并协调 AI 智能体（数据、量化、风控）来管理交易业务。

### The Core Loop / 核心循环
1.  **Trade**: The bot executes a `FixedSpreadStrategy`.
2.  **Analyze**: The **Quant Agent** reviews performance metrics (Sharpe Ratio, Win Rate).
3.  **Propose**: If performance is suboptimal, the Quant proposes changes (e.g., "Widen spread to 0.3%").
4.  **Validate**: The **Risk Agent** checks the proposal against strict safety limits.
5.  **Optimize**: If approved, the system updates its configuration instantly.

## 🗂 Governance Map / 治理地图

- `project_manifest.json` – Global map for modules, owners, directories, and dependencies / 用于记录模块、负责人、目录与依赖的全局地图。
- `docs/modules/{module}.json` – Module card with responsibilities, constraints, and embedded feature list (Spec/Story/Test/CI) / 模块卡片，包含职责、约束及内嵌的 Feature（含 Spec/Story/Test/CI）。
- `docs/progress/progress_index.json` – Read-only event log tying feature IDs to branches、PR 与 CI 结果 / 只读事件日志，把 Feature ID 与分支、PR、CI 结果串联起来。
- `scripts/audit_check.py` – Lightweight audit validating manifest, module cards, progress index, and artifact files / 轻量审计脚本，校验 manifest、模块卡片、进度索引及实物文件。
- `scripts/advance_feature.py` – **Automated feature advancement** / **自动化 Feature 推进**：一键更新模块 JSON、同步 roadmap、添加进度事件并运行审计检查。详见 [Feature Automation Guide](docs/development_protocol_feature_automation.md)。

> **Workflow Tip / 流程提示**：
> - **推荐**：使用 `python scripts/advance_feature.py <feature_id> <new_step>` 自动推进 Feature
> - **手动流程**：新增 Feature 前先更新模块 JSON；开发完成后在 progress index 追加事件，并运行 `python scripts/audit_check.py` 确认闭环

---

## 📚 Documentation Reading Guide / 文档阅读指南

This project has comprehensive documentation. **If you are new to the system**, follow this reading order:
本项目有完整的文档。**如果您是新手**，请按以下顺序阅读：

### 🎯 For First-Time Readers / 初次阅读者

**Start Here:**
1. **[Quick Start Guide](docs/quick_start.md)** ⭐ **NEW TEAM MEMBERS START HERE**
   - 5-minute overview of the project
   - Module structure, workflow, and key concepts
   - **新团队成员从这里开始** - 5 分钟项目概览

2. **[System Flow](docs/system_flow.md)** ⭐ **UNDERSTAND THE SYSTEM**
   - Understand what happens when you click "Start Bot"
   - See the complete interaction flow with diagrams
   - **理解系统** - 了解点击"启动 Bot"后发生的事情

3. **[Walkthrough](docs/walkthrough.md)**
   - See the system in action with real examples
   - Verification results and proof of work
   - 查看系统运行的实际示例

4. **[Architecture](docs/architecture.md)**
   - High-level system design
   - Component relationships and data flow
   - 高层系统设计和组件关系

### 🔧 For Developers / 开发者

**After understanding the basics, dive deeper:**

4. **[Development Workflow](docs/development_workflow.md)** ⭐ **NEW DEVELOPERS START HERE**
   - Complete 13-step development pipeline guide
   - Step-by-step instructions with examples
   - Automation tools and best practices
   - **新开发者从这里开始** - 完整的 13 步开发流程指南

5. **[Modules Overview](docs/modules_overview.md)** ⭐ **UNDERSTAND THE CODEBASE**
   - Clear explanation of all 6 modules
   - Module responsibilities, dependencies, and ownership
   - Directory structure and interaction examples
   - **理解代码库** - 清晰解释所有 6 个模块

7. **[Trading Strategy](docs/trading_strategy.md)**
   - How the market-making strategy works
   - Spread calculation and order placement logic
   - 做市策略的工作原理

8. **[Implementation Plan](docs/implementation_plan.md)**
   - Recent changes and planned features
   - Technical details of implementations
   - 最近的更改和计划功能

9. **[Development Protocol](docs/development_protocol.md)**
   - Mandatory development standards
   - Testing requirements and coverage goals
   - 强制性开发标准和测试要求

10. **[Feature Automation Guide](docs/development_protocol_feature_automation.md)** 🆕
    - Automated feature advancement scripts
    - Batch operations and Git hooks
    - 自动化功能推进脚本
    - 批量操作和 Git 钩子

11. **[CI/CD Process](docs/cicd.md)** 🆕
    - Automated testing and deployment pipeline
    - Quality gates and pre-commit checklist
    - 自动化测试和部署流程

12. **[Dashboard Guide](docs/dashboard.md)** 🆕
    - Monitoring metrics and charts
    - Professional definitions of KPIs
    - 监控指标和图表
    - KPI 的专业定义

13. **[API Reference Documentation](docs/api_reference.md)** 🆕
    - Auto-generated API docs (pdoc)
    - Interactive API documentation (FastAPI)
    - 自动生成的 API 文档
    - 交互式 API 文档

14. **[Strategy Development Guide](docs/strategy_development_guide.md)** 🆕
    - Step-by-step guide for adding new trading strategies
    - Integration requirements and best practices
    - 添加新交易策略的分步指南
    - 集成要求和最佳实践

15. **[Multi-LLM Evaluation Guide](docs/user_guide/multi_llm_evaluation.md)** 🆕
    - Compare strategies from Gemini, OpenAI, and Claude
    - Simulation-based strategy validation
    - 多模型策略评估与比较
    - 基于模拟的策略验证

16. **[Risk Indicators Guide](docs/user_guide/risk_indicators.md)** 🆕
    - Liquidation Buffer, Inventory Drift, Max Drawdown
    - Real-time risk monitoring
    - 强平缓冲、库存偏移、最大回撤
    - 实时风险监控

17. **[Error Handling Guide](docs/user_guide/error_handling.md)** 🆕
   - Comprehensive error handling and recovery
   - Multi-strategy error isolation
   - Troubleshooting common issues
   - 全面的错误处理和恢复机制
   - 多策略错误隔离
   - 常见问题故障排除

18. **AlphaLoop Framework Documentation** (docs/framework/)
   - **[Framework Design](docs/framework/framework_design.md)**: The "Agent-First" architecture
     - 框架设计 - "智能体优先"架构
   - **[Agent Roles and Hierarchy](docs/framework/agent_roles_and_hierarchy.md)**: Meet the AI agents
     - 智能体角色和层级 - 了解各个 AI 智能体
   - **[Agent Workflows](docs/framework/agent_workflows.md)**: How agents collaborate
     - 智能体工作流 - 智能体如何协作
   - **[Metrics Specification](docs/framework/metrics_specification.md)**: KPIs we track
     - 指标规范 - 我们跟踪的 KPI
   - **[Evaluation Framework](docs/framework/evaluation_framework.md)**: Testing and validation
     - 评估框架 - 测试和验证

19. **[Agent Documentation](docs/agents/README.md)** 🆕
   - Complete guide to the 9-Agent system
   - Agent responsibilities and ownership
   - Multi-agent development workflow
   - 9-Agent 体系完整指南
   - Agent 职责和所有权
   - 多 Agent 开发工作流

### 📊 Quick Reference / 快速参考

- **Project Review** ([project_review.md](docs/project_review.md)): Status updates and progress tracking
- **Task List** ([task.md](docs/task.md)): Current development tasks

---

## 🚀 Quick Start / 快速开始

### Prerequisites / 先决条件
*   Python 3.11+
*   Virtual environment (recommended)
*   Git
*   Cursor IDE (recommended for multi-agent development)

### Environment Setup / 环境设置

#### 1. Clone the Repository / 克隆仓库
```bash
git clone <repository-url>
cd MarketMakerDemo
```

#### 2. Create Virtual Environment / 创建虚拟环境
```bash
# Create virtual environment / 创建虚拟环境
python3 -m venv venv

# Activate virtual environment / 激活虚拟环境
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

#### 3. Install Dependencies / 安装依赖
```bash
# Install Python packages / 安装 Python 包
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers (for E2E tests) / 安装 Playwright 浏览器（用于 E2E 测试）
playwright install --with-deps
```

#### 4. Configure Environment Variables / 配置环境变量

Create a `.env` file in the project root directory:
在项目根目录创建 `.env` 文件：

```bash
# Copy example template (if available) / 复制示例模板（如果可用）
# cp .env.example .env

# Or create manually / 或手动创建
touch .env
```

**Required Environment Variables / 必需的环境变量：**

```bash
# Binance API Credentials (optional if using Hyperliquid only)
# Binance API 凭证（如果仅使用 Hyperliquid 则为可选）
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Hyperliquid API Credentials / Hyperliquid API 凭证
HYPERLIQUID_API_KEY=your_hyperliquid_api_key
HYPERLIQUID_API_SECRET=your_hyperliquid_api_secret

# Hyperliquid Network Configuration / Hyperliquid 网络配置
# Set to "true" for testnet, "false" for mainnet
# 设置为 "true" 使用测试网，"false" 使用主网
HYPERLIQUID_TESTNET=true

# Optional: Run Hyperliquid only (disable Binance)
# 可选：仅运行 Hyperliquid（禁用 Binance）
HYPERLIQUID_ONLY=false
```

**Optional: LLM API Keys (for Multi-LLM Evaluation) / 可选：LLM API 密钥（用于多 LLM 评估）**

```bash
# Google Gemini API Key / Google Gemini API 密钥
GEMINI_API_KEY=your_gemini_api_key

# OpenAI API Key / OpenAI API 密钥
OPENAI_API_KEY=your_openai_api_key

# Anthropic Claude API Key / Anthropic Claude API 密钥
ANTHROPIC_API_KEY=your_anthropic_api_key
```

**⚠️ Security Note / 安全提示：**
- Never commit `.env` file to Git (already in `.gitignore`)
- Never share API keys in public channels / 不要在公共渠道分享 API 密钥

#### 5. Verify Environment / 验证环境

Before starting the server, verify your environment is correctly configured:
在启动服务器之前，验证您的环境是否正确配置：

```bash
# Run environment verification script / 运行环境验证脚本
./scripts/verify_server_env.sh
```

This script checks:
此脚本检查：
- ✓ Virtual environment setup / 虚拟环境设置
- ✓ Required Python packages / 必需的 Python 包
- ✓ Environment file configuration / 环境文件配置
- ✓ Working directory / 工作目录
- ✓ Python interpreter / Python 解释器

#### 6. Start the Server / 启动服务器

**Important: Always use the standardized startup script / 重要：始终使用标准化启动脚本**

```bash
# Standardized startup (recommended) / 标准化启动（推荐）
./start_server.sh
```

The `start_server.sh` script ensures:
`start_server.sh` 脚本确保：
- ✓ Consistent working directory / 一致的工作目录
- ✓ Virtual environment activation / 虚拟环境激活
- ✓ Correct Python interpreter / 正确的 Python 解释器
- ✓ Proper PYTHONPATH configuration / 正确的 PYTHONPATH 配置
- ✓ Environment variable loading / 环境变量加载

**Why use the standardized script? / 为什么使用标准化脚本？**

Different agents (Agent TRADING, Agent WEB, Agent AI, etc.) may start the server from different contexts. The standardized script ensures all agents use the same environment configuration, preventing issues like:
不同的 agent（Agent TRADING、Agent WEB、Agent AI 等）可能从不同的上下文启动服务器。标准化脚本确保所有 agent 使用相同的环境配置，防止以下问题：
- ❌ Missing environment variables / 缺少环境变量
- ❌ Wrong Python interpreter / 错误的 Python 解释器
- ❌ Incorrect working directory / 不正确的工作目录
- ❌ PYTHONPATH misconfiguration / PYTHONPATH 配置错误

**Alternative: Manual startup (not recommended) / 替代方案：手动启动（不推荐）**

If you must start manually, ensure:
如果您必须手动启动，请确保：

```bash
# 1. Activate virtual environment / 激活虚拟环境
source .venv/bin/activate

# 2. Set working directory / 设置工作目录
cd /path/to/MarketMakerDemo

# 3. Set PYTHONPATH / 设置 PYTHONPATH
export PYTHONPATH="$(pwd):${PYTHONPATH}"

# 4. Start server / 启动服务器
python server.py
```
- 永远不要将 `.env` 文件提交到 Git（已在 `.gitignore` 中）
- Keep your API keys secure and never share them
- 妥善保管 API 密钥，不要分享

#### 5. Cursor IDE Configuration / Cursor IDE 配置

This project uses Cursor IDE with a multi-agent development workflow. The configuration is automatically loaded from:
本项目使用 Cursor IDE 进行多 Agent 开发工作流。配置会自动从以下文件加载：

**Configuration Files / 配置文件：**
- `.cursorrules` - AI assistant behavior rules and agent system definitions
  - AI 助手行为规则和 Agent 体系定义
- `.cursorignore` - Workspace indexing exclusions
  - 工作区索引排除规则

**After cloning the repository / 克隆仓库后：**
1. Open the project in Cursor IDE
   在 Cursor IDE 中打开项目
2. The `.cursorrules` file will be automatically loaded
   `.cursorrules` 文件会自动加载
3. Cursor will use the defined agent system and workflow rules
   Cursor 将使用定义的 Agent 体系和工作流规则

**Note / 注意：**
- The `.cursor/` directory contains temporary files and is not committed to Git
  `.cursor/` 目录包含临时文件，不会提交到 Git
- Each developer's Cursor environment will automatically adapt to the project rules
  每个开发者的 Cursor 环境会自动适配项目规则

#### 6. Verify Installation / 验证安装
```bash
# Check Python version / 检查 Python 版本
python3 --version  # Should be 3.11+

# Check installed packages / 检查已安装的包
pip list | grep -E "(fastapi|ccxt|pandas)"

# Run tests to verify setup / 运行测试以验证设置
pytest tests/unit/shared/ -v
```

### Project Structure / 项目结构
```
MarketMakerDemo/
├── src/                    # Source code (organized by module)
│   ├── shared/            # Shared platform (Agent ARCH)
│   ├── trading/           # Trading engine (Agent TRADING)
│   ├── portfolio/         # Portfolio & risk (Agent PORTFOLIO)
│   ├── ai/                # AI & evaluation (Agent AI)
│   └── web/               # Web & API (Agent WEB)
├── tests/                 # Tests (organized by type)
│   ├── unit/             # Unit tests (by module)
│   ├── smoke/             # Smoke tests (Agent QA)
│   └── integration/       # Integration tests (Agent QA)
├── docs/                  # Documentation
│   ├── agents/            # Agent documentation
│   ├── modules/           # Module cards (JSON)
│   ├── specs/             # Specifications (Agent PO)
│   ├── stories/           # User stories (Agent PO)
│   └── user_guide/        # User documentation (Agent QA)
├── contracts/             # Interface contracts (Agent ARCH)
├── status/                # Roadmap & progress tracking (Agent PM)
└── scripts/               # Automation scripts
```

### Running the Bot / 运行机器人

**Option 1: Command Line / 命令行**
```bash
# Launch the autonomous market maker
python3 run.py
```

**Option 2: Web Interface / Web 界面**
```bash
# Start the FastAPI server
# 启动 FastAPI 服务器

# Recommended: Use startup script (handles venv automatically)
# 推荐：使用启动脚本（自动处理虚拟环境）
./start_server.sh

# Alternative: Manual start (if startup script doesn't work)
# 备选：手动启动（如果启动脚本不工作）
# The script automatically finds venv site-packages and sets PYTHONPATH
# 脚本会自动查找虚拟环境 site-packages 并设置 PYTHONPATH

# Then open in browser:
# - Main dashboard: http://localhost:3000/
# - LLM Trade Lab: http://localhost:3000/evaluation
# - Hyperliquid Trading: http://localhost:3000/hyperliquid
```

### What to Watch / 观察内容
Check the logs to see the agents in action:
1.  **QuantAgent**: "Win rate is low (42%), I propose widening the spread to 0.25%."
2.  **RiskAgent**: "Validating proposal... Spread is within limits (Max 5%). APPROVED."
3.  **System**: "Applying new configuration. Spread updated to 0.25%."

---

## 🏗️ Architecture / 架构

### System Architecture / 系统架构

```mermaid
graph TD
    Market[Crypto Market] <-->|Orders/Fills| Exec[Execution Engine]
    Exec -->|Trade Data| Data[Data Agent]
    
    subgraph "AlphaLoop Framework"
        Data -->|Metrics| Quant[Quant Agent]
        Quant -->|Proposal| Risk[Risk Agent]
        Risk -->|Approval| Config[Configuration]
    end
    
    Config -->|Updates| Exec
```

### Module Dependencies / 模块依赖

```
shared (base)
  ↑
  ├── trading
  │     ↑
  │     ├── portfolio
  │     └── ai
  │           ↑
  │           └── web
```

### Development Pipeline / 开发流程

Every feature follows a **13-step pipeline**:
每个功能都遵循**13 步流程**：

```
Spec → Story → AC → Contract → Test → Code → Review → Unit → Smoke → Integration → Docs → Progress → CI/CD
```

See [Development Workflow](docs/development_workflow.md) for complete details.
详见 [开发流程](docs/development_workflow.md) 了解完整详情。
