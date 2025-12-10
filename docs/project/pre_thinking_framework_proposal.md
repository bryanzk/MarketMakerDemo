# Pre-Thinking Framework Proposal / 思维前置框架提案

## Overview / 概述

This document proposes enhancements to `.cursorrules` to ensure all agents follow a structured pre-thinking process before providing feedback or taking action.

本文档提出对 `.cursorrules` 的增强，确保所有 agent 在提供反馈或采取行动前都遵循结构化的思维前置过程。

**Proposed by / 提案人**: Cursor Expert Panel / Cursor 专家小组  
**Date / 日期**: 2025-12-09

---

## 🎯 Problem Statement / 问题陈述

### Current State / 当前状态

The existing `.cursorrules` Section 1 defines a reasoning framework, but:
现有的 `.cursorrules` 第 1 章定义了推理框架，但：

1. **Lack of Enforcement / 缺乏强制性**
   - Reasoning is "internal only" with no explicit checkpoint
   - 推理过程"仅内部进行"，没有明确的检查点
   - No verification that all steps are completed
   - 没有验证所有步骤是否完成

2. **No Structured Entry Point / 没有结构化入口**
   - Agents may skip or partially complete reasoning steps
   - Agent 可能跳过或部分完成推理步骤
   - No clear "pre-thinking checklist" before action
   - 行动前没有明确的"思维前置检查清单"

3. **Inconsistent Application / 应用不一致**
   - Different agents may interpret the framework differently
   - 不同 agent 可能对框架有不同的理解
   - No standardized format for complex tasks
   - 复杂任务没有标准化格式

### Desired State / 期望状态

Every agent should:
每个 agent 应该：

1. **Mandatory Pre-Thinking / 强制性思维前置**
   - Complete a structured checklist before any response
   - 在任何回复前完成结构化检查清单
   - Explicitly verify completion of reasoning steps
   - 明确验证推理步骤的完成

2. **Adaptive Output / 自适应输出**
   - For trivial tasks: Internal only (current behavior)
   - 对于简单任务：仅内部进行（当前行为）
   - For moderate/complex tasks: Explicit pre-thinking summary
   - 对于中等/复杂任务：显式思维前置摘要

3. **Consistent Format / 一致格式**
   - Standardized pre-thinking template
   - 标准化的思维前置模板
   - Clear integration with Plan/Code modes
   - 与 Plan/Code 模式清晰整合

---

## 💡 Proposed Solution / 提案方案

### Solution Architecture / 方案架构

```
┌─────────────────────────────────────────┐
│  User Request / 用户请求                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Pre-Thinking Phase / 思维前置阶段     │
│  (MANDATORY / 强制性)                   │
│                                         │
│  1. Task Classification / 任务分类      │
│  2. Constraint Analysis / 约束分析      │
│  3. Risk Assessment / 风险评估          │
│  4. Information Gathering / 信息收集   │
│  5. Hypothesis Formation / 假设形成    │
│  6. Solution Design / 方案设计         │
│  7. Self-Check / 自检                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Output Decision / 输出决策             │
│                                         │
│  Trivial → Internal Only / 仅内部      │
│  Moderate/Complex → Explicit Summary   │
│  中等/复杂 → 显式摘要                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Response / 回复                        │
└─────────────────────────────────────────┘
```

---

## 📋 Detailed Proposal / 详细提案

### 1. Enhanced Pre-Thinking Checklist / 增强的思维前置检查清单

Add a new section **1.0 Pre-Thinking Mandatory Checklist** before Section 1.1:

在第 1.1 节之前添加新章节 **1.0 思维前置强制性检查清单**：

```markdown
## 1.0 Pre-Thinking Mandatory Checklist / 思维前置强制性检查清单

**CRITICAL / 关键**: Before providing any response, code, or taking any action, 
you MUST complete ALL items in this checklist. This is a MANDATORY step that 
cannot be skipped.

**关键**: 在提供任何回复、代码或采取任何行动之前，你必须完成此检查清单中的
所有项目。这是一个强制性步骤，不能跳过。

### Checklist Items / 检查清单项目

#### ✅ Step 1: Task Classification / 任务分类
- [ ] Determine task complexity: trivial / moderate / complex
- [ ] Identify task type: bug fix / feature / refactor / documentation / other
- [ ] Check if task belongs to my responsibility (Agent role check)
- [ ] Verify current step in roadmap (if applicable)

#### ✅ Step 2: Constraint Analysis / 约束分析
- [ ] List all explicit rules and constraints from `.cursorrules`
- [ ] Identify module/file ownership constraints
- [ ] Check for any "DO NOT" or "PROHIBITED" rules
- [ ] Verify language/style requirements (Chinese/English, PEP 8, etc.)

#### ✅ Step 3: Risk Assessment / 风险评估
- [ ] Identify potential data loss or irreversible changes
- [ ] Check for API/interface breaking changes
- [ ] Assess impact on other modules/agents
- [ ] Determine if operation is reversible

#### ✅ Step 4: Information Gathering / 信息收集
- [ ] Read relevant files before proposing changes (MANDATORY)
- [ ] Check existing code patterns and conventions
- [ ] Review related documentation
- [ ] Gather context from session history if needed

#### ✅ Step 5: Hypothesis Formation / 假设形成
- [ ] Form 1-3 hypotheses about the problem (if applicable)
- [ ] Rank hypotheses by probability
- [ ] Identify what information is needed to validate hypotheses

#### ✅ Step 6: Solution Design / 方案设计
- [ ] Design solution considering all constraints
- [ ] Consider alternative approaches
- [ ] Identify implementation steps
- [ ] Plan verification strategy

#### ✅ Step 7: Self-Check / 自检
- [ ] Verify all constraints are satisfied
- [ ] Check for contradictions or omissions
- [ ] Ensure solution aligns with user's "Slow is Fast" philosophy
- [ ] Confirm no prohibited operations are planned

### Output Format Based on Complexity / 基于复杂度的输出格式

**For Trivial Tasks / 对于简单任务**:
- Complete checklist internally
- No explicit output required
- Proceed directly to response

**For Moderate/Complex Tasks / 对于中等/复杂任务**:
- Complete checklist internally
- **MUST output a Pre-Thinking Summary** before the main response:
  ```
  ## Pre-Thinking Summary / 思维前置摘要
  
  **Task Classification / 任务分类**: [trivial/moderate/complex]
  **Task Type / 任务类型**: [bug fix/feature/refactor/etc.]
  **Key Constraints / 关键约束**: [list top 3 constraints]
  **Risk Level / 风险级别**: [low/medium/high]
  **Information Gathered / 已收集信息**: [files read, context reviewed]
  **Solution Approach / 方案方法**: [brief approach description]
  ```
- Then proceed with Plan/Code mode as appropriate
```

### 2. Integration with Existing Framework / 与现有框架整合

The new checklist **enhances** rather than replaces Section 1.1-1.9:
新检查清单**增强**而非替换第 1.1-1.9 节：

- **Section 1.0**: Mandatory checklist (NEW)
- **Section 1.1-1.9**: Detailed reasoning framework (EXISTING, enhanced)

**Relationship / 关系**:
- Section 1.0 provides the **structure** and **enforcement**
- Section 1.1-1.9 provides the **depth** and **methodology**
- Together they ensure comprehensive pre-thinking

### 3. Agent-Specific Considerations / Agent 特定考虑

Each agent type may have additional pre-thinking steps:
每种 agent 类型可能有额外的思维前置步骤：

**Agent PO / 产品负责人**:
- Check if spec/story/AC already exists
- Verify against business requirements
- Ensure acceptance criteria are testable

**Agent ARCH / 架构师**:
- Verify interface compatibility
- Check for breaking changes
- Ensure contract compliance

**Dev Agents / 开发 Agent**:
- Check if tests exist (TDD requirement)
- Verify contract compliance
- Ensure code follows module conventions

**Agent REVIEW / 审查 Agent**:
- Review against code quality standards
- Check for security issues
- Verify test coverage

**Agent QA / 质量保证 Agent**:
- Verify all AC are covered
- Check test completeness
- Ensure documentation is updated

---

## 🔄 Implementation Plan / 实施计划

### Phase 1: Add Pre-Thinking Checklist / 阶段 1：添加思维前置检查清单

**Changes to `.cursorrules`**:

1. Insert new Section 1.0 before Section 1.1
2. Update Section 1 introduction to reference 1.0
3. Add output format requirements based on complexity

**Expected Impact / 预期影响**:
- All agents must complete checklist before action
- Moderate/complex tasks will show explicit pre-thinking summary
- Trivial tasks remain efficient (internal only)

### Phase 2: Enhance Agent-Specific Guidelines / 阶段 2：增强 Agent 特定指南

**Changes to `docs/agents/AGENT_XXX.md`**:

1. Add agent-specific pre-thinking steps
2. Provide examples of pre-thinking summaries
3. Link back to `.cursorrules` Section 1.0

**Expected Impact / 预期影响**:
- Each agent has tailored pre-thinking process
- Better alignment with agent responsibilities
- More consistent output quality

### Phase 3: Validation and Refinement / 阶段 3：验证与完善

**Activities / 活动**:
1. Test with various task types
2. Collect feedback from agent usage
3. Refine checklist items based on real-world usage
4. Update documentation

**Expected Impact / 预期影响**:
- Optimized checklist based on actual needs
- Reduced unnecessary steps
- Improved agent efficiency

---

## 📊 Expected Benefits / 预期收益

### 1. Quality Improvement / 质量提升

- **Consistency / 一致性**: All agents follow the same structured process
- **Completeness / 完整性**: Mandatory checklist ensures nothing is missed
- **Accuracy / 准确性**: Pre-thinking reduces errors and oversights

### 2. Transparency / 透明度

- **Moderate/Complex Tasks / 中等/复杂任务**: Explicit pre-thinking summary shows reasoning
- **Traceability / 可追溯性**: Clear documentation of decision-making process
- **Debugging / 调试**: Easier to identify where reasoning went wrong

### 3. Efficiency / 效率

- **Trivial Tasks / 简单任务**: No overhead, remains internal
- **Complex Tasks / 复杂任务**: Structured approach reduces back-and-forth
- **Error Prevention / 错误预防**: Catch issues before implementation

### 4. Agent Alignment / Agent 对齐

- **Standardized Process / 标准化流程**: All agents use the same framework
- **Role Clarity / 角色清晰**: Agent-specific steps clarify responsibilities
- **Collaboration / 协作**: Consistent format improves cross-agent communication

---

## ⚠️ Potential Concerns / 潜在担忧

### Concern 1: Overhead for Trivial Tasks / 担忧 1：简单任务的开销

**Mitigation / 缓解措施**:
- Trivial tasks remain internal (no explicit output)
- Checklist is lightweight for simple tasks
- Benefits outweigh costs for complex tasks

### Concern 2: Checklist Fatigue / 担忧 2：检查清单疲劳

**Mitigation / 缓解措施**:
- Checklist becomes second nature with practice
- Focus on quality over speed (aligns with "Slow is Fast")
- Can be optimized based on usage patterns

### Concern 3: Rigidity / 担忧 3：僵化

**Mitigation / 缓解措施**:
- Checklist is a guide, not a straitjacket
- Agents can adapt based on context
- Framework evolves based on feedback

---

## 🎯 Success Metrics / 成功指标

### Quantitative / 定量指标

- **Error Rate / 错误率**: Reduction in bugs and rework
- **Response Quality / 响应质量**: Fewer follow-up questions
- **Task Completion / 任务完成**: Higher first-time success rate

### Qualitative / 定性指标

- **Agent Consistency / Agent 一致性**: More uniform output quality
- **User Satisfaction / 用户满意度**: Better alignment with expectations
- **Code Quality / 代码质量**: Improved maintainability and clarity

---

## 📝 Example Implementation / 实施示例

### Example 1: Trivial Task / 示例 1：简单任务

**User Request / 用户请求**: "Fix typo in README.md"

**Pre-Thinking (Internal) / 思维前置（内部）**:
- ✅ Task: trivial (typo fix)
- ✅ Constraint: English code/comments, Chinese docs
- ✅ Risk: low (text change only)
- ✅ Info: Read README.md, find typo
- ✅ Solution: Direct fix

**Response / 回复**: (Direct fix, no explicit pre-thinking summary)

### Example 2: Complex Task / 示例 2：复杂任务

**User Request / 用户请求**: "Add new LLM provider support"

**Pre-Thinking Summary (Explicit) / 思维前置摘要（显式）**:

```markdown
## Pre-Thinking Summary / 思维前置摘要

**Task Classification / 任务分类**: complex
**Task Type / 任务类型**: feature
**Key Constraints / 关键约束**:
  1. Must follow existing LLM provider pattern (src/ai/llm.py)
  2. Must update contracts/ai.json if API changes
  3. Must add tests (TDD requirement)
**Risk Level / 风险级别**: medium
  - Breaking change risk if API contract modified
  - Need to ensure backward compatibility
**Information Gathered / 已收集信息**:
  - Read src/ai/llm.py (existing provider implementations)
  - Read contracts/ai.json (current API contract)
  - Reviewed docs/agents/AGENT_AI.md (AI agent responsibilities)
**Solution Approach / 方案方法**:
  1. Create new Provider class following existing pattern
  2. Update get_llm_client() to support new provider
  3. Add provider to get_provider_availability()
  4. Write unit tests first (TDD)
  5. Update documentation
```

**Response / 回复**: (Then proceed with Plan/Code mode)

---

## 🔗 Related Documents / 相关文档

- `.cursorrules` - Main rules file
- `docs/agents/AGENT_XXX.md` - Agent-specific guidelines
- `docs/project/cursorrules_sync.md` - CursorRules synchronization guide

---

## 📅 Next Steps / 下一步

1. **Review / 审查**: Review this proposal with the team
2. **Refine / 完善**: Incorporate feedback and refine checklist
3. **Implement / 实施**: Update `.cursorrules` with Section 1.0
4. **Test / 测试**: Test with various agents and task types
5. **Iterate / 迭代**: Refine based on real-world usage

---

**Document Status / 文档状态**: Proposal / 提案  
**Last Updated / 最后更新**: 2025-12-09

