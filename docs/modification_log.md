# 修改日志 / Modification Log

## 自上次推送到远程后的完整修改记录

**最后更新**: 本次提交 `bf1686c` - chore: update codebase with test fixes and improvements

### 一、已提交并推送到远程的更改（17 个提交）

#### 提交列表
1. `cdcc21e` - fix: improve error handling for market data and connection timeouts
2. `1ec860d` - feat(web): add LLM model selection with checkbox UI and backend filtering
3. `741b7fd` - fix(eval): 提升 LLM JSON 解析鲁棒性
4. `25aff90` - fix(ai): 使用稳定的 Gemini 模型并完善回退逻辑
5. `7486160` - feat(ai): 支持通过环境变量优先使用 gemini-3-pro
6. `4d64f74` - fix(web): ensure Hyperliquid strategy instance is created when applying LLM evaluation
7. `4362395` - chore(web): update HyperliquidTrade.html template
8. `0f3a7ba` - chore(ai): update llm.py
9. `6340126` - feat(ai): 强制使用 gemini-3-pro 并在失败时提示原因
10. `b62550e` - feat(web): integrate LLM parse_error into error handling system
11. `4ca3d78` - test(web): add unit, smoke, and integration tests for Hyperliquid strategy instance creation
12. `8fe2d24` - test(web): fix integration test imports and complete workflow test
13. `f2da4e5` - test(web): add tests for Hyperliquid strategy instance creation (WIP - some tests failing)
14. `dd58a5b` - test(web): fix mock setup for get_exchange_by_name in Hyperliquid tests
15. `7d83bd8` - fix(hyperliquid): improve order placement error handling and retry logic
16. `e1a28e6` - test(web): add unit, smoke and integration tests for hyperliquid API endpoints
17. `bf1686c` - chore: update codebase with test fixes and improvements (本次提交)

---

### 二、文件修改详情

#### A. server.py

**修改的端点/函数：**
- `@app.get("/api/hyperliquid/status")` - `get_hyperliquid_status()` (新增)
- `@app.get("/api/hyperliquid/prices")` - `get_hyperliquid_prices()` (新增)
- `@app.get("/api/hyperliquid/connection")` - `check_hyperliquid_connection()` (新增)
- `@app.post("/api/hyperliquid/config")` - `update_hyperliquid_config()` (修改)
- `@app.post("/api/hyperliquid/leverage")` - `update_hyperliquid_leverage()` (修改)
- `@app.post("/api/hyperliquid/pair")` - `update_hyperliquid_pair()` (修改)
- `@app.post("/api/evaluation/run")` - `run_evaluation()` (修改)
- `@app.post("/api/evaluation/apply")` - `apply_evaluation()` (修改)
- `create_error_response()` (修改)
- `get_exchange_by_name()` (修改)
- `_get_or_create_strategy_instance()` (修改)

#### B. src/trading/hyperliquid_client.py

**修改的类/方法：**
- `class RateLimiter` (修改)
  - `can_make_request()` (修改 - 新增 max_wait_time 参数)
- `class HyperliquidClient` (修改)
  - `_make_request()` (修改)
  - `place_orders()` (修改)
  - `_handle_order_error()` (修改)
  - `_parse_order_response()` (修改)
  - `fetch_market_data()` (修改)

#### C. src/ai/llm.py

**修改的函数：**
- `get_llm_client()` (修改)
- `get_available_models()` (修改)
- `LLMEvaluator.__init__()` (修改 - 移除默认 model 参数)

#### D. src/ai/evaluation/evaluator.py

**修改的类/方法：**
- `class LLMEvaluator` (修改)
  - `__init__()` (修改)
  - `evaluate()` (修改)
  - `_parse_evaluation_response()` (修改)
  - `_build_proposal_from_dict()` (新增)
  - `_extract_json_block()` (新增)
  - `translate_reasoning_to_bilingual()` (新增)

#### E. templates/HyperliquidTrade.html

**修改的 JavaScript 函数：**
- `checkConnection()` (修改)
- `switchPair()` (修改)
- `updateAllPairPrices()` (修改)
- `getEvaluationSymbol()` (修改)

#### F. templates/js/api_diagnostics.js

**修改的函数：**
- `makeApiCall()` (修改)

#### G. 测试文件

**新增测试文件：**
- `tests/unit/web/test_hyperliquid_api_endpoints.py` (新增)
- `tests/smoke/test_hyperliquid_api_endpoints_smoke.py` (新增)
- `tests/integration/test_hyperliquid_api_endpoints_integration.py` (新增)
- `tests/unit/web/test_hyperliquid_llm_evaluation.py` (修改)
- `tests/smoke/test_hyperliquid_llm_evaluation_smoke.py` (新增)
- `tests/integration/test_hyperliquid_llm_evaluation_integration.py` (新增)

**修改的测试文件：**
- `tests/test_llm.py` (修改)
- `tests/test_multi_llm_evaluation.py` (修改)

---

### 三、未暂存的修改（9 个文件）

#### A. server.py

**修改的端点/函数：**
- `@app.get("/api/hyperliquid/status")` - `get_hyperliquid_status()` (修改)
- `@app.post("/api/evaluation/run")` - `run_evaluation()` (修改)

#### B. src/trading/hyperliquid_client.py

**修改的类/方法：**
- `class RateLimiter` (修改)
  - `can_make_request()` (修改)
- `class HyperliquidClient` (修改)
  - `_make_request()` (修改)
  - `fetch_market_data()` (修改)

#### C. templates/HyperliquidTrade.html

**修改的 JavaScript 函数：**
- `checkConnection()` (修改)
- `switchPair()` (修改)
- `updateAllPairPrices()` (修改)

#### D. 测试文件修改

**修改的测试文件：**
- `tests/e2e/test_error_display.py` (修改)
- `tests/smoke/test_hyperliquid_connection.py` (修改)
- `tests/smoke/test_hyperliquid_trade_page_smoke.py` (修改)
- `tests/unit/trading/test_hyperliquid_connection.py` (修改)
- `tests/unit/trading/test_hyperliquid_rate_limiter.py` (修改)

**删除的测试文件：**
- `tests/unit/web/test_hyperliquid_trade_page.py` (删除)

---

### 四、未跟踪的新文件（5 个）

1. `docs/test_parse_error_summary.md` - 文档
2. `tests/integration/test_hyperliquid_status_connected.py` - 集成测试
3. `tests/smoke/test_status_trace_header.py` - 冒烟测试
4. `tests/unit/test_hyperliquid_client_order_logging.py` - 单元测试
5. `tests/unit/web/test_hyperliquid_trade_page_unit.py` - 单元测试

---

### 五、其他文件修改

- `README.md` (修改)
- `start_server.sh` (新增)
- `test_translation.py` (修改)

---

## 统计摘要

- **已提交并推送**: 17 个提交（包括本次提交）
- **修改的文件数**: 17 个文件
- **新增代码行数**: 约 3836 行
- **删除代码行数**: 约 232 行
- **本次提交**: 
  - 14 个文件修改
  - 817 行新增
  - 80 行删除
  - 包含完整的修改日志文档

## 本次提交详情 (bf1686c)

本次提交包含：
- 修复单元测试和冒烟测试
- 更新服务器端点和客户端代码
- 添加完整的修改日志文档 (`docs/modification_log.md`)
- 添加新的测试文件
- 重命名测试文件以保持一致性

