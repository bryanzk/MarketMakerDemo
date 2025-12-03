# Modules Overview / 模块概览

This document provides a clear overview of all modules in MarketMakerDemo, their responsibilities, dependencies, and ownership.
本文档提供了 MarketMakerDemo 中所有模块的清晰概览，包括它们的职责、依赖关系和所有权。

---

## 📦 Module Architecture / 模块架构

MarketMakerDemo is organized into **6 core modules**, each with a dedicated Agent owner and clear boundaries.
MarketMakerDemo 组织为 **6 个核心模块**，每个模块都有专门的 Agent 负责人和清晰的边界。

```
┌─────────────────────────────────────────────────────────────┐
│                    MarketMakerDemo                          │
│                     做市商演示系统                          │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌─────▼─────┐        ┌──────▼──────┐
   │ Shared  │          │  Trading  │        │  Portfolio  │
   │ Platform│◄─────────┤  Engine   │◄───────┤  & Risk     │
   │共享平台  │          │ 交易引擎   │        │组合与风险   │
   └────┬────┘          └─────┬─────┘        └──────┬──────┘
        │                     │                     │
        │              ┌──────▼──────┐              │
        │              │  AI & Eval  │              │
        │              │  AI 评估层   │              │
        │              └──────┬──────┘              │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                        ┌─────▼─────┐
                        │  Web & API│
                        │ Web 与 API│
                        └───────────┘
```

---

## 🧩 Module Details / 模块详情

### 1. Shared Platform / 共享平台

**ID:** `shared`  
**Owner:** Agent ARCH  
**Directory:** `src/shared/`  
**Test Directory:** None (shared utilities)

**Responsibilities / 职责：**
- ✅ Common utilities (logging, configuration, metrics)
- ✅ 通用工具（日志、配置、指标）
- ✅ Shared data structures and helpers
- ✅ 共享数据结构和辅助函数
- ✅ Platform-wide constants
- ✅ 平台级常量

**What it does NOT do / 它不做什么：**
- ❌ Business-specific trading logic
- ❌ 特定业务交易逻辑
- ❌ Portfolio capital allocation
- ❌ 组合资金分配

**Key Files / 关键文件：**
- `src/shared/config.py` - Configuration management
- `src/shared/logger.py` - Logging utilities
- `src/shared/metrics/` - Metrics framework
- `src/shared/utils.py` - Helper functions

**Dependencies / 依赖：**
- None (base module)

---

### 2. Trading Engine / 交易引擎

**ID:** `trading`  
**Owner:** Agent TRADING  
**Directory:** `src/trading/`  
**Test Directory:** `tests/unit/trading/`

**Responsibilities / 职责：**
- ✅ Exchange connectivity (Binance API)
- ✅ 交易所连接（Binance API）
- ✅ Order lifecycle management (place, cancel, track)
- ✅ 订单生命周期管理（下单、取消、跟踪）
- ✅ Strategy execution (FixedSpread, FundingRate)
- ✅ 策略执行（固定价差、资金费率）
- ✅ AlphaLoop main loop orchestration
- ✅ AlphaLoop 主循环编排
- ✅ Simulation tools for AI evaluators
- ✅ AI 评估器的模拟工具

**What it does NOT do / 它不做什么：**
- ❌ Portfolio-level capital allocation
- ❌ 组合级资金分配
- ❌ LLM evaluation orchestration
- ❌ LLM 评估编排
- ❌ User interface rendering
- ❌ 用户界面渲染

**Key Files / 关键文件：**
- `src/trading/exchange.py` - Exchange client
- `src/trading/order_manager.py` - Order management
- `src/trading/engine.py` - AlphaLoop main engine
- `src/trading/strategies/` - Strategy implementations

**Dependencies / 依赖：**
- `shared` (uses config, logger, metrics)

**Public API / 公共 API：**
```python
from src.trading.exchange import ExchangeClient
from src.trading.order_manager import OrderManager
from src.trading.engine import AlphaLoop
```

---

### 3. Portfolio & Risk / 组合与风险

**ID:** `portfolio`  
**Owner:** Agent PORTFOLIO  
**Directory:** `src/portfolio/`  
**Test Directory:** `tests/unit/portfolio/`

**Responsibilities / 职责：**
- ✅ Multi-strategy portfolio management
- ✅ 多策略组合管理
- ✅ Capital allocation across strategies
- ✅ 跨策略资金分配
- ✅ Risk indicators calculation (Sharpe, Max Drawdown)
- ✅ 风险指标计算（夏普比率、最大回撤）
- ✅ Portfolio health monitoring
- ✅ 组合健康度监控
- ✅ Strategy status tracking
- ✅ 策略状态跟踪

**What it does NOT do / 它不做什么：**
- ❌ Direct exchange API calls
- ❌ 直接交易所 API 调用
- ❌ Strategy logic implementation
- ❌ 策略逻辑实现
- ❌ LLM evaluation
- ❌ LLM 评估

**Key Files / 关键文件：**
- `src/portfolio/manager.py` - Portfolio manager
- `src/portfolio/risk.py` - Risk indicators
- `src/portfolio/health.py` - Health monitoring

**Dependencies / 依赖：**
- `shared` (uses config, logger, metrics)
- `trading` (needs order data, strategy status)

**Public API / 公共 API：**
```python
from src.portfolio.manager import PortfolioManager, StrategyStatus
from src.portfolio.risk import RiskIndicators
```

---

### 4. AI & Evaluation / AI 评估层

**ID:** `ai`  
**Owner:** Agent AI  
**Directory:** `src/ai/`  
**Test Directory:** `tests/unit/ai/`

**Responsibilities / 职责：**
- ✅ Multi-LLM evaluation orchestration
- ✅ 多 LLM 评估编排
- ✅ Strategy performance analysis
- ✅ 策略性能分析
- ✅ Parameter optimization suggestions
- ✅ 参数优化建议
- ✅ AI agent implementations (Quant, Risk, Data)
- ✅ AI 智能体实现（量化、风控、数据）
- ✅ Evaluation framework and prompts
- ✅ 评估框架和提示词

**What it does NOT do / 它不做什么：**
- ❌ Direct trading execution
- ❌ 直接交易执行
- ❌ Portfolio capital allocation
- ❌ 组合资金分配
- ❌ Exchange connectivity
- ❌ 交易所连接

**Key Files / 关键文件：**
- `src/ai/llm.py` - LLM provider management
- `src/ai/evaluation/evaluator.py` - Multi-LLM evaluator
- `src/ai/agents/quant.py` - Quant agent
- `src/ai/agents/risk.py` - Risk agent
- `src/ai/agents/data.py` - Data agent

**Dependencies / 依赖：**
- `shared` (uses config, logger)
- `trading` (needs simulation results, strategy data)

**Public API / 公共 API：**
```python
from src.ai.evaluation import MultiLLMEvaluator, EvaluationResult
from src.ai.agents.quant import QuantAgent
```

---

### 5. Web & API / Web 与 API

**ID:** `web`  
**Owner:** Agent WEB  
**Directory:** `src/web/`  
**Test Directory:** `tests/unit/web/`

**Responsibilities / 职责：**
- ✅ FastAPI REST API endpoints
- ✅ FastAPI REST API 端点
- ✅ Web dashboard and UI
- ✅ Web 仪表板和 UI
- ✅ API authentication and authorization
- ✅ API 认证和授权
- ✅ Real-time data streaming
- ✅ 实时数据流
- ✅ User interaction layer
- ✅ 用户交互层

**What it does NOT do / 它不做什么：**
- ❌ Business logic implementation
- ❌ 业务逻辑实现
- ❌ Direct database access (if applicable)
- ❌ 直接数据库访问（如适用）
- ❌ Strategy execution
- ❌ 策略执行

**Key Files / 关键文件：**
- `server.py` - FastAPI application entry point
- `src/web/` - API routes and handlers (to be implemented)

**Dependencies / 依赖：**
- `trading` (exposes trading APIs)
- `portfolio` (exposes portfolio APIs)
- `ai` (exposes evaluation APIs)

**Public API / 公共 API：**
```python
# REST API endpoints (FastAPI)
GET /api/portfolio/status
GET /api/trading/strategies
POST /api/ai/evaluate
```

---

### 6. Quality & Docs / 质量与文档

**ID:** `qa`  
**Owner:** Agent QA  
**Directory:** None (no source code)  
**Test Directory:** `tests/`

**Responsibilities / 职责：**
- ✅ Unit test strategy and coverage
- ✅ 单元测试策略和覆盖率
- ✅ Smoke tests (`tests/smoke/`)
- ✅ 冒烟测试 (`tests/smoke/`)
- ✅ Integration tests (`tests/integration/`)
- ✅ 集成测试 (`tests/integration/`)
- ✅ User documentation (`docs/user_guide/`)
- ✅ 用户文档 (`docs/user_guide/`)
- ✅ Test quality review
- ✅ 测试质量审查

**What it does NOT do / 它不做什么：**
- ❌ Writing business logic code
- ❌ 编写业务逻辑代码
- ❌ Module-specific implementation
- ❌ 模块特定实现

**Key Files / 关键文件：**
- `tests/unit/` - Unit tests (owned by module owners)
- `tests/smoke/` - Smoke tests
- `tests/integration/` - Integration tests
- `docs/user_guide/` - User documentation

**Dependencies / 依赖：**
- `trading` (tests trading functionality)
- `portfolio` (tests portfolio functionality)
- `web` (tests API functionality)
- `ai` (tests AI functionality)

---

## 🔗 Dependency Graph / 依赖关系图

```
shared (base)
  ↑
  ├── trading
  │     ↑
  │     ├── portfolio
  │     │     ↑
  │     └── ai
  │           ↑
  │           └── web
  │
  └── (all modules depend on shared)
```

**Rules / 规则：**
- `shared` has no dependencies (base module)
- `shared` 没有依赖（基础模块）
- `trading` depends only on `shared`
- `trading` 仅依赖 `shared`
- `portfolio` depends on `shared` and `trading`
- `portfolio` 依赖 `shared` 和 `trading`
- `ai` depends on `shared` and `trading`
- `ai` 依赖 `shared` 和 `trading`
- `web` depends on `trading`, `portfolio`, and `ai`
- `web` 依赖 `trading`、`portfolio` 和 `ai`
- `qa` depends on all modules (for testing)
- `qa` 依赖所有模块（用于测试）

---

## 👥 Agent Ownership / Agent 所有权

| Module | Owner Agent | Primary Responsibility |
|--------|-------------|------------------------|
| `shared` | Agent ARCH | Platform infrastructure |
| `trading` | Agent TRADING | Exchange & order management |
| `portfolio` | Agent PORTFOLIO | Capital & risk management |
| `ai` | Agent AI | LLM evaluation & agents |
| `web` | Agent WEB | API & user interface |
| `qa` | Agent QA | Testing & documentation |

**Important / 重要：**
- Each module has **exclusive ownership** by its Agent
- 每个模块都有其 Agent 的**独占所有权**
- Agents should not modify files outside their module
- Agent 不应修改其模块之外的文件
- Cross-module changes require coordination
- 跨模块更改需要协调

---

## 📁 Directory Structure / 目录结构

```
MarketMakerDemo/
├── src/
│   ├── shared/          # Shared platform
│   ├── trading/          # Trading engine
│   ├── portfolio/        # Portfolio & risk
│   ├── ai/               # AI & evaluation
│   └── web/              # Web & API
├── tests/
│   ├── unit/
│   │   ├── trading/
│   │   ├── portfolio/
│   │   ├── ai/
│   │   └── web/
│   ├── smoke/            # QA-owned
│   └── integration/      # QA-owned
├── docs/
│   ├── modules/          # Module cards (JSON)
│   ├── specs/            # Specifications
│   ├── stories/          # User stories
│   └── user_guide/       # User documentation
├── contracts/            # Interface contracts
└── status/               # Roadmap & progress
```

---

## 🎯 Module Interaction Examples / 模块交互示例

### Example 1: Trading Flow / 示例 1：交易流程

```
User Request → Web API
                ↓
         Trading Engine
         (place order)
                ↓
         Portfolio Manager
         (update allocation)
                ↓
         AI Evaluator
         (analyze performance)
                ↓
         Web API Response
```

### Example 2: Evaluation Flow / 示例 2：评估流程

```
AI Evaluator requests simulation
                ↓
         Trading Engine
         (runs simulation)
                ↓
         Portfolio Manager
         (calculates metrics)
                ↓
         AI Evaluator
         (generates proposal)
                ↓
         Web API
         (returns result)
```

---

## 📚 Module Cards / 模块卡片

Each module has a detailed JSON card in `docs/modules/{module}.json`:
每个模块在 `docs/modules/{module}.json` 中都有详细的 JSON 卡片：

- Module boundaries and responsibilities
- 模块边界和职责
- Public API files
- 公共 API 文件
- Feature list with status
- 带状态的功能列表
- Dependencies
- 依赖关系

**View module cards / 查看模块卡片：**
```bash
cat docs/modules/trading.json
cat docs/modules/portfolio.json
# ... etc
```

---

## 🔍 Finding Module Information / 查找模块信息

### Quick Reference / 快速参考

1. **Module owner / 模块负责人：**
   - Check `project_manifest.json` → `modules[].owner_agent`
   - 检查 `project_manifest.json` → `modules[].owner_agent`

2. **Module features / 模块功能：**
   - Check `docs/modules/{module}.json` → `features[]`
   - 检查 `docs/modules/{module}.json` → `features[]`

3. **Module dependencies / 模块依赖：**
   - Check `docs/modules/{module}.json` → `depends_on[]`
   - 检查 `docs/modules/{module}.json` → `depends_on[]`

4. **Public API / 公共 API：**
   - Check `docs/modules/{module}.json` → `public_api_files[]`
   - 检查 `docs/modules/{module}.json` → `public_api_files[]`

---

## 🚀 Getting Started / 快速开始

### For New Developers / 对于新开发者

1. **Identify your module / 识别您的模块：**
   - Check `project_manifest.json` to find module ownership
   - 检查 `project_manifest.json` 以查找模块所有权

2. **Read the module card / 阅读模块卡片：**
   - `docs/modules/{module}.json` has all details
   - `docs/modules/{module}.json` 包含所有详细信息

3. **Understand dependencies / 理解依赖关系：**
   - Check `depends_on[]` in the module card
   - 检查模块卡片中的 `depends_on[]`

4. **Follow the development workflow / 遵循开发流程：**
   - See [Development Workflow](development_workflow.md)
   - 参见 [开发流程](development_workflow.md)

---

## 📖 Related Documents / 相关文档

- [Development Workflow](development_workflow.md) - 17-step pipeline
- [Project Manifest](../project_manifest.json) - Complete project structure
- [Development Protocol](development_protocol.md) - Coding standards
- [Agent Documentation](agents/README.md) - Agent responsibilities

---

**Last Updated / 最后更新:** 2025-11-30  
**Maintained by / 维护者:** Agent PM


