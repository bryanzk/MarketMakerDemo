# Unit Tests / 单元测试

This directory contains unit tests organized by module.  
此目录包含按模块组织的单元测试。

## Directory Structure / 目录结构

```
tests/unit/
├── ai/               # AI/LLM tests / AI/LLM 测试 (Agent AI)
│   ├── test_data_agent.py
│   ├── test_evaluation_prompts.py
│   ├── test_gemini_provider.py
│   ├── test_llm_evaluation.py
│   ├── test_llm_gateway.py
│   ├── test_llm_providers.py
│   ├── test_multi_llm_evaluator.py
│   ├── test_openai_provider.py
│   ├── test_quant_agent.py
│   ├── test_risk_agent.py
│   └── test_translation.py
├── portfolio/        # Portfolio tests / 组合管理测试 (Agent PORTFOLIO)
│   ├── test_api.py
│   ├── test_health.py
│   ├── test_metrics.py
│   ├── test_risk_indicators.py
│   ├── test_risk_manager.py
│   └── test_sync.py
├── trading/          # Trading engine tests / 交易引擎测试 (Agent TRADING)
│   ├── test_exchange_base.py
│   ├── test_exchange_exceptions.py
│   ├── test_exchange_funding_multi.py
│   ├── test_exchange_funding_rate.py
│   ├── test_exchange_leverage.py
│   ├── test_exchange_volatility.py
│   ├── test_fixed_spread_strategy.py
│   ├── test_funding_strategy.py
│   ├── test_hyperliquid_api_direct.py
│   ├── test_hyperliquid_key.py
│   ├── test_order_manager.py
│   ├── test_performance_tracker.py
│   ├── test_simulation.py
│   ├── test_simulation_fixedspread.py
│   └── test_tick_size_resolution.py
├── web/              # Web/API tests / Web/API 测试 (Agent WEB)
│   ├── test_debug_panel.py
│   ├── test_error_history_panel.py
│   ├── test_error_response_trace_id.py
│   ├── test_evaluation_cancellation.py
│   ├── test_hyperliquid_api_endpoints.py
│   ├── test_hyperliquid_llm_evaluation.py
│   ├── test_hyperliquid_trade_page_unit.py
│   ├── test_pair_update_consistency.py
│   ├── test_server.py
│   ├── test_server_api.py
│   ├── test_server_funding_rates.py
│   ├── test_strategy_instance_errors.py
│   ├── test_trace_id_middleware.py
│   ├── test_validation.py
│   └── test_websocket_evaluation.py
└── shared/           # Shared utilities tests / 共享工具测试 (Agent SHARED)
    ├── test_error_handling.py
    ├── test_error_mapper.py
    ├── test_errors.py
    ├── test_metrics.py
    ├── test_tracing.py
    └── test_utils.py
```

## Ownership / 归属

Each subdirectory is owned by its respective Dev Agent:  
每个子目录由对应的 Dev Agent 负责：

| Directory | Owner |
|-----------|-------|
| `ai/` | Agent AI |
| `portfolio/` | Agent PORTFOLIO |
| `trading/` | Agent TRADING |
| `web/` | Agent WEB |
| `shared/` | Agent SHARED |

## Running Tests / 运行测试

```bash
# Run all unit tests / 运行所有单元测试
pytest tests/unit/ -v

# Run module-specific tests / 运行特定模块测试
pytest tests/unit/ai/ -v
pytest tests/unit/portfolio/ -v
pytest tests/unit/trading/ -v
pytest tests/unit/web/ -v
pytest tests/unit/shared/ -v

# Run specific feature tests / 运行特定功能测试
pytest tests/unit/web/test_hyperliquid_llm_evaluation.py -v
pytest tests/unit/trading/test_fixed_spread_strategy.py -v
```

## TDD Workflow / TDD 工作流

1. Dev Agent writes unit tests first (tests will fail)
2. Dev Agent implements code to make tests pass
3. Dev Agent runs tests to confirm pass

1. Dev Agent 先写单元测试（测试会失败）
2. Dev Agent 实现代码让测试通过
3. Dev Agent 运行测试确认通过
