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

### Planned for Phase 3
- Inventory skew (position-based spread adjustment)
- File logging
- PnL persistence
- Multi-symbol support
- Dynamic spread based on volatility
