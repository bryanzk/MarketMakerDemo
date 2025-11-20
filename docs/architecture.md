# 系统架构文档

## 系统概览

本项目实现了一个币安期货做市机器人，采用模块化设计，包含后端交易引擎和 Web UI 控制面板。

```mermaid
graph TB
    subgraph "Web UI (浏览器)"
        UI[Dashboard<br/>index.html]
    end
    
    subgraph "FastAPI 服务器"
        Server[server.py<br/>API 端点]
    end
    
    subgraph "交易引擎"
        Engine[main.py<br/>BotEngine]
        Strategy[strategy.py<br/>FixedSpreadStrategy]
        Risk[risk.py<br/>RiskManager]
        OM[order_manager.py<br/>OrderManager]
        Exchange[exchange.py<br/>BinanceClient]
    end
    
    subgraph "币安 API"
        Binance[Binance Futures<br/>Testnet]
    end
    
    UI -->|HTTP 请求| Server
    Server -->|获取状态| Engine
    Server -->|控制命令| Engine
    Engine --> Strategy
    Engine --> Risk
    Engine --> OM
    Engine --> Exchange
    Exchange -->|API 调用| Binance
    Binance -->|市场数据/订单| Exchange
```

---

## 核心模块架构

### 1. 配置层（Configuration）

```mermaid
graph LR
    ENV[.env<br/>API Keys] --> Config[config.py<br/>配置管理]
    Config --> Exchange[exchange.py]
    Config --> Engine[main.py]
```

**职责**：
- 加载环境变量（API 密钥）
- 定义交易参数（交易对、价差、仓位限制、杠杆）
- 系统参数（刷新间隔、日志级别）

---

### 2. 交易引擎层（Trading Engine）

```mermaid
graph TD
    Start[开始循环] --> FetchData[1. 获取数据]
    FetchData --> Market[市场数据<br/>orderbook]
    FetchData --> Account[账户数据<br/>position/balance]
    FetchData --> Orders[当前订单]
    FetchData --> Leverage[当前杠杆]
    
    Market --> CalcStrategy[2. 计算策略<br/>FixedSpreadStrategy]
    CalcStrategy --> TargetOrders[目标订单<br/>买/卖价格]
    
    TargetOrders --> RiskCheck[3. 风险检查<br/>RiskManager]
    Account --> RiskCheck
    RiskCheck --> FilteredOrders[过滤后订单]
    
    FilteredOrders --> Sync[4. 订单同步<br/>OrderManager]
    Orders --> Sync
    Sync --> ToCancel[待取消订单]
    Sync --> ToPlace[待下单订单]
    
    ToCancel --> Execute[5. 执行操作]
    ToPlace --> Execute
    Execute --> UpdateStatus[6. 更新状态]
    UpdateStatus --> Sleep[等待 2 秒]
    Sleep --> Start
```

**关键组件**：

#### BotEngine (main.py)
- **职责**: 主循环编排，状态管理
- **功能**:
  - 启动/停止控制
  - 数据聚合
  - 异常处理和自动恢复

#### FixedSpreadStrategy (strategy.py)
- **职责**: 计算目标订单价格
- **算法**:
  ```
  mid_price = (best_bid + best_ask) / 2
  buy_price = mid_price × (1 - spread_pct)
  sell_price = mid_price × (1 + spread_pct)
  ```

#### RiskManager (risk.py)
- **职责**: 仓位限制检查
- **规则**:
  - `position >= MAX_POSITION` → 禁止买入
  - `position <= -MAX_POSITION` → 禁止卖出

#### OrderManager (order_manager.py)
- **职责**: 订单同步逻辑
- **算法**: Diff 当前订单 vs 目标订单
  - 找出需要取消的订单（价格不匹配）
  - 找出需要新增的订单

---

### 3. 交易所接口层（Exchange Interface）

```mermaid
graph LR
    BinanceClient[BinanceClient<br/>exchange.py] --> Market[获取市场数据]
    BinanceClient --> Account[获取账户数据]
    BinanceClient --> Orders[订单管理]
    BinanceClient --> Leverage[杠杆设置]
    BinanceClient --> PnL[已实现盈亏]
    
    Orders --> Fetch[fetch_open_orders]
    Orders --> Place[place_orders]
    Orders --> Cancel[cancel_orders]
    Orders --> CancelAll[cancel_all_orders]
    
    Market --> Orderbook[fetch_order_book]
    Account --> AccountInfo[fapiPrivateV2GetAccount]
    Leverage --> GetLev[get_leverage]
    Leverage --> SetLev[set_leverage]
    PnL --> Income[fapiPrivateGetIncome]
```

**核心功能**：
- **市场数据**: 获取订单簿，计算中间价
- **账户数据**: 查询仓位、余额、入场价
- **订单管理**: 限价单下单、取消、批量取消
- **杠杆管理**: 获取/设置交易对杠杆
- **盈亏查询**: 获取已实现盈亏历史

---

### 4. Web UI 层（Web Interface）

```mermaid
graph TB
    subgraph "Frontend (HTML/JS)"
        Dashboard[仪表盘]
        Control[控制面板]
        Display[数据显示]
    end
    
    subgraph "Backend API"
        Status[GET /api/status]
        ControlAPI[POST /api/control]
        Config[POST /api/config]
        LeverageAPI[POST /api/leverage]
    end
    
    Dashboard -->|轮询 1s| Status
    Control -->|Start/Stop| ControlAPI
    Control -->|更新参数| Config
    Control -->|设置杠杆| LeverageAPI
    
    Status -->|返回状态| Display
```

**API 端点**：

| 端点 | 方法 | 功能 |
|------|------|------|
| `/` | GET | 返回 Dashboard HTML |
| `/api/status` | GET | 获取 bot 实时状态 |
| `/api/control` | POST | 启动/停止 bot |
| `/api/config` | POST | 更新策略参数 |
| `/api/leverage` | POST | 设置杠杆倍数 |

**状态数据结构**：
```json
{
  "mid_price": 2870.0,
  "position": -0.1,
  "balance": 6734.69,
  "orders": [...],
  "pnl": 1.0786,
  "realized_pnl": 0.0,
  "leverage": 5,
  "active": true,
  "error": null
}
```

---

## 数据流图

```mermaid
sequenceDiagram
    participant UI as Web UI
    participant Server as FastAPI
    participant Engine as BotEngine
    participant Exchange as BinanceClient
    participant Binance as Binance API
    
    Note over UI,Binance: 启动 Bot
    UI->>Server: POST /api/control?action=start
    Server->>Engine: engine.start()
    Engine->>Exchange: fetch_account_data() (验证连接)
    Exchange->>Binance: GET /fapi/v2/account
    Binance-->>Exchange: 账户数据
    Exchange-->>Engine: 返回
    Engine->>Engine: 启动后台线程
    Server-->>UI: {"status": "started"}
    
    Note over UI,Binance: 主循环（每 2 秒）
    loop 每次循环
        Engine->>Exchange: fetch_market_data()
        Exchange->>Binance: GET /fapi/v1/depth
        Binance-->>Exchange: 订单簿数据
        
        Engine->>Exchange: fetch_account_data()
        Exchange->>Binance: GET /fapi/v2/account
        Binance-->>Exchange: 仓位/余额
        
        Engine->>Exchange: fetch_open_orders()
        Exchange->>Binance: GET /fapi/v1/openOrders
        Binance-->>Exchange: 当前挂单
        
        Engine->>Engine: 计算策略 + 风险检查 + 订单同步
        
        Engine->>Exchange: cancel_orders(to_cancel)
        Exchange->>Binance: DELETE /fapi/v1/order
        
        Engine->>Exchange: place_orders(to_place)
        Exchange->>Binance: POST /fapi/v1/order
        
        Engine->>Engine: 更新 status
    end
    
    Note over UI,Binance: UI 轮询状态
    UI->>Server: GET /api/status
    Server->>Engine: engine.get_status()
    Engine-->>Server: 返回 status dict
    Server-->>UI: JSON 响应
    UI->>UI: 更新页面显示
```

---

## 错误处理流程

```mermaid
graph TD
    Start[运行中] --> Error{异常发生}
    Error -->|单次循环异常| Log[记录错误日志]
    Log --> Continue[继续下一次循环]
    Continue --> Start
    
    Error -->|严重异常| Critical[捕获在外层]
    Critical --> SetError[设置 status.error]
    Critical --> Stop[调用 stop()]
    Stop --> CancelOrders[取消所有订单]
    CancelOrders --> StatusInactive[设置 active=False]
    StatusInactive --> UIShow[UI 显示 ERROR 状态]
```

**安全机制**：
1. **双层异常捕获**: 循环内 + 循环外
2. **自动停止**: 严重错误时自动停止并撤单
3. **状态同步**: 错误信息实时传递到 UI
4. **Stop 时撤单**: 确保无残留订单

---

## 部署架构

```mermaid
graph TB
    subgraph "本地环境"
        Python[Python 3.11]
        Bot[Market Maker Bot<br/>main.py + server.py]
        Browser[浏览器<br/>localhost:8000]
    end
    
    subgraph "币安测试网"
        Testnet[Binance Futures Testnet<br/>testnet.binancefuture.com]
    end
    
    Python --> Bot
    Bot -->|WebSocket/HTTP| Testnet
    Browser -->|HTTP| Bot
```

**运行方式**：
```bash
# 启动服务器（包含 Web UI + Bot 引擎）
python3.11 server.py

# 或单独运行 Bot（命令行模式）
python3.11 main.py
```

---

## 技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **后端** | Python 3.11 | 主要编程语言 |
| **交易所 API** | ccxt | 统一交易所接口 |
| **Web 框架** | FastAPI | HTTP API 服务器 |
| **模板引擎** | Jinja2 | HTML 模板渲染 |
| **前端** | HTML/CSS/JS | 用户界面 |
| **配置管理** | python-dotenv | 环境变量加载 |

---

## 总结

该架构采用**分层解耦**设计：
- **展示层** (Web UI) 负责用户交互
- **应用层** (FastAPI) 负责 API 路由
- **业务层** (BotEngine) 负责策略编排
- **数据层** (BinanceClient) 负责外部交互

通过模块化设计，各组件职责清晰，易于测试和扩展。
