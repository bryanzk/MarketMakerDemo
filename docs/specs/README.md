# Specifications / 规格说明

This directory contains feature specifications organized by module.  
此目录包含按模块组织的功能规格说明。

## Directory Structure / 目录结构

```
docs/specs/
├── trading/          # Trading engine specs / 交易引擎规格
│   ├── CORE-001.md   # Exchange connection
│   ├── CORE-002.md   # Order management
│   └── ...
├── portfolio/        # Portfolio management specs / 组合管理规格
│   ├── PORT-001.md   # Capital allocation
│   └── ...
├── web/              # Web/API specs / Web/API 规格
│   ├── API-001.md    # Bot control API
│   └── ...
├── ai/               # AI/LLM specs / AI/LLM 规格
│   ├── LLM-001.md    # Multi-LLM evaluation
│   └── ...
└── qa/               # QA specs / QA 规格
    ├── TEST-001.md   # Test coverage
    └── ...
```

## Spec Template / 规格模板

Each spec file should follow this template:  
每个规格文件应遵循此模板：

```markdown
# {FEATURE_ID}: {Title} / {中文标题}

## Overview / 概述
Brief description of the feature.
功能简述。

## Requirements / 需求
- REQ-1: ...
- REQ-2: ...

## Acceptance Criteria / 验收标准
- [ ] AC-1: ...
- [ ] AC-2: ...

## Technical Design / 技术设计
...

## Dependencies / 依赖
- Depends on: {FEATURE_IDs}
- Blocks: {FEATURE_IDs}

## Owner / 负责人
Agent: {AGENT_NAME}
```

## Owner / 负责人

This directory is maintained by **Agent PO**.  
此目录由 **Agent PO** 维护。


