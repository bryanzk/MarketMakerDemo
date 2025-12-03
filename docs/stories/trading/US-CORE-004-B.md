# US-CORE-004-B: Hyperliquid Order Management / Hyperliquid 订单管理

## Metadata / 元数据

- **id**: "US-CORE-004-B"
- **parent_feature**: "EPIC-02: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "EPIC-02: Hyperliquid 交易所集成"
- **module**: "trading"
- **owner_agent**: "Agent TRADING"

## User Story / 用户故事

**As a** quantitative trader  
**I want** to place, cancel, and query orders on Hyperliquid exchange  
**So that** I can execute trading strategies on Hyperliquid just like I do on Binance

**作为** 量化交易员  
**我希望** 在 Hyperliquid 交易所上下单、取消和查询订单  
**以便** 我可以在 Hyperliquid 上执行交易策略，就像在 Binance 上一样

## Acceptance Criteria / 验收标准

### AC-1: Limit Order Placement / 限价单下单

**Given** I am connected to Hyperliquid and have sufficient balance  
**When** I place a limit order (buy or sell) with price and quantity  
**Then** the order should be placed successfully and I should receive order confirmation with order ID

**Given** 我已连接到 Hyperliquid 并有足够的余额  
**When** 我下一个限价单（买入或卖出），包含价格和数量  
**Then** 订单应该成功下单，我应该收到包含订单 ID 的订单确认

### AC-2: Market Order Placement / 市价单下单

**Given** I am connected to Hyperliquid and have sufficient balance  
**When** I place a market order (buy or sell) with quantity  
**Then** the order should be executed immediately and I should receive fill confirmation

**Given** 我已连接到 Hyperliquid 并有足够的余额  
**When** 我下一个市价单（买入或卖出），包含数量  
**Then** 订单应该立即执行，我应该收到成交确认

### AC-3: Order Cancellation / 订单取消

**Given** I have an open order on Hyperliquid  
**When** I cancel the order using its order ID  
**Then** the order should be cancelled successfully and I should receive cancellation confirmation

**Given** 我在 Hyperliquid 上有一个未成交订单  
**When** 我使用订单 ID 取消订单  
**Then** 订单应该成功取消，我应该收到取消确认

### AC-4: Cancel All Orders / 取消所有订单

**Given** I have multiple open orders on Hyperliquid  
**When** I request to cancel all open orders  
**Then** all orders should be cancelled and I should receive confirmation for each cancellation

**Given** 我在 Hyperliquid 上有多个未成交订单  
**When** 我请求取消所有未成交订单  
**Then** 所有订单应该被取消，我应该收到每个取消的确认

### AC-5: Order Status Query / 订单状态查询

**Given** I have placed an order on Hyperliquid  
**When** I query the order status using order ID  
**Then** I should receive order details including status (open, filled, cancelled), price, quantity, filled quantity, and timestamp

**Given** 我在 Hyperliquid 上已下一个订单  
**When** 我使用订单 ID 查询订单状态  
**Then** 我应该收到订单详情，包括状态（未成交、已成交、已取消）、价格、数量、已成交数量和时间戳

### AC-6: Open Orders Query / 未成交订单查询

**Given** I have multiple orders on Hyperliquid (some open, some filled)  
**When** I query all open orders  
**Then** I should receive a list of only open orders with their details

**Given** 我在 Hyperliquid 上有多个订单（一些未成交，一些已成交）  
**When** 我查询所有未成交订单  
**Then** 我应该收到仅包含未成交订单及其详情的列表

### AC-7: Order History / 订单历史

**Given** I have placed multiple orders on Hyperliquid  
**When** I query order history  
**Then** I should receive a list of recent orders (filled, cancelled, or open) with timestamps

**Given** 我在 Hyperliquid 上已下多个订单  
**When** 我查询订单历史  
**Then** 我应该收到最近订单（已成交、已取消或未成交）的列表，包含时间戳

### AC-8: Order Error Handling / 订单错误处理

**Given** I attempt to place an order with invalid parameters (e.g., insufficient balance, invalid price)  
**When** the order placement fails  
**Then** I should receive a clear error message in Chinese and English explaining the failure reason

**Given** 我尝试使用无效参数下单（例如，余额不足、无效价格）  
**When** 订单下单失败  
**Then** 我应该收到清晰的中英文错误消息，说明失败原因

### AC-9: Order Idempotency / 订单幂等性

**Given** I place the same order twice with the same parameters  
**When** both requests are processed  
**Then** the system should handle idempotency correctly (either create one order or return existing order ID)

**Given** 我使用相同参数两次下相同的订单  
**When** 两个请求都被处理  
**Then** 系统应该正确处理幂等性（要么创建一个订单，要么返回现有订单 ID）

### AC-10: Integration with Order Manager / 与订单管理器集成

**Given** the Hyperliquid client is connected and OrderManager is initialized  
**When** OrderManager uses HyperliquidClient to place/cancel orders  
**Then** orders should be synchronized correctly and tracked in OrderManager

**Given** Hyperliquid 客户端已连接且 OrderManager 已初始化  
**When** OrderManager 使用 HyperliquidClient 下单/取消订单  
**Then** 订单应该正确同步并在 OrderManager 中跟踪

## Technical Notes / 技术备注

### Implementation Details / 实现细节

1. **Order Methods / 订单方法**:
   - `place_order(side, type, price, quantity)` - Place limit or market order
   - `place_order(side, type, price, quantity)` - 下限价或市价单
   - `cancel_order(order_id)` - Cancel specific order
   - `cancel_order(order_id)` - 取消特定订单
   - `cancel_all_orders()` - Cancel all open orders
   - `cancel_all_orders()` - 取消所有未成交订单
   - `fetch_order(order_id)` - Get order status
   - `fetch_order(order_id)` - 获取订单状态
   - `fetch_open_orders()` - Get all open orders
   - `fetch_open_orders()` - 获取所有未成交订单
   - `fetch_orders_history()` - Get order history
   - `fetch_orders_history()` - 获取订单历史

2. **Order Format / 订单格式**:
   - Follow Hyperliquid API order format
   - 遵循 Hyperliquid API 订单格式
   - Convert to/from internal order format for consistency with Binance
   - 转换为/从内部订单格式，以与 Binance 保持一致

3. **Error Handling / 错误处理**:
   - Map Hyperliquid order errors to standard exceptions (InsufficientFunds, InvalidOrder, OrderNotFound)
   - 将 Hyperliquid 订单错误映射到标准异常（余额不足、无效订单、订单未找到）
   - Provide bilingual error messages
   - 提供双语错误消息

4. **Testing / 测试**:
   - Unit tests with mocked Hyperliquid API responses
   - 使用模拟的 Hyperliquid API 响应进行单元测试
   - Integration tests with Hyperliquid testnet
   - 与 Hyperliquid 测试网的集成测试

5. **Interface Contract / 接口契约**:
   - Ensure `HyperliquidClient` implements same order interface as `BinanceClient`
   - 确保 `HyperliquidClient` 实现与 `BinanceClient` 相同的订单接口
   - Update `contracts/trading.json` with order method specifications
   - 使用订单方法规范更新 `contracts/trading.json`

## Related / 相关

- Spec: `docs/specs/trading/CORE-004.md` (to be created)
- Feature: `CORE-004` (Hyperliquid Exchange Integration)
- Epic: `EPIC-02` (Hyperliquid Exchange Integration)
- Tests: `tests/unit/trading/test_hyperliquid_orders.py` (to be created)
- Contract: `contracts/trading.json#HyperliquidClient#OrderMethods` (to be created)
- Depends on: `US-CORE-004-A` (requires connection to be working)

## Owner / 负责人

Agent: Agent TRADING

## Dependencies / 依赖关系

- **Depends on**: US-CORE-004-A (Hyperliquid connection must be working)
- **依赖**: US-CORE-004-A（Hyperliquid 连接必须正常工作）
- **Blocks**: None (can be developed in parallel with US-CORE-004-C)
- **阻塞**: 无（可以与 US-CORE-004-C 并行开发）

