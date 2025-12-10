# AI Module Unit Tests / AI 模块单元测试

This directory contains unit tests for the AI/LLM module.  
此目录包含 AI/LLM 模块的单元测试。

## Owner / 负责人

**Agent AI**

## Test Files / 测试文件

- `test_data_agent.py` - Data Agent tests / Data Agent 测试
- `test_evaluation_prompts.py` - Evaluation prompt tests / 评估提示词测试
- `test_gemini_provider.py` - Gemini provider tests / Gemini 提供商测试
- `test_llm_evaluation.py` - LLM evaluation tests / LLM 评估测试
- `test_llm_gateway.py` - LLM Gateway tests / LLM Gateway 测试
- `test_llm_providers.py` - LLM provider tests / LLM 提供商测试
- `test_multi_llm_evaluator.py` - Multi-LLM evaluator tests / 多 LLM 评估器测试
- `test_openai_provider.py` - OpenAI provider tests / OpenAI 提供商测试
- `test_quant_agent.py` - Quant Agent tests / Quant Agent 测试
- `test_risk_agent.py` - Risk Agent tests / Risk Agent 测试
- `test_translation.py` - Translation tests / 翻译测试

## Running Tests / 运行测试

```bash
# Run all AI module tests / 运行所有 AI 模块测试
pytest tests/unit/ai/ -v

# Run specific test file / 运行特定测试文件
pytest tests/unit/ai/test_llm_gateway.py -v
```
