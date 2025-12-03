# US-API-004: Hyperliquid LLM Evaluation Support / Hyperliquid LLM 评估支持

## Metadata / 元数据

- **id**: "US-API-004"
- **parent_feature**: "EPIC-02: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "EPIC-02: Hyperliquid 交易所集成"
- **module**: "web"
- **owner_agent**: "Agent WEB"

## User Story / 用户故事

**As a** quantitative trader  
**I want** the LLM evaluation API to support Hyperliquid exchange  
**So that** I can get AI-powered trading parameter suggestions for Hyperliquid in a dedicated Hyperliquid trading page

**作为** 量化交易员  
**我希望** LLM 评估 API 支持 Hyperliquid 交易所  
**以便** 我可以在专用的 Hyperliquid 交易页面中获取 AI 驱动的交易参数建议

## Acceptance Criteria / 验收标准

### AC-1: LLM Evaluation API Support for Hyperliquid / Hyperliquid 的 LLM 评估 API 支持

**Given** I call the LLM evaluation API with Hyperliquid exchange parameter  
**When** the API processes the request  
**Then** the system should use Hyperliquid exchange context, fetch Hyperliquid market data, and return LLM parameter suggestions for Hyperliquid

**Given** 我使用 Hyperliquid 交易所参数调用 LLM 评估 API  
**When** API 处理请求  
**Then** 系统应该使用 Hyperliquid 交易所上下文，获取 Hyperliquid 市场数据，并返回 Hyperliquid 的 LLM 参数建议

### AC-3: Hyperliquid Market Data Integration / Hyperliquid 市场数据集成

**Given** I am running LLM evaluation for Hyperliquid  
**When** the evaluation process starts  
**Then** the system should fetch current market data from Hyperliquid (price, spread, funding rate, etc.) and include it in the LLM evaluation context

**Given** 我正在为 Hyperliquid 运行 LLM 评估  
**When** 评估过程开始  
**Then** 系统应该从 Hyperliquid 获取当前市场数据（价格、价差、资金费率等）并将其包含在 LLM 评估上下文中

### AC-2: LLM Response Format / LLM 响应格式

**Given** I call the LLM evaluation API for Hyperliquid  
**When** the evaluation completes  
**Then** the API should return LLM suggestions (spread, quantity, skew, leverage) in a consistent format, with each LLM provider's recommendations for Hyperliquid trading

**Given** 我为 Hyperliquid 调用 LLM 评估 API  
**When** 评估完成  
**Then** API 应该以一致的格式返回 LLM 建议（价差、数量、倾斜因子、杠杆），包含每个 LLM 提供商针对 Hyperliquid 交易的推荐

### AC-3: Apply LLM Suggestions to Hyperliquid / 将 LLM 建议应用到 Hyperliquid

**Given** I have LLM evaluation results for Hyperliquid  
**When** I call the apply API with a specific LLM provider's suggestion  
**Then** the system should apply the suggested trading parameters to Hyperliquid exchange configuration and update the strategy settings

**Given** 我有 Hyperliquid 的 LLM 评估结果  
**When** 我使用特定 LLM 提供商的建议调用应用 API  
**Then** 系统应该将建议的交易参数应用到 Hyperliquid 交易所配置并更新策略设置

### AC-4: Exchange Context in LLM Input / LLM 输入中的交易所上下文

**Given** I call the LLM evaluation API for Hyperliquid  
**When** the API builds the LLM context  
**Then** the context should clearly indicate that the evaluation is for Hyperliquid exchange, including Hyperliquid-specific market data and account information

**Given** 我为 Hyperliquid 调用 LLM 评估 API  
**When** API 构建 LLM 上下文  
**Then** 上下文应该清楚地表明评估是针对 Hyperliquid 交易所的，包括 Hyperliquid 特定的市场数据和账户信息

### AC-5: Error Handling for Hyperliquid LLM Evaluation / Hyperliquid LLM 评估的错误处理

**Given** I attempt to call the LLM evaluation API for Hyperliquid when Hyperliquid is not connected  
**When** the API call fails  
**Then** the API should return a clear error message in Chinese and English indicating that Hyperliquid connection is required, and the system should handle the error gracefully

**Given** 我尝试在 Hyperliquid 未连接时为 Hyperliquid 调用 LLM 评估 API  
**When** API 调用失败  
**Then** API 应该返回清晰的中英文错误消息，表明需要 Hyperliquid 连接，系统应该优雅地处理错误

## Technical Notes / 技术备注

### Implementation Details / 实现细节

1. **API Endpoint Modification / API 端点修改**:
   - Update `/api/evaluation/run` endpoint to accept `exchange` parameter (default: "binance", can be "hyperliquid")
   - 更新 `/api/evaluation/run` 端点以接受 `exchange` 参数（默认："binance"，可以是 "hyperliquid"）
   - Modify evaluation logic to use appropriate exchange client based on parameter
   - 根据参数修改评估逻辑以使用适当的交易所客户端

2. **API Response Format / API 响应格式**:
   - API should return results in the same format as Binance evaluation
   - API 应该以与 Binance 评估相同的格式返回结果
   - Include exchange name in the response for clarity
   - 在响应中包含交易所名称以便清晰
   - Ensure response is compatible with UI components (to be implemented in US-UI-004)
   - 确保响应与 UI 组件兼容（将在 US-UI-004 中实现）

3. **Market Data Fetching / 市场数据获取**:
   - When exchange is "hyperliquid", use `HyperliquidClient` to fetch market data
   - 当交易所为 "hyperliquid" 时，使用 `HyperliquidClient` 获取市场数据
   - Ensure market data format is consistent for LLM evaluation context
   - 确保市场数据格式与 LLM 评估上下文一致

4. **LLM Context Building / LLM 上下文构建**:
   - Include exchange name in LLM prompt context
   - 在 LLM 提示上下文中包含交易所名称
   - Include exchange-specific market data (funding rates, leverage limits, etc.)
   - 包含交易所特定的市场数据（资金费率、杠杆限制等）

5. **Configuration Application / 配置应用**:
   - When applying LLM suggestions, ensure configuration is applied to the correct exchange
   - 应用 LLM 建议时，确保配置应用于正确的交易所
   - Update strategy configuration for Hyperliquid when suggestions are applied
   - 应用建议时更新 Hyperliquid 的策略配置

6. **Error Handling / 错误处理**:
   - Check exchange connection status before running evaluation
   - 运行评估前检查交易所连接状态
   - Provide clear error messages if exchange is not connected
   - 如果交易所未连接，提供清晰的错误消息
   - Handle API errors gracefully with bilingual messages
   - 使用双语消息优雅地处理 API 错误

## Related / 相关

- Spec: `docs/specs/web/API-004.md` (to be created)
- Feature: `API-004` (Hyperliquid LLM Evaluation Support)
- Epic: `EPIC-02` (Hyperliquid Exchange Integration)
- Related UI Story: `US-UI-004` (Dedicated Hyperliquid Trading Page - can also use this LLM evaluation functionality)
- Depends on: `US-CORE-004-A` (Hyperliquid connection must be working), `US-CORE-004-C` (Position tracking for market context)
- Tests: `tests/unit/web/test_hyperliquid_llm_evaluation.py` (to be created)
- Contract: `contracts/web.json#EvaluationAPI#ExchangeParameter` (to be created)

## Implementation Note / 实现说明

**Note / 说明**: This user story focuses on **backend API support** for Hyperliquid LLM evaluation. The UI for displaying and interacting with Hyperliquid LLM suggestions will be implemented in **US-UI-004** (Dedicated Hyperliquid Trading Page). This separation allows the API to be reusable and the UI to be implemented in a dedicated page as required.

**注意 / 注意**: 此用户故事专注于 Hyperliquid LLM 评估的**后端 API 支持**。用于显示和交互 Hyperliquid LLM 建议的 UI 将在 **US-UI-004**（专用 Hyperliquid 交易页面）中实现。这种分离使 API 可重用，UI 可以在专用页面中实现。

## Owner / 负责人

Agent: Agent WEB

## Dependencies / 依赖关系

- **Depends on**: 
  - US-CORE-004-A (Hyperliquid connection must be working)
  - US-CORE-004-C (Position tracking for market context in LLM evaluation)
  - Existing Multi-LLM Evaluation functionality (LLM-001)
- **依赖**: 
  - US-CORE-004-A（Hyperliquid 连接必须正常工作）
  - US-CORE-004-C（LLM 评估中用于市场上下文的仓位追踪）
  - 现有的多 LLM 评估功能（LLM-001）
- **Blocks**: None
- **阻塞**: 无

