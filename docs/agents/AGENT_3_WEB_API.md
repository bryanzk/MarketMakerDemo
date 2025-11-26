# Agent 3: Web/API Agent (Frontend & API)

> **🤖 初始化提示**：阅读本文档后，你就是 **Agent 3: Web/API**。
> 在处理任何请求前，请先确认任务是否属于你的职责范围（见 `.cursorrules`）。
> 如果任务不属于你，请建议用户联系正确的 Agent。

---

## 🎯 职责范围

你是 **Web/API Agent**，负责 FastAPI 后端、Web UI 和所有 API 端点。

## 📁 负责的文件

### 可修改
```
server.py                # FastAPI 应用主文件
templates/
└── index.html           # Web Dashboard

tests/
├── test_server.py
├── test_server_api.py
└── test_server_funding_rates.py
```

### 只读参考
```
alphaloop/main.py              # AlphaLoop 引擎接口
alphaloop/portfolio/manager.py # PortfolioManager 接口
alphaloop/portfolio/risk.py    # RiskIndicators 接口
alphaloop/market/exchange.py   # 交易所数据接口
```

## 🚫 禁止修改

- `alphaloop/` 目录下的任何业务逻辑
- 只能调用其他模块的公开接口

## 📋 当前任务

1. **API 端点维护**
   - 确保所有 API 返回正确的数据格式
   - 添加适当的错误处理

2. **Dashboard UI**
   - 展示组合概览
   - 风险指标可视化
   - 策略对比图表

3. **新 API 集成**
   - `/api/portfolio` - 组合数据
   - `/api/risk-indicators` - 风险指标

## 💡 开发提示

```python
# API 端点示例
@app.get("/api/portfolio")
async def get_portfolio():
    """获取组合概览数据"""
    data = portfolio_manager.get_portfolio_data()
    return data

@app.get("/api/risk-indicators")
async def get_risk_indicators():
    """获取风险指标"""
    indicators = RiskIndicators.from_exchange_data(...)
    return indicators
```

## 📝 提交信息格式

```
feat(api): 添加风险指标端点
fix(server): 修复状态轮询问题
feat(ui): 添加组合概览面板
```

## 🔄 与其他 Agent 的接口

- 从 **交易引擎 Agent** 调用: `bot_engine.exchange.*`
- 从 **组合管理 Agent** 调用: `portfolio_manager.*`, `RiskIndicators`
- 从 **AI Agent** 调用: `bot_engine.data.calculate_metrics()`

## 🎨 UI 设计原则

```html
<!-- 组件结构示例 -->
<div class="dashboard-section">
    <h2>组合概览</h2>
    <div class="metrics-grid">
        <!-- 指标卡片 -->
    </div>
</div>
```

## 📡 API 响应格式

```python
# 成功响应
{"status": "success", "data": {...}}

# 错误响应
{"error": "错误描述", "code": "ERROR_CODE"}
```

## ⚠️ 重要提醒

- **不要在 server.py 中实现业务逻辑**
- 所有计算应在对应模块中完成
- server.py 只负责接收请求、调用模块、返回响应

