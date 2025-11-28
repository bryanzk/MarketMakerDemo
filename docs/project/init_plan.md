# Initialization Blueprint / 初始化蓝图

## Purpose / 目的

This document defines the assets and sequence that every **first session** (initializer agent) must produce before any incremental coding work begins.  
本文档定义每次**首轮会话**（初始化 Agent）在开展增量编码前必须生成的资产与执行顺序。

Reference: [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)  
参考：[长周期 Agent 有效支撑框架](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## Scope / 范围

The initializer session is responsible for producing **four core artifacts**:  
初始化会话需产出**四项核心工件**：

| Artifact / 工件 | Path / 路径 | Description / 描述 |
|-----------------|-------------|-------------------|
| `init.sh` | `scripts/init.sh` | Environment bootstrap & smoke test script / 环境启动与冒烟测试脚本 |
| `claude_progress.md` | `docs/project/claude_progress.md` | Session-by-session progress log / 逐会话进度日志 |
| `feature_matrix.json` | `docs/project/feature_matrix.json` | Structured feature tracker / 结构化功能追踪器 |
| First git commit | N/A | Snapshot of initial state / 初始状态快照 |

---

## Artifact Details / 工件详情

### 1. `init.sh` — Environment Bootstrap Script / 环境启动脚本

**Location / 位置**: `scripts/init.sh`

**Responsibilities / 职责**:

```bash
#!/usr/bin/env bash
# init.sh — MarketMakerDemo Environment Bootstrap
# Usage: ./scripts/init.sh [smoke]

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# 1. Activate virtual environment / 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "⚠️  venv not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 2. Install dependencies / 安装依赖
pip install -q -r requirements.txt

# 3. Verify environment variables / 验证环境变量
required_vars=("BINANCE_API_KEY" "BINANCE_API_SECRET")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️  Warning: $var not set (may be required for live trading)"
    fi
done

# 4. Smoke test (optional) / 冒烟测试（可选）
if [ "$1" = "smoke" ]; then
    echo "🔥 Running smoke tests..."
    
    # 4.1 Start server in background / 后台启动服务器
    python server.py &
    SERVER_PID=$!
    sleep 3
    
    # 4.2 Health check / 健康检查
    if curl -s http://127.0.0.1:8000/api/portfolio/status > /dev/null; then
        echo "✅ Server health check passed"
    else
        echo "❌ Server health check failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    fi
    
    # 4.3 Run core pytest subset / 运行核心 pytest 子集
    pytest tests/test_server.py tests/test_portfolio_api.py -v --tb=short || {
        echo "❌ Core tests failed"
        kill $SERVER_PID 2>/dev/null || true
        exit 1
    }
    
    # 4.4 Cleanup / 清理
    kill $SERVER_PID 2>/dev/null || true
    echo "✅ Smoke tests completed successfully"
fi

echo "✅ Environment ready. Project root: $PROJECT_ROOT"
```

**Key Points / 要点**:
- Idempotent execution / 幂等执行
- Graceful handling of missing env vars / 优雅处理缺失环境变量
- `smoke` argument triggers E2E validation / `smoke` 参数触发端到端验证

---

### 2. `claude_progress.md` — Progress Log / 进度日志

**Location / 位置**: `docs/project/claude_progress.md`

**Structure / 结构**:

| Date / 日期 | Agent | Feature ID | Files Changed / 变更文件 | Test Result / 测试结果 | Blockers / 阻塞项 | Notes / 备注 |
|-------------|-------|------------|-------------------------|----------------------|------------------|-------------|
| 2025-11-28 | Agent 5 | INIT-001 | docs/project/*.md | ✅ Pass | None | Initial harness setup |

**Update Protocol / 更新协议**:
1. Every session must append at least one row before ending.  
   每次会话结束前必须追加至少一行。
2. Use feature IDs from `feature_matrix.json`.  
   使用 `feature_matrix.json` 中的功能 ID。
3. Mark blockers clearly for next session pickup.  
   清晰标注阻塞项以便下轮会话接手。

---

### 3. `feature_matrix.json` — Feature Tracker / 功能追踪器

**Location / 位置**: `docs/project/feature_matrix.json`

**Schema / 结构**:

```json
{
  "version": "1.0.0",
  "last_updated": "2025-11-28",
  "features": [
    {
      "id": "FEAT-001",
      "category": "trading",
      "description": "Exchange connection and order placement",
      "steps": [
        "Initialize exchange client",
        "Fetch account balance",
        "Place limit order",
        "Verify order status"
      ],
      "passes": false,
      "owner": "Agent 1"
    }
  ]
}
```

**Mutation Rules / 修改规则**:
- ✅ Allowed: Change `passes` from `false` to `true` after verified testing.  
  允许：测试验证后将 `passes` 从 `false` 改为 `true`。
- ✅ Allowed: Add new feature entries with `passes: false`.  
  允许：添加新功能条目（`passes: false`）。
- ❌ Forbidden: Delete or modify existing feature descriptions.  
  禁止：删除或修改现有功能描述。
- ❌ Forbidden: Set `passes: true` without test evidence.  
  禁止：无测试证据直接设置 `passes: true`。

---

### 4. First Git Commit / 首次 Git 提交

After generating the above artifacts, the initializer session must:  
生成上述工件后，初始化会话必须：

```bash
git add docs/project/init_plan.md \
        docs/project/claude_progress.md \
        docs/project/feature_matrix.json \
        scripts/init.sh

git commit -m "feat(harness): initialize long-running agent framework

- Add init.sh for environment bootstrap and smoke tests
- Add claude_progress.md for session tracking
- Add feature_matrix.json for feature status
- Add init_plan.md documenting the initialization blueprint"
```

---

## First-Session Checklist / 首轮会话检查清单

The initializer agent must complete these steps in order:  
初始化 Agent 必须按顺序完成以下步骤：

| Step / 步骤 | Action / 操作 | Verification / 验证 |
|-------------|--------------|---------------------|
| 1 | `pwd` — Confirm project root | Output shows `MarketMakerDemo` |
| 2 | `git status` — Check clean state | No uncommitted changes |
| 3 | Create `scripts/init.sh` | File exists and is executable |
| 4 | Create `docs/project/feature_matrix.json` | Valid JSON with initial features |
| 5 | Create `docs/project/claude_progress.md` | Table header present |
| 6 | Run `./scripts/init.sh smoke` | All checks pass |
| 7 | Git commit all artifacts | Commit hash recorded |
| 8 | Update `claude_progress.md` | First row added |

---

## Acceptance Criteria / 验收标准

The initialization is complete when:  
满足以下条件时初始化完成：

- [ ] `scripts/init.sh` exists and runs without error.  
  [ ] `scripts/init.sh` 存在且可无错运行。
- [ ] `scripts/init.sh smoke` passes all health checks.  
  [ ] `scripts/init.sh smoke` 通过所有健康检查。
- [ ] `docs/project/feature_matrix.json` contains at least 5 high-priority features.  
  [ ] `docs/project/feature_matrix.json` 包含至少 5 个高优先级功能。
- [ ] `docs/project/claude_progress.md` has the table structure and first entry.  
  [ ] `docs/project/claude_progress.md` 具备表格结构及首条记录。
- [ ] All artifacts are committed to git with descriptive message.  
  [ ] 所有工件已提交至 git 并附描述性信息。
- [ ] Next session can run the standard startup checklist successfully.  
  [ ] 下一轮会话可成功执行标准启动检查清单。

---

## Responsible Agents / 责任 Agent

| Artifact / 工件 | Primary / 主责 | Support / 协助 |
|-----------------|---------------|----------------|
| `init_plan.md` | Agent 5 | — |
| `init.sh` | Agent 3 | Agent 1 |
| `feature_matrix.json` | Agent 5 | All Agents |
| `claude_progress.md` | Agent 5 | All Agents |

---

## Next Steps / 后续步骤

After initialization is complete, subsequent sessions should follow the **Session Startup Checklist** defined in `docs/agents/README.md`:  
初始化完成后，后续会话应遵循 `docs/agents/README.md` 中定义的**会话启动检查清单**：

1. `pwd` — Verify working directory  
2. `git log --oneline -5` — Review recent commits  
3. Read `docs/project/claude_progress.md` — Understand current state  
4. Read `docs/project/feature_matrix.json` — Pick next feature  
5. Run `./scripts/init.sh smoke` — Verify environment health  
6. Begin incremental work on selected feature  


