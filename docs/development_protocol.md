# Development Protocol / 开发协议

This document establishes the mandatory standards for all development work on the AlphaLoop project.
本文档确立了 AlphaLoop 项目所有开发工作的强制性标准。

## 1. Testing Standards / 测试标准

**Rule**: No code changes without verification.
**规则**：未经验证，不得更改代码。

*   **Unit Tests**: All business logic (Agents, Strategy, Risk) must have unit tests.
    *   **单元测试**：所有业务逻辑（智能体、策略、风控）必须有单元测试。
*   **Coverage**: Aim for 100% coverage on core modules (`src.ai.agents`, `src.trading.strategies`, `src.trading.market`).
    *   **覆盖率**：核心模块（`src.ai.agents`、`src.trading.strategies`、`src.trading.market`）的目标覆盖率 100%。
*   **Execution**: Run `pytest` before every commit.
    *   **执行**：每次提交前运行 `pytest`。

## 2. Documentation Standards / 文档标准

**Rule**: All documentation must be Bilingual (English/Chinese) and Auto-updated.
**规则**：所有文档必须是双语（英文/中文）且自动更新。

*   **Format**: English paragraph first, followed by Chinese translation on a new line.
    *   **格式**：先写英文段落，随后另起一行写中文翻译。
*   **Scope**: `README.md`, `docs/*.md`, and major code comments.
    *   **范围**：`README.md`、`docs/*.md` 和主要代码注释。
*   **Sync**: When logic changes, update the corresponding documentation immediately.
    *   **同步**：逻辑变更时，立即更新相应文档。

## 3. Agent Workflow / 智能体工作流

When an AI Agent (like me) works on this repo:
当 AI 智能体（像我一样）在此仓库工作时：

1.  **Plan**: Create/Update `task.md` and `implementation_plan.md`.
    *   **计划**：创建/更新 `task.md` 和 `implementation_plan.md`。
2.  **Test**: Check existing tests.
    *   **测试**：检查现有测试。
3.  **Code**: Implement changes.
    *   **编码**：实施变更。
4.  **Verify**: Run tests and verify functionality.
    *   **验证**：运行测试并验证功能。
5.  **Document**: Update bilingual docs.
    *   **文档**：更新双语文档。
