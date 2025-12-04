# Specs and User Stories List / 规范和用户故事列表

**Last Updated / 最后更新**: 2025-12-04

---

## 📋 Specifications (Specs) / 规范

### Trading Module / 交易模块

#### 1. CORE-004: Hyperliquid Exchange Integration
- **File**: `docs/specs/trading/CORE-004.md`
- **Epic**: EPIC-02
- **Module**: trading
- **Owner**: Agent TRADING
- **Status**: spec_defined
- **Description**: 
  - 添加对 Hyperliquid 交易所的支持，作为 Binance 的替代方案
  - 包括连接/认证、订单管理和仓位/余额追踪功能
  - Add support for Hyperliquid exchange as an alternative to Binance
  - Includes connection/authentication, order management, and position/balance tracking

**Requirements / 需求**:
- REQ-1: Hyperliquid Connection and Authentication
- REQ-2: Hyperliquid Order Management
- REQ-3: Hyperliquid Position and Balance Tracking

#### 2. CORE-004-STORY-BREAKDOWN.md
- **File**: `docs/specs/trading/CORE-004-STORY-BREAKDOWN.md`
- **Type**: Story breakdown document
- **Description**: 将 CORE-004 拆分为多个用户故事的详细分析

#### 3. US-CORE-004-B-REVIEW.md
- **File**: `docs/specs/trading/US-CORE-004-B-REVIEW.md`
- **Type**: Review document
- **Description**: US-CORE-004-B 的审查文档

### AI Module / AI 模块

#### 4. USER-STORY-STANDARDS.md
- **File**: `docs/specs/ai/USER-STORY-STANDARDS.md`
- **Module**: ai
- **Description**: 用户故事标准文档

#### 5. TODO.md
- **File**: `docs/specs/ai/TODO.md`
- **Module**: ai
- **Description**: AI 模块待办事项

---

## 📖 User Stories / 用户故事

### Trading Module / 交易模块

#### 1. US-CORE-004-A: Hyperliquid Connection and Authentication
- **File**: `docs/stories/trading/US-CORE-004-A.md`
- **ID**: US-CORE-004-A
- **Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Module**: trading
- **Owner**: Agent TRADING
- **Status**: DONE ✅ (ci_cd_passed)
- **Branch**: feat/US-CORE-004-A-hyperliquid-connection (merged)

**User Story / 用户故事**:
> As a quantitative trader  
> I want to connect to Hyperliquid exchange and authenticate with my API credentials  
> So that I can access Hyperliquid trading API and use it as an alternative to Binance

**Acceptance Criteria / 验收标准**: 7 个 (AC-1 到 AC-7)

---

#### 2. US-CORE-004-B: Hyperliquid Order Management
- **File**: `docs/stories/trading/US-CORE-004-B.md`
- **ID**: US-CORE-004-B
- **Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Module**: trading
- **Owner**: Agent TRADING
- **Status**: DONE ✅ (ci_cd_passed)
- **Branch**: feat/US-CORE-004-B-hyperliquid-orders (merged)

**User Story / 用户故事**:
> As a quantitative trader  
> I want to place, cancel, and query orders on Hyperliquid exchange  
> So that I can execute trading strategies on Hyperliquid just like I do on Binance

**Acceptance Criteria / 验收标准**: 多个 AC

---

#### 3. US-CORE-004-C: Hyperliquid Position and Balance Tracking
- **File**: `docs/stories/trading/US-CORE-004-C.md`
- **ID**: US-CORE-004-C
- **Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Module**: trading
- **Owner**: Agent TRADING
- **Status**: TODO (spec_defined)
- **Branch**: feat/US-CORE-004-C-hyperliquid-positions (created)

**User Story / 用户故事**:
> As a quantitative trader  
> I want to track my positions, balance, and PnL on Hyperliquid exchange  
> So that I can monitor my trading performance and risk exposure on Hyperliquid

**Acceptance Criteria / 验收标准**: 10 个 (AC-1 到 AC-10)
- AC-1: Balance Fetching
- AC-2: Position Tracking
- AC-3: Unrealized PnL Calculation
- AC-4: Realized PnL Tracking
- AC-5: Position History
- AC-6: Margin Information
- AC-7: Multi-Symbol Position Support
- AC-8: Position Updates
- AC-9: Integration with Performance Tracker
- AC-10: Error Handling

**Current Step**: spec_defined (Step 1/14)
**Completion**: 21.4% (3/14 steps)

---

### Web Module / Web 模块

#### 4. US-API-004: Hyperliquid LLM Evaluation Support
- **File**: `docs/stories/web/US-API-004.md`
- **ID**: US-API-004
- **Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Module**: web
- **Owner**: Agent WEB
- **Status**: IN_PROGRESS (unit_test_passed)
- **Branch**: feat/US-API-004 (merged to main)

**User Story / 用户故事**:
> As a quantitative trader  
> I want the LLM evaluation API to support Hyperliquid exchange  
> So that I can get AI-powered trading parameter suggestions for Hyperliquid in a dedicated Hyperliquid trading page

**Acceptance Criteria / 验收标准**: 多个 AC
- AC-1: LLM Evaluation API Support for Hyperliquid
- AC-2: LLM Response Format
- AC-3: Hyperliquid Market Data Integration
- AC-4: Exchange Context in LLM Input
- AC-5: Error Handling for Hyperliquid LLM Evaluation
- AC-3 (Apply): Apply LLM Suggestions to Hyperliquid

**Current Step**: unit_test_passed (Step 9/14)
**Completion**: 64.3% (9/14 steps)

---

#### 5. US-UI-004: Dedicated Hyperliquid Trading Page
- **File**: `docs/stories/web/US-UI-004.md`
- **ID**: US-UI-004
- **Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Module**: web
- **Owner**: Agent WEB
- **Status**: TODO (spec_defined)
- **Branch**: pending

**User Story / 用户故事**:
> As a quantitative trader  
> I want a dedicated Hyperliquid trading page (similar to LLMTrade.html but specifically for Hyperliquid)  
> So that I can have a focused interface for all Hyperliquid trading activities including strategy control, LLM evaluation, position tracking, and order management

**Acceptance Criteria / 验收标准**: 多个 AC
- AC-1: Dedicated Page Creation
- AC-2: Exchange Selection
- AC-3: Strategy Control for Hyperliquid
- AC-4: LLM Evaluation Integration
- AC-5: Position and Balance Display
- AC-6: Order Management Interface
- AC-7: Real-time Updates
- AC-8: Error Handling and Alerts

**Current Step**: spec_defined (Step 1/14)
**Completion**: 7.1% (1/14 steps)

---

## 📊 Summary Statistics / 统计摘要

### By Status / 按状态

| Status | Count | Stories |
|--------|-------|---------|
| **DONE** | 2 | US-CORE-004-A, US-CORE-004-B |
| **IN_PROGRESS** | 1 | US-API-004 |
| **TODO** | 2 | US-CORE-004-C, US-UI-004 |

### By Module / 按模块

| Module | Specs | Stories |
|--------|-------|---------|
| **trading** | 3 | 3 |
| **web** | 0 | 2 |
| **ai** | 2 | 0 |

### By Epic / 按 Epic

| Epic | Stories | Status |
|------|---------|--------|
| **EPIC-02** | 5 | IN_PROGRESS |
| - US-CORE-004-A | ✅ DONE |
| - US-CORE-004-B | ✅ DONE |
| - US-CORE-004-C | ⏳ TODO |
| - US-API-004 | 🔄 IN_PROGRESS |
| - US-UI-004 | ⏳ TODO |

---

## 📁 File Locations / 文件位置

### Specifications / 规范
```
docs/specs/
├── trading/
│   ├── CORE-004.md
│   ├── CORE-004-STORY-BREAKDOWN.md
│   └── US-CORE-004-B-REVIEW.md
└── ai/
    ├── USER-STORY-STANDARDS.md
    └── TODO.md
```

### User Stories / 用户故事
```
docs/stories/
├── trading/
│   ├── US-CORE-004-A.md ✅
│   ├── US-CORE-004-B.md ✅
│   └── US-CORE-004-C.md ⏳
└── web/
    ├── US-API-004.md 🔄
    └── US-UI-004.md ⏳
```

---

## 🔗 Related Documents / 相关文档

- **Roadmap**: `status/roadmap.json`
- **Progress Index**: `docs/progress/progress_index.json`
- **Module Cards**: `docs/modules/*.json`
- **Contracts**: `contracts/*.json`

---

**Generated by / 生成者**: Agent PM  
**Last Updated / 最后更新**: 2025-12-04

