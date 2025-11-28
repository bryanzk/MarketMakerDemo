# Issue Tracker / 问题追踪器

## Purpose / 目的

This document tracks code issues, bugs, technical debt, and improvement suggestions across the codebase.  
本文档追踪代码库中的问题、缺陷、技术债务和改进建议。

It integrates with the existing collaboration framework to ensure issues are discovered, assigned, and resolved systematically.  
它与现有协作框架集成，确保问题被系统性地发现、分配和解决。

---

## Issue Types / 问题类型

| Type / 类型 | Symbol / 符号 | Description / 描述 |
|-------------|---------------|-------------------|
| **BUG** | 🐛 | Code defect that needs fixing / 需要修复的代码缺陷 |
| **TECH_DEBT** | 🔧 | Technical debt requiring refactoring / 需要重构的技术债务 |
| **PERF** | ⚡ | Performance issue needing optimization / 需要优化的性能问题 |
| **SECURITY** | 🔒 | Security vulnerability needing hardening / 需要加固的安全隐患 |
| **TODO** | 📝 | TODO comment in code needing resolution / 代码中需处理的 TODO 注释 |
| **IMPROVE** | 💡 | Improvement suggestion, non-urgent / 改进建议，非紧急 |

---

## Priority Levels / 优先级

| Priority / 优先级 | Symbol / 符号 | Response SLA / 响应时限 | Description / 描述 |
|------------------|---------------|------------------------|-------------------|
| **P0 - Critical** | 🔴 | Immediate | Blocks production or core functionality / 阻塞生产或核心功能 |
| **P1 - High** | 🟠 | Within 1 session | Affects user experience or important features / 影响用户体验或重要功能 |
| **P2 - Medium** | 🟡 | Within 1 week | Should fix but not urgent / 应修复但不紧急 |
| **P3 - Low** | 🟢 | When convenient | Nice-to-have improvements / 有空再修的改进 |

---

## Status Definitions / 状态定义

| Status / 状态 | Symbol / 符号 | Description / 描述 |
|---------------|---------------|-------------------|
| **OPEN** | 🆕 | Newly reported, not yet assigned / 新报告，尚未分配 |
| **IN_PROGRESS** | 🔵 | Being actively worked on / 正在处理中 |
| **RESOLVED** | ✅ | Fix implemented, awaiting verification / 已修复，待验证 |
| **VERIFIED** | 🔒 | Fix verified and closed / 已验证并关闭 |
| **WONT_FIX** | ❌ | Decided not to fix (with reason) / 决定不修复（需说明原因） |
| **DUPLICATE** | 🔄 | Duplicate of another issue / 与其他 Issue 重复 |

---

## Issue Lifecycle / 问题生命周期

```
┌─────────────────────────────────────────────────────────────────┐
│                      Issue Lifecycle / 问题生命周期              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Phase 1: REPORT / 报告                                        │
│   ─────────────────────────────────────────────────────────     │
│   Anyone discovering an issue:                                  │
│   1. Add new row to appropriate priority table                  │
│   2. Assign next ISSUE-XXX ID                                   │
│   3. Set Status = 🆕 OPEN                                       │
│   4. Record in claude_progress.md: "Raised ISSUE-XXX"           │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 2: TRIAGE / 分类                                        │
│   ─────────────────────────────────────────────────────────     │
│   Owner Agent (based on file_locking_rules.md):                 │
│   1. Review issue at session start                              │
│   2. Confirm priority and type                                  │
│   3. Set Status = 🔵 IN_PROGRESS when starting work             │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 3: RESOLVE / 解决                                       │
│   ─────────────────────────────────────────────────────────     │
│   Owner Agent:                                                  │
│   1. Implement fix with tests                                   │
│   2. Commit with message referencing ISSUE-XXX                  │
│   3. Set Status = ✅ RESOLVED                                   │
│   4. Fill Resolution column with fix details                    │
│   5. Record in claude_progress.md                               │
│                                                                 │
│                         ▼                                       │
│                                                                 │
│   Phase 4: VERIFY / 验证                                        │
│   ─────────────────────────────────────────────────────────     │
│   Reporter or Agent 5:                                          │
│   1. Verify fix works as expected                               │
│   2. Set Status = 🔒 VERIFIED                                   │
│   3. Move to "Recently Closed" section                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Issue Tables / 问题表格

### 🔴 P0 - Critical Issues / 关键问题

| ID | Type | Title | File | Owner | Feature | Created | Status | Resolution |
|----|------|-------|------|-------|---------|---------|--------|------------|
| — | — | — | — | — | — | — | — | — |

### 🟠 P1 - High Priority Issues / 高优先级问题

| ID | Type | Title | File | Owner | Feature | Created | Status | Resolution |
|----|------|-------|------|-------|---------|---------|--------|------------|
| — | — | — | — | — | — | — | — | — |

### 🟡 P2 - Medium Priority Issues / 中优先级问题

| ID | Type | Title | File | Owner | Feature | Created | Status | Resolution |
|----|------|-------|------|-------|---------|---------|--------|------------|
| ISSUE-001 | 📝 TODO | Pass precision from Exchange module | `alphaloop/strategies/strategy.py:60` | Agent 1 | STRAT-001 | 2025-11-28 | 🆕 OPEN | — |

### 🟢 P3 - Low Priority Issues / 低优先级问题

| ID | Type | Title | File | Owner | Feature | Created | Status | Resolution |
|----|------|-------|------|-------|---------|---------|--------|------------|
| — | — | — | — | — | — | — | — | — |

---

## Recently Closed Issues / 最近关闭的问题

| ID | Type | Title | Owner | Resolution | Closed | Commit |
|----|------|-------|-------|------------|--------|--------|
| — | — | — | — | — | — | — |

---

## How to Report an Issue / 如何报告问题

### Step 1: Determine Priority / 确定优先级

```
问题影响什么？
     │
     ├─► 生产环境崩溃/核心功能不可用
     │         └─► 🔴 P0 - Critical
     │
     ├─► 用户体验受损/重要功能异常
     │         └─► 🟠 P1 - High
     │
     ├─► 功能可用但有瑕疵/需要改进
     │         └─► 🟡 P2 - Medium
     │
     └─► 代码质量/可维护性问题
               └─► 🟢 P3 - Low
```

### Step 2: Determine Type / 确定类型

```
问题性质是什么？
     │
     ├─► 代码运行结果错误 → 🐛 BUG
     ├─► 代码结构需要重构 → 🔧 TECH_DEBT
     ├─► 性能慢/资源占用高 → ⚡ PERF
     ├─► 安全漏洞/风险 → 🔒 SECURITY
     ├─► 代码中的 TODO 注释 → 📝 TODO
     └─► 功能增强建议 → 💡 IMPROVE
```

### Step 3: Determine Owner / 确定负责人

Based on `file_locking_rules.md`:  
根据 `file_locking_rules.md`：

| File Path / 文件路径 | Owner / 负责人 |
|---------------------|---------------|
| `alphaloop/market/*`, `alphaloop/strategies/*` | Agent 1 |
| `alphaloop/portfolio/*` | Agent 2 |
| `server.py`, `templates/*` | Agent 3 |
| `alphaloop/agents/*`, `alphaloop/evaluation/*` | Agent 4 |
| `docs/*`, `tests/*` | Agent 5 |

### Step 4: Add to Table / 添加到表格

```markdown
| ISSUE-002 | 🐛 BUG | Order not cancelled on timeout | `alphaloop/market/order_manager.py:123` | Agent 1 | CORE-002 | 2025-11-28 | 🆕 OPEN | — |
```

### Step 5: Record in Progress Log / 记录到进度日志

Add to `claude_progress.md`:  
在 `claude_progress.md` 中添加：

```markdown
| 2025-11-28 | Agent X | — | — | — | ISSUE-002 raised | Discovered order cancellation bug |
```

---

## How to Resolve an Issue / 如何解决问题

### At Session Start / 会话开始时

1. Check this file for OPEN issues where `Owner = self`  
   检查本文件中 `Owner = 自己` 的 OPEN 问题

2. Prioritize P0 > P1 > P2 > P3  
   按 P0 > P1 > P2 > P3 优先处理

3. Check if issue blocks any feature in `feature_matrix.json`  
   检查问题是否阻塞 `feature_matrix.json` 中的功能

### During Resolution / 解决过程中

1. Update Status to 🔵 IN_PROGRESS  
   更新状态为 🔵 IN_PROGRESS

2. Implement fix with appropriate tests  
   实现修复并添加测试

3. Commit with message referencing issue:  
   提交时引用问题编号：
   ```bash
   git commit -m "fix(module): ISSUE-XXX description"
   ```

### After Resolution / 解决后

1. Update Status to ✅ RESOLVED  
   更新状态为 ✅ RESOLVED

2. Fill Resolution column with details:  
   在 Resolution 列填写详情：
   ```markdown
   Fixed timeout handling in order_manager.py:125. Added retry logic. Commit: abc123
   ```

3. Record in `claude_progress.md`  
   在 `claude_progress.md` 中记录

---

## Integration with Feature Matrix / 与功能矩阵集成

### Blocking Issues / 阻塞性问题

If an issue blocks a feature:  
如果问题阻塞某个功能：

1. Add Feature ID to the issue's `Feature` column  
   在问题的 `Feature` 列添加功能 ID

2. Do NOT set `passes: true` in `feature_matrix.json` until issue is VERIFIED  
   在问题被 VERIFIED 之前，不要在 `feature_matrix.json` 中设置 `passes: true`

3. Note the blocker in `claude_progress.md`  
   在 `claude_progress.md` 中记录阻塞

### Example / 示例

```
Feature CORE-002 is blocked by ISSUE-002
功能 CORE-002 被 ISSUE-002 阻塞

→ ISSUE-002 must be VERIFIED before CORE-002 can be marked passes: true
→ ISSUE-002 必须被 VERIFIED 后，CORE-002 才能标记为 passes: true
```

---

## Issue ID Assignment / 问题 ID 分配

Issue IDs follow the format `ISSUE-NNN` where NNN is a sequential number.  
问题 ID 格式为 `ISSUE-NNN`，其中 NNN 为顺序编号。

To assign a new ID:  
分配新 ID 时：

1. Find the highest existing ID across all tables  
   在所有表格中找到最大的现有 ID

2. Increment by 1  
   加 1

3. Use the new ID for your issue  
   使用新 ID 创建问题

**Current highest ID / 当前最大 ID**: ISSUE-001

---

## Session Startup Checklist / 会话启动检查清单

Every agent should check this file at session start:  
每个 Agent 在会话开始时应检查本文件：

```
□ Check P0/P1 issues where Owner = self (handle immediately)
  检查 Owner = 自己 的 P0/P1 问题（立即处理）

□ Check P2/P3 issues where Owner = self (plan for later)
  检查 Owner = 自己 的 P2/P3 问题（计划后续处理）

□ Check RESOLVED issues where Reporter = self (verify fixes)
  检查 Reporter = 自己 的 RESOLVED 问题（验证修复）
```

---

## Related Documents / 相关文档

- `docs/project/file_locking_rules.md` — Determines issue ownership / 确定问题归属
- `docs/project/feature_matrix.json` — Links issues to features / 关联问题与功能
- `docs/project/claude_progress.md` — Records issue activities / 记录问题活动
- `docs/project/agent_requests.md` — For cross-agent issue handoffs / 跨 Agent 问题移交
- `docs/contrib_guidelines.md` — Commit message format for fixes / 修复提交格式


