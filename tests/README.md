# Tests Documentation / 测试文档

## Overview / 概述

This directory contains the complete test suite organized by test type and module.  
此目录包含按测试类型和模块组织的完整测试套件。

## Directory Structure / 目录结构

```
tests/
├── unit/              # Unit tests organized by module / 按模块组织的单元测试
│   ├── ai/           # AI/LLM module tests / AI/LLM 模块测试
│   ├── portfolio/    # Portfolio management tests / 组合管理测试
│   ├── trading/      # Trading engine tests / 交易引擎测试
│   ├── web/          # Web/API tests / Web/API 测试
│   └── shared/       # Shared utilities tests / 共享工具测试
├── integration/      # Integration tests / 集成测试
├── smoke/            # Smoke tests / 冒烟测试
├── contract/         # Contract tests / 契约测试
└── e2e/              # End-to-end tests / 端到端测试
```

## Test Categories / 测试类别

### Unit Tests / 单元测试 (`tests/unit/`)

Unit tests for individual modules and components.  
单个模块和组件的单元测试。

- **AI Module** (`tests/unit/ai/`): LLM providers, agents, evaluation
- **Portfolio Module** (`tests/unit/portfolio/`): Portfolio management, risk indicators, metrics
- **Trading Module** (`tests/unit/trading/`): Strategies, exchanges, order management
- **Web Module** (`tests/unit/web/`): API endpoints, server functionality
- **Shared Module** (`tests/unit/shared/`): Shared utilities, error handling

### Integration Tests / 集成测试 (`tests/integration/`)

Tests that verify cross-module interactions and end-to-end workflows.  
验证跨模块交互和端到端工作流的测试。

### Smoke Tests / 冒烟测试 (`tests/smoke/`)

Quick health checks to verify basic functionality.  
快速健康检查以验证基本功能。

### Contract Tests / 契约测试 (`tests/contract/`)

Tests that verify API contracts and interfaces.  
验证 API 契约和接口的测试。

### End-to-End Tests / 端到端测试 (`tests/e2e/`)

Full system tests including UI and browser interactions.  
包括 UI 和浏览器交互的完整系统测试。

## Running Tests / 运行测试

```bash
# Run all tests / 运行所有测试
pytest tests/ -v

# Run specific test category / 运行特定测试类别
pytest tests/unit/ -v              # Unit tests only / 仅单元测试
pytest tests/integration/ -v       # Integration tests only / 仅集成测试
pytest tests/smoke/ -v              # Smoke tests only / 仅冒烟测试

# Run module-specific tests / 运行特定模块测试
pytest tests/unit/ai/ -v
pytest tests/unit/portfolio/ -v
pytest tests/unit/trading/ -v
pytest tests/unit/web/ -v

# Run with coverage / 运行并生成覆盖率报告
pytest tests/ --cov=. --cov-report=html

# Run specific test file / 运行特定测试文件
pytest tests/unit/trading/test_fixed_spread_strategy.py -v
```

## Test Organization / 测试组织

Tests are organized by module to improve maintainability and discoverability:

1. **Module-based structure**: Each module has its own test directory
2. **Clear naming**: Test files follow `test_<module>_<feature>.py` pattern
3. **Separation of concerns**: Unit, integration, smoke tests are clearly separated

测试按模块组织以提高可维护性和可发现性：

1. **基于模块的结构**：每个模块都有自己的测试目录
2. **清晰的命名**：测试文件遵循 `test_<module>_<feature>.py` 模式
3. **关注点分离**：单元测试、集成测试、冒烟测试清晰分离

## Ownership / 归属

Each test directory is owned by its respective Agent:

| Directory | Owner |
|-----------|-------|
| `unit/ai/` | Agent AI |
| `unit/portfolio/` | Agent PORTFOLIO |
| `unit/trading/` | Agent TRADING |
| `unit/web/` | Agent WEB |
| `unit/shared/` | Agent SHARED |
| `integration/` | Agent QA |
| `smoke/` | Agent QA |
| `contract/` | Agent QA |
| `e2e/` | Agent QA |

## Dependencies / 依赖

Required packages (in `requirements.txt`):
- pytest
- pytest-cov
- pytest-mock
