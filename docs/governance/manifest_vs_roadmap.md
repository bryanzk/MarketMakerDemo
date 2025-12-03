# project_manifest.json vs roadmap.json / 项目清单 vs 路线图

## 📋 Overview / 概述

这两个文件是项目治理体系的核心，但服务于不同的目的：
These two files are core to the project governance system, but serve different purposes:

- **`project_manifest.json`** - 项目的"结构地图" / Project "structure map"
- **`status/roadmap.json`** - 功能的"状态索引" / Feature "status index"

---

## 🗺️ project_manifest.json / 项目清单

### Purpose / 目的

**全局项目结构定义文件** - 定义了项目的"骨架"和"规则"
**Global project structure definition** - Defines the project's "skeleton" and "rules"

### What It Contains / 包含内容

1. **Project Metadata / 项目元数据**
   ```json
   {
     "project": {
       "name": "MarketMakerDemo",
       "description": "Agent-first market making system",
       "language": "Python 3.11+",
       "framework": "FastAPI + Binance API"
     }
   }
   ```

2. **Module Definitions / 模块定义**
   - 所有模块的完整定义（id, name, owner, 目录, 依赖）
   - Complete module definitions (id, name, owner, directories, dependencies)
   - 每个模块指向其 `module_card`（`docs/modules/{module}.json`）
   - Each module points to its `module_card` (`docs/modules/{module}.json`)

3. **Governance Configuration / 治理配置**
   - 治理文件的位置（roadmap, progress_index, agent_requests）
   - Locations of governance files (roadmap, progress_index, agent_requests)
   - 审计脚本路径
   - Audit script path

4. **Pipeline Definition / 流程定义**
   - 17 步开发流程的完整定义
   - Complete definition of the 17-step development pipeline
   - 每个步骤的负责 Agent 和产出物
   - Responsible agent and artifacts for each step

5. **Naming Conventions / 命名规范**
   - 模块 ID、功能 ID、分支、提交消息的命名规则
   - Naming rules for module IDs, feature IDs, branches, commit messages

### Characteristics / 特征

- ✅ **相对静态** / Relatively static - 项目结构变化时才更新
- ✅ **只读策略** / Readonly policy - 仅 Agent PM 可修改
- ✅ **全局参考** / Global reference - 所有 Agent 可读取
- ✅ **结构定义** / Structure definition - 定义"是什么"，不跟踪"在哪里"

### Example / 示例

```json
{
  "modules": [
    {
      "id": "trading",
      "name": "Trading Engine",
      "owner_agent": "Agent TRADING",
      "source_dir": "src/trading/",
      "module_card": "docs/modules/trading.json",
      "feature_source": "docs/modules/trading.json#/features"
    }
  ],
  "governance": {
    "status_registry": "status/roadmap.json"
  }
}
```

---

## 🗓️ status/roadmap.json / 路线图

### Purpose / 目的

**轻量级功能状态索引** - 提供所有功能的快速状态概览
**Lightweight feature status index** - Provides quick status overview of all features

### What It Contains / 包含内容

1. **Feature Pointers / 功能指针**
   ```json
   {
     "features": [
       {
         "id": "CORE-001",
         "module_id": "trading",
         "current_step": "spec_defined",
         "sync_source": "docs/modules/trading.json"
       }
     ]
   }
   ```

2. **Minimal Information / 最小信息**
   - 只包含：功能 ID、模块 ID、当前步骤、同步源
   - Only contains: feature ID, module ID, current step, sync source
   - **详细状态存储在 module cards 中** / **Detailed state stored in module cards**

### Characteristics / 特征

- ✅ **动态更新** / Dynamic - 功能推进时频繁更新
- ✅ **轻量级** / Lightweight - 只存储指针，不存储完整状态
- ✅ **快速查询** / Fast query - 用于快速查找功能状态
- ✅ **状态跟踪** / Status tracking - 跟踪"在哪里"，不定义"是什么"

### Example / 示例

```json
{
  "features": [
    {
      "id": "CORE-001",
      "module_id": "trading",
      "current_step": "spec_defined",
      "sync_source": "docs/modules/trading.json"
    }
  ],
  "notes": "Feature states are defined inside module cards; roadmap keeps lightweight pointers only."
}
```

---

## 🔄 Relationship / 关系

### Data Flow / 数据流

```
project_manifest.json
    ↓ (defines structure)
docs/modules/{module}.json
    ↓ (contains detailed feature states)
status/roadmap.json
    ↑ (lightweight pointers, synced from module cards)
```

### Synchronization / 同步

1. **Module Cards 是真相源** / **Module Cards are source of truth**
   - 功能的详细状态（artifacts, status fields）存储在 `docs/modules/{module}.json`
   - Detailed feature states (artifacts, status fields) stored in `docs/modules/{module}.json`

2. **Roadmap 是索引** / **Roadmap is index**
   - `status/roadmap.json` 只存储轻量级指针
   - `status/roadmap.json` only stores lightweight pointers
   - 通过 `sync_source` 字段指向 module card
   - Points to module card via `sync_source` field

3. **自动化同步** / **Automated sync**
   - `scripts/advance_feature.py` 自动同步 roadmap
   - `scripts/advance_feature.py` automatically syncs roadmap
   - 更新 module card 时，roadmap 自动更新
   - When module card is updated, roadmap is automatically updated

---

## 📊 Comparison Table / 对比表

| Aspect / 方面 | project_manifest.json | status/roadmap.json |
|--------------|----------------------|---------------------|
| **Purpose / 目的** | 定义项目结构 | 跟踪功能状态 |
| **Scope / 范围** | 全局项目配置 | 功能状态索引 |
| **Update Frequency / 更新频率** | 低（结构变化时） | 高（功能推进时） |
| **Data Detail / 数据详细程度** | 完整定义 | 轻量级指针 |
| **Read Access / 读取权限** | 所有 Agent | 所有 Agent |
| **Write Access / 写入权限** | 仅 Agent PM | Agent PM（通过自动化脚本） |
| **Contains / 包含** | 模块定义、流程定义、命名规范 | 功能 ID、当前步骤、同步源 |
| **Size / 大小** | ~100+ lines | ~30 lines（20+ features） |

---

## 🎯 When to Use / 何时使用

### Use project_manifest.json / 使用项目清单

- ✅ 了解项目整体结构
- ✅ Understanding overall project structure
- ✅ 查找模块定义和依赖关系
- ✅ Finding module definitions and dependencies
- ✅ 查看开发流程定义
- ✅ Viewing development pipeline definition
- ✅ 了解命名规范
- ✅ Understanding naming conventions

### Use roadmap.json / 使用路线图

- ✅ 快速查看所有功能的当前状态
- ✅ Quick view of all features' current status
- ✅ 查找特定功能在哪个步骤
- ✅ Finding which step a specific feature is at
- ✅ 生成进度报告
- ✅ Generating progress reports
- ✅ 检查功能是否被阻塞
- ✅ Checking if features are blocked

---

## 🔍 Example Workflow / 示例工作流

### Scenario: 查看功能 CORE-001 的状态
### Scenario: Check status of feature CORE-001

1. **从 roadmap.json 查找** / **Look up in roadmap.json**
   ```json
   {
     "id": "CORE-001",
     "module_id": "trading",
     "current_step": "spec_defined",
     "sync_source": "docs/modules/trading.json"
   }
   ```

2. **从 manifest 了解模块结构** / **Understand module structure from manifest**
   ```json
   {
     "id": "trading",
     "module_card": "docs/modules/trading.json"
   }
   ```

3. **从 module card 获取详细信息** / **Get detailed info from module card**
   ```json
   {
     "id": "CORE-001",
     "current_step": "spec_defined",
     "artifacts": {
       "spec": "docs/specs/trading/CORE-001.md",
       "story": null,
       "tests": null,
       "code": null
     }
   }
   ```

---

## 📝 Maintenance / 维护

### project_manifest.json

- **维护者** / **Maintainer**: Agent PM
- **更新时机** / **Update when**:
  - 新增模块
  - Adding new modules
  - 修改开发流程
  - Modifying development pipeline
  - 更改命名规范
  - Changing naming conventions

### roadmap.json

- **维护者** / **Maintainer**: Agent PM（通过自动化脚本）
- **更新时机** / **Update when**:
  - 功能推进到新步骤（自动）
  - Feature advances to new step (automatic)
  - 新增功能（需要手动添加指针）
  - Adding new feature (requires manual pointer addition)

---

## ✅ Key Takeaways / 关键要点

1. **manifest = 结构定义** / **manifest = structure definition**
   - 定义"项目是什么" / Defines "what the project is"

2. **roadmap = 状态索引** / **roadmap = status index**
   - 跟踪"功能在哪里" / Tracks "where features are"

3. **module cards = 真相源** / **module cards = source of truth**
   - 存储功能的完整状态 / Stores complete feature states

4. **自动化同步** / **Automated sync**
   - 使用 `advance_feature.py` 保持一致性 / Use `advance_feature.py` to maintain consistency

---

**Last Updated / 最后更新**: 2025-11-30  
**Maintained by / 维护者**: Agent PM

