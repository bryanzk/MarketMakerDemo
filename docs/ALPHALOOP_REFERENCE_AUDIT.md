# AlphaLoop Reference Audit / AlphaLoop 引用审计

## Summary / 摘要

This document lists all files that contain references to `alphaloop` (directory path) that need to be updated to `src/` after the project structure migration.

本文档列出了所有包含需要从 `alphaloop/` 更新为 `src/` 的目录路径引用的文件。

**Note / 注意**: References to the `AlphaLoop` class name are **correct** and should **NOT** be changed. Only directory/import path references need updating.

**注意**：对 `AlphaLoop` 类名的引用是**正确的**，**不应**更改。只有目录/导入路径引用需要更新。

---

## Categories / 分类

### ✅ Correct References (No Change Needed) / 正确引用（无需更改）

These files reference the `AlphaLoop` **class name** which is correct:
这些文件引用了 `AlphaLoop` **类名**，这是正确的：

- `src/trading/engine.py` - Defines `class AlphaLoop`
- `src/trading/__init__.py` - Exports `AlphaLoop` class
- `server.py` - Imports and uses `AlphaLoop` class
- `run.py` - Imports and uses `AlphaLoop` class
- `tests/test_integration_business.py` - Tests `AlphaLoop` class
- `tests/test_main.py` - Tests `AlphaLoop` class
- All documentation mentioning "AlphaLoop framework" or "AlphaLoop system" (product name)

---

## ❌ Files Requiring Updates / 需要更新的文件

### 1. Test Coverage Commands / 测试覆盖率命令

#### `tests/TEST_COVERAGE_ANALYSIS.md`
- **Line 132**: `pytest tests/ --cov=alphaloop --cov-report=html`
- **Should be**: `pytest tests/ --cov=src --cov-report=html`

#### `docs/agents/AGENT_5_DOCS_QA.md`
- **Line 160**: `pytest --cov=alphaloop tests/`
- **Should be**: `pytest --cov=src tests/`

---

### 2. Import Path Examples / 导入路径示例

#### `docs/agents/AGENT_5_DOCS_QA.md`
- **Line 109**: `from alphaloop.xxx import YYY`
- **Should be**: `from src.xxx import YYY`

#### `docs/user_guide/multi_llm_evaluation.md`
- **Line 63**: `python -m alphaloop.evaluation.cli --symbol ETHUSDT`
- **Line 66**: `python -m alphaloop.evaluation.cli --symbol ETHUSDT --steps 1000`
- **Line 69**: `python -m alphaloop.evaluation.cli --symbol ETHUSDT --providers gemini,openai`
- **Line 75**: `from alphaloop.evaluation import MultiLLMEvaluator, MarketContext`
- **Line 76**: `from alphaloop.core.llm import create_all_providers`
- **Line 169**: `# alphaloop/core/config.py`
- **Line 411**: `from alphaloop.evaluation import MultiLLMEvaluator, MarketContext, AggregatedResult`
- **Line 412**: `from alphaloop.core.llm import create_all_providers`
- **Should be**: Update all to `src.ai.evaluation` and `src.ai.llm`

#### `docs/modules_overview.md`
- **Line 116**: `from src.trading.engine import AlphaLoop` (This is correct, but check context)

---

### 3. Directory Path References / 目录路径引用

#### `docs/specs/ai/TODO.md`
- **Line 39**: `alphaloop/strategies/strategy.py`
- **Line 40**: `alphaloop/evaluation/evaluator.py:271`
- **Line 41**: `alphaloop/strategies/funding.py`
- **Line 112**: `alphaloop/strategies/strategy.py`
- **Line 113**: `alphaloop/strategies/funding.py`
- **Line 177**: `alphaloop/evaluation/evaluator.py`
- **Line 472**: `alphaloop/evaluation/evaluator.py`
- **Line 473**: `alphaloop/evaluation/schemas.py`
- **Line 474**: `alphaloop/market/performance.py`
- **Line 475**: `alphaloop/agents/data.py`
- **Line 477**: `alphaloop/evaluation/backtester.py`
- **Line 478**: `alphaloop/evaluation/tracker.py`
- **Line 498**: `alphaloop/evaluation/evaluator.py`
- **Should be**: Update all to `src/trading/strategies/`, `src/ai/evaluation/`, `src/trading/market/`, `src/ai/agents/`

#### `docs/agents/AGENT_5_DOCS_QA.md`
- **Line 19**: `├── alphaloop/           # 框架文档`
- **Should be**: `├── src/           # 源代码目录` (or update context)

#### `docs/development_protocol.md`
- **Line 13**: `alphaloop.agents`, `alphaloop.strategies`, `alphaloop.market`
- **Line 14**: `alphaloop.agents`、`alphaloop.strategies`、`alphaloop.market`
- **Should be**: `src.ai.agents`, `src.trading.strategies`, `src.trading.market`

#### `docs/architecture_changes_per_instance_exchange.md`
- **Line 235**: `alphaloop.market.strategy_instance.BinanceClient`
- **Line 236**: `alphaloop.main.BinanceClient`
- **Should be**: `src.trading.market.strategy_instance.BinanceClient` and `src.trading.engine.BinanceClient` (if applicable)

#### `CHANGELOG.md`
- **Line 66**: `alphaloop/portfolio/risk.py`
- **Line 73**: `alphaloop/portfolio/health.py`
- **Line 83**: `alphaloop/market/strategy_instance.py`
- **Should be**: `src/portfolio/risk.py`, `src/portfolio/health.py`, `src/trading/market/strategy_instance.py`

#### `docs/api_reference.md`
- **Line 228**: `alphaloop/framework_design.md`
- **Should be**: `docs/framework/framework_design.md` (check if this is a relative path)

---

### 4. Module Coverage References / 模块覆盖率引用

#### `docs/development_protocol.md`
- **Line 13-14**: Coverage targets for `alphaloop.agents`, `alphaloop.strategies`, `alphaloop.market`
- **Should be**: Update to `src.ai.agents`, `src.trading.strategies`, `src.trading.market`

---

## 📋 Update Priority / 更新优先级

### High Priority / 高优先级
1. ✅ `tests/TEST_COVERAGE_ANALYSIS.md` - Test commands used in CI/CD
2. ✅ `docs/agents/AGENT_5_DOCS_QA.md` - Agent documentation with examples
3. ✅ `docs/development_protocol.md` - Development standards document
4. ✅ `CHANGELOG.md` - Project changelog

### Medium Priority / 中优先级
5. `docs/user_guide/multi_llm_evaluation.md` - User guide with code examples
6. `docs/specs/ai/TODO.md` - Specification document (may be outdated)
7. `docs/architecture_changes_per_instance_exchange.md` - Architecture documentation

### Low Priority / 低优先级
8. `docs/api_reference.md` - API reference (check if path is relative)
9. Other documentation files mentioning `alphaloop/` in descriptive text

---

## 🔍 Verification / 验证

After updates, verify with:
更新后，使用以下命令验证：

```bash
# Check for remaining alphaloop directory references (excluding class names)
grep -r "alphaloop/" docs/ tests/ --exclude-dir=__pycache__ | grep -v "AlphaLoop class" | grep -v "AlphaLoop framework" | grep -v "AlphaLoop system"

# Check for import path references
grep -r "from alphaloop\." docs/ tests/
grep -r "import alphaloop\." docs/ tests/
```

---

## 📝 Notes / 注意事项

1. **Class Name vs Directory**: `AlphaLoop` (class) is correct, `alphaloop/` (directory) needs update
2. **Product Name**: "AlphaLoop framework" or "AlphaLoop system" in documentation is correct
3. **Import Paths**: All `alphaloop.xxx` should become `src.xxx` (mapped to actual module structure)
4. **Directory Paths**: All `alphaloop/xxx` should become `src/xxx` (mapped to actual directory structure)

---

**Generated**: 2025-01-27
**Status**: Audit Complete / 审计完成

