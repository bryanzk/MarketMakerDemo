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


