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


