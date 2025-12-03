# US-UI-004: Dedicated Hyperliquid Trading Page / 专用 Hyperliquid 交易页面

## Metadata / 元数据

- **id**: "US-UI-004"
- **parent_feature**: "EPIC-02: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "EPIC-02: Hyperliquid 交易所集成"
- **module**: "web"
- **owner_agent**: "Agent WEB"

## User Story / 用户故事

**As a** quantitative trader  
**I want** a dedicated Hyperliquid trading page (similar to LLMTrade.html but specifically for Hyperliquid)  
**So that** I can have a focused interface for all Hyperliquid trading activities including strategy control, LLM evaluation, position tracking, and order management

**作为** 量化交易员  
**我希望** 有一个专用的 Hyperliquid 交易页面（类似于 LLMTrade.html，但专门用于 Hyperliquid）  
**以便** 我可以有一个专注于所有 Hyperliquid 交易活动的界面，包括策略控制、LLM 评估、仓位追踪和订单管理

## Acceptance Criteria / 验收标准

### AC-1: Dedicated Page Creation / 专用页面创建

**Given** I navigate to the Hyperliquid trading page  
**When** the page loads  
**Then** I should see a dedicated page (e.g., `HyperliquidTrade.html` or `/hyperliquid`) with Hyperliquid-specific branding and layout, similar to LLMTrade.html but focused on Hyperliquid

**Given** 我导航到 Hyperliquid 交易页面  
**When** 页面加载  
**Then** 我应该看到一个专用页面（例如 `HyperliquidTrade.html` 或 `/hyperliquid`），具有 Hyperliquid 特定的品牌和布局，类似于 LLMTrade.html 但专注于 Hyperliquid

### AC-2: Strategy Control Panel / 策略控制面板

**Given** I am on the Hyperliquid trading page  
**When** I view the strategy control panel  
**Then** I should see controls for Fixed Spread Strategy parameters (spread, quantity, leverage) specifically for Hyperliquid, with Hyperliquid-specific trading pair options

**Given** 我在 Hyperliquid 交易页面上  
**When** 我查看策略控制面板  
**Then** 我应该看到固定价差策略参数（价差、数量、杠杆）的控件，专门用于 Hyperliquid，包含 Hyperliquid 特定的交易对选项

### AC-3: Hyperliquid Position and Balance Panel / Hyperliquid 仓位与余额面板

**Given** I am on the Hyperliquid trading page and connected to Hyperliquid  
**When** I view the position and balance panel  
**Then** I should see my Hyperliquid account balance (available, total, margin), open positions table, unrealized/realized PnL, and margin information displayed in a dedicated panel

**Given** 我在 Hyperliquid 交易页面上且已连接到 Hyperliquid  
**When** 我查看仓位和余额面板  
**Then** 我应该看到我的 Hyperliquid 账户余额（可用、总计、保证金）、未平仓仓位表、未实现/已实现盈亏和保证金信息显示在专用面板中

### AC-4: Hyperliquid LLM Evaluation / Hyperliquid LLM 评估

**Given** I am on the Hyperliquid trading page  
**When** I use the Multi-LLM Evaluation section  
**Then** I should be able to run LLM evaluation specifically for Hyperliquid, get trading parameter suggestions, and apply them to Hyperliquid exchange configuration

**Given** 我在 Hyperliquid 交易页面上  
**When** 我使用多 LLM 评估部分  
**Then** 我应该能够专门为 Hyperliquid 运行 LLM 评估，获取交易参数建议，并将其应用到 Hyperliquid 交易所配置

### AC-5: Hyperliquid Order Management / Hyperliquid 订单管理

**Given** I am on the Hyperliquid trading page  
**When** I view the orders section  
**Then** I should see my current Hyperliquid orders, be able to place new orders, cancel orders, and view order history specific to Hyperliquid

**Given** 我在 Hyperliquid 交易页面上  
**When** 我查看订单部分  
**Then** 我应该看到我当前的 Hyperliquid 订单，能够下新订单、取消订单，并查看特定于 Hyperliquid 的订单历史

### AC-6: Real-time Updates / 实时更新

**Given** I am viewing the Hyperliquid trading page  
**When** my positions, balance, or orders change on Hyperliquid  
**Then** the UI should automatically refresh and display updated information without requiring manual page refresh

**Given** 我正在查看 Hyperliquid 交易页面  
**When** 我在 Hyperliquid 上的仓位、余额或订单发生变化  
**Then** UI 应该自动刷新并显示更新的信息，无需手动刷新页面

### AC-7: Navigation and Integration / 导航与集成

**Given** I am on the main dashboard or LLMTrade page  
**When** I want to access Hyperliquid trading  
**Then** I should see a link or button to navigate to the dedicated Hyperliquid trading page

**Given** 我在主仪表盘或 LLMTrade 页面上  
**When** 我想访问 Hyperliquid 交易  
**Then** 我应该看到一个链接或按钮来导航到专用的 Hyperliquid 交易页面

### AC-8: Bilingual Support / 双语支持

**Given** I am viewing the Hyperliquid trading page  
**When** I see any text or labels  
**Then** all text should be displayed in both English and Chinese, consistent with the rest of the application

**Given** 我正在查看 Hyperliquid 交易页面  
**When** 我看到任何文本或标签  
**Then** 所有文本应该以英文和中文显示，与应用程序的其余部分保持一致

### AC-9: Connection Status Display / 连接状态显示

**Given** I am on the Hyperliquid trading page  
**When** I view the page header or status area  
**Then** I should see the Hyperliquid connection status, current trading pair, and any connection errors clearly displayed

**Given** 我在 Hyperliquid 交易页面上  
**When** 我查看页面标题或状态区域  
**Then** 我应该看到 Hyperliquid 连接状态、当前交易对以及任何连接错误清晰显示

### AC-10: Error Handling / 错误处理

**Given** I am on the Hyperliquid trading page and Hyperliquid is not connected  
**When** I attempt to use any trading features  
**Then** I should receive clear error messages in Chinese and English indicating that Hyperliquid connection is required, and the system should handle errors gracefully

**Given** 我在 Hyperliquid 交易页面上且 Hyperliquid 未连接  
**When** 我尝试使用任何交易功能  
**Then** 我应该收到清晰的中英文错误消息，表明需要 Hyperliquid 连接，系统应该优雅地处理错误

## Technical Notes / 技术备注

### Implementation Details / 实现细节

1. **Page Structure / 页面结构**:
   - Create new HTML file: `templates/HyperliquidTrade.html` or route: `/hyperliquid`
   - 创建新的 HTML 文件：`templates/HyperliquidTrade.html` 或路由：`/hyperliquid`
   - Follow similar structure to `LLMTrade.html` but with Hyperliquid-specific content
   - 遵循与 `LLMTrade.html` 类似的结构，但包含 Hyperliquid 特定的内容
   - Include panels for: Strategy Control, Position/Balance, LLM Evaluation, Orders
   - 包含面板：策略控制、仓位/余额、LLM 评估、订单

2. **API Integration / API 集成**:
   - All API calls should use Hyperliquid exchange context
   - 所有 API 调用应使用 Hyperliquid 交易所上下文
   - Ensure exchange parameter is set to "hyperliquid" for all requests
   - 确保所有请求的交易所参数设置为 "hyperliquid"
   - Reuse existing API endpoints with exchange parameter
   - 使用带有交易所参数的现有 API 端点

3. **UI Components / UI 组件**:
   - Strategy Control Panel: Similar to LLMTrade.html but for Hyperliquid
   - 策略控制面板：类似于 LLMTrade.html 但用于 Hyperliquid
   - Position/Balance Panel: Display Hyperliquid-specific position and balance data
   - 仓位/余额面板：显示 Hyperliquid 特定的仓位和余额数据
   - LLM Evaluation Panel: Multi-LLM evaluation with Hyperliquid context
   - LLM 评估面板：具有 Hyperliquid 上下文的多 LLM 评估
   - Orders Panel: Display and manage Hyperliquid orders
   - 订单面板：显示和管理 Hyperliquid 订单

4. **Navigation / 导航**:
   - Add link/button in main dashboard (`index.html`) to navigate to Hyperliquid page
   - 在主仪表盘（`index.html`）中添加链接/按钮以导航到 Hyperliquid 页面
   - Add link/button in LLMTrade.html to navigate to Hyperliquid page
   - 在 LLMTrade.html 中添加链接/按钮以导航到 Hyperliquid 页面
   - Include "Back to Dashboard" link in Hyperliquid page
   - 在 Hyperliquid 页面中包含"返回仪表盘"链接

5. **Data Fetching / 数据获取**:
   - Use HyperliquidClient for all data fetching
   - 使用 HyperliquidClient 进行所有数据获取
   - Implement real-time updates using polling or WebSocket (if available)
   - 使用轮询或 WebSocket（如果可用）实现实时更新
   - Cache data appropriately to reduce API calls
   - 适当缓存数据以减少 API 调用

6. **Error Handling / 错误处理**:
   - Check Hyperliquid connection status before displaying data
   - 在显示数据前检查 Hyperliquid 连接状态
   - Display clear error messages if connection fails
   - 如果连接失败，显示清晰的错误消息
   - Handle API errors gracefully with bilingual messages
   - 使用双语消息优雅地处理 API 错误

7. **Styling / 样式**:
   - Follow same design pattern as LLMTrade.html
   - 遵循与 LLMTrade.html 相同的设计模式
   - Use consistent color scheme and layout
   - 使用一致的颜色方案和布局
   - Ensure responsive design for different screen sizes
   - 确保不同屏幕尺寸的响应式设计

## Related / 相关

- Spec: `docs/specs/web/UI-004.md` (to be created)
- Feature: `UI-004` (Dedicated Hyperliquid Trading Page)
- Epic: `EPIC-02` (Hyperliquid Exchange Integration)
- Depends on: 
  - `US-CORE-004-A` (Hyperliquid connection must be working)
  - `US-CORE-004-B` (Order management functionality)
  - `US-CORE-004-C` (Position tracking functionality)
  - `US-API-004` (LLM evaluation functionality, can be adapted for this page)
- Tests: `tests/unit/web/test_hyperliquid_trade_page.py` (to be created)
- Contract: `contracts/web.json#HyperliquidTradePage` (to be created)

## Owner / 负责人

Agent: Agent WEB

## Dependencies / 依赖关系

- **Depends on**: 
  - US-CORE-004-A (Hyperliquid connection must be working)
  - US-CORE-004-B (Order management functionality)
  - US-CORE-004-C (Position tracking functionality)
  - US-API-004 (LLM evaluation functionality, can be adapted for this page)
- **依赖**: 
  - US-CORE-004-A（Hyperliquid 连接必须正常工作）
  - US-CORE-004-B（订单管理功能）
  - US-CORE-004-C（仓位追踪功能）
  - US-API-004（LLM 评估功能，可以适配到此页面）
- **Blocks**: None
- **阻塞**: 无

