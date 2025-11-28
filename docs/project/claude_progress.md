# Claude Progress Log / Claude 进度日志

## Purpose / 目的

This file tracks session-by-session progress across multiple Cursor agents.  
本文件追踪多个 Cursor Agent 的逐会话进度。

Every agent must update this log at the end of their session before committing.  
每个 Agent 必须在会话结束提交前更新此日志。

Reference: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
参考：[长周期 Agent 有效支撑框架](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Update Protocol / 更新协议

1. **Before ending your session / 结束会话前**:
   - Append a new row to the progress table below.  
     在下方表格追加新行。
   - Reference the Feature ID from `feature_matrix.json`.  
     引用 `feature_matrix.json` 中的功能 ID。
   - List all files you modified.  
     列出所有修改过的文件。
   - Note test results (✅ Pass / ❌ Fail / ⏸️ Skipped).  
     记录测试结果（✅ 通过 / ❌ 失败 / ⏸️ 跳过）。
   - Document any blockers for the next session.  
     记录任何阻塞下轮会话的问题。

2. **Commit with progress update / 提交时包含进度更新**:
   ```bash
   git add docs/project/claude_progress.md
   git commit -m "docs(progress): update session log for FEAT-XXX"
   ```

---

## Progress Table / 进度表

| Date / 日期 | Agent | Feature ID | Files Changed / 变更文件 | Test Result / 测试结果 | Blockers / 阻塞项 | Notes / 备注 |
|-------------|-------|------------|-------------------------|----------------------|------------------|-------------|
| 2025-11-28 | Agent 5 | INIT-001 | `docs/project/init_plan.md`, `docs/project/feature_matrix.json`, `docs/project/claude_progress.md`, `scripts/init.sh`, `docs/project/deliverable_plan_framework_and_task.md` | ⏸️ Skipped | None | Initial harness setup: created initialization blueprint, feature tracker, progress log template, and init.sh script / 初始化支撑体系：创建初始化蓝图、功能追踪器、进度日志模板及 init.sh 脚本 |
| 2025-11-28 | Agent 5 | INIT-002 | `docs/project/file_locking_rules.md`, `docs/project/agent_requests.md`, `docs/contrib_guidelines.md`, `docs/project/deliverable_plan_framework_and_task.md` | ⏸️ Skipped | None | Collaboration framework: created file locking rules (4 permission levels), cross-agent request protocol (lifecycle, types, examples), and incremental commit policy / 协作框架：创建文件锁定规则（4 级权限）、跨 Agent 请求协议（生命周期、类型、示例）及增量提交策略 |

---

## Legend / 图例

| Symbol / 符号 | Meaning / 含义 |
|---------------|---------------|
| ✅ | All tests passed / 所有测试通过 |
| ❌ | Tests failed (see blockers) / 测试失败（见阻塞项） |
| ⏸️ | Tests skipped or not applicable / 跳过测试或不适用 |
| 🚧 | Work in progress (incomplete) / 进行中（未完成） |

---

## Session Handoff Checklist / 会话交接清单

Before ending your session, verify:  
结束会话前请确认：

- [ ] Progress table updated with today's work.  
  [ ] 进度表已更新今日工作。
- [ ] All modified files committed to git.  
  [ ] 所有修改文件已提交 git。
- [ ] `feature_matrix.json` updated if any feature status changed.  
  [ ] 如有功能状态变更，已更新 `feature_matrix.json`。
- [ ] Blockers clearly documented for next session.  
  [ ] 阻塞项已清晰记录以便下轮会话。
- [ ] No broken tests left behind.  
  [ ] 未遗留失败测试。


