# Contribution Guidelines / 贡献指南

## Purpose / 目的

This document defines the incremental commit policy and contribution workflow for multi-agent parallel development.  
本文档定义多 Agent 并行开发的增量提交策略与贡献工作流。

Reference: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
参考：[长周期 Agent 有效支撑框架](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Core Principles / 核心原则

### 1️⃣ One Feature Per Session / 单功能原则

Each session should focus on **one feature** from `feature_matrix.json`.  
每次会话应聚焦于 `feature_matrix.json` 中的**一个功能**。

```
✅ Good / 正确:
   Session goal: Complete CORE-001 (Exchange connection)
   会话目标：完成 CORE-001（交易所连接）

❌ Bad / 错误:
   Session goal: Complete CORE-001, CORE-002, and CORE-003
   会话目标：完成 CORE-001、CORE-002 和 CORE-003
```

**Exceptions / 例外**:
- Fixing blocking bugs discovered during implementation  
  修复实现过程中发现的阻塞性 bug
- Small related changes that cannot be separated  
  无法分离的小型相关变更

### 2️⃣ Test-Backed Commits / 测试闭环

Every code change must be accompanied by tests.  
每个代码变更必须附带测试。

```
┌─────────────────────────────────────────────────────────────────┐
│                    Commit Prerequisites / 提交前置条件           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Before committing, verify:                                    │
│   提交前请确认：                                                 │
│                                                                 │
│   □ Related tests exist and pass                                │
│     相关测试存在且通过                                           │
│                                                                 │
│   □ No existing tests are broken                                │
│     现有测试未被破坏                                             │
│                                                                 │
│   □ Test evidence recorded in claude_progress.md                │
│     测试证据已记录在 claude_progress.md                          │
│                                                                 │
│   Only then can you:                                            │
│   满足以上条件后才能：                                           │
│                                                                 │
│   □ Set passes: true in feature_matrix.json                     │
│     在 feature_matrix.json 中设置 passes: true                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3️⃣ Mergeable State / 可合并状态

Every commit must leave the codebase in a working state.  
每次提交必须保持代码库处于可工作状态。

```
✅ Mergeable State / 可合并状态:
   - All tests pass / 所有测试通过
   - Server starts without errors / 服务器可正常启动
   - No half-implemented features / 无半实现的功能
   - Code is documented / 代码有文档

❌ Non-Mergeable State / 不可合并状态:
   - Broken tests / 测试失败
   - Syntax errors / 语法错误
   - Incomplete implementations with TODOs / 带 TODO 的不完整实现
   - Missing imports / 缺失导入
```

### 4️⃣ Progress Sync / 进度同步

Every session must update progress tracking files.  
每次会话必须更新进度追踪文件。

```
At session end / 会话结束时:

1. Update claude_progress.md with session summary
   更新 claude_progress.md，记录会话摘要

2. Update feature_matrix.json if feature completed
   如功能完成，更新 feature_matrix.json

3. Check/update agent_requests.md for pending requests
   检查/更新 agent_requests.md 中的待处理请求

4. Commit all changes together
   一起提交所有变更
```

---

## Session Workflow / 会话工作流

### Session Start / 会话开始

```bash
# 1. Verify working directory / 确认工作目录
pwd

# 2. Check recent commits / 查看最近提交
git log --oneline -5

# 3. Read progress files / 阅读进度文件
# - docs/project/claude_progress.md
# - docs/project/feature_matrix.json
# - docs/project/agent_requests.md

# 4. Run smoke test (optional but recommended) / 运行冒烟测试（推荐）
./scripts/init.sh smoke

# 5. Select ONE feature to work on / 选择一个功能开始工作
# Choose from feature_matrix.json where passes: false and owner: self
```

### During Session / 会话期间

```
┌─────────────────────────────────────────────────────────────────┐
│                    Implementation Loop / 实现循环                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. Implement feature incrementally                            │
│      增量实现功能                                                │
│                                                                 │
│   2. Write/update tests as you go                               │
│      边实现边写测试                                              │
│                                                                 │
│   3. Run tests frequently                                       │
│      频繁运行测试                                                │
│      pytest tests/test_xxx.py -v                                │
│                                                                 │
│   4. If blocked by another agent:                               │
│      如果被其他 Agent 阻塞：                                     │
│      - Raise request in agent_requests.md                       │
│        在 agent_requests.md 发起请求                             │
│      - Work on another feature                                  │
│        处理其他功能                                              │
│                                                                 │
│   5. Check for incoming requests periodically                   │
│      定期检查收到的请求                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Session End / 会话结束

```bash
# 1. Run all related tests / 运行所有相关测试
pytest tests/test_xxx.py -v

# 2. If tests pass, update feature_matrix.json
#    如果测试通过，更新 feature_matrix.json
#    Change: "passes": false → "passes": true

# 3. Update claude_progress.md
#    更新 claude_progress.md
#    Add new row with session summary

# 4. Check agent_requests.md
#    检查 agent_requests.md
#    - Respond to incoming requests
#    - Update status of own requests

# 5. Stage and commit / 暂存并提交
git add .
git commit -m "feat(module): FEAT-XXX description"

# 6. Verify commit / 验证提交
git log --oneline -1
```

---

## Commit Message Format / 提交信息格式

### Format / 格式

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types / 类型

| Type / 类型 | When to Use / 使用场景 |
|-------------|----------------------|
| `feat` | New feature / 新功能 |
| `fix` | Bug fix / 修复 bug |
| `docs` | Documentation only / 仅文档 |
| `refactor` | Code refactoring / 代码重构 |
| `test` | Test-related changes / 测试相关 |
| `chore` | Build/config changes / 构建/配置变更 |

### Scopes / 范围

| Scope / 范围 | Agent | Examples / 示例 |
|--------------|-------|----------------|
| `trading` | Agent TRADING | `feat(trading): add order cancellation` |
| `strategy` | Agent TRADING | `feat(strategy): implement funding rate logic` |
| `portfolio` | Agent PORTFOLIO | `feat(portfolio): add rebalance method` |
| `risk` | Agent PORTFOLIO | `fix(risk): correct margin calculation` |
| `api` | Agent WEB | `feat(api): add /api/risk-indicators endpoint` |
| `ui` | Agent WEB | `feat(ui): add portfolio overview panel` |
| `llm` | Agent AI | `feat(llm): integrate OpenAI provider` |
| `eval` | Agent AI | `refactor(eval): improve prompt structure` |
| `docs` | Agent QA | `docs(guide): update user stories` |
| `test` | Agent QA | `test(integration): add portfolio sync tests` |
| `harness` | Agent QA | `feat(harness): add file locking rules` |

### Examples / 示例

```bash
# Feature completion
feat(trading): CORE-001 implement exchange connection

Add BinanceClient with authentication support.
- Initialize with API credentials
- Verify testnet/mainnet connection
- Fetch account balance

Closes CORE-001

# Bug fix
fix(portfolio): PORT-001 correct allocation percentage calculation

The allocation was being calculated as absolute value instead of percentage.

# Documentation
docs(harness): add file locking rules and agent request protocol

Part of engineering harness setup for multi-agent collaboration.
```

---

## Feature Completion Checklist / 功能完成检查清单

Before marking a feature as `passes: true`:  
在将功能标记为 `passes: true` 之前：

```
□ All steps in feature_matrix.json are implemented
  feature_matrix.json 中所有步骤已实现

□ Unit tests exist and pass
  单元测试存在且通过

□ Integration tests (if applicable) pass
  集成测试（如适用）通过

□ No regressions in existing tests
  现有测试无回归

□ Code follows project style (PEP 8)
  代码遵循项目风格（PEP 8）

□ Docstrings added for public functions
  公开函数已添加文档字符串

□ claude_progress.md updated
  claude_progress.md 已更新

□ Commit message references feature ID
  提交信息引用功能 ID
```

---

## Rollback Guidance / 回滚指引

If an experiment fails or introduces bugs:  
如果实验失败或引入 bug：

### Option 1: Discard All Changes / 丢弃所有变更

```bash
# Discard all uncommitted changes
git checkout -- .

# Or stash for later review
git stash save "Failed experiment for FEAT-XXX"
```

### Option 2: Revert Last Commit / 回滚上次提交

```bash
# Revert the last commit (keeps changes staged)
git reset --soft HEAD~1

# Or completely remove (discards changes)
git reset --hard HEAD~1
```

### Option 3: Revert Specific Commit / 回滚特定提交

```bash
# Create a new commit that undoes a specific commit
git revert <commit-hash>
```

### After Rollback / 回滚后

1. Record in `claude_progress.md`:  
   在 `claude_progress.md` 中记录：
   ```markdown
   | 2025-11-28 | Agent XXX | FEAT-XXX | — | ❌ | Rolled back | Attempted approach failed: [reason] |
   ```

2. Keep `passes: false` in `feature_matrix.json`  
   保持 `feature_matrix.json` 中 `passes: false`

3. Document the failed approach for future reference  
   记录失败方案供后续参考

---

## Handling Incomplete Features / 处理未完成功能

If you cannot complete a feature in one session:  
如果无法在一次会话中完成功能：

### DO / 应该做

```
✅ Commit working partial implementation
   提交可工作的部分实现

✅ Keep passes: false in feature_matrix.json
   保持 feature_matrix.json 中 passes: false

✅ Document progress in claude_progress.md
   在 claude_progress.md 中记录进度

✅ Note what remains to be done
   记录剩余待完成事项
```

### DON'T / 不应该做

```
❌ Leave broken code uncommitted
   留下未提交的损坏代码

❌ Set passes: true for incomplete features
   为未完成功能设置 passes: true

❌ Leave TODO comments without documentation
   留下无文档的 TODO 注释

❌ Commit code that breaks existing tests
   提交破坏现有测试的代码
```

---

## Code Style / 代码风格

### Python

- Follow PEP 8 / 遵循 PEP 8
- Use type hints / 使用类型注解
- Google-style docstrings / Google 风格文档字符串
- Maximum line length: 88 (Black default) / 最大行长：88

### Docstring Example / 文档字符串示例

```python
def calculate_risk_score(
    margin_ratio: float,
    leverage: int,
    position_size: float
) -> float:
    """Calculate overall risk score based on multiple factors.
    
    Args:
        margin_ratio: Current margin ratio (0.0 to 1.0).
        leverage: Current leverage multiplier.
        position_size: Absolute position size in base currency.
    
    Returns:
        Risk score from 0.0 (lowest risk) to 1.0 (highest risk).
    
    Raises:
        ValueError: If margin_ratio is outside valid range.
    
    Example:
        >>> calculate_risk_score(0.5, 10, 1000.0)
        0.65
    """
    ...
```

---

## Issue Discovery and Resolution / 问题发现与解决

### When You Discover an Issue / 发现问题时

During development, you may encounter bugs, performance issues, or code that needs improvement.  
开发过程中，你可能会遇到 bug、性能问题或需要改进的代码。

```
┌─────────────────────────────────────────────────────────────────┐
│                    Issue Discovery Flow / 问题发现流程           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. Determine if it blocks your current work                   │
│      判断是否阻塞当前工作                                        │
│                                                                 │
│      ├─► YES: Fix immediately, then continue                    │
│      │        是：立即修复，然后继续                             │
│      │                                                          │
│      └─► NO: Report in issue_tracker.md                         │
│               否：在 issue_tracker.md 中报告                     │
│                                                                 │
│   2. Determine ownership (check file_locking_rules.md)          │
│      确定归属（查看 file_locking_rules.md）                      │
│                                                                 │
│      ├─► Your file: Add to your session backlog                 │
│      │              你的文件：加入会话待办                        │
│      │                                                          │
│      └─► Other's file: Report with Owner = that Agent           │
│                        别人的文件：报告并指定 Owner              │
│                                                                 │
│   3. Record in claude_progress.md                               │
│      在 claude_progress.md 中记录                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Issue Commit Message Format / 问题修复提交格式

When fixing an issue, use this commit message format:  
修复问题时，使用以下提交格式：

```bash
# For bugs
fix(module): ISSUE-XXX brief description

# For performance issues
perf(module): ISSUE-XXX brief description

# For security fixes
security(module): ISSUE-XXX brief description

# For tech debt
refactor(module): ISSUE-XXX brief description
```

### Session Workflow with Issues / 包含问题处理的会话流程

```
Session Start / 会话开始
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Check issue_tracker.md           │
│    检查 issue_tracker.md            │
│    - P0/P1 issues with Owner = self │
│      Owner = 自己 的 P0/P1 问题     │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 2. Prioritize                       │
│    优先级排序                        │
│    P0 issues > P1 issues > Features │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 3. Work on highest priority item    │
│    处理最高优先级项目                │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 4. Update issue_tracker.md          │
│    更新 issue_tracker.md            │
│    - Set RESOLVED when fixed        │
│      修复后设为 RESOLVED            │
└─────────────────────────────────────┘
     │
     ▼
Session End / 会话结束
```

---

## Related Documents / 相关文档

- `docs/project/file_locking_rules.md` — File ownership and permissions / 文件归属与权限
- `docs/project/agent_requests.md` — Cross-agent request protocol / 跨 Agent 请求协议
- `docs/project/claude_progress.md` — Progress tracking / 进度追踪
- `docs/project/feature_matrix.json` — Feature status tracker / 功能状态追踪
- `docs/project/issue_tracker.md` — Bug and issue tracking / 问题追踪
- `docs/project/init_plan.md` — Initialization blueprint / 初始化蓝图
- `docs/agents/README.md` — Agent overview / Agent 概览

