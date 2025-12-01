# API Reference / API 参考

This page lists every API and code reference artifact available for the AlphaLoop Market Maker project.
本页列出了 AlphaLoop 做市项目中所有可用的 API 及代码参考资料。

## 📚 Documentation Resources / 文档资源

### 1. Auto-Generated Reference (pdoc) / 自动生成参考（pdoc）
Browse the complete API reference, including modules, classes, and functions, at **[docs/api/index.html](api/index.html)**.
访问 **[docs/api/index.html](api/index.html)** 可浏览包含模块、类和函数的完整 API 参考文档。

- **Highlights**: Generated from inline docstrings, includes type hints, refreshed on every push to `main`.
  **要点**：由代码注释自动生成，涵盖类型提示，并在每次推送到 `main` 时刷新。
- **Best Practice**: Keep docstrings updated so this reference never drifts from the code.
  **最佳实践**：及时维护 Docstring，确保文档与代码保持一致。

### 2. Interactive FastAPI Docs / FastAPI 交互式文档
Start the server (`python run.py` 或 `uvicorn server:app --port 3000`) to access the built-in interactive explorers.
启动服务器（`python run.py` 或 `uvicorn server:app --port 3000`）即可使用内置的交互式文档界面。

- **[Swagger UI](/docs)** offers a “Try it out” experience for every REST endpoint.
  **[Swagger UI](/docs)** 为所有 REST 接口提供 “Try it out” 交互体验。
- **[ReDoc](/redoc)** provides a reader-friendly rendering of the same OpenAPI spec.
  **[ReDoc](/redoc)** 以更易阅读的方式展示同一份 OpenAPI 规范。

## 🔧 Developer Workflow / 开发者工作流

### Generate Docs Locally / 本地生成文档
```bash
# Install dependencies if needed
pip install -r requirements.txt

# Build API docs with pdoc
./scripts/build_docs.sh

# Open the generated index
open docs/api/index.html
```
Run the script whenever you change public APIs, docstrings, or configuration to avoid stale references.
只要修改了公共 API、Docstring 或配置，就应运行该脚本以防参考资料过期。

### Documentation Standards / 文档标准
- **Docstrings**: Use Google- or NumPy-style docstrings for every public symbol.
  **Docstring**：所有公开符号使用 Google 或 NumPy 风格注释。
- **Type Hints**: Provide precise type annotations so pdoc can render accurate signatures.
  **类型提示**：提供准确的类型注解，方便 pdoc 输出正确签名。
- **Module Summaries**: Begin each module with a short statement of purpose.
  **模块摘要**：每个模块开头添加简短的用途说明。

### Auto-Documentation in CI/CD / CI/CD 自动生成
GitHub Actions regenerates and publishes the API documentation on every push to `main`, guaranteeing consistency between code and docs.
GitHub Actions 会在每次推送到 `main` 时重新生成并发布 API 文档，确保代码与文档同步。

## 🔧 REST API Endpoints / REST API 端点

### Portfolio Management / 组合管理

#### `GET /api/portfolio`

Get portfolio overview and strategy comparison data.
获取组合概览和策略对比数据。

**Response Example / 响应示例:**
```json
{
  "total_pnl": 150.5,
  "commission": 5.0,
  "net_pnl": 145.5,
  "portfolio_sharpe": 1.8,
  "active_count": 2,
  "total_count": 3,
  "risk_level": "low",
  "total_capital": 10000.0,
  "available_balance": 9500.0,
  "session_start_time": 1701234000000,
  "strategies": [
    {
      "id": "fixed_spread",
      "name": "Fixed Spread",
      "status": "live",
      "pnl": 100.0,
      "sharpe": 2.0,
      "health": 85,
      "allocation": 0.6,
      "roi": 0.0167
    }
  ]
}
```

**Fields / 字段说明:**

| Field | Type | Description |
|-------|------|-------------|
| `total_pnl` | float | Total PnL from session start / 会话开始后的总盈亏 |
| `commission` | float | Total trading fees paid / 已缴纳交易费 |
| `net_pnl` | float | Net PnL (total_pnl - commission) / 净盈亏 |
| `portfolio_sharpe` | float | Portfolio Sharpe ratio / 组合夏普比率 |
| `active_count` | int | Number of active strategies / 活跃策略数 |
| `total_count` | int | Total number of strategies / 总策略数 |
| `risk_level` | string | `low` / `medium` / `high` / `critical` |
| `total_capital` | float | Total wallet balance / 总资金 |
| `available_balance` | float | Available balance for trading / 可用余额 |
| `session_start_time` | int | Session start timestamp (ms) / 会话起始时间（毫秒） |
| `strategies` | array | List of strategy data / 策略列表 |

**Related Documentation / 相关文档:**
- [Portfolio Management Guide](user_guide/portfolio_management.md)
- [Portfolio User Stories](user_guide/user_stories_portfolio.md)

---

#### `GET /api/funding-rates`

Get funding rates for all supported trading pairs, sorted by absolute value.
获取所有支持交易对的资金费率，按绝对值排序。

**Response Example / 响应示例:**
```json
[
  {
    "symbol": "ETH/USDT:USDT",
    "funding_rate": 0.0001,
    "daily_yield": 0.0003,
    "direction": "short_favored"
  }
]
```

**Fields / 字段说明:**

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | string | Trading pair symbol / 交易对符号 |
| `funding_rate` | float | Current funding rate / 当前资金费率 |
| `daily_yield` | float | Estimated daily yield (rate × 3) / 预估日收益率 |
| `direction` | string | `short_favored` / `long_favored` / `neutral` |

---

#### `POST /api/strategy/{strategy_id}/pause`

Pause a specific strategy.
暂停指定策略。

**Parameters / 参数:**
- `strategy_id` (path): Strategy identifier / 策略标识符

**Response / 响应:**
```json
{
  "status": "paused",
  "strategy_id": "fixed_spread"
}
```

---

#### `POST /api/strategy/{strategy_id}/resume`

Resume a paused strategy.
恢复已暂停的策略。

**Parameters / 参数:**
- `strategy_id` (path): Strategy identifier / 策略标识符

**Response / 响应:**
```json
{
  "status": "live",
  "strategy_id": "fixed_spread"
}
```

---

### Risk Indicators / 风险指标

#### `GET /api/risk-indicators`

Returns real-time risk monitoring indicators.
返回实时风险监控指标。

**Response Example / 响应示例:**
```json
{
  "liquidation_buffer": 15.2,
  "liquidation_buffer_status": "warning",
  "inventory_drift": 32.5,
  "inventory_drift_status": "offset",
  "inventory_direction": "long",
  "max_drawdown": -4.8,
  "max_drawdown_status": "excellent",
  "overall_risk_level": "medium"
}
```

**Fields / 字段说明:**

| Field | Type | Description |
|-------|------|-------------|
| `liquidation_buffer` | float | Distance to liquidation price (%) / 距离强平价格的百分比 |
| `liquidation_buffer_status` | string | `safe` / `warning` / `danger` / `critical` |
| `inventory_drift` | float | Position bias percentage (-100 to +100) / 持仓偏移百分比 |
| `inventory_drift_status` | string | `balanced` / `offset` / `severe` / `extreme` |
| `inventory_direction` | string | `long` / `short` / `neutral` |
| `max_drawdown` | float | Maximum drawdown from peak (negative %) / 最大回撤百分比 |
| `max_drawdown_status` | string | `excellent` / `normal` / `warning` / `danger` |
| `overall_risk_level` | string | `low` / `medium` / `high` / `critical` |

**Related Documentation / 相关文档:**
- [Risk Indicators Guide](user_guide/risk_indicators.md)
- [Risk User Stories](user_guide/user_stories_risk.md)

---

## 📖 Related Documentation / 相关文档
- [README](../README.md) – Project overview and quick start.
  [README](../README.md) – 项目概览与快速上手。
- [CI/CD Guide](cicd.md) – Continuous integration and deployment pipeline.
  [CI/CD 指南](cicd.md) – 持续集成与部署流程。
- [Dashboard Guide](dashboard.md) – Monitoring metrics and charts.
  [Dashboard 指南](dashboard.md) – 监控指标与图表。
- [Risk Indicators Guide](user_guide/risk_indicators.md) – Risk monitoring user guide.
  [风险指标指南](user_guide/risk_indicators.md) – 风险监控用户指南。
- [Multi-LLM Evaluation Guide](user_guide/multi_llm_evaluation.md) – Multi-model strategy evaluation.
  [多 LLM 评估指南](user_guide/multi_llm_evaluation.md) – 多模型策略评估。
- [AlphaLoop Framework](framework/framework_design.md) – Architecture and design reference.
  [AlphaLoop 框架](framework/framework_design.md) – 架构与设计参考。
