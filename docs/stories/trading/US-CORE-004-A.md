# US-CORE-004-A: Hyperliquid Connection and Authentication / Hyperliquid 连接与认证

## Metadata / 元数据

- **id**: "US-CORE-004-A"
- **parent_feature**: "EPIC-02: Hyperliquid Exchange Integration"
- **parent_feature_zh**: "EPIC-02: Hyperliquid 交易所集成"
- **module**: "trading"
- **owner_agent**: "Agent TRADING"

## User Story / 用户故事

**As a** quantitative trader  
**I want** to connect to Hyperliquid exchange and authenticate with my API credentials  
**So that** I can access Hyperliquid trading API and use it as an alternative to Binance

**作为** 量化交易员  
**我希望** 连接到 Hyperliquid 交易所并使用我的 API 凭证进行认证  
**以便** 我可以访问 Hyperliquid 交易 API 并将其作为 Binance 的替代方案

## Acceptance Criteria / 验收标准

### AC-1: Hyperliquid Client Implementation / Hyperliquid 客户端实现

**Given** the system has Hyperliquid API credentials configured  
**When** I initialize a `HyperliquidClient` instance  
**Then** it should create a connection to Hyperliquid API (testnet or mainnet based on configuration)

**Given** 系统已配置 Hyperliquid API 凭证  
**When** 我初始化一个 `HyperliquidClient` 实例  
**Then** 它应该创建到 Hyperliquid API 的连接（根据配置使用测试网或主网）

### AC-2: Authentication Success / 认证成功

**Given** valid Hyperliquid API credentials are provided  
**When** the client attempts to authenticate  
**Then** authentication should succeed and return connection status

**Given** 提供了有效的 Hyperliquid API 凭证  
**When** 客户端尝试认证  
**Then** 认证应该成功并返回连接状态

### AC-3: Authentication Failure Handling / 认证失败处理

**Given** invalid or missing Hyperliquid API credentials  
**When** the client attempts to authenticate  
**Then** it should raise a clear authentication error with user-friendly message in Chinese and English

**Given** 提供了无效或缺失的 Hyperliquid API 凭证  
**When** 客户端尝试认证  
**Then** 应该抛出清晰的认证错误，并提供中英文用户友好的错误消息

### AC-4: Testnet and Mainnet Support / 测试网和主网支持

**Given** the system is configured for testnet or mainnet  
**When** I initialize the Hyperliquid client  
**Then** it should connect to the correct environment (testnet.hyperliquid.xyz or api.hyperliquid.xyz)

**Given** 系统配置为测试网或主网  
**When** 我初始化 Hyperliquid 客户端  
**Then** 它应该连接到正确的环境（testnet.hyperliquid.xyz 或 api.hyperliquid.xyz）

### AC-5: Health Monitoring / 健康监控

**Given** the Hyperliquid client is connected  
**When** I check the connection health  
**Then** it should return connection status (connected/disconnected) and last successful API call timestamp

**Given** Hyperliquid 客户端已连接  
**When** 我检查连接健康状态  
**Then** 应该返回连接状态（已连接/已断开）和最后一次成功的 API 调用时间戳

### AC-6: Connection Error Handling / 连接错误处理

**Given** the Hyperliquid API is temporarily unavailable  
**When** the client attempts to connect  
**Then** it should handle network errors gracefully and provide retry mechanism with exponential backoff

**Given** Hyperliquid API 暂时不可用  
**When** 客户端尝试连接  
**Then** 应该优雅地处理网络错误，并提供带指数退避的重试机制

### AC-7: Exchange Selection / 交易所选择

**Given** both Binance and Hyperliquid clients are available  
**When** I select Hyperliquid from the exchange dropdown in the UI  
**Then** the system should switch to use HyperliquidClient and display the connection status

**Given** Binance 和 Hyperliquid 客户端都可用  
**When** 我在 UI 中从交易所下拉菜单中选择 Hyperliquid  
**Then** 系统应该切换到使用 HyperliquidClient 并显示连接状态

## Technical Notes / 技术备注

### Implementation Details / 实现细节

1. **Class Structure / 类结构**:
   - Create `HyperliquidClient` class in `src/trading/exchange.py` or separate file
   - 在 `src/trading/exchange.py` 或单独文件中创建 `HyperliquidClient` 类
   - Follow similar pattern to `BinanceClient` for consistency
   - 遵循与 `BinanceClient` 类似的模式以保持一致性

2. **API Integration / API 集成**:
   - Use Hyperliquid REST API (https://api.hyperliquid.xyz or https://testnet.hyperliquid.xyz)
   - 使用 Hyperliquid REST API
   - Implement authentication using API key and signature
   - 使用 API 密钥和签名实现认证

3. **Error Mapping / 错误映射**:
   - Map Hyperliquid-specific errors to standard exceptions
   - 将 Hyperliquid 特定错误映射到标准异常
   - Ensure error messages are bilingual (Chinese and English)
   - 确保错误消息是双语的（中文和英文）

4. **Configuration / 配置**:
   - Add Hyperliquid API credentials to environment variables
   - 将 Hyperliquid API 凭证添加到环境变量
   - Support `HYPERLIQUID_API_KEY` and `HYPERLIQUID_API_SECRET`
   - 支持 `HYPERLIQUID_API_KEY` 和 `HYPERLIQUID_API_SECRET`
   - Add `HYPERLIQUID_TESTNET` flag for environment selection
   - 添加 `HYPERLIQUID_TESTNET` 标志用于环境选择

5. **Interface Contract / 接口契约**:
   - `HyperliquidClient` should implement the same interface as `BinanceClient`
   - `HyperliquidClient` 应该实现与 `BinanceClient` 相同的接口
   - Update `contracts/trading.json` to include HyperliquidClient interface
   - 更新 `contracts/trading.json` 以包含 HyperliquidClient 接口

## Related / 相关

- Spec: `docs/specs/trading/CORE-004.md` (to be created)
- Feature: `CORE-004` (Hyperliquid Exchange Integration)
- Epic: `EPIC-02` (Hyperliquid Exchange Integration)
- Tests: `tests/unit/trading/test_hyperliquid_connection.py` (to be created)
- Contract: `contracts/trading.json#HyperliquidClient` (to be created)
- Dependencies: None (first story in the epic)

## Owner / 负责人

Agent: Agent TRADING

## Dependencies / 依赖关系

- **Blocks**: US-CORE-004-B, US-CORE-004-C (both require connection to be working)
- **阻塞**: US-CORE-004-B, US-CORE-004-C（两者都需要连接正常工作）

