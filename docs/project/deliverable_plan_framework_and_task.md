# Deliverable Plan Framework & Tasks / 交付计划框架与任务

## Purpose / 目的
This document structures the engineering harness rollout so multiple Cursor agents can collaborate incrementally without losing context.  
本文档用于规划工程化支撑体系，确保多个 Cursor Agent 能在多轮会话中增量协作且不丢上下文。

## Reference / 参考
The plan follows the harness practices described in [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents).  
本计划参考了 [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) 中的工程化方法。

## Workstreams Overview / 工作流总览
- Initializer assets seed a consistent baseline for later sessions.  
  初始化工件为后续会话提供一致的基线。
- Structured trackers keep every feature’s status transparent.  
  结构化追踪器确保每个功能状态透明。
- Standard checklists and policies enforce incremental, test-backed commits.  
  标准检查清单与策略保证增量提交和测试闭环。

---

## 1. Initialization Blueprint / 初始化蓝图 ✅ COMPLETED
**Deliverable / 交付物**: `docs/project/init_plan.md` describing `init.sh`, `claude_progress.md`, `feature_matrix.json`, and smoke steps.  
**Responsible Agent / 责任 Agent**: Agent 5 主导文档，Agent 1 & 3 提供技术输入。

### Artifacts Created / 已创建工件
- `docs/project/init_plan.md` — Initialization blueprint with acceptance criteria  
- `docs/project/feature_matrix.json` — Feature tracker with 22 initial features  
- `docs/project/claude_progress.md` — Progress log template with first entry  
- `scripts/init.sh` — Environment bootstrap and smoke test script  

### Tasks / 任务
- [x] Draft bilingual outline covering purpose, scope, and acceptance criteria.  
  [x] 撰写双语纲要，涵盖目的、范围及验收标准。
- [x] Detail `init.sh` responsibilities (services, env vars, smoke triggers).  
  [x] 描述 `init.sh` 需承担的服务、环境变量与自检触发。
- [x] Define first-session checklist referencing the initializer sequence.  
  [x] 明确首轮会话需执行的初始化步骤清单。

---

## 2. Feature Tracker Schema / 功能追踪结构 ✅ COMPLETED
**Deliverable / 交付物**: `docs/project/feature_matrix.json` plus editing rules.  
**Responsible Agent / 责任 Agent**: Agent 5 维护模板，各业务 Agent 更新 `passes`。

### Artifact Created / 已创建工件
- `docs/project/feature_matrix.json` — Contains 22 features across 8 categories with mutation rules embedded

### Tasks / 任务
- [x] Specify mandatory fields (id, category, description, steps, passes).  
  [x] 规定必填字段（id、category、description、steps、passes）。
- [x] Document "passes-only" mutation policy and review workflow.  
  [x] 记录仅允许修改 passes 的策略及审查流程。
- [x] Provide sample entries tied to high-priority features.  
  [x] 添加高优先级功能示例条目。

---

## 3. Progress Log Template / 进度日志模板 ✅ COMPLETED
**Deliverable / 交付物**: `docs/project/claude_progress.md` with structured tables.  
**Responsible Agent / 责任 Agent**: Agent 5 维护格式，所有 Agent 填写。

### Artifact Created / 已创建工件
- `docs/project/claude_progress.md` — Progress log with table structure, update protocol, and first entry

### Tasks / 任务
- [x] Design table columns (date, agent, feature id, files changed, tests, blockers).  
  [x] 设计表格列（日期、Agent、功能ID、变更文件、测试结果、阻塞项）。
- [x] Describe end-of-session update protocol and storage location.  
  [x] 描述会话结束更新流程及存放位置。
- [x] Include example entry showing expected bilingual tone.  
  [x] 添加示例记录，展示双语写法。

---

## 4. Session Checklist Upgrade / 会话检查清单强化
**Deliverable / 交付物**: Update `docs/agents/README.md` with mandatory startup routine.  
**Responsible Agent / 责任 Agent**: Agent 5。

### Tasks / 任务
- [ ] Insert ordered list (`pwd → git log → claude-progress → feature_matrix → init.sh smoke`).  
  [ ] 加入有序列表（`pwd → git log → claude-progress → feature_matrix → init.sh smoke`）。
- [ ] Clarify per-Agent interpretation (e.g., which directories to inspect).  
  [ ] 说明各 Agent 应检查的目录与文件。
- [ ] Add reminder to log findings back into progress file.  
  [ ] 添加提示：自检结果需回写到进度日志。

---

## 5. Incremental Commit Policy / 增量提交策略 ✅ COMPLETED
**Deliverable / 交付物**: `docs/contrib_guidelines.md` focused on incremental work.  
**Responsible Agent / 责任 Agent**: Agent 5。

### Artifact Created / 已创建工件
- `docs/contrib_guidelines.md` — Comprehensive contribution guidelines with commit policy, session workflow, and rollback guidance

### Tasks / 任务
- [x] Define "one feature per session" expectation and exception path.  
  [x] 明确"单次会话仅推进一个功能"及例外处理。
- [x] Require linked tests, git commit, and progress entry before marking passes=true.  
  [x] 规定通过测试、提交记录、进度日志是设置 passes=true 的前置条件。
- [x] Document rollback guidance for failed experiments.  
  [x] 记录失败实验的回滚指引。

---

## 6. Testing Harness Guide / 测试支撑指南
**Deliverable / 交付物**: `docs/testing/smoke_check.md` tied to `init.sh smoke`.  
**Responsible Agent / 责任 Agent**: Agent 5 协调，测试内容由 Agent 1/2/3 提供。

### Tasks / 任务
- [ ] List minimal E2E steps (start services, API ping, pytest subset).  
  [ ] 罗列最小 E2E 步骤（启动服务、API 探活、pytest 子集）。
- [ ] Map each step to owning Agent for maintenance.  
  [ ] 将各步骤映射到维护 Agent。
- [ ] Describe failure escalation and logging requirements.  
  [ ] 描述失败后的升级与记录要求。

---

## 7. Cross-Agent Responsibility Map / 跨 Agent 责任映射 ✅ COMPLETED
**Deliverable / 交付物**: `docs/project/file_locking_rules.md` + `docs/project/agent_requests.md`.  
**Responsible Agent / 责任 Agent**: Agent 5。

### Artifacts Created / 已创建工件
- `docs/project/file_locking_rules.md` — File ownership matrix with permission levels (EXCLUSIVE, COORDINATED, SHARED-APPEND, FREE)
- `docs/project/agent_requests.md` — Cross-agent request protocol with lifecycle, types, and examples

### Tasks / 任务
- [x] Build matrix linking each harness artifact to owning Agent(s).  
  [x] 构建矩阵，将每个工件对应到负责 Agent。
- [x] Highlight shared files requiring coordination (`config.py`, deps, etc.).  
  [x] 标注需协同维护的共享文件（如 `config.py`、依赖文件）。
- [x] Provide guidance on raising cross-Agent requests.  
  [x] 提供发起跨 Agent 请求的指引。

---

## Tracking Notes / 跟踪备注
- Update this checklist whenever scopes change or new artifacts emerge.  
  当范围调整或新增工件时需同步更新本清单。
- Reference the progress log to confirm task completion before ticking boxes.  
  打钩前请对照进度日志确认任务完成。
- Store all multi-agent progress tracking artifacts under `docs/project/` for easy discovery and shared context.  
  所有多 Agent 协作所需的进度追踪文档统一放置于 `docs/project/` 目录，便于集中访问与共享上下文。

