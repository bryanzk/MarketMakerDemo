# CORE-004: Hyperliquid Exchange Integration / Hyperliquid 交易所集成

## Overview / 概述

This feature adds support for Hyperliquid exchange as an alternative to Binance, allowing traders to switch between exchanges and diversify their trading options. The integration includes connection/authentication, order management, and position/balance tracking capabilities.

此功能添加对 Hyperliquid 交易所的支持，作为 Binance 的替代方案，允许交易员在交易所之间切换并分散交易选择。集成包括连接/认证、订单管理和仓位/余额追踪功能。

**Epic / Epic**: EPIC-02: Hyperliquid Exchange Integration  
**Module / 模块**: trading  
**Owner / 负责人**: Agent TRADING  
**Status / 状态**: spec_defined

---

## Purpose / 目的

### Business Value / 业务价值

- **Exchange Diversification / 交易所多样化**: Enable traders to use multiple exchanges, reducing dependency on a single platform
- **交易所多样化**: 使交易员能够使用多个交易所，减少对单一平台的依赖
- **Risk Mitigation / 风险缓解**: Spread trading across exchanges to mitigate exchange-specific risks
- **风险缓解**: 在多个交易所分散交易以缓解特定交易所的风险
- **Feature Parity / 功能对等**: Provide same trading capabilities on Hyperliquid as on Binance
- **功能对等**: 在 Hyperliquid 上提供与 Binance 相同的交易能力

### User Value / 用户价值

- Traders can choose the exchange that offers better fees, liquidity, or features
- 交易员可以选择提供更好费用、流动性或功能的交易所
- Seamless switching between exchanges without code changes
- 无需代码更改即可在交易所之间无缝切换
- Consistent trading experience across different exchanges
- 在不同交易所之间保持一致的交易体验

---

## Requirements / 需求

### REQ-1: Hyperliquid Connection and Authentication / Hyperliquid 连接与认证

**Description / 描述**:  
The system must support connecting to Hyperliquid exchange (both testnet and mainnet) and authenticating with API credentials.

系统必须支持连接到 Hyperliquid 交易所（测试网和主网）并使用 API 凭证进行认证。

**Details / 详情**:
- Support Hyperliquid REST API (https://api.hyperliquid.xyz and https://testnet.hyperliquid.xyz)
- 支持 Hyperliquid REST API
- Implement API key and signature-based authentication
- 实现基于 API 密钥和签名的认证
- Provide health monitoring and connection status
- 提供健康监控和连接状态
- Handle connection errors gracefully with retry mechanism
- 优雅地处理连接错误并提供重试机制

**User Story / 用户故事**: US-CORE-004-A

---

### REQ-2: Hyperliquid Order Management / Hyperliquid 订单管理

**Description / 描述**:  
The system must support placing, canceling, and querying orders on Hyperliquid exchange.

系统必须支持在 Hyperliquid 交易所上下单、取消和查询订单。

**Details / 详情**:
- Support limit and market orders (buy and sell)
- 支持限价和市价订单（买入和卖出）
- Support order cancellation (single and bulk)
- 支持订单取消（单个和批量）
- Support order status query and order history
- 支持订单状态查询和订单历史
- Ensure order idempotency
- 确保订单幂等性
- Integrate with existing OrderManager
- 与现有 OrderManager 集成

**User Story / 用户故事**: US-CORE-004-B  
**Depends on / 依赖**: REQ-1 (Connection must be working)

---

### REQ-3: Hyperliquid Position and Balance Tracking / Hyperliquid 仓位与余额追踪

**Description / 描述**:  
The system must support tracking positions, balance, and PnL on Hyperliquid exchange, and display this information in the LLMTrade.html page UI.

系统必须支持追踪 Hyperliquid 交易所上的仓位、余额和盈亏，并在 LLMTrade.html 页面 UI 中显示此信息。

**Details / 详情**:
- Fetch account balance and margin information
- 获取账户余额和保证金信息
- Track open positions with details (symbol, side, size, entry price, mark price)
- 追踪未平仓仓位及其详情（交易对、方向、数量、开仓价格、标记价格）
- Calculate unrealized and realized PnL
- 计算未实现和已实现盈亏
- Support position history
- 支持仓位历史
- Integrate with existing PerformanceTracker
- 与现有 PerformanceTracker 集成
- Display position and balance information in LLMTrade.html page as a dedicated panel
- 在 LLMTrade.html 页面中作为专用面板显示仓位和余额信息
- Support real-time UI updates when position or balance changes
- 支持仓位或余额变化时的实时 UI 更新
- Ensure UI is bilingual (Chinese and English)
- 确保 UI 是双语的（中文和英文）

**User Story / 用户故事**: US-CORE-004-C  
**Depends on / 依赖**: REQ-1 (Connection must be working)

---

### REQ-4: Exchange Selection / 交易所选择

**Description / 描述**:  
The system must allow users to select between Binance and Hyperliquid exchanges at runtime.

系统必须允许用户在运行时在 Binance 和 Hyperliquid 交易所之间选择。

**Details / 详情**:
- Provide UI control (dropdown or toggle) for exchange selection
- 提供用于交易所选择的 UI 控件（下拉菜单或切换开关）
- Support runtime switching without code changes
- 支持运行时切换，无需代码更改
- Display current exchange and connection status
- 显示当前交易所和连接状态
- Maintain separate configurations for each exchange
- 为每个交易所维护单独的配置

---

### REQ-5: Error Handling and Mapping / 错误处理与映射

**Description / 描述**:  
The system must handle Hyperliquid-specific errors and map them to standard exceptions with bilingual error messages.

系统必须处理 Hyperliquid 特定错误并将其映射到标准异常，提供双语错误消息。

**Details / 详情**:
- Map Hyperliquid API errors to standard exceptions (AuthenticationError, InsufficientFunds, InvalidOrder, etc.)
- 将 Hyperliquid API 错误映射到标准异常（认证错误、余额不足、无效订单等）
- Provide user-friendly error messages in Chinese and English
- 提供中英文用户友好的错误消息
- Handle network errors with retry logic
- 使用重试逻辑处理网络错误
- Log errors for debugging
- 记录错误以便调试

---

### REQ-6: Interface Consistency / 接口一致性

**Description / 描述**:  
The HyperliquidClient must implement the same interface as BinanceClient to ensure seamless integration with existing code.

HyperliquidClient 必须实现与 BinanceClient 相同的接口，以确保与现有代码的无缝集成。

**Details / 详情**:
- HyperliquidClient should implement same methods as BinanceClient
- HyperliquidClient 应该实现与 BinanceClient 相同的方法
- Maintain consistent method signatures and return types
- 保持一致的方法签名和返回类型
- Ensure existing code (OrderManager, PerformanceTracker) works with both clients
- 确保现有代码（OrderManager、PerformanceTracker）与两个客户端都能工作

---

## Acceptance Criteria / 验收标准

### Phase 1: Connection and Authentication / 阶段 1：连接与认证

- [ ] **AC-1.1**: HyperliquidClient can connect to testnet and mainnet based on configuration
- [ ] **AC-1.1**: HyperliquidClient 可以根据配置连接到测试网和主网
- [ ] **AC-1.2**: Authentication succeeds with valid API credentials
- [ ] **AC-1.2**: 使用有效的 API 凭证时认证成功
- [ ] **AC-1.3**: Authentication fails gracefully with clear error messages for invalid credentials
- [ ] **AC-1.3**: 对于无效凭证，认证优雅地失败并显示清晰的错误消息
- [ ] **AC-1.4**: Connection health monitoring returns status and last API call timestamp
- [ ] **AC-1.4**: 连接健康监控返回状态和最后一次 API 调用时间戳
- [ ] **AC-1.5**: Connection errors are handled with retry mechanism (exponential backoff)
- [ ] **AC-1.5**: 连接错误使用重试机制处理（指数退避）
- [ ] **AC-1.6**: Users can select Hyperliquid from exchange dropdown in UI
- [ ] **AC-1.6**: 用户可以在 UI 中从交易所下拉菜单中选择 Hyperliquid

### Phase 2: Order Management / 阶段 2：订单管理

- [ ] **AC-2.1**: Can place limit orders (buy and sell) on Hyperliquid
- [ ] **AC-2.1**: 可以在 Hyperliquid 上下限价单（买入和卖出）
- [ ] **AC-2.2**: Can place market orders (buy and sell) on Hyperliquid
- [ ] **AC-2.2**: 可以在 Hyperliquid 上下市价单（买入和卖出）
- [ ] **AC-2.3**: Can cancel single order by order ID
- [ ] **AC-2.3**: 可以通过订单 ID 取消单个订单
- [ ] **AC-2.4**: Can cancel all open orders
- [ ] **AC-2.4**: 可以取消所有未成交订单
- [ ] **AC-2.5**: Can query order status by order ID
- [ ] **AC-2.5**: 可以通过订单 ID 查询订单状态
- [ ] **AC-2.6**: Can fetch all open orders
- [ ] **AC-2.6**: 可以获取所有未成交订单
- [ ] **AC-2.7**: Can fetch order history
- [ ] **AC-2.7**: 可以获取订单历史
- [ ] **AC-2.8**: Order errors are handled with clear bilingual error messages
- [ ] **AC-2.8**: 订单错误使用清晰的双语错误消息处理
- [ ] **AC-2.9**: Order operations integrate correctly with OrderManager
- [ ] **AC-2.9**: 订单操作与 OrderManager 正确集成

### Phase 3: Position and Balance Tracking / 阶段 3：仓位与余额追踪

- [ ] **AC-3.1**: Can fetch account balance and margin information
- [ ] **AC-3.1**: 可以获取账户余额和保证金信息
- [ ] **AC-3.2**: Can fetch all open positions with details (symbol, side, size, entry price, mark price)
- [ ] **AC-3.2**: 可以获取所有未平仓仓位及其详情（交易对、方向、数量、开仓价格、标记价格）
- [ ] **AC-3.3**: Can fetch position for specific symbol
- [ ] **AC-3.3**: 可以获取特定交易对的仓位
- [ ] **AC-3.4**: Unrealized PnL is calculated correctly for open positions
- [ ] **AC-3.4**: 未实现盈亏为未平仓仓位正确计算
- [ ] **AC-3.5**: Realized PnL is tracked for closed positions
- [ ] **AC-3.5**: 已实现盈亏为已平仓仓位追踪
- [ ] **AC-3.6**: Can fetch position history
- [ ] **AC-3.6**: 可以获取仓位历史
- [ ] **AC-3.7**: Can fetch margin information (used, available, ratio, liquidation price)
- [ ] **AC-3.7**: 可以获取保证金信息（已用、可用、比率、清算价格）
- [ ] **AC-3.8**: Supports multi-symbol positions
- [ ] **AC-3.8**: 支持多交易对仓位
- [ ] **AC-3.9**: Position data integrates correctly with PerformanceTracker
- [ ] **AC-3.9**: 仓位数据与 PerformanceTracker 正确集成
- [ ] **AC-3.10**: Hyperliquid position and balance information is displayed in LLMTrade.html page as a dedicated panel
- [ ] **AC-3.10**: Hyperliquid 仓位和余额信息在 LLMTrade.html 页面中作为专用面板显示
- [ ] **AC-3.11**: UI panel displays account balance (available, total, margin), open positions table, unrealized/realized PnL, and margin information
- [ ] **AC-3.11**: UI 面板显示账户余额（可用、总计、保证金）、未平仓仓位表、未实现/已实现盈亏和保证金信息
- [ ] **AC-3.12**: UI automatically refreshes when position or balance changes occur
- [ ] **AC-3.12**: 当仓位或余额发生变化时，UI 自动刷新
- [ ] **AC-3.13**: UI panel follows the same design pattern as other panels in LLMTrade.html (Fixed Spread Strategy Control Panel, Multi-LLM Evaluation, Current Orders)
- [ ] **AC-3.13**: UI 面板遵循与 LLMTrade.html 中其他面板相同的设计模式（固定价差策略控制面板、多 LLM 评估、当前订单）
- [ ] **AC-3.14**: All UI text and labels are displayed in both English and Chinese
- [ ] **AC-3.14**: 所有 UI 文本和标签都以英文和中文显示

### Phase 4: Integration and Consistency / 阶段 4：集成与一致性

- [ ] **AC-4.1**: HyperliquidClient implements same interface as BinanceClient
- [ ] **AC-4.1**: HyperliquidClient 实现与 BinanceClient 相同的接口
- [ ] **AC-4.2**: Existing code (OrderManager, PerformanceTracker) works with both BinanceClient and HyperliquidClient
- [ ] **AC-4.2**: 现有代码（OrderManager、PerformanceTracker）与 BinanceClient 和 HyperliquidClient 都能工作
- [ ] **AC-4.3**: Exchange selection works in UI without code changes
- [ ] **AC-4.3**: 交易所选择在 UI 中工作，无需代码更改
- [ ] **AC-4.4**: All error messages are bilingual (Chinese and English)
- [ ] **AC-4.4**: 所有错误消息都是双语的（中文和英文）
- [ ] **AC-4.5**: Configuration supports both exchanges (separate API keys)
- [ ] **AC-4.5**: 配置支持两个交易所（单独的 API 密钥）

---

## Technical Design / 技术设计

### Architecture Overview / 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    Exchange Abstraction Layer                 │
│                      交易所抽象层                              │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐              ┌──────────────┐            │
│  │ BinanceClient│              │HyperliquidCl │            │
│  │              │              │     ient      │            │
│  └──────┬───────┘              └──────┬───────┘            │
│         │                              │                     │
│         └──────────┬───────────────────┘                     │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │  Exchange Interface  │                             │
│         │   (Common Methods)   │                             │
│         └──────────┬──────────┘                             │
│                    │                                         │
│    ┌───────────────┼───────────────┐                        │
│    │               │               │                        │
│ ┌──▼──┐      ┌────▼────┐    ┌────▼────┐                  │
│ │Order│      │Performance│    │ Strategy │                  │
│ │Mgr  │      │  Tracker  │    │ Instance │                  │
│ └─────┘      └──────────┘    └──────────┘                  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Design / 组件设计

#### 1. HyperliquidClient Class / HyperliquidClient 类

**Location / 位置**: `src/trading/exchange.py` or `src/trading/hyperliquid_client.py`

**Interface / 接口**: Same as `BinanceClient`

**Key Methods / 关键方法**:
- `__init__()` - Initialize with API credentials and environment (testnet/mainnet)
- `connect()` - Establish connection and authenticate
- `fetch_balance()` - Get account balance and margin
- `place_order()` - Place limit or market order
- `cancel_order()` - Cancel order by ID
- `cancel_all_orders()` - Cancel all open orders
- `fetch_order()` - Get order status
- `fetch_open_orders()` - Get all open orders
- `fetch_positions()` - Get all open positions
- `fetch_position()` - Get position for specific symbol
- `fetch_realized_pnl()` - Get realized PnL

**Error Handling / 错误处理**:
- Map Hyperliquid errors to standard exceptions
- 将 Hyperliquid 错误映射到标准异常
- Provide bilingual error messages
- 提供双语错误消息

---

#### 2. Configuration / 配置

**Environment Variables / 环境变量**:
```bash
# Hyperliquid API Credentials
HYPERLIQUID_API_KEY=your_api_key
HYPERLIQUID_API_SECRET=your_api_secret
HYPERLIQUID_TESTNET=true  # or false for mainnet
```

**Configuration File / 配置文件**: `src/shared/config.py`

Add Hyperliquid configuration similar to Binance:
添加类似于 Binance 的 Hyperliquid 配置：

```python
HYPERLIQUID_API_KEY = os.getenv("HYPERLIQUID_API_KEY")
HYPERLIQUID_API_SECRET = os.getenv("HYPERLIQUID_API_SECRET")
HYPERLIQUID_TESTNET = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"
```

---

#### 3. API Integration / API 集成

**Hyperliquid REST API / Hyperliquid REST API**:
- **Testnet**: https://testnet.hyperliquid.xyz
- **Mainnet**: https://api.hyperliquid.xyz

**Authentication / 认证**:
- Use API key and signature-based authentication
- 使用基于 API 密钥和签名的认证
- Follow Hyperliquid API documentation for signature generation
- 遵循 Hyperliquid API 文档进行签名生成

**API Endpoints / API 端点** (to be implemented):
- Connection/Health check
- 连接/健康检查
- Order placement/cancellation
- 订单下单/取消
- Position/balance queries
- 仓位/余额查询

---

#### 4. Error Mapping / 错误映射

**Standard Exceptions / 标准异常**:
- `AuthenticationError` - Invalid API credentials
- `AuthenticationError` - 无效的 API 凭证
- `InsufficientFunds` - Not enough balance for order
- `InsufficientFunds` - 订单余额不足
- `InvalidOrder` - Invalid order parameters
- `InvalidOrder` - 无效的订单参数
- `OrderNotFound` - Order ID not found
- `OrderNotFound` - 订单 ID 未找到
- `NetworkError` - Connection/network issues
- `NetworkError` - 连接/网络问题
- `RateLimitExceeded` - API rate limit exceeded
- `RateLimitExceeded` - API 频率限制超出

---

#### 5. UI Integration / UI 集成

**Exchange Selection / 交易所选择**:
- Add exchange dropdown/toggle in dashboard
- 在仪表盘中添加交易所下拉菜单/切换开关
- Display current exchange and connection status
- 显示当前交易所和连接状态
- Update configuration when exchange is changed
- 更改交易所时更新配置

**Location / 位置**: `templates/index.html` or `templates/LLMTrade.html`

**Hyperliquid Position and Balance Panel / Hyperliquid 仓位与余额面板**:
- Add dedicated panel in LLMTrade.html to display Hyperliquid position and balance information
- 在 LLMTrade.html 中添加专用面板以显示 Hyperliquid 仓位和余额信息
- Panel should display: account balance (available, total, margin), open positions table, unrealized/realized PnL, margin information
- 面板应显示：账户余额（可用、总计、保证金）、未平仓仓位表、未实现/已实现盈亏、保证金信息
- Support real-time updates when position or balance changes
- 支持仓位或余额变化时的实时更新
- Follow same design pattern as other panels (Fixed Spread Strategy Control Panel, Multi-LLM Evaluation, Current Orders)
- 遵循与其他面板相同的设计模式（固定价差策略控制面板、多 LLM 评估、当前订单）
- All UI text should be bilingual (English and Chinese)
- 所有 UI 文本应为双语（英文和中文）

**Location / 位置**: `templates/LLMTrade.html`

---

### Data Flow / 数据流

#### Order Placement Flow / 订单下单流程

```
User → UI → Server → StrategyInstance → OrderManager → HyperliquidClient → Hyperliquid API
                                                              ↓
                                                         Order Response
                                                              ↓
User ← UI ← Server ← StrategyInstance ← OrderManager ← HyperliquidClient
```

#### Position Tracking Flow / 仓位追踪流程

```
User → UI → Server → PerformanceTracker → HyperliquidClient → Hyperliquid API
                                                              ↓
                                                         Position Data
                                                              ↓
User ← UI ← Server ← PerformanceTracker ← HyperliquidClient
```

---

## Dependencies / 依赖

### Internal Dependencies / 内部依赖

- **CORE-001**: Exchange connection and authentication (Binance) - Provides reference implementation
- **CORE-001**: 交易所连接与认证（Binance）- 提供参考实现
- **CORE-002**: Order placement and management (Binance) - Provides OrderManager interface
- **CORE-002**: 订单下单与管理（Binance）- 提供 OrderManager 接口
- **CORE-003**: Position tracking and PnL calculation (Binance) - Provides PerformanceTracker interface
- **CORE-003**: 仓位追踪与盈亏计算（Binance）- 提供 PerformanceTracker 接口

### External Dependencies / 外部依赖

- **Hyperliquid API**: REST API access (testnet and mainnet)
- **Hyperliquid API**: REST API 访问（测试网和主网）
- **Python Libraries**: `requests`, `ccxt` (if using CCXT library), or custom HTTP client
- **Python 库**: `requests`、`ccxt`（如果使用 CCXT 库）或自定义 HTTP 客户端

### Blocks / 阻塞

- None (this is a new feature, doesn't block other features)
- 无（这是新功能，不阻塞其他功能）

---

## User Stories / 用户故事

This feature is implemented through 3 user stories:

此功能通过 3 个用户故事实现：

1. **US-CORE-004-A**: Hyperliquid Connection and Authentication
   - **US-CORE-004-A**: Hyperliquid 连接与认证
   - Story: `docs/stories/trading/US-CORE-004-A.md`
   - Duration: 1-2 days
   - 持续时间：1-2 天

2. **US-CORE-004-B**: Hyperliquid Order Management
   - **US-CORE-004-B**: Hyperliquid 订单管理
   - Story: `docs/stories/trading/US-CORE-004-B.md`
   - Duration: 2-3 days
   - 持续时间：2-3 天
   - Depends on: US-CORE-004-A
   - 依赖：US-CORE-004-A

3. **US-CORE-004-C**: Hyperliquid Position and Balance Tracking
   - **US-CORE-004-C**: Hyperliquid 仓位与余额追踪
   - Story: `docs/stories/trading/US-CORE-004-C.md`
   - Duration: 1-2 days
   - 持续时间：1-2 天
   - Depends on: US-CORE-004-A
   - 依赖：US-CORE-004-A

**Total Duration / 总持续时间**: 4-7 days  
**Epic / Epic**: EPIC-02: Hyperliquid Exchange Integration

---

## Success Criteria / 成功标准

### Functional Success / 功能成功

- ✅ Users can switch between Binance and Hyperliquid exchanges seamlessly
- ✅ 用户可以在 Binance 和 Hyperliquid 交易所之间无缝切换
- ✅ All trading operations (orders, positions, balance) work on Hyperliquid
- ✅ 所有交易操作（订单、仓位、余额）在 Hyperliquid 上工作
- ✅ Error handling provides clear, bilingual feedback
- ✅ 错误处理提供清晰的双语反馈
- ✅ Performance is comparable to Binance integration
- ✅ 性能与 Binance 集成相当

### Technical Success / 技术成功

- ✅ HyperliquidClient implements same interface as BinanceClient
- ✅ HyperliquidClient 实现与 BinanceClient 相同的接口
- ✅ Existing code (OrderManager, PerformanceTracker) works without modification
- ✅ 现有代码（OrderManager、PerformanceTracker）无需修改即可工作
- ✅ Test coverage meets project standards (>80%)
- ✅ 测试覆盖率满足项目标准（>80%）
- ✅ All acceptance criteria are met
- ✅ 所有验收标准都已满足

---

## Testing Strategy / 测试策略

### Unit Tests / 单元测试

- Mock Hyperliquid API responses
- 模拟 Hyperliquid API 响应
- Test all methods (connection, orders, positions)
- 测试所有方法（连接、订单、仓位）
- Test error handling and mapping
- 测试错误处理和映射

**Location / 位置**: `tests/unit/trading/test_hyperliquid_client.py`

### Integration Tests / 集成测试

- Test with Hyperliquid testnet
- 使用 Hyperliquid 测试网进行测试
- Test order placement and cancellation
- 测试订单下单和取消
- Test position and balance queries
- 测试仓位和余额查询

**Location / 位置**: `tests/integration/test_hyperliquid_integration.py`

### Smoke Tests / 冒烟测试

- Quick sanity check: Can connect and fetch balance
- 快速健全性检查：可以连接并获取余额
- Verify exchange selection works in UI
- 验证交易所选择在 UI 中工作

---

## Risks and Mitigation / 风险与缓解

### Risk 1: API Differences / 风险 1：API 差异

**Risk / 风险**: Hyperliquid API may have different structure than Binance, requiring more implementation effort.

Hyperliquid API 的结构可能与 Binance 不同，需要更多实现工作。

**Mitigation / 缓解**: 
- Study Hyperliquid API documentation thoroughly
- 彻底研究 Hyperliquid API 文档
- Create adapter layer to normalize API differences
- 创建适配器层以规范化 API 差异

### Risk 2: Error Handling Complexity / 风险 2：错误处理复杂性

**Risk / 风险**: Hyperliquid may have different error codes and messages than Binance.

Hyperliquid 可能有与 Binance 不同的错误代码和消息。

**Mitigation / 缓解**:
- Create comprehensive error mapping table
- 创建全面的错误映射表
- Test all error scenarios
- 测试所有错误场景

### Risk 3: Testing on Mainnet / 风险 3：主网测试

**Risk / 风险**: Testing on mainnet requires real funds and carries risk.

在主网上测试需要真实资金并存在风险。

**Mitigation / 缓解**:
- Use testnet for all development and testing
- 使用测试网进行所有开发和测试
- Only test on mainnet with small amounts after thorough testnet validation
- 仅在测试网充分验证后使用小额资金在主网上测试

---

## Related Documents / 相关文档

- **User Stories / 用户故事**:
  - `docs/stories/trading/US-CORE-004-A.md`
  - `docs/stories/trading/US-CORE-004-B.md`
  - `docs/stories/trading/US-CORE-004-C.md`
- **Epic / Epic**: EPIC-02: Hyperliquid Exchange Integration
- **Contract / 契约**: `contracts/trading.json#HyperliquidClient` (to be created)
- **Tests / 测试**: `tests/unit/trading/test_hyperliquid_client.py` (to be created)
- **User Guide / 用户指南**: `docs/user_guide/trading/hyperliquid_integration.md` (to be created)

---

## Owner / 负责人

**Agent**: Agent TRADING  
**Product Owner**: Agent PO  
**Architect**: Agent ARCH (for interface contract definition)

---

**Last Updated / 最后更新**: 2025-11-30  
**Status / 状态**: spec_defined  
**Next Step / 下一步**: Create user stories (already completed) → Plan approval (Step 4)

