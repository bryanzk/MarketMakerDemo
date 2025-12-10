# CursorRules Pre-Thinking Enhancement Patch / CursorRules 思维前置增强补丁

## Overview / 概述

This document provides the exact patch to add the Pre-Thinking Mandatory Checklist to `.cursorrules`.

本文档提供将思维前置强制性检查清单添加到 `.cursorrules` 的确切补丁。

---

## 📝 Patch Instructions / 补丁说明

### Location / 位置

Insert the new Section 1.0 **before** the existing Section 1.1 in `.cursorrules`.

在 `.cursorrules` 中，在现有第 1.1 节**之前**插入新的第 1.0 节。

### Current Structure / 当前结构

```markdown
## 1 · 总体推理与规划框架 / Overall Reasoning and Planning Framework

在进行任何操作前（包括：回复用户、调用工具或给出代码），你必须先在内部完成如下推理与规划。这些推理过程 **只在你内部进行**，不需要显式输出思维步骤，除非用户明确要求展示。

### 1.1 依赖关系与约束优先级 / Dependency and Constraint Priority
...
```

### New Structure / 新结构

```markdown
## 1 · 总体推理与规划框架 / Overall Reasoning and Planning Framework

在进行任何操作前（包括：回复用户、调用工具或给出代码），你必须先在内部完成如下推理与规划。

**重要更新 / Important Update**: 从本节开始，所有 Agent 必须完成 **1.0 思维前置强制性检查清单**。对于 moderate/complex 任务，必须显式输出思维前置摘要。

**Important Update**: Starting from this section, all Agents must complete the **1.0 Pre-Thinking Mandatory Checklist**. For moderate/complex tasks, an explicit pre-thinking summary is required.

### 1.0 Pre-Thinking Mandatory Checklist / 思维前置强制性检查清单

**CRITICAL / 关键**: Before providing any response, code, or taking any action, you MUST complete ALL items in this checklist. This is a MANDATORY step that cannot be skipped.

**关键**: 在提供任何回复、代码或采取任何行动之前，你必须完成此检查清单中的所有项目。这是一个强制性步骤，不能跳过。

#### ✅ Step 1: Task Classification / 任务分类
- [ ] Determine task complexity: **trivial** / **moderate** / **complex**
- [ ] Identify task type: bug fix / feature / refactor / documentation / other
- [ ] Check if task belongs to my responsibility (Agent role check from Section "⚠️ Agent 职责确认规则")
- [ ] Verify current step in `status/roadmap.json` (if applicable)

#### ✅ Step 2: Constraint Analysis / 约束分析
- [ ] List all explicit rules and constraints from `.cursorrules` (especially Section 1.1-1.9)
- [ ] Identify module/file ownership constraints (from "📁 文件归属矩阵")
- [ ] Check for any "DO NOT" or "PROHIBITED" rules (from "🚫 禁止操作")
- [ ] Verify language/style requirements (Chinese/English, PEP 8, etc. from Section 4)

#### ✅ Step 3: Risk Assessment / 风险评估
- [ ] Identify potential data loss or irreversible changes (Section 1.2)
- [ ] Check for API/interface breaking changes
- [ ] Assess impact on other modules/agents
- [ ] Determine if operation is reversible
- [ ] For high-risk operations, prepare explicit risk warning

#### ✅ Step 4: Information Gathering / 信息收集
- [ ] **MANDATORY**: Read relevant files before proposing changes (Section 5.2 Plan 模式规则)
- [ ] Check existing code patterns and conventions
- [ ] Review related documentation (contracts, specs, stories)
- [ ] Gather context from session history if needed
- [ ] Use codebase_search or grep to find related code

#### ✅ Step 5: Hypothesis Formation / 假设形成 (if applicable)
- [ ] For problem-solving tasks: Form 1-3 hypotheses about the problem (Section 1.3)
- [ ] Rank hypotheses by probability
- [ ] Identify what information is needed to validate hypotheses
- [ ] Plan hypothesis validation approach

#### ✅ Step 6: Solution Design / 方案设计
- [ ] Design solution considering all constraints from Step 2
- [ ] Consider alternative approaches (Section 1.7)
- [ ] Identify implementation steps
- [ ] Plan verification strategy (tests, manual checks, etc.)
- [ ] For moderate/complex tasks: Determine if Plan/Code mode is needed (Section 5)

#### ✅ Step 7: Self-Check / 自检
- [ ] Verify all constraints are satisfied (Section 1.4)
- [ ] Check for contradictions or omissions
- [ ] Ensure solution aligns with user's "Slow is Fast" philosophy (Section 0)
- [ ] Confirm no prohibited operations are planned (Section "🚫 禁止操作")
- [ ] Verify solution follows conflict resolution priority (Section 1.7)

### Output Format Based on Complexity / 基于复杂度的输出格式

**For Trivial Tasks / 对于简单任务**:
- Complete checklist internally (no explicit output)
- Proceed directly to response
- No pre-thinking summary required

**For Moderate/Complex Tasks / 对于中等/复杂任务**:
- Complete checklist internally
- **MUST output a Pre-Thinking Summary** before the main response, using this format:

```markdown
## Pre-Thinking Summary / 思维前置摘要

**Task Classification / 任务分类**: [trivial/moderate/complex]
**Task Type / 任务类型**: [bug fix/feature/refactor/documentation/other]
**Agent Responsibility / Agent 职责**: [Confirmed/Not My Responsibility - if not, suggest correct agent]
**Key Constraints / 关键约束**: 
  1. [Top constraint 1]
  2. [Top constraint 2]
  3. [Top constraint 3]
**Risk Level / 风险级别**: [low/medium/high]
**Information Gathered / 已收集信息**: 
  - Files read: [list key files]
  - Context reviewed: [specs/contracts/stories/documentation]
  - Code patterns checked: [existing patterns reviewed]
**Solution Approach / 方案方法**: [Brief description of approach]
**Next Steps / 下一步**: [Plan mode / Code mode / Direct implementation]
```

Then proceed with Plan/Code mode as appropriate (Section 5).

### 1.1 依赖关系与约束优先级 / Dependency and Constraint Priority
...
```

---

## 🔄 Complete Section 1 Replacement / 完整第 1 节替换

Here is the complete replacement for Section 1, incorporating the new checklist:

以下是第 1 节的完整替换，包含新检查清单：

```markdown
## 1 · 总体推理与规划框架 / Overall Reasoning and Planning Framework

在进行任何操作前（包括：回复用户、调用工具或给出代码），你必须先在内部完成如下推理与规划。

**重要更新 / Important Update**: 从本节开始，所有 Agent 必须完成 **1.0 思维前置强制性检查清单**。对于 moderate/complex 任务，必须显式输出思维前置摘要。

**Important Update**: Starting from this section, all Agents must complete the **1.0 Pre-Thinking Mandatory Checklist**. For moderate/complex tasks, an explicit pre-thinking summary is required.

### 1.0 Pre-Thinking Mandatory Checklist / 思维前置强制性检查清单

**CRITICAL / 关键**: Before providing any response, code, or taking any action, you MUST complete ALL items in this checklist. This is a MANDATORY step that cannot be skipped.

**关键**: 在提供任何回复、代码或采取任何行动之前，你必须完成此检查清单中的所有项目。这是一个强制性步骤，不能跳过。

#### ✅ Step 1: Task Classification / 任务分类
- [ ] Determine task complexity: **trivial** / **moderate** / **complex** (see Section 2)
- [ ] Identify task type: bug fix / feature / refactor / documentation / other
- [ ] Check if task belongs to my responsibility (Agent role check from Section "⚠️ Agent 职责确认规则")
- [ ] Verify current step in `status/roadmap.json` (if applicable)

#### ✅ Step 2: Constraint Analysis / 约束分析
- [ ] List all explicit rules and constraints from `.cursorrules` (especially Section 1.1-1.9)
- [ ] Identify module/file ownership constraints (from "📁 文件归属矩阵")
- [ ] Check for any "DO NOT" or "PROHIBITED" rules (from "🚫 禁止操作")
- [ ] Verify language/style requirements (Chinese/English, PEP 8, etc. from Section 4)

#### ✅ Step 3: Risk Assessment / 风险评估
- [ ] Identify potential data loss or irreversible changes (Section 1.2)
- [ ] Check for API/interface breaking changes
- [ ] Assess impact on other modules/agents
- [ ] Determine if operation is reversible
- [ ] For high-risk operations, prepare explicit risk warning

#### ✅ Step 4: Information Gathering / 信息收集
- [ ] **MANDATORY**: Read relevant files before proposing changes (Section 5.2 Plan 模式规则)
- [ ] Check existing code patterns and conventions
- [ ] Review related documentation (contracts, specs, stories)
- [ ] Gather context from session history if needed
- [ ] Use codebase_search or grep to find related code

#### ✅ Step 5: Hypothesis Formation / 假设形成 (if applicable)
- [ ] For problem-solving tasks: Form 1-3 hypotheses about the problem (Section 1.3)
- [ ] Rank hypotheses by probability
- [ ] Identify what information is needed to validate hypotheses
- [ ] Plan hypothesis validation approach

#### ✅ Step 6: Solution Design / 方案设计
- [ ] Design solution considering all constraints from Step 2
- [ ] Consider alternative approaches (Section 1.7)
- [ ] Identify implementation steps
- [ ] Plan verification strategy (tests, manual checks, etc.)
- [ ] For moderate/complex tasks: Determine if Plan/Code mode is needed (Section 5)

#### ✅ Step 7: Self-Check / 自检
- [ ] Verify all constraints are satisfied (Section 1.4)
- [ ] Check for contradictions or omissions
- [ ] Ensure solution aligns with user's "Slow is Fast" philosophy (Section 0)
- [ ] Confirm no prohibited operations are planned (Section "🚫 禁止操作")
- [ ] Verify solution follows conflict resolution priority (Section 1.7)

### Output Format Based on Complexity / 基于复杂度的输出格式

**For Trivial Tasks / 对于简单任务**:
- Complete checklist internally (no explicit output)
- Proceed directly to response
- No pre-thinking summary required

**For Moderate/Complex Tasks / 对于中等/复杂任务**:
- Complete checklist internally
- **MUST output a Pre-Thinking Summary** before the main response, using this format:

```markdown
## Pre-Thinking Summary / 思维前置摘要

**Task Classification / 任务分类**: [trivial/moderate/complex]
**Task Type / 任务类型**: [bug fix/feature/refactor/documentation/other]
**Agent Responsibility / Agent 职责**: [Confirmed/Not My Responsibility - if not, suggest correct agent]
**Key Constraints / 关键约束**: 
  1. [Top constraint 1]
  2. [Top constraint 2]
  3. [Top constraint 3]
**Risk Level / 风险级别**: [low/medium/high]
**Information Gathered / 已收集信息**: 
  - Files read: [list key files]
  - Context reviewed: [specs/contracts/stories/documentation]
  - Code patterns checked: [existing patterns reviewed]
**Solution Approach / 方案方法**: [Brief description of approach]
**Next Steps / 下一步**: [Plan mode / Code mode / Direct implementation]
```

Then proceed with Plan/Code mode as appropriate (Section 5).

### 1.1 依赖关系与约束优先级 / Dependency and Constraint Priority

按以下优先级分析当前任务：

1. **规则与约束**（最高优先）
   - 所有显式给定的规则、策略、硬性约束（例如语言/库版本、禁止操作、性能上限等）
   - 不得为了"省事"而违反这些约束

2. **操作顺序与可逆性**
   - 分析任务的自然依赖顺序，确保某一步不会阻碍后续必要步骤
   - 即使用户按随机顺序提需求，你也可以在内部重新排序步骤以保证整体任务可完成

3. **前置条件与缺失信息**
   - 判断当前是否已有足够信息推进
   - 仅当缺失信息会 **显著影响方案选择或正确性** 时，再向用户提问澄清

4. **用户偏好**
   - 在不违背上述更高优先级的前提下，尽量满足用户偏好（语言选择、风格偏好等）

[... rest of Section 1.1-1.9 remains unchanged ...]
```

---

## 📋 Implementation Checklist / 实施检查清单

- [ ] Backup current `.cursorrules` file
- [ ] Insert Section 1.0 before Section 1.1
- [ ] Update Section 1 introduction to reference 1.0
- [ ] Verify all cross-references are correct
- [ ] Test with a trivial task (should work internally)
- [ ] Test with a moderate task (should show pre-thinking summary)
- [ ] Test with a complex task (should show pre-thinking summary + Plan/Code mode)
- [ ] Update agent-specific docs if needed

---

## 🎯 Key Benefits / 关键收益

1. **Mandatory Process / 强制性流程**: Every agent must complete the checklist
2. **Adaptive Output / 自适应输出**: Trivial tasks remain efficient
3. **Transparency / 透明度**: Complex tasks show explicit reasoning
4. **Consistency / 一致性**: All agents follow the same structured process
5. **Quality / 质量**: Reduces errors and oversights

---

**Document Status / 文档状态**: Implementation Guide / 实施指南  
**Last Updated / 最后更新**: 2025-12-09

