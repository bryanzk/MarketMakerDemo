---
name: update-cursorrules-guidance
overview: 更新 .cursorrules 以纳入用户提供的工作方式与质量准则
todos:
  - id: backup-cursorrules
    content: 备份并审阅当前 .cursorrules
    status: completed
  - id: merge-rules
    content: 合并新增 Plan/Code、语言、风险、禁令规则
    status: completed
    dependencies:
      - backup-cursorrules
  - id: structure-check
    content: 自检冲突和条理性
    status: completed
    dependencies:
      - merge-rules
  - id: note-changes
    content: 记录关键变更说明
    status: completed
    dependencies:
      - structure-check
---

# 更新 .cursorrules 计划

## 目标 / Goal

在 `.cursorrules` 中加入用户提供的角色定位与工作方式约束，确保后续协作遵循“Slow is Fast”、高质量推理规划、Plan/Code 工作流、语言与风格规范。

## 步骤 / Steps

1. **备份与审阅 / Backup & Review**  

- 备份现有 `.cursorrules` 内容，快速审阅当前规则结构与章节。

2. **合并新增规则 / Merge New Rules**  

- 在角色/工作模式章节增加：Agent PM 角色说明、Plan/Code 工作流要求、风险与依赖优先级、问答策略。  
- 在语言/风格章节增加：中文说明、英文代码与注释、命名规范（PEP8 等）、测试要求。  
- 在行为准则章节增加：避免无谓澄清、优先一次到位、低风险直接推进，高风险提示风险。  
- 在禁令/限制章节补充：禁止破坏性操作（reset --hard 等）、避免重写历史，遵循“Slow is Fast”。

3. **结构化与示例 / Structure & Examples**  

- 保持与现有 `.cursorrules` 章节风格一致，按条目列出，避免冗长。  
- 必要时添加简短示例（如 Plan/Code 模式触发条件）。

4. **自检 / Self-check**  

- 确认无冲突重复条款，语言一致；确保不会与现有专有规则相矛盾。  
- 保持最小修改面，避免影响其他代理约束。

5. **变更说明 / Change Note**  

- 在提交信息或变更说明中总结新增的关键约束（Plan/Code、语言风格、风险提示、禁止破坏性命令）。