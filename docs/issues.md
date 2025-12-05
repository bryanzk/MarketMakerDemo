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

## Issue #019: TypeError in fetch_market_data - dict instead of number / fetch_market_data 中的 TypeError - 字典而不是数字

**Date / 日期**: 2025-01-XX  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: trading (Agent TRADING)  
**Related Feature / 相关功能**: Hyperliquid Market Data Fetching / Hyperliquid 市场数据获取

### Description / 描述

在获取 Hyperliquid 市场数据时，出现 `TypeError: float() argument must be a string or a real number, not 'dict'` 错误。

**Error Message / 错误消息**:
```
Error fetching market data: float() argument must be a string or a real number, not 'dict'
Traceback (most recent call last):
  File "src/trading/hyperliquid_client.py", line 608, in fetch_market_data
    best_bid = float(bids[0][0])
TypeError: float() argument must be a string or a real number, not 'dict'
```

**Root Cause / 根本原因**:
- Hyperliquid API 返回的 `bids` 和 `asks` 数据格式可能包含字典结构
- 代码只处理了列表/元组和数字格式，没有处理字典格式
- 当 `bids[0][0]` 是字典时，尝试转换为 float 会失败

### Solution / 解决方案

增强了 `fetch_market_data` 方法中的类型检查和错误处理：

1. **添加字典格式支持**:
   - 检查 `bids[0][0]` 或 `asks[0][0]` 是否为字典
   - 如果是字典，尝试从常见键（`price`, `px`, `0`）中提取价格

2. **添加字典格式的 bids/asks 支持**:
   - 处理 `bids[0]` 或 `asks[0]` 直接是字典的情况
   - 支持 `{"price": 1234.5, "size": 1.0}` 或 `{"px": 1234.5, "sz": 1.0}` 格式

3. **增强错误处理**:
   - 使用 try-except 捕获所有解析错误
   - 添加详细的警告日志，记录无法解析的数据格式

### Files Modified / 修改的文件

- `src/trading/hyperliquid_client.py`: 增强 `fetch_market_data` 方法的类型检查和错误处理

### Testing / 测试

- ✅ 代码修复完成
- ⏳ 需要验证：观察服务器日志，确认不再出现此错误

### Related Documentation / 相关文档

- `src/trading/hyperliquid_client.py` (fetch_market_data method)

---

## Issue #020: Exception Handling Mismatch in get_exchange_by_name / get_exchange_by_name 中的异常处理不匹配

**Date / 日期**: 2025-01-XX  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: Hyperliquid Exchange Initialization / Hyperliquid 交易所初始化

### Description / 描述

在 `get_exchange_by_name` 函数中，尝试捕获 `ConnectionError` 和 `AuthenticationError`，但这些异常类没有正确导入，导致异常无法被捕获，继续传播。

**Error Message / 错误消息**:
```
src.trading.hyperliquid_client.ConnectionError: Failed to connect to Hyperliquid API after 3 attempts. 连接 Hyperliquid API 失败，已重试 3 次。

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "server.py", line 1606, in get_hyperliquid_status
    exchange = get_exchange_by_name("hyperliquid")
  File "server.py", line 147, in get_exchange_by_name
    except AuthenticationError as e:
```

**Root Cause / 根本原因**:
- `get_exchange_by_name` 函数中使用了 `AuthenticationError` 和 `ConnectionError`，但没有从 `src.trading.hyperliquid_client` 导入这些异常类
- Python 的 `ConnectionError` 是内置异常，与 `src.trading.hyperliquid_client.ConnectionError` 不同
- 导致异常无法被正确捕获，继续传播

### Solution / 解决方案

1. **导入正确的异常类**:
   ```python
   from src.trading.hyperliquid_client import (
       HyperliquidClient,
       AuthenticationError,
       ConnectionError as HyperliquidConnectionError,
   )
   ```

2. **使用正确的异常类名**:
   - 使用 `HyperliquidConnectionError` 来避免与内置 `ConnectionError` 冲突
   - 确保 `AuthenticationError` 和 `HyperliquidConnectionError` 都能被正确捕获

### Files Modified / 修改的文件

- `server.py`: 修复异常导入和处理

### Testing / 测试

- ✅ 语法检查通过
- ⏳ 需要验证：当 HyperliquidClient 初始化失败时，错误能被正确捕获和处理

### Related Documentation / 相关文档

- `server.py` (get_exchange_by_name function)
- `src/trading/hyperliquid_client.py` (exception classes)

---

## Issue #021: Generic Error Message for Exchange Initialization / 交易所初始化的通用错误消息

**Date / 日期**: 2025-01-XX  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: Medium / 中  
**Module / 模块**: web (Agent WEB)  
**Related Feature / 相关功能**: Hyperliquid Exchange Initialization / Hyperliquid 交易所初始化

### Description / 描述

当 HyperliquidClient 初始化失败时，错误响应只显示通用的 "Hyperliquid exchange not initialized" 消息，没有提供具体的失败原因（认证失败、连接失败等），导致用户难以诊断问题。

**Error Message / 错误消息**:
```json
{
  "error": "ValueError",
  "error_type": "validation",
  "error_code": "EXCHANGE_NOT_INITIALIZED",
  "message": "Hyperliquid exchange not initialized. Please check API credentials...",
  ...
}
```

**Root Cause / 根本原因**:
- `get_exchange_by_name` 函数在捕获异常后返回 `None`，但没有保存具体的错误信息
- `/api/hyperliquid/status` 端点无法区分不同类型的初始化失败（认证、连接、其他错误）
- 错误响应使用通用的 `EXCHANGE_NOT_INITIALIZED` 错误代码，没有针对性的建议

### Solution / 解决方案

1. **存储错误信息**:
   - 在 `get_exchange_by_name` 函数中使用 `_last_error` 属性存储最后一次初始化失败的错误信息
   - 存储错误类型（authentication、connection、unknown）和异常对象

2. **改进错误响应**:
   - 在 `/api/hyperliquid/status` 端点中检查 `_last_error` 属性
   - 根据错误类型返回不同的错误代码：
     - `EXCHANGE_AUTHENTICATION_FAILED` - 认证失败
     - `EXCHANGE_CONNECTION_FAILED` - 连接失败
     - `EXCHANGE_INITIALIZATION_FAILED` - 其他初始化失败
   - 在 `details` 中包含 `initialization_error_type` 和 `initialization_error_message`

### Files Modified / 修改的文件

- `server.py`: 
  - 改进 `get_exchange_by_name` 函数，存储错误信息
  - 改进 `/api/hyperliquid/status` 端点，返回详细的错误信息

### Testing / 测试

- ✅ 语法检查通过
- ⏳ 需要验证：不同类型的初始化失败返回相应的错误代码和消息

### Related Documentation / 相关文档

- `server.py` (get_exchange_by_name function, get_hyperliquid_status endpoint)
- `src/trading/hyperliquid_client.py` (exception classes)

---

## Issue #022: Connection Error Lacks Diagnostic Information / 连接错误缺少诊断信息

**Date / 日期**: 2025-01-XX  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: trading (Agent TRADING)  
**Related Feature / 相关功能**: Hyperliquid Connection / Hyperliquid 连接

### Description / 描述

当 HyperliquidClient 连接失败时，错误消息只显示 "Failed to connect to Hyperliquid API after 3 attempts"，缺少详细的诊断信息，如：
- 尝试连接的 URL
- HTTP 状态码
- API 响应内容
- 具体的异常类型
- 每次重试的详细信息

这导致用户难以诊断连接问题的根本原因。

**Error Message / 错误消息**:
```json
{
  "error": "ConnectionError",
  "error_code": "EXCHANGE_CONNECTION_FAILED",
  "message": "Failed to connect to Hyperliquid API after 3 attempts. 连接 Hyperliquid API 失败，已重试 3 次",
  ...
}
```

**Root Cause / 根本原因**:
- `_connect_and_authenticate` 方法中的日志记录不够详细
- 错误消息不包含 base_url、状态码、响应内容等关键信息
- 重试逻辑没有记录每次尝试的详细信息

### Solution / 解决方案

1. **增强日志记录**:
   - 在连接开始时记录 base_url、testnet 状态、重试次数
   - 记录每次连接尝试的 URL、请求方法
   - 记录每次响应的状态码和响应内容（前 200 字符）
   - 记录重试延迟和重试次数

2. **改进错误消息**:
   - 在错误消息中包含 base_url
   - 包含 HTTP 状态码（如果有）
   - 包含 API 响应内容（如果有，截取前 200 字符）
   - 包含异常类型名称

3. **改进重试逻辑**:
   - 使用安全的数组索引访问 retry_delays（避免索引越界）
   - 记录每次重试的详细信息

### Files Modified / 修改的文件

- `src/trading/hyperliquid_client.py`: 
  - 改进 `_connect_and_authenticate` 方法，添加详细的日志记录
  - 改进错误消息，包含更多诊断信息
  - 改进重试逻辑，使用安全的数组索引访问

### Testing / 测试

- ✅ 语法检查通过
- ⏳ 需要验证：连接失败时，日志和错误消息包含详细的诊断信息

### Related Documentation / 相关文档

- `src/trading/hyperliquid_client.py` (_connect_and_authenticate method)

---

## Issue #023: HTTP 429 Rate Limiting - Too Many Requests / HTTP 429 速率限制 - 请求过多

**Date / 日期**: 2025-01-XX  
**Status / 状态**: ✅ Fixed / 已修复  
**Priority / 优先级**: High / 高  
**Module / 模块**: trading, web (Agent TRADING, Agent WEB)  
**Related Feature / 相关功能**: Hyperliquid API Rate Limiting / Hyperliquid API 速率限制

### Description / 描述

前端页面频繁调用 Hyperliquid API，导致 HTTP 429 错误（Too Many Requests）。错误消息：
```
HTTP error: 429 Client Error: Too Many Requests for url: https://api.hyperliquid-testnet.xyz/info
```

**Root Cause / 根本原因**:
1. **前端调用频率过高**:
   - `refreshOrders()` - 每 3 秒调用一次
   - `refreshPosition()` - 每 5 秒调用一次
   - `checkConnection()` - 每 10 秒调用一次
   - 总计约 38 次 API 调用/分钟

2. **后端缺少 429 错误处理**:
   - `_make_request` 方法对 429 错误只记录日志并返回 `None`
   - 没有实现重试逻辑或延迟处理

3. **前端缺少请求去重**:
   - 没有防止同时发起多个相同请求的机制
   - 可能导致重复请求叠加

### Solution / 解决方案

#### 1. 后端：实现 429 错误的重试逻辑 / Backend: Implement Retry Logic for 429 Errors

在 `_make_request` 方法中添加对 429 错误的特殊处理：
- 检查响应头中的 `Retry-After` 字段（如果存在）
- 默认延迟 60 秒后重试
- 只重试一次，避免无限循环
- 记录详细的日志信息

#### 2. 前端：减少刷新频率 / Frontend: Reduce Refresh Frequency

增加自动刷新的间隔：
- `refreshOrders()` - 从 3 秒增加到 10 秒
- `refreshPosition()` - 从 5 秒增加到 15 秒
- `checkConnection()` - 从 10 秒增加到 30 秒
- 总计约 10 次 API 调用/分钟（减少 73%）

#### 3. 前端：添加请求去重机制 / Frontend: Add Request Deduplication

为每个刷新函数添加去重标志：
- `isRefreshingOrders` - 防止重复的订单刷新请求
- `isRefreshingPosition` - 防止重复的仓位刷新请求
- `isCheckingConnection` - 防止重复的连接检查请求
- 使用 `finally` 块确保标志在异常情况下也能重置

### Files Modified / 修改的文件

- `src/trading/hyperliquid_client.py`: 
  - 在 `_make_request` 方法中添加 429 错误的重试逻辑
  - 实现基于 `Retry-After` header 的延迟重试

- `templates/HyperliquidTrade.html`: 
  - 增加自动刷新间隔（订单 10 秒，仓位 15 秒，连接 30 秒）
  - 添加请求去重标志和检查逻辑
  - 在 `finally` 块中重置去重标志

### Testing / 测试

- ✅ 语法检查通过
- ✅ 后端：429 错误处理逻辑已实现
- ✅ 前端：刷新间隔已增加，请求去重已实现
- ⏳ 需要验证：在实际使用中，429 错误是否减少，重试逻辑是否正常工作

### Related Documentation / 相关文档

- `src/trading/hyperliquid_client.py` (_make_request method)
- `templates/HyperliquidTrade.html` (refreshOrders, refreshPosition, checkConnection functions)

---


