# Agent Requests / 跨 Agent 请求追踪

## Purpose / 目的

This document tracks all cross-agent requests in a structured format.  
本文档以结构化格式追踪所有跨 Agent 请求。

When an agent needs another agent to make changes, add interfaces, or provide data, the request must be documented here.  
当一个 Agent 需要另一个 Agent 进行变更、添加接口或提供数据时，必须在此记录请求。

Reference: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
参考：[长周期 Agent 有效支撑框架](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Request Lifecycle / 请求生命周期

```
┌─────────────────────────────────────────────────────────────────┐
│                      Request Lifecycle / 请求生命周期            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Phase 1: INITIATE / 发起                                      │
│   ─────────────────────────────────────────────────────────     │
│   Requester:                                                    │
│   1. Add new row to "🟡 OPEN Requests" table                    │
│   2. Assign next available REQ-XXX ID                           │
│   3. Record in claude_progress.md: "Raised REQ-XXX"             │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 2: RESPOND / 响应                                       │
│   ─────────────────────────────────────────────────────────     │
│   Responder (at session start):                                 │
│   1. Check for OPEN requests where To = self                    │
│   2. Evaluate feasibility                                       │
│      → Accept: Move to "🔵 IN_PROGRESS", start work             │
│      → Reject: Move to "❌ REJECTED", provide reason            │
│   3. Record in claude_progress.md: "Accepted/Rejected REQ-XXX"  │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 3: COMPLETE / 完成                                      │
│   ─────────────────────────────────────────────────────────     │
│   Responder:                                                    │
│   1. Implement the requested change                             │
│   2. Move to "✅ COMPLETED Requests"                            │
│   3. Fill Resolution column with implementation details         │
│   4. Record in claude_progress.md: "Completed REQ-XXX"          │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 4: VERIFY / 验证                                        │
│   ─────────────────────────────────────────────────────────     │
│   Requester (at next session):                                  │
│   1. Check status of own requests                               │
│   2. Verify implementation meets requirements                   │
│   3. Record in claude_progress.md: "Verified REQ-XXX"           │
│   4. Continue blocked work                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Request Types / 请求类型

| Type / 类型 | When to Use / 使用场景 | Priority / 优先级 |
|-------------|----------------------|------------------|
| `INTERFACE` | Need target agent to add/modify public API | Varies |
| `DATA` | Need target agent to provide data format or source | Varies |
| `CONFIG` | Need to modify shared config files | 🟡 MEDIUM |
| `BLOCKER` | Blocked by target agent's incomplete work | 🔴 HIGH |
| `REVIEW` | Need target agent to review code/design | 🟢 LOW |
| `CLARIFY` | Need clarification on interface behavior | 🟢 LOW |

### Type Decision Tree / 类型决策树

```
你需要什么？
     │
     ├─► 需要对方的代码提供新功能/接口
     │         └─► Type: INTERFACE
     │             例: "需要 PortfolioManager 添加 get_summary() 方法"
     │
     ├─► 需要对方提供数据或数据格式
     │         └─► Type: DATA
     │             例: "需要 exchange 返回的 position 包含 entry_price"
     │
     ├─► 需要修改 config.py / requirements.txt / pyproject.toml
     │         └─► Type: CONFIG
     │             例: "需要在 config 中添加 LLM_TIMEOUT 配置项"
     │
     ├─► 你的工作被对方阻塞，无法继续
     │         └─► Type: BLOCKER (Priority: 🔴 HIGH)
     │             例: "API-002 依赖 PORT-001，请优先完成"
     │
     ├─► 需要对方审查代码或设计
     │         └─► Type: REVIEW
     │             例: "请审查 server.py 中新增的 /api/risk 端点"
     │
     └─► 不确定对方接口的行为
               └─► Type: CLARIFY
                   例: "PortfolioManager.rebalance() 失败时返回什么？"
```

---

## Request Tables / 请求表格

### 🟡 OPEN Requests / 待处理请求

| ID | From | To | Type | Priority | Feature | Description | Created |
|----|------|----|------|----------|---------|-------------|---------|
| — | — | — | — | — | — | — | — |

### 🔵 IN_PROGRESS Requests / 处理中请求

| ID | From | To | Type | Priority | Feature | Description | Accepted | Assignee |
|----|------|----|------|----------|---------|-------------|----------|----------|
| — | — | — | — | — | — | — | — | — |

### ✅ COMPLETED Requests / 已完成请求

| ID | From | To | Type | Feature | Resolution | Completed |
|----|------|----|------|---------|------------|-----------|
| — | — | — | — | — | — | — |

### ❌ REJECTED Requests / 已拒绝请求

| ID | From | To | Type | Feature | Rejection Reason | Rejected |
|----|------|----|------|---------|------------------|----------|
| — | — | — | — | — | — | — |

---

## How to Create a Request / 如何创建请求

### Step 1: Determine Request Type / 确定请求类型

Use the decision tree above to select the appropriate type.  
使用上方决策树选择合适的类型。

### Step 2: Add to OPEN Table / 添加到 OPEN 表格

```markdown
| REQ-001 | Agent 3 | Agent 2 | INTERFACE | 🔴 HIGH | API-002 | 需要 PortfolioManager.get_summary() 返回策略摘要，包含 allocation、pnl、health_score 字段 | 2025-11-28 |
```

### Step 3: Record in Progress Log / 记录到进度日志

Add to `claude_progress.md`:  
在 `claude_progress.md` 中添加：

```markdown
| 2025-11-28 | Agent 3 | API-002 | — | ⏸️ | REQ-001 raised | Raised REQ-001: need PortfolioManager.get_summary() |
```

### Step 4: Continue Other Work / 继续其他工作

If blocked, work on other features while waiting.  
如果被阻塞，等待期间处理其他功能。

---

## How to Respond to a Request / 如何响应请求

### At Session Start / 会话开始时

1. Read this file and filter for `To = your agent` and `Status = 🟡 OPEN`  
   读取本文件，筛选 `To = 自己` 且 `Status = 🟡 OPEN` 的请求

2. For each matching request:  
   对于每个匹配的请求：

   **If accepting / 如果接受**:
   ```markdown
   # Move from OPEN to IN_PROGRESS
   # 从 OPEN 移动到 IN_PROGRESS
   
   | REQ-001 | Agent 3 | Agent 2 | INTERFACE | 🔴 HIGH | API-002 | 需要 PortfolioManager.get_summary() | 2025-11-28 | Agent 2 |
   ```

   **If rejecting / 如果拒绝**:
   ```markdown
   # Move from OPEN to REJECTED
   # 从 OPEN 移动到 REJECTED
   
   | REQ-001 | Agent 3 | Agent 2 | INTERFACE | API-002 | get_summary() 已存在于 manager.py:L45，请直接调用 | 2025-11-28 |
   ```

3. Record in `claude_progress.md`  
   在 `claude_progress.md` 中记录

---

## How to Complete a Request / 如何完成请求

1. Implement the requested change  
   实现请求的变更

2. Move from IN_PROGRESS to COMPLETED  
   从 IN_PROGRESS 移动到 COMPLETED

   ```markdown
   | REQ-001 | Agent 3 | Agent 2 | INTERFACE | API-002 | Added get_summary() in manager.py:L89, returns {allocation, pnl, health_score}. Commit: abc123 | 2025-11-28 |
   ```

3. Record in `claude_progress.md`  
   在 `claude_progress.md` 中记录

---

## Priority Guidelines / 优先级指南

| Priority / 优先级 | Symbol / 符号 | Response SLA / 响应时限 | When to Use / 使用场景 |
|------------------|---------------|------------------------|----------------------|
| **HIGH** | 🔴 | Same session if possible | Blocker for critical path |
| **MEDIUM** | 🟡 | Within 1-2 sessions | Normal dependency |
| **LOW** | 🟢 | When convenient | Nice-to-have, not blocking |

---

## Request ID Assignment / 请求 ID 分配

Request IDs follow the format `REQ-NNN` where NNN is a sequential number.  
请求 ID 格式为 `REQ-NNN`，其中 NNN 为顺序编号。

To assign a new ID:  
分配新 ID 时：

1. Find the highest existing ID across all tables  
   在所有表格中找到最大的现有 ID

2. Increment by 1  
   加 1

3. Use the new ID for your request  
   使用新 ID 创建请求

---

## Session Startup Checklist / 会话启动检查清单

Every agent should check this file at session start:  
每个 Agent 在会话开始时应检查本文件：

```
□ Check OPEN requests where To = self
  检查 To = 自己 的 OPEN 请求
  
□ Check IN_PROGRESS requests where Assignee = self
  检查 Assignee = 自己 的 IN_PROGRESS 请求
  
□ Check COMPLETED requests where From = self (verify implementation)
  检查 From = 自己 的 COMPLETED 请求（验证实现）
```

---

## Example Request Flow / 请求流程示例

### Scenario / 场景

Agent 3 needs Agent 2 to add a `get_summary()` method to `PortfolioManager`.  
Agent 3 需要 Agent 2 在 `PortfolioManager` 中添加 `get_summary()` 方法。

### Day 1: Agent 3 Session / 第一天：Agent 3 会话

```markdown
# 1. Agent 3 adds to OPEN table
| REQ-001 | Agent 3 | Agent 2 | INTERFACE | 🔴 HIGH | API-002 | 需要 PortfolioManager.get_summary() 返回 {allocation, pnl, health_score} | 2025-11-28 |

# 2. Agent 3 records in claude_progress.md
| 2025-11-28 | Agent 3 | API-002 | — | ⏸️ | REQ-001 raised | Blocked: need get_summary() from Agent 2 |

# 3. Agent 3 works on other features (API-001, UI-001)
```

### Day 1: Agent 2 Session / 第一天：Agent 2 会话

```markdown
# 1. Agent 2 sees REQ-001 in OPEN, accepts it
# Move to IN_PROGRESS:
| REQ-001 | Agent 3 | Agent 2 | INTERFACE | 🔴 HIGH | API-002 | 需要 PortfolioManager.get_summary() | 2025-11-28 | Agent 2 |

# 2. Agent 2 implements get_summary()
# 3. Agent 2 moves to COMPLETED:
| REQ-001 | Agent 3 | Agent 2 | INTERFACE | API-002 | Added get_summary() in manager.py:L89. Commit: def456 | 2025-11-28 |

# 4. Agent 2 records in claude_progress.md
| 2025-11-28 | Agent 2 | PORT-001 | alphaloop/portfolio/manager.py | ✅ | None | Completed REQ-001: added get_summary() |
```

### Day 2: Agent 3 Session / 第二天：Agent 3 会话

```markdown
# 1. Agent 3 checks COMPLETED, sees REQ-001 is done
# 2. Agent 3 verifies the implementation works
# 3. Agent 3 continues API-002 implementation
# 4. Agent 3 records in claude_progress.md
| 2025-11-29 | Agent 3 | API-002 | server.py | ✅ | None | Verified REQ-001, completed API-002 |
```

---

## Related Documents / 相关文档

- `docs/project/file_locking_rules.md` — File ownership and permissions / 文件归属与权限
- `docs/project/claude_progress.md` — Progress tracking / 进度追踪
- `docs/project/feature_matrix.json` — Feature status tracker / 功能状态追踪
- `docs/agents/README.md` — Agent overview / Agent 概览


