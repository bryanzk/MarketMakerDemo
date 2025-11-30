# Project Baseline & Implementation Overview / 项目基线与实现概览

## 📌 Business Baseline / 业务基线

- **Goal / 目标**: An autonomous, self‑optimising market‑making bot for crypto assets that continuously analyses performance and adapts strategy. / 一个自主、自我优化的加密资产做市机器人，持续分析表现并调整策略。
- **Core Loop / 核心循环**: Data → Risk → Quant → Execution → Infrastructure → QA → Ops. / 数据 → 风控 → 量化 → 执行 → 基础设施 → QA → 运维。
- **Key KPIs / 关键指标**: PnL, Sharpe Ratio, Win Rate, Slippage, Tick‑to‑Trade latency. / 盈利、夏普比率、胜率、滑点、Tick‑to‑Trade 延迟。
- **Safety / 安全**: Risk Agent enforces hard limits (max position, max draw‑down) and has veto power over any deployment. / 风控智能体强制硬性限制（最大持仓、最大回撤），拥有否决权。

## ⚙️ Automated Implementation / 自动化实现

| Business Function / 业务功能 | Implemented By | Source File(s) |
|---|---|---|
| Data ingestion & metrics / 数据采集与指标 | **Data Agent** | `src/ai/agents/data.py` |
| Risk validation & limits / 风控校验与限制 | **Risk Agent** | `src/ai/agents/risk.py` |
| Strategy analysis & proposal / 策略分析与提案 | **Quant Agent** | `src/ai/agents/quant.py` |
| Order execution & slippage control / 订单执行与滑点控制 | **Execution Agent** | `src/trading/execution.py` (or similar) |
| Connectivity & latency monitoring / 连接与延迟监控 | **Infrastructure Agent** | `src/shared/config.py`, `src/shared/logger.py` |
| QA & test coverage / QA 与测试覆盖 | **QA Agent** | `tests/` (unit & integration tests) |
| CI/CD pipeline & Ops / CI/CD 与运维 | **Operations Agent** | `.github/workflows/ci.yml` |

## ✅ CI / Quality Gates / CI 与质量门禁

- **Tests**: `pytest --cov=src` (coverage ≥ 70%). / 覆盖率 ≥ 70%。
- **Lint**: `flake8`. / 代码检查。
- **Formatting**: `black --check`, `isort --check-only`. / 格式化检查。
- **Badge**: CI status badge shown in `README.md`. / 在 README 中显示 CI 徽章。

All components run automatically on every push/PR to `main` or `develop`, ensuring continuous validation. / 所有组件在每次 push/PR 到 main 或 develop 时自动运行，确保持续验证。


