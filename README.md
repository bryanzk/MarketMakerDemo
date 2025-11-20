# Binance Futures Market Maker

一个用于币安期货市场的做市机器人，采用固定价差策略，支持 Web UI 实时监控和控制。

![Status](https://img.shields.io/badge/status-MVP-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-brightgreen)

---

## 📖 项目概述

**策略**: 固定价差双边做市（Fixed-Spread Market Making）

在 ETH/USDT 永续合约上，围绕市场中间价上下各 0.2% 的位置持续挂出买卖限价单（Post-Only），通过赚取买卖价差获利，同时设置绝对仓位限制控制风险。

**适用场景**: 主流币种（ETH、BTC）的流动性做市

---

## ✨ 核心功能

### 已实现 (MVP + Phase 2)

- ✅ **固定价差策略**: 围绕中间价上下 0.2% 挂单
- ✅ **自动订单管理**: 价格变动时自动调整订单
- ✅ **仓位风险控制**: ±0.2 ETH 绝对仓位限制
- ✅ **Web UI 控制面板**:
  - 实时数据监控（价格、仓位、余额、PnL）
  - Start/Stop 控制
  - 参数动态调整（价差、数量、杠杆）
  - 已实现盈亏追踪
- ✅ **安全停止机制**: Stop 时自动撤销所有订单
- ✅ **错误处理**: 异常时自动停止并撤单
- ✅ **杠杆控制**: 1-125x 杠杆设置

### 计划中 (Phase 3)

- 📋 库存倾斜（Inventory Skew）
- 📋 文件日志
- 📋 PnL 持久化

---

## 🚀 快速开始

### 1. 前置要求

- Python 3.11+
- Binance Futures Testnet 账户（[注册地址](https://testnet.binancefuture.com/zh-CN/futures/ETHUSDT)）

### 2. 安装依赖

```bash
# 克隆项目
git clone <your-repo-url>
cd market_maker

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API 密钥

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 填入你的 API Key 和 Secret
# BINANCE_API_KEY=your_testnet_api_key
# BINANCE_API_SECRET=your_testnet_api_secret
```

### 4. 启动服务器

```bash
python3.11 server.py
```

### 5. 访问 Web UI

打开浏览器访问: **http://localhost:8000**

---

## 📁 项目结构

```
market_maker/
├── config.py           # 配置管理（API 密钥、交易参数）
├── utils.py            # 工具函数（精度处理）
├── exchange.py         # 交易所接口（Binance API 封装）
├── strategy.py         # 策略逻辑（固定价差计算）
├── risk.py             # 风险管理（仓位限制）
├── order_manager.py    # 订单同步（Diff 算法）
├── main.py             # 主程序（BotEngine）
├── server.py           # FastAPI 服务器
├── templates/
│   └── index.html      # Web UI 界面
├── requirements.txt    # Python 依赖
└── .env.example        # 环境变量示例
```

---

## ⚙️ 配置参数

在 `config.py` 中调整策略参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `SYMBOL` | "ETH/USDT:USDT" | 交易对（永续合约） |
| `QUANTITY` | 0.02 | 每单数量（ETH） |
| `SPREAD_PCT` | 0.002 | 价差百分比（0.2%） |
| `MAX_POSITION` | 0.5 | 最大仓位（ETH） |
| `LEVERAGE` | 5 | 杠杆倍数 |
| `REFRESH_INTERVAL` | 2 | 刷新间隔（秒） |

**⚠️ 风险提示**: 
- 测试网仅供学习，不涉及真实资金
- 实盘前务必充分测试和理解策略风险

---

## 📊 使用指南

### 启动 Bot

1. 访问 http://localhost:8000
2. 点击 **"Start Bot"** 按钮
3. 观察 "Active Orders" 表格，确认订单已挂出

### 调整参数

**价差与数量**:
- 在 "Control Panel" 输入新的 Spread 和 Qty
- 点击 "Update Config"

**杠杆倍数**:
- 在 "Leverage (1-125x)" 输入框输入杠杆
- 点击 "Update Leverage"

### 停止 Bot

点击 **"Stop Bot"** 按钮，系统会：
1. 停止主循环
2. **自动撤销所有挂单**
3. 更新状态为 "STOPPED"

---

## 📈 监控指标

### 实时数据卡片

- **Mid Price**: 当前市场中间价
- **Position**: 当前持仓（正数=多头，负数=空头）
- **Balance**: 可用余额（USDT）
- **Unrealized PnL**: 未实现盈亏
- **Total Realized PnL**: 已实现盈亏（自设定起始时间）
- **Leverage**: 当前杠杆倍数

### Active Orders 表格

显示当前所有挂单的详细信息（ID、方向、价格、数量）

---

## 🏗️ 架构设计

详见 [architecture.md](./architecture.md) - 包含完整的架构图和模块说明。

**核心流程**:
```
获取数据 → 计算策略 → 风险检查 → 订单同步 → 执行操作 → 更新状态
```

---

## 🔧 开发

### 命令行模式

不使用 Web UI，直接运行 Bot：

```bash
python3.11 main.py
```

### 调试工具

项目包含多个调试脚本：
- `debug_markets.py`: 查看可用交易对
- `debug_realized_pnl.py`: 查看盈亏历史

---

## 📚 文档

- [交易策略说明](./trading_strategy.md) - 详细的策略解释（专家级 + 新手友好）
- [架构文档](./architecture.md) - 系统架构和数据流图
- [实现计划](./implementation_plan.md) - 技术实现细节

---

## 🛣️ Roadmap

- [x] **Phase 1**: Core MVP（命令行做市）
- [x] **Phase 2**: Web UI（监控面板 + 控制）
- [ ] **Phase 3**: 高级功能（库存倾斜、日志、PnL 持久化）
- [ ] **Future**: 多币种支持、动态价差、回测系统

---

## ⚠️ 免责声明

本项目仅供学习和研究使用。加密货币交易存在高风险，可能导致本金损失。作者不对任何交易损失承担责任。

使用本项目即表示您：
- 了解加密货币交易的风险
- 仅在测试网环境进行初步测试
- 对自己的交易决策负全责

---

## 📄 License

MIT License - 详见 [LICENSE](./LICENSE) 文件

---

## 🙏 致谢

- [CCXT](https://github.com/ccxt/ccxt) - 统一的加密货币交易所 API
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [Binance](https://www.binance.com/) - 提供 Testnet 环境

---

**开发者**: [@kezheng](https://github.com/kezheng)  
**最后更新**: 2025-11-20
