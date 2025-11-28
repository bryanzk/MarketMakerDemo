# File Locking Rules / 文件锁定规则

## Purpose / 目的

This document defines the file ownership and modification permissions for parallel multi-agent development.  
本文档定义多 Agent 并行开发时的文件归属与修改权限。

Clear boundaries prevent merge conflicts and ensure each agent knows exactly what they can and cannot modify.  
明确的边界可防止合并冲突，确保每个 Agent 清楚知道自己能改什么、不能改什么。

Reference: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
参考：[长周期 Agent 有效支撑框架](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Permission Levels / 权限级别

| Level / 级别 | Symbol / 符号 | Description / 描述 |
|--------------|---------------|-------------------|
| **EXCLUSIVE** | 🔴 | Only one agent can modify / 仅一个 Agent 可修改 |
| **COORDINATED** | 🟡 | Modification requires RFC / 修改需发起 RFC 请求 |
| **SHARED-APPEND** | 🟢 | Multiple agents can append, no deletion / 多 Agent 可追加，不可删改 |
| **FREE** | 🔵 | Each agent maintains their own scope / 各 Agent 独立维护自己范围 |

---

## File Ownership Matrix / 文件归属矩阵

### 🔴 EXCLUSIVE Files / 独占文件

Only the designated owner can modify these files. Other agents must raise a request via `agent_requests.md`.  
仅指定的 Owner 可修改这些文件。其他 Agent 需通过 `agent_requests.md` 发起请求。

| File / 文件 | Owner / 归属 | Notes / 备注 |
|-------------|-------------|--------------|
| `server.py` | Agent 3 (Web/API) | FastAPI main application |
| `templates/index.html` | Agent 3 (Web/API) | Main dashboard |
| `templates/LLMTrade.html` | Agent 3 (Web/API) | LLM trade page |
| `alphaloop/main.py` | Agent 1 (Trading) | AlphaLoop engine entry |
| `alphaloop/market/exchange.py` | Agent 1 (Trading) | Exchange client |
| `alphaloop/market/order_manager.py` | Agent 1 (Trading) | Order management |
| `alphaloop/market/risk_manager.py` | Agent 1 (Trading) | Risk management |
| `alphaloop/market/simulation.py` | Agent 1 (Trading) | Market simulation |
| `alphaloop/market/performance.py` | Agent 1 (Trading) | Performance tracking |
| `alphaloop/market/strategy_instance.py` | Agent 1 (Trading) | Strategy instance |
| `alphaloop/strategies/strategy.py` | Agent 1 (Trading) | Fixed spread strategy |
| `alphaloop/strategies/funding.py` | Agent 1 (Trading) | Funding rate strategy |
| `alphaloop/portfolio/manager.py` | Agent 2 (Portfolio) | Portfolio manager |
| `alphaloop/portfolio/risk.py` | Agent 2 (Portfolio) | Risk indicators |
| `alphaloop/portfolio/health.py` | Agent 2 (Portfolio) | Health scoring |
| `alphaloop/agents/data.py` | Agent 4 (AI) | Data agent |
| `alphaloop/agents/quant.py` | Agent 4 (AI) | Quant agent |
| `alphaloop/agents/risk.py` | Agent 4 (AI) | Risk agent |
| `alphaloop/evaluation/evaluator.py` | Agent 4 (AI) | LLM evaluator |
| `alphaloop/evaluation/prompts.py` | Agent 4 (AI) | Evaluation prompts |
| `alphaloop/evaluation/schemas.py` | Agent 4 (AI) | Evaluation schemas |
| `alphaloop/core/llm.py` | Agent 4 (AI) | LLM providers |

---

### 🟡 COORDINATED Files / 协调文件

Modification requires raising an RFC (Request for Change) in `agent_requests.md` with type `CONFIG`.  
修改需在 `agent_requests.md` 中发起 `CONFIG` 类型的 RFC。

| File / 文件 | Coordination Rule / 协调规则 |
|-------------|----------------------------|
| `alphaloop/core/config.py` | All agents must be notified; changes must be backward-compatible / 需通知所有 Agent；变更需向后兼容 |
| `requirements.txt` | Raise RFC before adding dependencies; avoid version conflicts / 添加依赖前需发起 RFC；避免版本冲突 |
| `pyproject.toml` | Raise RFC for any modification / 任何修改都需发起 RFC |
| `.cursorrules` | Agent 5 maintains; changes affect all agents / Agent 5 维护；变更影响所有 Agent |
| `alphaloop/core/utils.py` | Shared utilities; changes may affect multiple agents / 共享工具；变更可能影响多个 Agent |
| `alphaloop/core/logger.py` | Shared logging; changes may affect multiple agents / 共享日志；变更可能影响多个 Agent |

**RFC Process for Coordinated Files / 协调文件的 RFC 流程**:

```
1. 在 agent_requests.md 创建 CONFIG 类型请求
2. 描述变更内容和影响范围
3. 等待相关 Agent 确认（至少 24 小时或明确回复）
4. 执行变更并更新 claude_progress.md
5. 通知所有 Agent 变更已完成
```

---

### 🟢 SHARED-APPEND Files / 共享追加文件

Multiple agents can append content, but cannot delete or modify existing entries.  
多个 Agent 可追加内容，但不能删除或修改现有条目。

| File / 文件 | Append Rules / 追加规则 |
|-------------|------------------------|
| `docs/project/claude_progress.md` | Append new rows to progress table / 在进度表追加新行 |
| `docs/project/feature_matrix.json` | Only change `passes` field; add new features with `passes: false` / 仅改 `passes` 字段；新增功能需 `passes: false` |
| `docs/project/agent_requests.md` | Append new requests; update status of own requests / 追加新请求；更新自己请求的状态 |
| `CHANGELOG.md` | Agent 5 consolidates; others can suggest entries / Agent 5 汇总；其他 Agent 可建议条目 |

**feature_matrix.json Modification Rules / feature_matrix.json 修改规则**:

| Field / 字段 | Who Can Modify / 谁能改 | When / 何时 |
|--------------|------------------------|-------------|
| `passes` | Feature Owner (see `owner` field) | After tests pass / 测试通过后 |
| New feature entry | Any Agent | When discovering new requirement / 发现新需求时 |
| `version`, `last_updated` | Agent 5 | On release / 发布时 |
| `mutation_rules` | ❌ Forbidden | — |
| Existing `id`, `category`, `description`, `steps` | ❌ Forbidden (use RFC) | — |

---

### 🔵 FREE Files / 自由文件

Each agent independently maintains files within their designated scope.  
各 Agent 独立维护自己范围内的文件。

| Scope / 范围 | Owner / 归属 | Files / 文件 |
|--------------|-------------|--------------|
| Trading tests | Agent 1 | `tests/test_exchange*.py`, `tests/test_strategy*.py`, `tests/test_order*.py`, `tests/test_simulation*.py` |
| Portfolio tests | Agent 2 | `tests/test_portfolio*.py`, `tests/test_risk*.py` |
| Server tests | Agent 3 | `tests/test_server*.py` |
| AI/LLM tests | Agent 4 | `tests/test_*agent*.py`, `tests/test_llm*.py`, `tests/test_evaluation*.py` |
| Integration tests | Agent 5 | `tests/test_integration*.py` |
| Trading docs | Agent 1 | `docs/strategies/*` |
| Portfolio docs | Agent 2 | `docs/portfolio/*` |
| API docs | Agent 3 | `docs/api_reference.md`, `docs/dashboard.md` |
| AI docs | Agent 4 | `docs/alphaloop/agent_*.md`, `docs/alphaloop/evaluation_*.md` |
| User guides | Agent 5 | `docs/user_guide/*` |
| Project docs | Agent 5 | `docs/project/*`, `docs/agents/*` |

---

## Decision Tree / 决策树

When you need to modify a file, follow this decision tree:  
当你需要修改文件时，遵循以下决策树：

```
你要修改的文件
      │
      ├─► 在 🔴 EXCLUSIVE 表中？
      │         │
      │         ├─► Owner 是自己 → ✅ 直接修改
      │         │
      │         └─► Owner 不是自己 → ❌ 在 agent_requests.md 发起 INTERFACE 请求
      │
      ├─► 在 🟡 COORDINATED 表中？
      │         │
      │         └─► 在 agent_requests.md 发起 CONFIG 请求
      │             等待确认后再修改
      │
      ├─► 在 🟢 SHARED-APPEND 表中？
      │         │
      │         └─► 只追加内容，不删改现有内容
      │             遵循该文件的追加规则
      │
      └─► 在 🔵 FREE 表中且属于自己范围？
                │
                └─► ✅ 自由修改
```

---

## Violation Handling / 违规处理

If an agent modifies a file outside their permission:  
如果 Agent 修改了权限范围外的文件：

1. **Immediate**: Revert the change using `git checkout -- <file>`  
   **立即**：使用 `git checkout -- <file>` 回滚变更

2. **Document**: Record the incident in `claude_progress.md`  
   **记录**：在 `claude_progress.md` 中记录该事件

3. **Correct**: Raise proper request in `agent_requests.md`  
   **纠正**：在 `agent_requests.md` 中发起正确的请求

4. **Proceed**: Wait for the owner to make the change  
   **继续**：等待 Owner 进行变更

---

## Quick Reference Card / 快速参考卡

```
┌─────────────────────────────────────────────────────────────────┐
│                    文件锁定快速参考                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Agent 1 (Trading)     │  Agent 2 (Portfolio)                   │
│  ────────────────────  │  ────────────────────                  │
│  🔴 alphaloop/main.py  │  🔴 alphaloop/portfolio/*              │
│  🔴 alphaloop/market/* │                                        │
│  🔴 alphaloop/strategies/*                                      │
│                                                                 │
│  Agent 3 (Web/API)     │  Agent 4 (AI)                          │
│  ────────────────────  │  ────────────────────                  │
│  🔴 server.py          │  🔴 alphaloop/agents/*                 │
│  🔴 templates/*        │  🔴 alphaloop/evaluation/*             │
│                        │  🔴 alphaloop/core/llm.py              │
│                                                                 │
│  Agent 5 (Docs/QA)                                              │
│  ────────────────────                                           │
│  🔴 docs/project/*                                              │
│  🔴 docs/agents/*                                               │
│  🔴 docs/user_guide/*                                           │
│  🔵 tests/test_integration*.py                                  │
│                                                                 │
│  共享文件 (All Agents)                                          │
│  ────────────────────                                           │
│  🟡 config.py, requirements.txt, pyproject.toml → RFC 流程      │
│  🟢 claude_progress.md, feature_matrix.json → 仅追加            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Related Documents / 相关文档

- `docs/project/agent_requests.md` — Cross-agent request protocol / 跨 Agent 请求协议
- `docs/project/claude_progress.md` — Progress tracking / 进度追踪
- `docs/project/feature_matrix.json` — Feature status tracker / 功能状态追踪
- `docs/agents/README.md` — Agent overview / Agent 概览


