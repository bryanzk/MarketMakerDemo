# Feature Advancement Automation / Feature 推进自动化

本文档说明如何使用自动化脚本推进 Feature 到下一个流程节点。

## 📋 Overview / 概览

传统流程需要手动：
1. 修改 `docs/modules/{module}.json` 中的 `current_step`
2. 同步更新 `status/roadmap.json`
3. 在 `docs/progress/progress_index.json` 添加事件
4. 运行 `scripts/audit_check.py` 验证

现在可以通过 `scripts/advance_feature.py` 一键完成。

---

## 🚀 Quick Start / 快速开始

### Basic Usage / 基础用法

```bash
# 将 CORE-001 推进到 story_defined 步骤
python scripts/advance_feature.py CORE-001 story_defined

# 带 PR 和分支信息
python scripts/advance_feature.py CORE-001 code_implemented \
  --pr "#123" \
  --branch "feature/CORE-001" \
  --author "Agent TRADING" \
  --notes "Implementation complete, tests passing"
```

### Dry Run / 预览模式

```bash
# 查看会做什么修改，但不实际写入文件
python scripts/advance_feature.py CORE-001 story_defined --dry-run
```

### Skip Audit / 跳过审计

```bash
# 如果确定没问题，可以跳过审计检查（不推荐）
python scripts/advance_feature.py CORE-001 story_defined --skip-audit
```

---

## 📝 Command Reference / 命令参考

### `advance_feature.py`

```bash
python scripts/advance_feature.py <feature_id> <new_step> [OPTIONS]
```

**Arguments:**
- `feature_id`: Feature ID (e.g., `CORE-001`, `API-002`)
- `new_step`: 新步骤名称（必须是 17 步流程中的一步）

**Options:**
- `--pr <number>`: PR 编号（如 `#123`）
- `--branch <name>`: Git 分支名
- `--author <name>`: 作者（默认：`Agent PM`）
- `--notes <text>`: 额外备注
- `--skip-audit`: 跳过审计检查
- `--dry-run`: 预览模式，不实际修改文件

**Valid Steps / 有效步骤:**
1. `spec_defined`
2. `story_defined`
3. `ac_defined`
4. `contract_defined`
5. `unit_test_written`
6. `code_implemented`
7. `code_reviewed`
8. `unit_test_passed`
9. `smoke_test_passed`
10. `integration_passed`
11. `docs_updated`
12. `progress_logged`
13. `ci_cd_passed`

---

## 🔄 Workflow Examples / 工作流示例

### Example 1: Agent PO 完成用户故事

```bash
# Agent PO 完成 CORE-001 的用户故事
python scripts/advance_feature.py CORE-001 story_defined \
  --author "Agent PO" \
  --notes "User story US-CORE-001 completed with acceptance criteria"
```

### Example 2: Dev Agent 完成代码实现

```bash
# Agent TRADING 完成 CORE-001 的代码实现
python scripts/advance_feature.py CORE-001 code_implemented \
  --pr "#456" \
  --branch "feature/CORE-001-exchange" \
  --author "Agent TRADING" \
  --notes "Exchange client implementation complete, unit tests passing"
```

### Example 3: Agent QA 完成集成测试

```bash
# Agent QA 完成集成测试
python scripts/advance_feature.py CORE-001 integration_passed \
  --pr "#789" \
  --author "Agent QA" \
  --notes "Integration tests passed, coverage 85%"
```

---

## 📦 Batch Operations / 批量操作

使用 `scripts/batch_advance.py` 批量推进多个 Feature。

### Input File Format / 输入文件格式

创建 `batch_advance.json`:

```json
{
  "advancements": [
    {
      "feature_id": "CORE-001",
      "new_step": "story_defined",
      "pr": "#123",
      "branch": "feature/CORE-001",
      "author": "Agent PO",
      "notes": "User story completed"
    },
    {
      "feature_id": "CORE-002",
      "new_step": "code_implemented",
      "pr": "#124",
      "branch": "feature/CORE-002",
      "author": "Agent TRADING",
      "notes": "Implementation complete"
    }
  ]
}
```

### Run Batch / 运行批量操作

```bash
python scripts/batch_advance.py batch_advance.json

# 预览模式
python scripts/batch_advance.py batch_advance.json --dry-run
```

---

## 🔗 Git Integration / Git 集成

### Pre-commit Hook / 提交前检查

安装 Git hook 以在提交前检查是否使用了自动化脚本：

```bash
# 复制 hook 到 .git/hooks/
cp scripts/git-hooks/pre-commit-feature-check .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

Hook 会检查：
- 如果修改了治理 JSON 文件（`docs/modules/*.json`, `status/roadmap.json`, `docs/progress/progress_index.json`）
- 提示是否运行了 `advance_feature.py`
- 可以选择继续或取消提交

### Commit Message Template / 提交信息模板

建议的 commit message 格式：

```
feat(trading): CORE-001 advance to code_implemented

- Updated module JSON: current_step → code_implemented
- Synced roadmap.json
- Added progress event E-2025-0002
- PR: #123, Branch: feature/CORE-001

Run: python scripts/advance_feature.py CORE-001 code_implemented --pr "#123" --branch "feature/CORE-001"
```

---

## 🔍 What the Script Does / 脚本做了什么

1. **验证输入**
   - 检查 `feature_id` 是否存在于模块卡片中
   - 验证 `new_step` 是否为有效步骤

2. **更新模块 JSON**
   - 在 `docs/modules/{module}.json` 中找到对应 Feature
   - 更新 `current_step` 字段
   - 更新 `last_updated` 时间戳

3. **同步 Roadmap**
   - 在 `status/roadmap.json` 中更新对应 Feature 的 `current_step`
   - 如果不存在则添加新条目

4. **添加进度事件**
   - 在 `docs/progress/progress_index.json` 中生成新事件
   - 事件 ID 格式：`E-YYYY-NNNN`
   - 包含 Feature ID、模块、步骤、作者、时间戳等信息

5. **运行审计检查**
   - 自动运行 `scripts/audit_check.py`
   - 验证所有 JSON 文件一致性
   - 检查 artifact 文件是否存在

---

## ⚠️ Best Practices / 最佳实践

1. **总是使用脚本**
   - 不要手动修改治理 JSON 文件
   - 使用脚本确保一致性

2. **提供完整信息**
   - 尽量提供 `--pr`、`--branch`、`--notes` 等信息
   - 方便后续追踪和审计

3. **运行审计检查**
   - 不要使用 `--skip-audit`，除非确定没问题
   - 审计检查可以发现遗漏的 artifact 文件

4. **提交前验证**
   - 使用 `--dry-run` 预览修改
   - 确认无误后再实际执行

5. **批量操作时**
   - 先测试单个 Feature
   - 确认流程正确后再批量处理

---

## 🐛 Troubleshooting / 故障排除

### Error: Feature not found

```
❌ Feature CORE-001 not found in any module card
```

**Solution:** 检查 Feature ID 是否正确，或先在模块 JSON 中添加该 Feature。

### Error: Invalid step

```
❌ Invalid step: invalid_step_name
```

**Solution:** 检查步骤名称是否在 17 步流程中。使用 `--help` 查看有效步骤列表。

### Error: Audit check failed

```
⚠️  Audit check failed. Please review the issues above.
```

**Solution:** 查看审计输出，通常是因为缺少 artifact 文件（spec、test、code 等）。补充缺失文件后重试。

### Error: Module card not found

```
❌ Module card not found: docs/modules/trading.json
```

**Solution:** 确保模块 JSON 文件存在。如果不存在，需要先创建模块卡片。

---

## 📚 Related Documentation / 相关文档

- [Development Protocol](development_protocol.md) - 开发协议
- [Project Manifest](../project_manifest.json) - 项目清单
- [Audit Check Script](../scripts/audit_check.py) - 审计检查脚本

---

## 💡 Future Enhancements / 未来增强

计划中的功能：
- [ ] CI/CD 集成：PR 合并时自动推进 Feature
- [ ] Web UI：可视化 Feature 状态和推进流程
- [ ] Slack/Email 通知：Feature 状态变更时通知相关 Agent
- [ ] 自动生成 PR 描述：基于 Feature 信息生成 PR 模板



