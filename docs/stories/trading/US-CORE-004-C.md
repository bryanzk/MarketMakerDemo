# US-CORE-004-C: Hyperliquid Position and Balance Tracking / Hyperliquid 仓位与余额追踪

## Metadata / 元数据

- **id**: "US-CORE-004-C"
- **parent_feature**: "EPIC-02: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "EPIC-02: Hyperliquid 交易所集成"
- **module**: "trading"
- **owner_agent**: "Agent TRADING"

## User Story / 用户故事

**As a** quantitative trader  
**I want** to track my positions, balance, and PnL on Hyperliquid exchange  
**So that** I can monitor my trading performance and risk exposure on Hyperliquid

**作为** 量化交易员  
**我希望** 追踪我在 Hyperliquid 交易所上的仓位、余额和盈亏  
**以便** 我可以监控我在 Hyperliquid 上的交易表现和风险敞口

## Acceptance Criteria / 验收标准

### AC-1: Balance Fetching / 余额获取

**Given** I am connected to Hyperliquid  
**When** I fetch my account balance  
**Then** I should receive my available balance, total balance, and margin information in USDT

**Given** 我已连接到 Hyperliquid  
**When** 我获取我的账户余额  
**Then** 我应该收到我的可用余额、总余额和保证金信息（以 USDT 为单位）

### AC-2: Position Tracking / 仓位追踪

**Given** I have open positions on Hyperliquid  
**When** I fetch my current positions  
**Then** I should receive position details including symbol, side (long/short), size, entry price, mark price, and unrealized PnL

**Given** 我在 Hyperliquid 上有未平仓仓位  
**When** 我获取我的当前仓位  
**Then** 我应该收到仓位详情，包括交易对、方向（多头/空头）、数量、开仓价格、标记价格和未实现盈亏

### AC-3: Unrealized PnL Calculation / 未实现盈亏计算

**Given** I have open positions on Hyperliquid  
**When** I calculate unrealized PnL  
**Then** it should be calculated correctly based on entry price, current mark price, and position size

**Given** 我在 Hyperliquid 上有未平仓仓位  
**When** 我计算未实现盈亏  
**Then** 应该根据开仓价格、当前标记价格和仓位数量正确计算

### AC-4: Realized PnL Tracking / 已实现盈亏追踪

**Given** I have closed positions on Hyperliquid  
**When** I query realized PnL  
**Then** I should receive realized PnL for closed positions with timestamps and trade details

**Given** 我在 Hyperliquid 上有已平仓仓位  
**When** 我查询已实现盈亏  
**Then** 我应该收到已平仓仓位的已实现盈亏，包含时间戳和交易详情

### AC-5: Position History / 仓位历史

**Given** I have opened and closed multiple positions on Hyperliquid  
**When** I query position history  
**Then** I should receive a list of historical positions (both open and closed) with timestamps

**Given** 我在 Hyperliquid 上已开仓和平仓多个仓位  
**When** 我查询仓位历史  
**Then** 我应该收到历史仓位（包括未平仓和已平仓）的列表，包含时间戳

### AC-6: Margin Information / 保证金信息

**Given** I am connected to Hyperliquid  
**When** I fetch margin information  
**Then** I should receive margin used, margin available, margin ratio, and liquidation price (if applicable)

**Given** 我已连接到 Hyperliquid  
**When** 我获取保证金信息  
**Then** 我应该收到已用保证金、可用保证金、保证金比率和清算价格（如适用）

### AC-7: Multi-Symbol Position Support / 多交易对仓位支持

**Given** I have positions in multiple symbols on Hyperliquid (e.g., ETH/USDT, BTC/USDT)  
**When** I fetch all positions  
**Then** I should receive positions for all symbols with their respective details

**Given** 我在 Hyperliquid 上有多个交易对的仓位（例如 ETH/USDT, BTC/USDT）  
**When** 我获取所有仓位  
**Then** 我应该收到所有交易对的仓位及其各自的详情

### AC-8: Position Updates / 仓位更新

**Given** I have an open position and new trades occur  
**When** I refresh position data  
**Then** position details should be updated with latest mark price, unrealized PnL, and size changes

**Given** 我有一个未平仓仓位且发生新交易  
**When** 我刷新仓位数据  
**Then** 仓位详情应该更新为最新的标记价格、未实现盈亏和数量变化

### AC-9: Integration with Performance Tracker / 与性能追踪器集成

**Given** the Hyperliquid client is connected and PerformanceTracker is initialized  
**When** PerformanceTracker uses HyperliquidClient to fetch positions and PnL  
**Then** performance metrics should be calculated correctly and displayed in the dashboard

**Given** Hyperliquid 客户端已连接且 PerformanceTracker 已初始化  
**When** PerformanceTracker 使用 HyperliquidClient 获取仓位和盈亏  
**Then** 性能指标应该正确计算并显示在仪表盘中

### AC-10: Error Handling / 错误处理

**Given** I attempt to fetch position data when API is unavailable  
**When** the request fails  
**Then** I should receive a clear error message in Chinese and English, and the system should handle the error gracefully

**Given** 我尝试在 API 不可用时获取仓位数据  
**When** 请求失败  
**Then** 我应该收到清晰的中英文错误消息，系统应该优雅地处理错误

## UI Implementation Note / UI 实现说明

**Note / 说明**: UI display requirements for Hyperliquid position and balance tracking are covered in **US-UI-004** (Dedicated Hyperliquid Trading Page). This user story (US-CORE-004-C) focuses on the backend API functionality for position and balance tracking.

**注意 / 注意**: Hyperliquid 仓位和余额追踪的 UI 显示需求在 **US-UI-004**（专用 Hyperliquid 交易页面）中涵盖。此用户故事（US-CORE-004-C）专注于仓位和余额追踪的后端 API 功能。

## Technical Notes / 技术备注

### Implementation Details / 实现细节

1. **Position Methods / 仓位方法**:
   - `fetch_balance()` - Get account balance and margin
   - `fetch_balance()` - 获取账户余额和保证金
   - `fetch_positions()` - Get all open positions
   - `fetch_positions()` - 获取所有未平仓仓位
   - `fetch_position(symbol)` - Get position for specific symbol
   - `fetch_position(symbol)` - 获取特定交易对的仓位
   - `fetch_position_history()` - Get position history
   - `fetch_position_history()` - 获取仓位历史
   - `fetch_realized_pnl()` - Get realized PnL
   - `fetch_realized_pnl()` - 获取已实现盈亏

2. **Data Format / 数据格式**:
   - Follow Hyperliquid API response format
   - 遵循 Hyperliquid API 响应格式
   - Convert to/from internal format for consistency with Binance
   - 转换为/从内部格式，以与 Binance 保持一致
   - Ensure all monetary values are in USDT
   - 确保所有货币值都以 USDT 为单位

3. **PnL Calculation / 盈亏计算**:
   - Unrealized PnL = (mark_price - entry_price) × size × side_multiplier
   - 未实现盈亏 = (标记价格 - 开仓价格) × 数量 × 方向乘数
   - Realized PnL = sum of closed position PnL
   - 已实现盈亏 = 已平仓仓位盈亏的总和
   - Handle both long and short positions correctly
   - 正确处理多头和空头仓位

4. **Caching / 缓存**:
   - Cache position data to reduce API calls
   - 缓存仓位数据以减少 API 调用
   - Implement cache invalidation on position updates
   - 在仓位更新时实现缓存失效

5. **Testing / 测试**:
   - Unit tests with mocked Hyperliquid API responses
   - 使用模拟的 Hyperliquid API 响应进行单元测试
   - Integration tests with Hyperliquid testnet
   - 与 Hyperliquid 测试网的集成测试
   - Test PnL calculations with various scenarios
   - 使用各种场景测试盈亏计算

6. **Interface Contract / 接口契约**:
   - Ensure `HyperliquidClient` implements same position interface as `BinanceClient`
   - 确保 `HyperliquidClient` 实现与 `BinanceClient` 相同的仓位接口
   - Update `contracts/trading.json` with position method specifications
   - 使用仓位方法规范更新 `contracts/trading.json`

## Related / 相关

- Spec: `docs/specs/trading/CORE-004.md`
- Feature: `CORE-004` (Hyperliquid Exchange Integration)
- Epic: `EPIC-02` (Hyperliquid Exchange Integration)
- UI Story: `US-UI-004` (Dedicated Hyperliquid Trading Page - contains UI requirements)
- Tests: `tests/unit/trading/test_hyperliquid_positions.py` (to be created)
- Contract: `contracts/trading.json#HyperliquidClient#PositionMethods` (to be created)
- Depends on: `US-CORE-004-A` (requires connection to be working)

## Owner / 负责人

Agent: Agent TRADING

## Dependencies / 依赖关系

- **Depends on**: US-CORE-004-A (Hyperliquid connection must be working)
- **依赖**: US-CORE-004-A（Hyperliquid 连接必须正常工作）
- **Blocks**: None (can be developed in parallel with US-CORE-004-B)
- **阻塞**: 无（可以与 US-CORE-004-B 并行开发）

