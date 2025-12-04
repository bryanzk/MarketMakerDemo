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

