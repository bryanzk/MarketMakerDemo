# Unit Tests / 单元测试

This directory contains unit tests organized by module.  
此目录包含按模块组织的单元测试。

## Directory Structure / 目录结构

```
tests/unit/
├── trading/          # Trading engine tests / 交易引擎测试 (Agent TRADING)
│   ├── test_exchange_connection.py
│   ├── test_order_manager.py
│   └── ...
├── portfolio/        # Portfolio tests / 组合管理测试 (Agent PORTFOLIO)
│   ├── test_capital_allocation.py
│   ├── test_risk_indicators.py
│   └── ...
├── web/              # Web/API tests / Web/API 测试 (Agent WEB)
│   ├── test_bot_control_api.py
│   ├── test_portfolio_api.py
│   └── ...
└── ai/               # AI/LLM tests / AI/LLM 测试 (Agent AI)
    ├── test_multi_llm_evaluator.py
    ├── test_data_agent.py
    └── ...
```

## Ownership / 归属

Each subdirectory is owned by its respective Dev Agent:  
每个子目录由对应的 Dev Agent 负责：

| Directory | Owner |
|-----------|-------|
| `trading/` | Agent TRADING |
| `portfolio/` | Agent PORTFOLIO |
| `web/` | Agent WEB |
| `ai/` | Agent AI |

## Running Tests / 运行测试

```bash
# Run all unit tests / 运行所有单元测试
pytest tests/unit/ -v

# Run module-specific tests / 运行特定模块测试
pytest tests/unit/trading/ -v
pytest tests/unit/portfolio/ -v
pytest tests/unit/web/ -v
pytest tests/unit/ai/ -v
```

## TDD Workflow / TDD 工作流

1. Dev Agent writes unit tests first (tests will fail)
2. Dev Agent implements code to make tests pass
3. Dev Agent runs tests to confirm pass

1. Dev Agent 先写单元测试（测试会失败）
2. Dev Agent 实现代码让测试通过
3. Dev Agent 运行测试确认通过

