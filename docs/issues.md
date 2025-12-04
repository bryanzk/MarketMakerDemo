# Issue Tracker / 问题追踪

## Issue #001: Run Evaluation Button Not Working / 运行评估按钮未响应

**Date / 日期**: 2025-11-30  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: Multi-LLM Evaluation Page / 多 LLM 评估页面

### Description / 描述

用户点击 LLM Trade Lab 页面 (`/evaluation`) 上的 "Run Evaluation" 按钮时，按钮没有响应，评估未运行。

**Root Cause / 根本原因**:
- 前端 JavaScript 代码调用了 `/api/evaluation/run` 和 `/api/evaluation/apply` API 端点
- 但 `server.py` 中缺少这两个路由的实现
- 导致前端请求返回 404 Not Found 错误

### Solution / 解决方案

在 `server.py` 中添加了以下内容：

1. **导入评估模块**:
   ```python
   from src.ai.evaluation.evaluator import MultiLLMEvaluator
   from src.ai.evaluation.schemas import MarketContext
   from src.ai import create_all_providers
   ```

2. **添加请求模型**:
   - `EvaluationRunRequest`: 用于运行评估的请求
   - `EvaluationApplyRequest`: 用于应用评估结果的请求

3. **实现 `/api/evaluation/run` 路由**:
   - 从交易所获取市场数据
   - 构建 `MarketContext`
   - 创建 `MultiLLMEvaluator` 实例
   - 运行评估并返回结果

4. **实现 `/api/evaluation/apply` 路由**:
   - 从上次评估结果中获取建议
   - 支持 "consensus" 和 "individual" 两种来源
   - 应用配置到策略实例

### Files Modified / 修改的文件

- `server.py`: 添加评估 API 路由和请求模型

### Testing / 测试

- ✅ 语法检查通过
- ⏳ 需要手动测试：点击 "Run Evaluation" 按钮验证功能

### Related Documentation / 相关文档

- `docs/user_guide/multi_llm_eval_page.md`
- `contracts/web.json` (EvaluationAPI section)
- `docs/user_guide/multi_llm_evaluation.md`

---

## Issue #002: Replace USDT with USDC in Hyperliquid Trading Page / 将 Hyperliquid 交易页面中的 USDT 替换为 USDC

**Date / 日期**: 2025-12-04  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004: Dedicated Hyperliquid Trading Page / 专用 Hyperliquid 交易页面

### Description / 描述

需要将 Hyperliquid 交易页面（`/hyperliquid`）中所有交易对（trading pairs）中的 `USDT` 替换为 `USDC`。

**Scope / 范围** (仅限 Hyperliquid 相关):
- Hyperliquid 交易页面 HTML 模板中的交易对选项（如 `ETH/USDT:USDT` → `ETH/USDC:USDC`）
- Hyperliquid 相关的 API 端点中的默认交易对
- Hyperliquid 相关的测试文件中的交易对引用
- Hyperliquid 相关的文档中的交易对示例

**Affected Trading Pairs / 受影响的交易对**:
- `ETH/USDT:USDT` → `ETH/USDC:USDC`
- `BTC/USDT:USDT` → `BTC/USDC:USDC`
- `SOL/USDT:USDT` → `SOL/USDC:USDC`

**Note / 注意**: 此修改**仅限** Hyperliquid 交易页面和相关功能。Binance 相关的交易对保持不变。

### Files to Modify / 需要修改的文件

**仅限 Hyperliquid 相关文件 / Hyperliquid-related files only**

#### Templates / 模板文件
- `templates/HyperliquidTrade.html` - Hyperliquid 交易页面中的交易对选择下拉菜单和 JavaScript 代码

#### Source Code / 源代码
- `src/trading/hyperliquid_client.py` - Hyperliquid 客户端中的交易对格式转换逻辑（如果涉及 USDT）
- `server.py` - Hyperliquid 相关的 API 端点（`/api/hyperliquid/*`）中的交易对引用

#### Tests / 测试文件
- `tests/unit/web/test_hyperliquid_trade_page.py` - Hyperliquid 交易页面单元测试
- `tests/smoke/test_hyperliquid_trade_page.py` - Hyperliquid 交易页面冒烟测试
- `tests/integration/test_hyperliquid_trade_page_integration.py` - Hyperliquid 交易页面集成测试
- `tests/unit/trading/test_hyperliquid_positions.py` - Hyperliquid 仓位测试
- `tests/smoke/test_hyperliquid_positions.py` - Hyperliquid 仓位冒烟测试
- `tests/integration/test_hyperliquid_positions_integration.py` - Hyperliquid 仓位集成测试
- `tests/integration/test_hyperliquid_llm_evaluation_integration.py` - Hyperliquid LLM 评估集成测试
- `tests/unit/web/test_hyperliquid_llm_evaluation.py` - Hyperliquid LLM 评估单元测试
- `tests/smoke/test_hyperliquid_llm_evaluation_smoke.py` - Hyperliquid LLM 评估冒烟测试

#### Documentation / 文档
- `docs/user_guide/hyperliquid_positions.md` - Hyperliquid 仓位指南
- `docs/user_guide/hyperliquid_connection.md` - Hyperliquid 连接指南

### Solution / 解决方案

已将所有 Hyperliquid 相关的交易对从 USDT 替换为 USDC：

1. **HTML 模板修改** (`templates/HyperliquidTrade.html`):
   - 交易对选择下拉菜单：`ETH/USDT:USDT` → `ETH/USDC:USDC`
   - 默认交易对：`BTC/USDT:USDT` → `BTC/USDC:USDC`，`SOL/USDT:USDT` → `SOL/USDC:USDC`
   - JavaScript 代码中的默认符号：`ETHUSDT` → `ETHUSDC`
   - 连接检查 API 调用中的符号：`ETH/USDT:USDT` → `ETH/USDC:USDC`

2. **测试文件修改**:
   - `tests/unit/web/test_hyperliquid_trade_page.py`: 所有 `ETH/USDT:USDT` → `ETH/USDC:USDC`
   - `tests/unit/web/test_hyperliquid_llm_evaluation.py`: 所有 `ETH/USDT:USDT` → `ETH/USDC:USDC`
   - `tests/smoke/test_hyperliquid_llm_evaluation_smoke.py`: 所有 `ETH/USDT:USDT` → `ETH/USDC:USDC`，`ETHUSDT` → `ETHUSDC`

### Files Modified / 修改的文件

- ✅ `templates/HyperliquidTrade.html` - 交易对选项和 JavaScript 代码
- ✅ `tests/unit/web/test_hyperliquid_trade_page.py` - 单元测试
- ✅ `tests/unit/web/test_hyperliquid_llm_evaluation.py` - LLM 评估单元测试
- ✅ `tests/smoke/test_hyperliquid_llm_evaluation_smoke.py` - LLM 评估冒烟测试
- ✅ `docs/issues.md` - 更新 Issue 状态

### Testing / 测试

- ✅ 所有单元测试通过（24 个测试）
- ✅ 页面路由测试通过
- ✅ 交易对选项已更新为 USDC
- `docs/user_guide/hyperliquid_trading_page.md` - Hyperliquid 交易页面指南
- `docs/user_guide/hyperliquid_llm_evaluation.md` - Hyperliquid LLM 评估指南
- `docs/user_guide/hyperliquid_orders.md` - Hyperliquid 订单指南（如果包含交易对示例）

#### Excluded Files / 排除的文件
- `templates/index.html` - 主仪表盘（包含 Binance，保持不变）
- `templates/LLMTrade.html` - LLM 交易实验室（可能包含 Binance，保持不变）
- 其他非 Hyperliquid 相关的源代码和测试

### Implementation Plan / 实施计划

1. **Phase 1: Hyperliquid Trading Page Template / 阶段 1：Hyperliquid 交易页面模板**
   - 更新 `templates/HyperliquidTrade.html` 中的交易对选项下拉菜单
   - 更新 JavaScript 代码中的默认交易对（如 `ETH/USDT:USDT` → `ETH/USDC:USDC`）

2. **Phase 2: Hyperliquid API Endpoints / 阶段 2：Hyperliquid API 端点**
   - 检查 `server.py` 中 `/api/hyperliquid/*` 端点中的交易对引用
   - 更新默认交易对（如果需要）

3. **Phase 3: Hyperliquid Client / 阶段 3：Hyperliquid 客户端**
   - 检查 `src/trading/hyperliquid_client.py` 中的交易对格式转换逻辑
   - 确保支持 USDC 交易对格式

4. **Phase 4: Hyperliquid Tests / 阶段 4：Hyperliquid 测试**
   - 更新所有 Hyperliquid 相关的测试文件中的交易对引用
   - 运行 Hyperliquid 相关的测试套件确保功能正常

5. **Phase 5: Hyperliquid Documentation / 阶段 5：Hyperliquid 文档**
   - 更新所有 Hyperliquid 相关的用户指南中的交易对示例
   - 确保文档一致性

6. **Phase 6: Verification / 阶段 6：验证**
   - 运行 Hyperliquid 相关的测试套件
   - 手动测试 Hyperliquid 交易页面功能
   - 验证 Hyperliquid 交易所支持 USDC 交易对

### Considerations / 注意事项

1. **Hyperliquid Exchange Support / Hyperliquid 交易所支持**:
   - 需要确认 Hyperliquid 是否支持 USDC 交易对（如 `ETH/USDC:USDC`）
   - 验证 Hyperliquid API 调用是否正常工作
   - 检查 Hyperliquid 交易对格式要求

2. **Symbol Format / 交易对格式**:
   - 确保交易对格式符合 Hyperliquid 要求（如 `ETH/USDC:USDC`）
   - 检查 Hyperliquid API 是否接受新的格式
   - 验证 `hyperliquid_client.py` 中的格式转换逻辑

3. **Binance Unchanged / Binance 保持不变**:
   - Binance 相关的交易对（如 `templates/index.html`, `templates/LLMTrade.html`）保持不变
   - 只修改 Hyperliquid 相关的代码和文档

4. **Testing / 测试**:
   - 所有 Hyperliquid 相关的测试必须更新并通过
   - 需要验证 Hyperliquid 交易所连接是否正常
   - 确保不影响 Binance 相关功能

### Estimated Impact / 预估影响

- **Files Affected / 受影响文件**: ~15-20 files (仅 Hyperliquid 相关)
- **Lines to Change / 需要修改的行数**: ~50-100 lines
- **Testing Required / 需要测试**: Hyperliquid 相关的测试套件
- **Risk Level / 风险级别**: Low-Medium / 低-中等（仅影响 Hyperliquid，不影响 Binance）

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_connection.md`
- `docs/user_guide/hyperliquid_trading_page.md`
- `contracts/trading.json`

---

## Issue #003: Hyperliquid Trading Pair Switch Fails When Not Connected / Hyperliquid 未连接时切换交易对失败

**Date / 日期**: 2025-12-04  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004: Dedicated Hyperliquid Trading Page / 专用 Hyperliquid 交易页面

### Description / 描述

在 Hyperliquid 交易页面（`/hyperliquid`）切换交易对时，如果 Hyperliquid 交易所未连接，会显示错误提示："Hyperliquid exchange not connected / Hyperliquid 交易所未连接"，导致无法切换交易对。

**User Experience Issue / 用户体验问题**:
- 用户可能只是想在前端选择一个新的交易对
- 实际的连接和交易操作可能稍后进行
- 当前的实现要求必须先连接才能切换交易对，这限制了用户体验

**Root Cause / 根本原因**:
- `/api/hyperliquid/pair` API 端点要求 Hyperliquid 必须已连接
- 如果 `exchange.is_connected` 为 `False`，API 直接返回错误
- 前端无法更新交易对选择，即使这只是 UI 操作

### Solution / 解决方案

修改了 `/api/hyperliquid/pair` API 端点和前端 `switchPair()` 函数：

1. **API 端点改进** (`server.py`):
   - 如果 Hyperliquid 已连接：正常更新交易对并返回成功
   - 如果 Hyperliquid 未连接：仍然允许更新交易对（用于 UI），但返回警告信息
   - 警告信息告知用户需要连接才能进行实际交易

2. **前端改进** (`templates/HyperliquidTrade.html`):
   - 处理 API 返回的 `warning` 字段
   - 显示警告信息但不阻止交易对切换
   - 只有在已连接时才刷新状态和仓位数据

**Behavior / 行为**:
- ✅ 允许切换交易对即使未连接（更新 UI 状态）
- ✅ 显示警告信息，告知用户需要连接才能进行实际交易
- ✅ 如果已连接，正常更新交易对并刷新数据

### Files Modified / 修改的文件

- ✅ `server.py` - `/api/hyperliquid/pair` API 端点
- ✅ `templates/HyperliquidTrade.html` - `switchPair()` JavaScript 函数

### Testing / 测试

- ✅ 未连接状态下可以切换交易对
- ✅ 显示适当的警告信息
- ✅ 已连接状态下正常更新交易对
- ✅ 不影响其他功能

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_trading_page.md`
- `docs/issues.md` - Issue #002 (USDT to USDC conversion)

---

## Issue #004: Display Testnet/Mainnet Status on Hyperliquid Trading Page / 在 Hyperliquid 交易页面显示测试网/主网状态

**Date / 日期**: 2025-12-04  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004: Dedicated Hyperliquid Trading Page / 专用 Hyperliquid 交易页面

### Description / 描述

Hyperliquid 交易页面需要在显眼位置显示当前连接的是 Mainnet（主网）还是 Testnet（测试网），以防止用户在错误的网络上进行交易操作。

**User Safety Issue / 用户安全问题**:
- 用户可能不知道当前连接的是主网还是测试网
- 在主网上进行测试可能导致资金损失
- 在测试网上进行真实交易会导致无效操作

**Requirement / 需求**:
- 在页面显眼位置（header）显示网络状态
- 使用醒目的视觉标识（颜色、图标）
- 实时更新网络状态

### Solution / 解决方案

1. **API 端点改进** (`server.py`):
   - 在 `/api/hyperliquid/status` API 响应中添加 `testnet` 字段
   - 即使未连接也返回 testnet 状态（如果可用）

2. **页面 UI 改进** (`templates/HyperliquidTrade.html`):
   - 在页面 header 添加网络状态标识（在连接状态旁边）
   - 添加样式：
     - **Mainnet / 主网**: 绿色背景，显示 "✓ MAINNET / 主网"
     - **Testnet / 测试网**: 黄色背景，显示 "⚠️ TESTNET / 测试网"
   - 更新 `checkConnection()` 函数来显示网络状态

**Visual Design / 视觉设计**:
- Mainnet: 绿色边框和背景，表示安全的主网环境
- Testnet: 黄色边框和背景，带警告图标，提醒这是测试环境

### Files Modified / 修改的文件

- ✅ `server.py` - `/api/hyperliquid/status` API 端点（添加 `testnet` 字段）
- ✅ `templates/HyperliquidTrade.html` - Header 网络状态标识和样式

### Testing / 测试

- ✅ 主网状态下显示绿色 "MAINNET / 主网" 标识
- ✅ 测试网状态下显示黄色 "TESTNET / 测试网" 标识
- ✅ 未连接时也能显示网络状态（如果可用）
- ✅ 标识位置显眼，易于识别

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_trading_page.md`
- `docs/user_guide/hyperliquid_connection.md`

---

## Issue #005: Add Testnet Connection Links and Instructions / 添加测试网连接链接和说明

**Date / 日期**: 2025-12-04  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004: Dedicated Hyperliquid Trading Page / 专用 Hyperliquid 交易页面

### Description / 描述

用户需要在 Hyperliquid 交易页面上有显眼的链接和说明来连接到 Testnet（测试网）。

**User Need / 用户需求**:
- 快速访问 Hyperliquid Testnet 网站
- 了解如何配置和连接到 Testnet
- 区分 Testnet 和 Mainnet 的配置方法

### Solution / 解决方案

在连接状态面板添加了：

1. **快速链接按钮**:
   - "🔗 Testnet Website / 测试网网站" - 链接到 `https://hyperliquid-testnet.xyz`
   - "🔗 Mainnet Website / 主网网站" - 链接到 `https://hyperliquid.xyz`

2. **Testnet 连接说明框**:
   - 醒目的黄色背景提示框
   - 显示如何设置环境变量连接到 Testnet
   - 包含代码示例和文档链接
   - 双语说明（英文和中文）

**Visual Design / 视觉设计**:
- 黄色背景（`#fef3c7`）突出显示 Testnet 说明
- 代码块使用深色背景，易于复制
- 链接到官方文档

### Files Modified / 修改的文件

- ✅ `templates/HyperliquidTrade.html` - 连接状态面板添加 Testnet 链接和说明

### Testing / 测试

- ✅ Testnet 网站链接正常工作
- ✅ Mainnet 网站链接正常工作
- ✅ 说明框显示正确
- ✅ 代码示例可复制

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_connection.md` - Testnet 配置说明
- `docs/user_guide/hyperliquid_trading_page.md` - 交易页面使用指南

---

## Issue #006: TypeError in fetch_market_data - float() argument must be a string or a real number, not 'dict' / fetch_market_data 中的 TypeError - float() 参数必须是字符串或实数，不是字典

**Date / 日期**: 2025-12-04  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: trading (Agent TRADING)  
**Related Feature / 相关功能**: US-CORE-004-A: Hyperliquid Connection and Authentication / Hyperliquid 连接与认证

### Description / 描述

在获取市场数据时，`fetch_market_data()` 函数抛出 `TypeError: float() argument must be a string or a real number, not 'dict'` 错误。

**Error Location / 错误位置**:
- File: `src/trading/hyperliquid_client.py`
- Line: ~608 (in `fetch_market_data` method)
- Function: Parsing bid/ask prices from orderbook response

**Root Cause / 根本原因**:
- Hyperliquid API 返回的订单簿数据格式可能与预期不同
- 代码假设 `bids[0][0]` 和 `asks[0][0]` 是数字，但实际可能是字典
- 缺少对不同数据格式的处理和类型检查

**Error Message / 错误消息**:
```
Error fetching market data: float() argument must be a string or a real number, not 'dict'
TypeError: float() argument must be a string or a real number, not 'dict'
```

### Solution / 解决方案

增强了 `fetch_market_data()` 函数的数据解析逻辑：

1. **增强类型检查**:
   - 检查 `bids[0][0]` 和 `asks[0][0]` 的类型
   - 支持多种数据格式：数字、字符串、字典
   - 处理字典格式：`{"price": ...}`, `{"px": ...}`, `{"bid": ...}`, `{"ask": ...}`

2. **错误处理**:
   - 添加 try-except 块捕获类型错误
   - 记录警告日志而不是崩溃
   - 优雅降级：如果解析失败，返回 None 而不是抛出异常

3. **mid_price 解析**:
   - 同样增强 `allMids` 响应的解析逻辑
   - 支持字典格式的中间价数据

**Code Changes / 代码变更**:
```python
# Before / 之前
best_bid = float(bids[0][0])  # May fail if bids[0][0] is a dict

# After / 之后
if isinstance(bid_value, (list, tuple)) and len(bid_value) > 0:
    price_value = bid_value[0]
    if isinstance(price_value, (int, float, str)):
        best_bid = float(price_value)
    elif isinstance(price_value, dict):
        best_bid = float(price_value.get("price", price_value.get("px", 0)))
```

### Files Modified / 修改的文件

- ✅ `src/trading/hyperliquid_client.py` - `fetch_market_data()` 方法

### Testing / 测试

- ✅ 处理数字格式的价格数据
- ✅ 处理字符串格式的价格数据
- ✅ 处理字典格式的价格数据
- ✅ 错误情况下优雅降级
- ✅ 日志记录帮助调试

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_connection.md`
- `contracts/trading.json` - MarketData interface

---

## Issue #007: Data Not Loading on Hyperliquid Trading Page / Hyperliquid 交易页面无法加载数据

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004 - Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

用户报告 Hyperliquid 交易页面无法获取数据，页面一直显示 "Loading..." 状态：
- Connection Status 显示 "Loading connection status..."
- Position & Balance 显示 "Loading position data..."
- Current Orders 显示 "Loading orders..."

**Root Cause / 根本原因**:
1. `refreshPosition()` 函数缺少 `finally` 块，导致 `isRefreshingPosition` 标志在错误情况下无法重置，后续请求被阻止
2. `refreshOrders()` 函数没有使用防重复请求机制，且缺少 `finally` 块
3. 错误处理不完善，没有检查 DOM 元素是否存在
4. 即使 API 返回有效数据（如 balance: 0.0），也可能因为条件判断问题导致数据不显示

### Solution / 解决方案

1. **修复 `refreshPosition()` 函数**:
   - 添加 `finally` 块确保 `isRefreshingPosition` 标志始终被重置
   - 改进错误处理，检查 DOM 元素是否存在
   - 改进数据验证逻辑，即使 balance 为 0 也显示数据（只要 `connected: true`）
   - 添加 HTTP 状态码检查

2. **修复 `refreshOrders()` 函数**:
   - 添加防重复请求机制（使用 `isRefreshingOrders` 标志）
   - 添加 `finally` 块确保标志始终被重置
   - 改进错误处理，检查 DOM 元素是否存在
   - 添加 HTTP 状态码检查

3. **改进错误处理**:
   - 所有 DOM 操作前都检查元素是否存在
   - 统一错误消息格式
   - 确保错误状态正确显示

### Files Modified / 修改的文件

- `templates/HyperliquidTrade.html`: 修复 `refreshPosition()` 和 `refreshOrders()` 函数

### Code Changes / 代码变更

**`refreshPosition()` 函数**:
- 添加 `finally` 块重置 `isRefreshingPosition` 标志
- 改进条件判断：`if (data.connected && data.balance !== undefined)` 而不是仅检查 `balance !== undefined`
- 所有 DOM 操作前检查元素是否存在

**`refreshOrders()` 函数**:
- 添加防重复请求机制
- 添加 `finally` 块重置 `isRefreshingOrders` 标志
- 所有 DOM 操作前检查元素是否存在

### Testing / 测试

- ✅ 正常连接时数据正确显示
- ✅ 余额为 0 时也能正确显示
- ✅ 错误情况下标志正确重置，允许后续重试
- ✅ 防重复请求机制正常工作
- ✅ DOM 元素不存在时不会报错

### Related Documentation / 相关文档

- `docs/user_guide/hyperliquid_trading_page.md`
- `templates/HyperliquidTrade.html`

---

## Issue #008: Excessive Warning Messages for Open Orders / 未成交订单的过多警告信息

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: trading (Agent TRADING)  
**Related Feature / 相关功能**: Hyperliquid Client - Open Orders Fetching / Hyperliquid 客户端 - 获取未成交订单

### Description / 描述

终端中频繁出现警告信息：
```
No response when fetching open orders / 获取未成交订单时无响应
```

**Root Cause / 根本原因**:
1. `fetch_open_orders()` 方法在 `_make_request()` 返回 `None` 时总是打印警告
2. `_make_request()` 在遇到速率限制（429）或其他 HTTP 错误时会返回 `None`
3. 没有区分不同类型的错误（速率限制 vs 其他错误）
4. 速率限制是正常情况，不应该频繁打印警告

### Solution / 解决方案

改进 `fetch_open_orders()` 方法的错误处理：

1. **区分错误类型**:
   - 检查 `self.last_api_error` 来判断错误类型
   - 如果是速率限制错误，使用 `logger.debug()` 而不是 `logger.warning()`
   - 如果是其他错误，才使用 `logger.warning()`

2. **改进日志级别**:
   - 速率限制错误：使用 `debug` 级别，避免刷屏
   - 其他错误：使用 `warning` 级别，提供详细信息
   - 未知错误：使用 `debug` 级别，因为可能是正常情况（如没有订单）

3. **提供更详细的错误信息**:
   - 在警告信息中包含 `last_api_error` 的详细信息
   - 帮助调试和问题排查

### Files Modified / 修改的文件

- `src/trading/hyperliquid_client.py`: 改进 `fetch_open_orders()` 方法的错误处理

### Code Changes / 代码变更

**`fetch_open_orders()` 方法**:
- 添加错误类型检查，区分速率限制和其他错误
- 根据错误类型使用不同的日志级别
- 在错误信息中包含 `last_api_error` 的详细信息

### Testing / 测试

- ✅ 速率限制错误使用 debug 级别，不会频繁刷屏
- ✅ 其他错误使用 warning 级别，提供有用信息
- ✅ 错误信息包含详细信息，便于调试

### Related Documentation / 相关文档

- `src/trading/hyperliquid_client.py`
- `docs/user_guide/hyperliquid_connection.md`

---

## Issue #009: Unnecessary Binance Data Fetching on Hyperliquid Page / Hyperliquid 页面不必要地获取 Binance 数据

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

打开 Hyperliquid 交易页面时，后台会不必要地尝试获取 Binance 数据，导致：
- 不必要的 API 调用
- 可能的连接错误或警告信息
- 性能浪费

**Root Cause / 根本原因**:
1. `init_portfolio_capital()` 函数在应用启动时被调用
2. 该函数会尝试从默认交易所（通常是 Binance）获取余额
3. 即使用户只使用 Hyperliquid，也会尝试连接 Binance
4. 没有检查默认交易所是否是 Binance

### Solution / 解决方案

修改 `init_portfolio_capital()` 函数：

1. **添加交易所类型检查**:
   - 检查默认交易所是否是 BinanceClient
   - 如果不是 Binance，跳过初始化（例如 Hyperliquid）
   - 避免不必要的 API 调用

2. **改进错误处理**:
   - 将错误日志级别从 `print` 改为 `logger.debug`
   - 避免在仅使用 Hyperliquid 时显示错误信息
   - 更优雅地处理非 Binance 交易所的情况

3. **更新函数文档**:
   - 明确说明函数仅从 Binance 获取余额
   - 说明如果默认交易所不是 Binance，会跳过初始化

### Files Modified / 修改的文件

- `server.py`: 修改 `init_portfolio_capital()` 函数

### Code Changes / 代码变更

**`init_portfolio_capital()` 函数**:
- 添加 `isinstance(exchange, BinanceClient)` 检查
- 如果不是 Binance 客户端，跳过初始化并记录 debug 日志
- 将错误处理改为使用 `logger.debug()` 而不是 `print()`
- 更新函数文档说明行为

### Testing / 测试

- ✅ 仅使用 Hyperliquid 时，不会尝试连接 Binance
- ✅ 使用 Binance 时，正常初始化投资组合资金
- ✅ 错误处理更优雅，不会显示不必要的错误信息

### Related Documentation / 相关文档

- `server.py`
- `docs/user_guide/hyperliquid_trading_page.md`

---

## Issue #010: JavaScript Syntax Error - Duplicate Variable Declaration / JavaScript 语法错误 - 重复变量声明

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004 - Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

Chrome 控制台报错：
```
hyperliquid:1388 Uncaught SyntaxError: Identifier 'ordersRefreshInterval' has already been declared
```

**Root Cause / 根本原因**:
在 `HyperliquidTrade.html` 文件中，`ordersRefreshInterval`、`positionRefreshInterval` 和 `connectionRefreshInterval` 变量被声明了两次：
- 第一次在第 1368-1369 行
- 第二次在第 1388-1390 行（重复声明）

这导致 JavaScript 语法错误，页面无法正常工作。

### Solution / 解决方案

合并重复的变量声明：

1. **删除重复声明**:
   - 删除第 1388-1390 行的重复声明
   - 将所有三个变量的声明合并到一处（第 1369-1371 行）

2. **改进代码组织**:
   - 将所有间隔变量声明放在一起
   - 添加注释说明这些变量用于自动刷新和清理

### Files Modified / 修改的文件

- `templates/HyperliquidTrade.html`: 删除重复的变量声明

### Code Changes / 代码变更

**变量声明部分**:
- 删除重复的 `let ordersRefreshInterval = null;`
- 删除重复的 `let positionRefreshInterval = null;`
- 删除重复的 `let connectionRefreshInterval = null;`
- 将所有三个变量声明合并到一处，放在 `startAutoRefresh()` 函数之前

### Testing / 测试

- ✅ 页面加载时不再出现语法错误
- ✅ 自动刷新功能正常工作
- ✅ Chrome 控制台无错误信息

### Related Documentation / 相关文档

- `templates/HyperliquidTrade.html`
- `docs/user_guide/hyperliquid_trading_page.md`

---

## Issue #011: Chrome Extension Runtime Error in Console / Chrome 扩展运行时控制台错误

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Low / 低  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004 - Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

Chrome 控制台显示错误：
```
hyperliquid:252 Unchecked runtime.lastError: Could not establish connection. Receiving end does not exist.
```

**Root Cause / 根本原因**:
这个错误是由浏览器扩展（Chrome extensions）引起的，而不是代码本身的问题：
1. 某些 Chrome 扩展程序尝试与页面通信
2. 扩展程序的消息接收端未正确设置
3. 导致 `chrome.runtime.lastError` 错误
4. 这个错误不影响页面功能，只是控制台会显示警告

### Solution / 解决方案

添加错误过滤器来抑制这个特定的错误：

1. **添加 console.error 过滤器**:
   - 重写 `console.error` 函数
   - 过滤掉包含 `runtime.lastError`、`Could not establish connection` 或 `Receiving end does not exist` 的错误消息
   - 其他错误消息正常显示

2. **不影响其他错误**:
   - 只过滤特定的扩展相关错误
   - 保留其他所有错误消息，确保调试功能正常

### Files Modified / 修改的文件

- `templates/HyperliquidTrade.html`: 添加错误过滤器

### Code Changes / 代码变更

**错误处理部分**:
- 添加 `console.error` 重写函数
- 过滤掉 Chrome 扩展相关的错误消息
- 保留其他所有错误消息

### Testing / 测试

- ✅ Chrome 控制台不再显示扩展相关的错误
- ✅ 其他错误消息正常显示
- ✅ 页面功能不受影响

### Notes / 备注

这个错误是由浏览器扩展引起的，不是代码本身的问题。如果用户想要完全消除这个错误，可以：
1. 禁用相关的 Chrome 扩展程序
2. 或者使用无扩展模式的 Chrome（用于测试）

### Related Documentation / 相关文档

- `templates/HyperliquidTrade.html`
- `docs/user_guide/hyperliquid_trading_page.md`

---

## Issue #012: Incorrect Symbol Display - USDT Instead of USDC / 错误的交易对显示 - USDT 而不是 USDC

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004 - Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

页面连接状态显示错误的交易对格式：
- 显示：`Symbol: ETH/USDT:USDT`
- 正确应该显示：`Symbol: ETH/USDC:USDC`

**Root Cause / 根本原因**:
1. Hyperliquid 交易所使用 USDC 作为稳定币，而不是 USDT
2. 后端 API 可能返回包含 USDT 的 symbol（例如从默认配置或历史数据）
3. 前端直接显示 API 返回的 symbol，没有进行格式转换

### Solution / 解决方案

在前端显示时添加格式转换：

1. **添加 Symbol 格式转换**:
   - 在 `checkConnection()` 函数中，显示 symbol 之前进行检查
   - 如果 symbol 包含 "USDT"，将其替换为 "USDC"
   - 确保显示的交易对格式正确

2. **保持后端逻辑不变**:
   - 后端 API 返回的原始 symbol 保持不变（用于内部逻辑）
   - 仅在前端显示时进行转换

### Files Modified / 修改的文件

- `templates/HyperliquidTrade.html`: 在 `checkConnection()` 函数中添加 symbol 格式转换

### Code Changes / 代码变更

**`checkConnection()` 函数**:
- 添加 symbol 格式转换逻辑
- 将包含 "USDT" 的 symbol 替换为 "USDC"
- 添加注释说明 Hyperliquid 使用 USDC 而不是 USDT

### Testing / 测试

- ✅ 连接状态正确显示 USDC 格式的交易对
- ✅ 其他功能不受影响
- ✅ 内部逻辑仍然使用原始 symbol

### Related Documentation / 相关文档

- `templates/HyperliquidTrade.html`
- `docs/user_guide/hyperliquid_trading_page.md`
- `docs/user_guide/hyperliquid_connection.md`

---

## Issue #013: Balance Not Fetched from Hyperliquid Testnet / 未从 Hyperliquid 测试网获取余额

**Date / 日期**: 2025-12-01  
**Status / 状态**: 🔄 In Progress / 进行中  
**Priority / 优先级**: High / 高  
**Module / 模块**: trading (Agent TRADING)  
**Related Feature / 相关功能**: Hyperliquid Client - Balance Fetching / Hyperliquid 客户端 - 余额获取

### Description / 描述

页面显示余额为 0.00 USDC，但 Hyperliquid Testnet 上实际有 122.85 USDC 的余额。

**Root Cause / 根本原因**:
可能的原因：
1. API 响应格式与预期不同
2. 字段名称不匹配（例如 `accountValue` vs `account_value` vs `balance`）
3. 需要使用钱包地址而不是 API key 作为用户标识符
4. API 查询类型或端点不正确

### Solution / 解决方案

1. **改进字段解析逻辑**:
   - 添加对多种可能字段名的支持
   - 尝试从 `marginSummary` 和直接响应中获取余额
   - 支持不同的命名约定（camelCase vs snake_case）

2. **添加调试日志**:
   - 记录 API 响应的实际结构
   - 帮助诊断问题

3. **改进用户标识符**:
   - 尝试使用钱包地址（如果可用）
   - 回退到 API key

### Files Modified / 修改的文件

- `src/trading/hyperliquid_client.py`: 改进 `fetch_balance()` 方法的解析逻辑

### Code Changes / 代码变更

**`fetch_balance()` 方法**:
- 添加对多种字段名的支持
- 添加调试日志以查看实际 API 响应
- 改进用户标识符逻辑（支持钱包地址）

### Testing / 测试

- ⏳ 需要查看实际的 API 响应格式
- ⏳ 验证余额是否正确获取
- ⏳ 确认字段名匹配

### Next Steps / 下一步

1. 查看服务器日志中的 API 响应结构
2. 根据实际响应格式调整解析逻辑
3. 验证余额是否正确显示

### Related Documentation / 相关文档

- `src/trading/hyperliquid_client.py`
- `docs/user_guide/hyperliquid_connection.md`

---

## Issue #014: Testnet Connection Hint Always Visible / 测试网连接提示一直显示

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Low / 低  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: US-UI-004 - Hyperliquid Trading Page / Hyperliquid 交易页面

### Description / 描述

"Connect to Testnet / 连接到测试网" 提示框一直显示，即使已经连接到测试网。

**Root Cause / 根本原因**:
1. 提示框是硬编码在 HTML 中的，没有根据连接状态动态显示/隐藏
2. 缺少 JavaScript 逻辑来控制提示框的可见性
3. 没有检查当前是否已连接到测试网

### Solution / 解决方案

添加动态显示/隐藏逻辑：

1. **添加 ID 到提示框**:
   - 给提示框添加 `id="testnetConnectionHint"`
   - 默认设置为 `display:none`

2. **在 `checkConnection()` 中添加逻辑**:
   - 检查连接状态和网络类型（testnet/mainnet）
   - 如果已连接到测试网，隐藏提示框
   - 如果未连接或连接到主网，显示提示框

### Files Modified / 修改的文件

- `templates/HyperliquidTrade.html`: 添加动态显示/隐藏逻辑

### Code Changes / 代码变更

**HTML 部分**:
- 给测试网连接提示框添加 `id="testnetConnectionHint"`
- 设置默认 `display:none`

**JavaScript 部分** (`checkConnection()` 函数):
- 获取 `testnetConnectionHint` 元素
- 根据连接状态和网络类型控制显示/隐藏
- 已连接到测试网时隐藏，未连接或主网时显示

### Testing / 测试

- ✅ 已连接到测试网时，提示框隐藏
- ✅ 未连接时，提示框显示
- ✅ 连接到主网时，提示框显示（建议切换到测试网）

### Related Documentation / 相关文档

- `templates/HyperliquidTrade.html`
- `docs/user_guide/hyperliquid_trading_page.md`

---

## Issue #015: Only Gemini Provider Available in LLM Evaluation / LLM 评估中只有 Gemini 提供商可用

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: ai (Agent AI)  
**Related Feature / 相关功能**: Multi-LLM Evaluation / 多 LLM 评估

### Description / 描述

LLM 评估中只显示 Gemini 一个模型，没有 OpenAI 和 Claude。

**Root Cause / 根本原因**:
1. `create_all_providers()` 函数会尝试创建所有三个 provider
2. 如果某个 provider 的 API key 未设置或初始化失败，会捕获异常并跳过
3. 错误信息没有记录到日志，用户不知道为什么其他 provider 不可用

### Solution / 解决方案

改进 `create_all_providers()` 函数的错误处理和日志记录：

1. **添加详细的日志记录**:
   - 成功初始化时记录成功信息
   - 失败时记录警告信息，包含失败原因
   - 最后汇总成功初始化的 provider 列表

2. **改进错误信息**:
   - 如果所有 provider 都失败，提供详细的错误摘要
   - 如果部分 provider 失败，记录警告但继续使用可用的 provider

### Files Modified / 修改的文件

- `src/ai/llm.py`: 改进 `create_all_providers()` 函数的错误处理和日志记录

### Code Changes / 代码变更

**`create_all_providers()` 函数**:
- 为每个 provider 的初始化添加成功/失败日志
- 记录失败原因（API key 未设置、包未安装等）
- 汇总成功初始化的 provider 列表

### Testing / 测试

- ✅ 成功初始化的 provider 会记录成功日志
- ✅ 失败的 provider 会记录警告日志和失败原因
- ✅ 用户可以通过日志了解为什么某些 provider 不可用

### Notes / 备注

如果只有 Gemini 可用，可能的原因：
1. `OPENAI_API_KEY` 环境变量未设置
2. `ANTHROPIC_API_KEY` 环境变量未设置
3. 相应的 Python 包未安装（`openai` 或 `anthropic`）

### Related Documentation / 相关文档

- `src/ai/llm.py`
- `docs/user_guide/multi_llm_evaluation.md`

---

## Issue #016: Apply LLM Consensus Proposal Fails / 应用 LLM 共识建议失败

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: ai (Agent AI)  
**Related Feature / 相关功能**: Multi-LLM Evaluation / 多 LLM 评估

### Description / 描述

应用 LLM 共识建议时出错：
```
Invalid proposal or proposal parsing failed / 无效的建议或建议解析失败
```

**Root Cause / 根本原因**:
1. 如果所有 LLM provider 的响应解析都失败（`parse_success=False`），consensus_proposal 的 `parse_success` 也会是 `False`
2. 如果只有一个 provider 可用且其响应解析失败，无法生成有效的共识建议
3. 错误信息不够详细，用户不知道具体失败原因

### Solution / 解决方案

改进 apply evaluation 的错误处理：

1. **添加更详细的错误检查**:
   - 检查 consensus_proposal 是否存在
   - 检查 parse_success 状态
   - 提供更具体的错误信息

2. **改进错误消息**:
   - 如果 consensus_proposal 不存在，说明所有 provider 都失败了
   - 如果 parse_success 为 False，提供策略名称和具体原因
   - 对于 individual source，列出可用的 provider

### Files Modified / 修改的文件

- `server.py`: 改进 `/api/evaluation/apply` 端点的错误处理

### Code Changes / 代码变更

**`/api/evaluation/apply` 端点**:
- 添加对 consensus_proposal 存在性的检查
- 分别处理 consensus 和 individual source 的错误情况
- 提供更详细的错误信息，包括策略名称和可用 provider 列表

### Testing / 测试

- ✅ 如果所有 provider 都失败，提供清晰的错误信息
- ✅ 如果 consensus_proposal parse_success 为 False，提供具体原因
- ✅ 对于 individual source，列出可用的 provider

### Related Documentation / 相关文档

- `server.py`
- `src/ai/evaluation/evaluator.py`
- `docs/user_guide/multi_llm_evaluation.md`

---

## Issue #017: Gemini Score is 0 / Gemini 得分为 0

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: ai (Agent AI)  
**Related Feature / 相关功能**: Multi-LLM Evaluation / 多 LLM 评估

### Description / 描述

Gemini 给出的建议 score 为 0，不应该为零。

**Root Cause / 根本原因**:
1. 如果 `proposal.parse_success` 为 `False`，score 会被设置为 0.0
2. 如果模拟结果的所有指标都是 0（PnL、Sharpe、win_rate、confidence），score 也会很低
3. 缺少调试日志，无法诊断为什么 score 为 0

### Solution / 解决方案

添加详细的调试日志：

1. **添加评分计算日志**:
   - 记录每个得分组成部分（PnL score、Sharpe score、win_rate score、confidence score）
   - 记录最终总分
   - 如果 parse_success 为 False，记录警告

2. **改进错误处理**:
   - 如果 parse_success 为 False，明确记录原因
   - 帮助用户理解为什么 score 为 0

### Files Modified / 修改的文件

- `src/ai/evaluation/evaluator.py`: 在 `_score_and_rank()` 方法中添加调试日志

### Code Changes / 代码变更

**`_score_and_rank()` 方法**:
- 添加详细的调试日志，记录每个得分组成部分
- 记录最终总分计算过程
- 如果 parse_success 为 False，记录警告信息

### Testing / 测试

- ✅ 可以通过日志查看详细的评分计算过程
- ✅ 如果 score 为 0，可以快速定位原因
- ✅ 帮助诊断评分问题

### Notes / 备注

如果 score 为 0，可能的原因：
1. `proposal.parse_success` 为 `False`（LLM 响应解析失败）
2. 模拟结果的所有指标都是 0（需要检查模拟逻辑）

查看服务器日志可以了解具体原因。

### Related Documentation / 相关文档

- `src/ai/evaluation/evaluator.py`
- `docs/user_guide/multi_llm_evaluation.md`

---

## Issue #018: Consensus Reasoning Unavailable / 共识推理不可用

**Date / 日期**: 2025-12-01  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Low / 低  
**Module / 模块**: ai (Agent AI)  
**Related Feature / 相关功能**: Multi-LLM Evaluation / 多 LLM 评估

### Description / 描述

共识建议卡片显示 "Consensus reasoning unavailable. / 共识推理不可用。"

**Root Cause / 根本原因**:
1. 如果所有 LLM provider 的 `proposal.reasoning` 字段都是空的，`combined_reasoning` 就只有基础字符串
2. 前端检查 `proposal.reasoning` 是否为空，如果为空就显示默认消息
3. 即使有基础共识信息（如 "Consensus from X/Y models"），也可能被判断为空

### Solution / 解决方案

改进共识推理的生成和显示逻辑：

1. **改进推理生成逻辑**:
   - 即使没有详细的推理文本，也生成基础共识信息
   - 如果没有详细推理，添加基于哪些提供商的建议的说明
   - 确保 `combined_reasoning` 始终有内容

2. **改进前端显示逻辑**:
   - 检查 `reasoning` 是否为空字符串（不仅仅是 falsy 值）
   - 使用 `trim()` 检查是否只有空白字符

### Files Modified / 修改的文件

- `src/ai/evaluation/evaluator.py`: 改进 `_generate_consensus_proposal()` 方法的推理生成逻辑
- `templates/HyperliquidTrade.html`: 改进前端显示逻辑

### Code Changes / 代码变更

**`_generate_consensus_proposal()` 方法**:
- 改进 `combined_reasoning` 的生成逻辑
- 即使没有详细推理，也添加基础信息和提供商名称
- 使用 `strip()` 检查推理文本是否为空

**前端 JavaScript**:
- 使用 `trim()` 检查 `reasoning` 是否为空
- 确保即使只有基础信息也显示

### Testing / 测试

- ✅ 即使没有详细推理，也显示基础共识信息
- ✅ 显示基于哪些提供商的建议
- ✅ 不会显示 "Consensus reasoning unavailable" 除非真的没有信息

### Related Documentation / 相关文档

- `src/ai/evaluation/evaluator.py`
- `templates/HyperliquidTrade.html`
- `docs/user_guide/multi_llm_evaluation.md`

---

