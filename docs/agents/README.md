# 🤖 Cursor Multi-Agent 并行开发指南

本文档描述如何使用多个 Cursor Chat 会话作为独立的 Agent 并行开发本项目。

## 📋 Agent 概览

| Agent | 职责 | 负责目录 | 状态 |
|-------|------|----------|------|
| [Agent TRADING: 交易引擎](AGENT_1_TRADING_ENGINE.md) | 交易所接口、订单管理、策略 | `src/trading/`, `src/trading/strategies/` | ✅ 可启动 |
| [Agent PORTFOLIO: 组合管理](AGENT_2_PORTFOLIO.md) | 组合管理、风险指标 | `src/portfolio/` | ✅ 可启动 |
| [Agent WEB: Web/API](AGENT_3_WEB_API.md) | FastAPI、Dashboard | `server.py`, `templates/` | ✅ 可启动 |
| [Agent AI: AI 智能体](AGENT_4_AI_AGENTS.md) | 量化分析、评估框架 | `src/ai/agents/`, `src/ai/evaluation/` | ✅ 可启动 |
| [Agent QA: 文档/测试](AGENT_5_DOCS_QA.md) | 文档、测试、质量 | `docs/`, `tests/` | ✅ 可启动 |

## 🚀 快速启动

### 步骤 1: 打开多个 Cursor Chat

在 Cursor 中按 `Cmd+L` 打开 Chat，然后点击 `+` 新建多个聊天会话。

### 步骤 2: 初始化每个 Agent

在每个新的 Chat 会话中，粘贴以下初始化提示：

```
请阅读文件 docs/agents/AGENT_XXX.md，了解你作为该 Agent 的职责和规范。
从现在开始，你只负责该文件中指定的模块。
```

将 `XXX` 替换为对应的 Agent 名称（TRADING、PORTFOLIO、WEB、AI、QA）。

### 步骤 3: 开始工作

每个 Agent 可以独立工作于其负责的模块。

## 📊 模块依赖图

```
                    ┌─────────────────────────┐
                    │   Agent QA: 文档/测试    │
                    │    (只读 + 文档)         │
                    └─────────────────────────┘
                              ▲
                              │ 分析
    ┌─────────────────────────┼─────────────────────────┐
    │                         │                         │
    ▼                         ▼                         ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Agent TRADING │     │ Agent AI      │     │ Agent         │
│ 交易引擎       │◄───▶│ AI 智能体     │◄───▶│ PORTFOLIO     │
│ market/       │     │ agents/       │     │ 组合管理      │
│ strategies/   │     │ evaluation/   │     │ portfolio/    │
└───────────────┘     └───────────────┘     └───────────────┘
        ▲                     ▲                     ▲
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │ 调用接口
                              ▼
                    ┌─────────────────────────┐
                    │   Agent WEB: Web/API    │
                    │   server.py             │
                    └─────────────────────────┘
```

## ⚠️ 冲突避免规则

### 🔴 禁止同时修改的文件

| 文件 | 唯一负责者 |
|------|-----------|
| `server.py` | Agent WEB |
| `templates/index.html` | Agent WEB |
| `src/trading/engine.py` | Agent TRADING |

### 🟡 需要协调修改的文件

| 文件 | 修改时需通知 |
|------|-------------|
| `src/shared/config.py` | 所有 Agent |
| `requirements.txt` | 所有 Agent |
| `pyproject.toml` | 所有 Agent |

### 🟢 可以安全并行修改

- 不同目录下的文件
- 不同的测试文件
- 不同的文档文件

## 📝 协作协议

### 接口变更通知

当某个 Agent 需要修改公开接口时：

1. 在对应的 Agent 文档中记录变更
2. 通知依赖该接口的其他 Agent
3. 同步更新相关文档

### 共享配置变更

修改 `config.py` 时：

1. 先在 Agent 文档中说明原因
2. 确保向后兼容
3. 更新所有相关测试

## 🔧 常用命令

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定 Agent 相关测试
pytest tests/test_exchange*.py -v       # Agent TRADING
pytest tests/test_portfolio*.py -v      # Agent PORTFOLIO
pytest tests/test_server*.py -v         # Agent WEB
pytest tests/test_*agent*.py -v         # Agent AI

# 启动服务器
python server.py

# 检查代码风格
python -m flake8 src/
```

## 💡 最佳实践

1. **开始工作前**：先拉取最新代码
2. **修改前检查**：确认文件属于自己的职责范围
3. **完成后测试**：运行相关测试确保无破坏
4. **提交时注明**：使用规范的 commit 格式

## 📞 Agent 间通信

如果需要其他 Agent 配合：

```
@Agent TRADING: 请在 exchange.py 中添加 fetch_xxx 方法
@Agent PORTFOLIO: 请在 RiskIndicators 中添加 xxx 指标
```

将请求记录在此文档或相关 Agent 文档中。
