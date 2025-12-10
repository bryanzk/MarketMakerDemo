# CursorRules Synchronization Guide / CursorRules 同步指南

## Overview / 概述

This document explains how to ensure all Agents read the updated `.cursorrules` file after changes.
本文档说明如何确保所有 Agent 在 `.cursorrules` 更新后都能读取到最新版本。

---

## How CursorRules Works / CursorRules 工作原理

### Automatic Loading Mechanism / 自动加载机制

According to the **Tiered Context Architecture** defined in `.cursorrules`:
根据 `.cursorrules` 中定义的**上下文分层架构**：

1. **Working Context / 工作上下文** (Base Layer)
   - `.cursorrules` is part of the **Base Layer** that is rebuilt before each Agent call
   - `.cursorrules` 是**基础层**的一部分，每次 Agent 调用前会重建
   - System instructions from `.cursorrules` are automatically included
   - 来自 `.cursorrules` 的系统指令会自动包含

2. **Cursor IDE Behavior / Cursor IDE 行为**
   - Cursor IDE automatically loads `.cursorrules` when opening the project
   - Cursor IDE 在打开项目时自动加载 `.cursorrules`
   - Each new chat session will use the current version of `.cursorrules`
   - 每个新的聊天会话都会使用当前版本的 `.cursorrules`

### Context Compilation Process / 上下文编译流程

```
1. Base Layer (基础层)
   ├─ System instructions (.cursorrules relevant sections)
   │  系统指令（.cursorrules 相关章节）
   ├─ Agent identity (docs/agents/AGENT_XXX.md)
   │  Agent 身份（docs/agents/AGENT_XXX.md）
   └─ Current task goal (from user request or status/roadmap.json)
      当前任务目标（从用户请求或 status/roadmap.json）
```

---

## Ensuring All Agents Read Updated CursorRules / 确保所有 Agent 读取更新的 CursorRules

### Method 1: Git Version Control (Recommended) / 方法 1：Git 版本控制（推荐）

**Steps / 步骤：**

1. **Commit `.cursorrules` changes / 提交 `.cursorrules` 更改**
   ```bash
   git add .cursorrules
   git commit -m "docs: update .cursorrules with new rules"
   git push origin <branch-name>
   ```

2. **For other developers / 对于其他开发者**
   - Pull the latest changes: `git pull`
   - 拉取最新更改：`git pull`
   - Restart Cursor IDE or open a new chat session
   - 重启 Cursor IDE 或打开新的聊天会话

3. **For same developer / 对于同一开发者**
   - If `.cursorrules` is already committed and pushed, Cursor IDE should automatically reload
   - 如果 `.cursorrules` 已提交并推送，Cursor IDE 应该自动重新加载
   - If not, restart Cursor IDE or open a new chat session
   - 如果没有，重启 Cursor IDE 或打开新的聊天会话

### Method 2: Explicit Agent Initialization / 方法 2：显式 Agent 初始化

When starting a new Agent session, explicitly reference `.cursorrules`:
启动新的 Agent 会话时，显式引用 `.cursorrules`：

```
Please read .cursorrules to understand the current project rules and agent system.
请阅读 .cursorrules 以了解当前项目规则和 Agent 体系。
```

### Method 3: Version Check / 方法 3：版本检查

Add a version or timestamp to `.cursorrules` to track updates:
在 `.cursorrules` 中添加版本或时间戳以跟踪更新：

```markdown
# MarketMakerDemo Cursor Rules
# 多 Agent 协作开发规范 v2.0
# Last Updated: 2025-01-XX
# 最后更新：2025-01-XX
```

Then, Agents can check this version to confirm they're using the latest rules.
然后，Agent 可以检查此版本以确认它们使用的是最新规则。

---

## Best Practices / 最佳实践

### 1. Always Commit `.cursorrules` Changes / 始终提交 `.cursorrules` 更改

- ✅ Commit `.cursorrules` changes to Git
- ✅ 将 `.cursorrules` 更改提交到 Git
- ✅ Push to remote repository
- ✅ 推送到远程仓库
- ❌ Never keep `.cursorrules` changes only locally
- ❌ 永远不要只在本地保留 `.cursorrules` 更改

### 2. Document Significant Changes / 记录重大更改

When making significant changes to `.cursorrules`:
对 `.cursorrules` 进行重大更改时：

1. Update the version number in the file header
   更新文件头中的版本号
2. Add a commit message explaining the changes
   添加说明更改的提交信息
3. Consider notifying team members (if applicable)
   考虑通知团队成员（如果适用）

### 3. Verify Agent Behavior / 验证 Agent 行为

After updating `.cursorrules`, verify that Agents follow the new rules:
更新 `.cursorrules` 后，验证 Agent 是否遵循新规则：

1. Start a new chat session
   启动新的聊天会话
2. Ask the Agent to confirm it has read `.cursorrules`
   要求 Agent 确认已阅读 `.cursorrules`
3. Test a specific rule to ensure it's being followed
   测试特定规则以确保其被遵循

### 4. Use Git Hooks (Optional) / 使用 Git Hooks（可选）

Create a pre-commit hook to remind developers to commit `.cursorrules`:
创建 pre-commit hook 以提醒开发者提交 `.cursorrules`：

```bash
#!/bin/bash
# .git/hooks/pre-commit

if git diff --cached --name-only | grep -q ".cursorrules"; then
    echo "⚠️  .cursorrules has been modified. Make sure to restart Cursor IDE or open a new chat session after commit."
    echo "⚠️  .cursorrules 已被修改。提交后请确保重启 Cursor IDE 或打开新的聊天会话。"
fi
```

---

## Troubleshooting / 故障排除

### Issue: Agent doesn't follow updated rules / 问题：Agent 不遵循更新的规则

**Possible causes / 可能的原因：**

1. `.cursorrules` changes not committed to Git
   `.cursorrules` 更改未提交到 Git
2. Cursor IDE not restarted after changes
   更改后 Cursor IDE 未重启
3. Using an old chat session (before changes)
   使用旧的聊天会话（更改前）

**Solutions / 解决方案：**

1. ✅ Commit and push `.cursorrules` changes
   ✅ 提交并推送 `.cursorrules` 更改
2. ✅ Restart Cursor IDE or open a new chat session
   ✅ 重启 Cursor IDE 或打开新的聊天会话
3. ✅ Explicitly ask Agent to read `.cursorrules`:
   ✅ 显式要求 Agent 阅读 `.cursorrules`：
   ```
   Please read the latest .cursorrules file to understand the current project rules.
   请阅读最新的 .cursorrules 文件以了解当前项目规则。
   ```

### Issue: Different Agents see different rules / 问题：不同 Agent 看到不同的规则

**Possible causes / 可能的原因：**

1. Different developers have different local versions
   不同开发者有不同的本地版本
2. Not all changes have been pushed to remote
   并非所有更改都已推送到远程

**Solutions / 解决方案：**

1. ✅ Ensure all `.cursorrules` changes are committed and pushed
   ✅ 确保所有 `.cursorrules` 更改都已提交并推送
2. ✅ All developers should pull the latest changes: `git pull`
   ✅ 所有开发者都应拉取最新更改：`git pull`
3. ✅ Verify `.cursorrules` version/timestamp matches across all environments
   ✅ 验证 `.cursorrules` 版本/时间戳在所有环境中匹配

---

## Checklist for Updating CursorRules / 更新 CursorRules 的检查清单

When updating `.cursorrules`, follow this checklist:
更新 `.cursorrules` 时，请遵循此检查清单：

- [ ] Make changes to `.cursorrules`
  - [ ] 对 `.cursorrules` 进行更改
- [ ] Update version number or timestamp (if applicable)
  - [ ] 更新版本号或时间戳（如果适用）
- [ ] Test changes locally (start new chat session)
  - [ ] 在本地测试更改（启动新的聊天会话）
- [ ] Commit changes with descriptive message
  - [ ] 使用描述性消息提交更改
- [ ] Push to remote repository
  - [ ] 推送到远程仓库
- [ ] Verify other developers can see changes (if applicable)
  - [ ] 验证其他开发者可以看到更改（如果适用）
- [ ] Document significant changes (if applicable)
  - [ ] 记录重大更改（如果适用）

---

## Related Documents / 相关文档

- `.cursorrules` - Main configuration file
  - 主配置文件
- `docs/agents/AGENT_XXX.md` - Individual Agent context documents
  - 各个 Agent 的上下文文档
- `README.md` - Project setup and configuration
  - 项目设置和配置

---

## Summary / 总结

**Key Points / 关键点：**

1. **`.cursorrules` is automatically loaded by Cursor IDE**
   **`.cursorrules` 由 Cursor IDE 自动加载**

2. **Always commit `.cursorrules` changes to Git**
   **始终将 `.cursorrules` 更改提交到 Git**

3. **Restart Cursor IDE or open new chat session after updates**
   **更新后重启 Cursor IDE 或打开新的聊天会话**

4. **Verify Agent behavior matches updated rules**
   **验证 Agent 行为与更新的规则匹配**

By following these practices, you can ensure all Agents consistently read and follow the updated `.cursorrules`.
通过遵循这些实践，您可以确保所有 Agent 一致地读取并遵循更新的 `.cursorrules`。



