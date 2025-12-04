# Smoke Tests / 冒烟测试

This directory contains smoke tests for quick system health verification.  
此目录包含用于快速系统健康验证的冒烟测试。

## Owner / 负责人

This directory is owned by **Agent QA**.  
此目录由 **Agent QA** 负责。

## Running Tests / 运行测试

```bash
# Run smoke tests / 运行冒烟测试
pytest tests/smoke/ -v

# Or use the smoke test script / 或使用冒烟测试脚本
./scripts/smoke_test.sh
```

## What Smoke Tests Check / 冒烟测试检查内容

1. Server starts successfully / 服务器启动成功
2. API endpoints respond / API 端点响应
3. Core functionality works / 核心功能正常
4. No critical errors / 无严重错误

## Test Files / 测试文件

### `test_hyperliquid_connection.py`
Smoke tests for US-CORE-004-A: Hyperliquid Connection and Authentication  
US-CORE-004-A 冒烟测试：Hyperliquid 连接与认证

**Coverage / 覆盖范围:**
- AC-1: Client initialization / 客户端初始化
- AC-2: Authentication success / 认证成功
- AC-3: Authentication failure handling / 认证失败处理
- AC-4: Testnet connection / 测试网连接
- AC-5: Connection health / 连接健康状态

**Run specific test / 运行特定测试:**
```bash
pytest tests/smoke/test_hyperliquid_connection.py -v
```

### `test_hyperliquid_orders.py`
Smoke tests for US-CORE-004-B: Hyperliquid Order Management  
US-CORE-004-B 冒烟测试：Hyperliquid 订单管理

**Coverage / 覆盖范围:**
- AC-1: Limit order placement / 限价单下单
- AC-3: Order cancellation / 订单取消
- AC-6: Open orders query / 未成交订单查询
- Order methods existence / 订单方法存在性
- Interface compatibility / 接口兼容性

**Run specific test / 运行特定测试:**
```bash
pytest tests/smoke/test_hyperliquid_orders.py -v
```

### `test_hyperliquid_positions.py`
Smoke tests for US-CORE-004-C: Hyperliquid Position and Balance Tracking  
US-CORE-004-C 冒烟测试：Hyperliquid 仓位与余额追踪

**Coverage / 覆盖范围:**
- AC-1: Balance fetching / 余额获取
- AC-2: Position tracking / 仓位追踪
- AC-3: Unrealized PnL calculation / 未实现盈亏计算
- AC-4: Realized PnL tracking / 已实现盈亏追踪
- AC-5: Position history / 仓位历史
- AC-6: Margin information / 保证金信息
- AC-7: Multi-symbol position support / 多交易对仓位支持
- AC-10: Error handling / 错误处理
- Method existence verification / 方法存在性验证

**Run specific test / 运行特定测试:**
```bash
pytest tests/smoke/test_hyperliquid_positions.py -v
```

### `test_hyperliquid_llm_evaluation.py`
Smoke tests for US-API-004: Hyperliquid LLM Evaluation Support  
US-API-004 冒烟测试：Hyperliquid LLM 评估支持

**Coverage / 覆盖范围:**
- AC-1: API accepts Hyperliquid exchange parameter / API 接受 Hyperliquid 交易所参数
- AC-2: Response format is correct / 响应格式正确
- AC-3: Hyperliquid market data is fetched / 获取 Hyperliquid 市场数据
- AC-5: Error handling when Hyperliquid is not connected / Hyperliquid 未连接时的错误处理
- Exchange parameter validation / 交易所参数验证

**Run specific test / 运行特定测试:**
```bash
pytest tests/smoke/test_hyperliquid_llm_evaluation.py -v
```

