# TODO - Future Improvements


## 2025.11.30
### QA
- pass unit tests
- push the code

### Project Management
- Review Current process progress
- Add missed scenarios
- Clear Roles definition 
- Clear Done Definition
- Clear process clarification
- To sum: 
  -  https://github.com/sarwarbeing-ai/Agentic_Design_Patterns/blob/main/Agentic_Design_Patterns.pdf

### Business
- Right way to measure the suggestion from LLMs
  - docs
  - implementation using the new PM process






## High Priority

### Leverage Verification
- [ ] **Check on leverage settings**
  - Verify leverage is correctly applied to positions
  - Test leverage changes during active trading
  - Validate margin calculations with different leverage levels
  - Document leverage impact on risk and capital efficiency

### Trading Pair Optimization
- [ ] **Confirm pair selection or implement automatic strategy adjustment**
  - Evaluate current strategy performance on ETH/USDT
  - Test strategy on other major pairs (BTC/USDT, BNB/USDT, SOL/USDT)
  - Implement pair-specific parameter presets:
    - Different spread percentages for different volatility levels
    - Position size adjustments based on pair characteristics
  - **Option A**: Manual pair selection with optimized presets
  - **Option B**: Automatic strategy parameter adjustment based on:
    - Real-time volatility detection
    - Spread analysis
    - Liquidity metrics

---

## Phase 3 - Advanced Features

### Inventory Skew (Inventory Management)
- [ ] Implement position-based spread adjustment
  - When long-biased: widen buy spread, narrow sell spread
  - When short-biased: widen sell spread, narrow buy spread
  - Configurable skew intensity parameter

### File Logging
- [ ] Implement rotating file logger
  - Daily log rotation
  - Separate logs for different components (strategy, orders, errors)
  - Log retention policy

### PnL Persistence
- [ ] Save PnL history to database/file
  - SQLite or JSON storage
  - Historical PnL chart on Web UI
  - Export functionality (CSV/Excel)

---

## Long-term Enhancements

### Multi-Symbol Support
- [ ] Extend bot to handle multiple trading pairs simultaneously
- [ ] Per-symbol configuration and risk limits
- [ ] Unified dashboard for all pairs

### Dynamic Spread
- [ ] Volatility-based spread adjustment
  - Calculate rolling volatility (ATR/std dev)
  - Widen spread in high volatility
  - Narrow spread in low volatility

### Backtesting System
- [ ] Historical data downloader
- [ ] Backtest engine
- [ ] Performance metrics and visualization

### Advanced Risk Management
- [x] Maximum drawdown limits ✅ (Implemented in `RiskIndicators.calculate_max_drawdown()`)
- [x] Liquidation buffer monitoring ✅ (Implemented in `RiskIndicators.calculate_liquidation_buffer()`)
- [x] Inventory drift tracking ✅ (Implemented in `RiskIndicators.calculate_inventory_drift()`)
- [ ] Daily loss limits
- [ ] Circuit breaker on unusual market conditions

---

## Technical Debt

- [ ] Add unit tests for core components
- [ ] Add integration tests for API endpoints
- [ ] Improve error messages and logging
- [ ] Add monitoring/alerting for production use
- [ ] Performance optimization (reduce API calls)

---

**Last Updated**: 2025-11-26
