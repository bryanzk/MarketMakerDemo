# LLM Trade Evaluation Page User Guide / LLM 交易评估页面用户指南

## Overview / 概述

The `LLMTrade` page provides a focused environment to tweak the Fixed Spread Strategy, run multi-LLM evaluations (Gemini, OpenAI, Claude), and immediately apply consensus or individual proposals.  
`LLMTrade` 页面提供一个专注环境，可调整固定价差策略、运行多 LLM 评估（Gemini、OpenAI、Claude），并快速应用共识或单模型建议。

---

## Flow / 流程

1. **Control Panel** – adjust spread, quantity, skew (funding) and leverage.  
   **控制面板** – 调整价差、数量、倾斜因子（资金费率）和杠杆。
2. **Evaluation Module** – click “Run Evaluation” to call `/api/evaluation/run`.  
   **评估模块** – 点击“Run Evaluation”触发 `/api/evaluation/run`。
3. **View Results** – compare each LLM’s strategy proposal + simulation stats.  
   **查看结果** – 对比各 LLM 的策略建议与模拟结果。
4. **Apply** – choose consensus or any provider via `/api/evaluation/apply`.  
   **一键应用** – 通过 `/api/evaluation/apply` 应用共识或单一模型建议。

---

## UI Sections / 界面模块

### Control Panel / 控制面板
- Symbol selector + Fixed Spread parameters.
- 历史上与主面板一致的参数输入组件（Spread、Quantity、Skew、Leverage）。

### Evaluation Module / 评估模块
- Run button, status text, error box.
- Results table with provider, spread, skew, quantity, leverage, confidence, PnL, Sharpe, win rate, score, Apply button.
- Consensus card showing consensus strategy, confidence, aggregated metrics (avg PnL/Sharpe/Win%).

### Navigation / 导航
- A link/button from the main dashboard to open `/evaluation` (LLMTrade page).

---

## API Usage / API 使用

- **Run**: `POST /api/evaluation/run` with `{ "symbol": "ETHUSDT" }` (optional `simulation_steps`).  
- **Apply**: `POST /api/evaluation/apply` with `{ "source": "consensus" }` or `{ "source": "individual", "provider_name": "Claude ..." }`.

---

## Notes / 注意事项

- Requires `GEMINI_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` set in `.env`.  
- 编写遵循项目双语文档要求；模块与主页面共用后端逻辑。***

