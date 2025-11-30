# User Stories / 用户故事

This directory contains user stories organized by module.  
此目录包含按模块组织的用户故事。

## Directory Structure / 目录结构

```
docs/stories/
├── trading/              # Trading engine stories / 交易引擎故事
│   ├── US-CORE-001.md    # Exchange connection story
│   ├── US-CORE-002.md    # Order management story
│   └── ...
├── portfolio/            # Portfolio management stories / 组合管理故事
│   ├── US-PORT-001.md    # Capital allocation story
│   └── ...
├── web/                  # Web/API stories / Web/API 故事
│   ├── US-API-001.md     # Bot control API story
│   └── ...
├── ai/                   # AI/LLM stories / AI/LLM 故事
│   ├── US-LLM-001.md     # Multi-LLM evaluation story
│   └── ...
└── qa/                   # QA stories / QA 故事
    ├── US-TEST-001.md    # Test coverage story
    └── ...
```

## User Story Template / 用户故事模板

Each story file should follow this template:  
每个故事文件应遵循此模板：

```markdown
# {STORY_ID}: {Title} / {中文标题}

## User Story / 用户故事

**As a** {role}  
**I want** {feature}  
**So that** {benefit}

**作为** {角色}  
**我希望** {功能}  
**以便** {收益}

## Acceptance Criteria / 验收标准

### AC-1: {Criterion Title}
**Given** {precondition}  
**When** {action}  
**Then** {expected result}

### AC-2: ...

## Technical Notes / 技术备注
...

## Related / 相关
- Spec: {SPEC_LINK}
- Feature: {FEATURE_ID}
- Tests: {TEST_LINK}

## Owner / 负责人
Agent: {AGENT_NAME}
```

## Owner / 负责人

This directory is maintained by **Agent PO**.  
此目录由 **Agent PO** 维护。

