# Scripts Directory / 脚本目录

本目录包含项目自动化脚本。

## 📋 Available Scripts / 可用脚本

### `advance_feature.py` - Feature 推进自动化

**用途 / Purpose:** 自动推进 Feature 到下一个流程节点

**用法 / Usage:**
```bash
# 基础用法
python scripts/advance_feature.py CORE-001 story_defined

# 完整示例（带 PR、分支、作者、备注）
python scripts/advance_feature.py CORE-001 code_implemented \
  --pr "#123" \
  --branch "feature/CORE-001" \
  --author "Agent TRADING" \
  --notes "Implementation complete"

# 预览模式（不实际修改文件）
python scripts/advance_feature.py CORE-001 story_defined --dry-run
```

**功能 / Features:**
- ✅ 自动更新模块 JSON 中的 `current_step`
- ✅ 同步 `status/roadmap.json`
- ✅ 在 `docs/progress/progress_index.json` 添加事件
- ✅ 自动运行 `audit_check.py` 验证

**详细文档:** [Feature Automation Guide](../docs/development_protocol_feature_automation.md)

---

### `batch_advance.py` - 批量 Feature 推进

**用途 / Purpose:** 批量推进多个 Feature

**用法 / Usage:**
```bash
# 从 JSON 文件批量推进
python scripts/batch_advance.py batch_advance.json

# 预览模式
python scripts/batch_advance.py batch_advance.json --dry-run
```

**输入文件格式 / Input Format:**
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
    }
  ]
}
```

---

### `audit_check.py` - 结构化审计检查

**用途 / Purpose:** 验证 JSON 控制平面和 artifact 文件的一致性

**用法 / Usage:**
```bash
python scripts/audit_check.py
```

**检查内容 / Checks:**
- ✅ 模块卡片中的 Feature artifact 文件是否存在
- ✅ `status/roadmap.json` 与模块卡片是否对齐
- ✅ `docs/progress/progress_index.json` 中的事件是否引用有效 Feature

---

## 🔧 Git Hooks / Git 钩子

### `git-hooks/pre-commit-feature-check`

**用途 / Purpose:** 提交前检查是否使用了自动化脚本

**安装 / Install:**
```bash
cp scripts/git-hooks/pre-commit-feature-check .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**功能 / Features:**
- 检测是否修改了治理 JSON 文件
- 提示是否运行了 `advance_feature.py`
- 可选择继续或取消提交

---

## 📚 Related Documentation / 相关文档

- [Feature Automation Guide](../docs/development_protocol_feature_automation.md) - 详细使用指南
- [Development Protocol](../docs/development_protocol.md) - 开发协议
- [Project Manifest](../project_manifest.json) - 项目清单


