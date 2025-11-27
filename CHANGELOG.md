# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-20

### Added
- **Core Market Making Engine**
  - Fixed-spread strategy (0.2% around mid-price)
  - Automatic order synchronization
  - Position risk management (±0.2 ETH limit)
  - Post-only orders (GTX) for maker fee rebates

- **Web UI Dashboard**
  - Real-time metrics display (price, position, balance, PnL)
  - Start/Stop bot control
  - Dynamic parameter adjustment (spread, quantity, leverage)
  - Real-time order monitoring
  - Error state display

- **Leverage Management**
  - Configurable leverage (1-125x)
  - Real-time leverage display
  - API endpoint for leverage updates

- **PnL Tracking**
  - Unrealized PnL calculation
  - Realized PnL tracking with configurable start time
  - Historical income data fetching

- **Safety Features**
  - Automatic order cancellation on stop
  - Connection validation on start
  - Error handling with auto-stop and order cancellation
  - Graceful shutdown mechanism

- **Documentation**
  - Trading strategy documentation (Chinese)
  - System architecture diagrams (Mermaid)
  - Implementation plan
  - Feature walkthrough
  - Comprehensive README

### Technical Details
- Python 3.11
- FastAPI web framework
- CCXT for exchange connectivity
- Binance Futures Testnet support
- Modular architecture (Strategy, Risk, OrderManager, Exchange)

---

## [Unreleased]

### Added
- **Multi-LLM Strategy Evaluation Framework**
  - Support for Gemini, OpenAI (GPT-4o), and Claude providers
  - `MultiLLMEvaluator` for parallel strategy evaluation
  - Automatic provider discovery with `create_all_providers()`
  - Simulation-based strategy comparison with scoring and ranking
  - Comparison table generation for decision making

- **Risk Indicators Module** (`alphaloop/portfolio/risk.py`)
  - Liquidation Buffer calculation (US-R1)
  - Inventory Drift monitoring (US-R2)
  - Max Drawdown tracking (US-R3)
  - Overall Risk Level assessment (US-R4)
  - `GET /api/risk-indicators` API endpoint (US-R5)

- **Portfolio Health Score Module** (`alphaloop/portfolio/health.py`)
  - Strategy health score calculation (0-100) based on:
    - Profitability (40% weight)
    - Risk-adjusted return (30% weight)
    - Execution quality (20% weight)
    - Stability (10% weight)
  - Health status classification (excellent/good/fair/poor)
  - Color coding for health visualization
  - Comprehensive unit test coverage

- **New Dependencies**
  - `openai` - OpenAI API client
  - `anthropic` - Anthropic Claude API client

### Fixed
- Portfolio Overview balance display
- Portfolio API tests and isort formatting issues
- Health score calculation: Fixed negative Sharpe ratio handling to ensure 0-100 range
- Test patch paths for LLM providers (OpenAI, Claude)

### Changed
- Trading fee calculation and display improvements
- Health score calculation: Added final range clamping to guarantee 0-100 output
- Documentation: Updated all user guides to bilingual format (English/Chinese)

### Planned for Phase 3
- Inventory skew (position-based spread adjustment)
- File logging
- PnL persistence
- Multi-symbol support
- Dynamic spread based on volatility
