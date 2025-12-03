# Hyperliquid Connection and Authentication Guide / Hyperliquid 连接与认证指南

## Overview / 概述

This guide explains how to connect to Hyperliquid exchange and authenticate with API credentials. HyperliquidClient provides the same interface as BinanceClient, allowing seamless switching between exchanges.

本指南介绍如何连接到 Hyperliquid 交易所并使用 API 凭证进行认证。HyperliquidClient 提供与 BinanceClient 相同的接口，允许在交易所之间无缝切换。

**Code Location / 代码位置**: `src/trading/hyperliquid_client.py#HyperliquidClient`

---

## Features / 功能特性

- ✅ **Connection Management / 连接管理**: Automatic connection and authentication during initialization
- ✅ **Testnet Support / 测试网支持**: Switch between testnet and mainnet environments
- ✅ **Error Handling / 错误处理**: Bilingual error messages (English/Chinese)
- ✅ **Interface Compatibility / 接口兼容性**: Same interface as BinanceClient for seamless integration
- ✅ **Retry Mechanism / 重试机制**: Automatic retry with exponential backoff for network errors

---

## Configuration / 配置

### Environment Variables / 环境变量

Set the following environment variables before using HyperliquidClient:

在使用 HyperliquidClient 之前，请设置以下环境变量：

```bash
# Hyperliquid API Credentials / Hyperliquid API 凭证
export HYPERLIQUID_API_KEY="your_api_key_here"
export HYPERLIQUID_API_SECRET="your_api_secret_here"

# Testnet Configuration / 测试网配置
# Set to "true" for testnet, "false" or omit for mainnet
# 设置为 "true" 使用测试网，"false" 或省略使用主网
export HYPERLIQUID_TESTNET="true"
```

### Configuration File / 配置文件

The configuration is also loaded from `src/shared/config.py`:

配置也会从 `src/shared/config.py` 加载：

```python
HYPERLIQUID_API_KEY = os.getenv("HYPERLIQUID_API_KEY")
HYPERLIQUID_API_SECRET = os.getenv("HYPERLIQUID_API_SECRET")
HYPERLIQUID_TESTNET = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"
```

---

## Usage / 使用方法

### Basic Connection / 基本连接

The simplest way to connect is to initialize HyperliquidClient with default configuration:

最简单的连接方式是使用默认配置初始化 HyperliquidClient：

```python
from src.trading.hyperliquid_client import HyperliquidClient

# Initialize with environment variables
# 使用环境变量初始化
client = HyperliquidClient()

# Check connection status
# 检查连接状态
if client.is_connected:
    print("Connected to Hyperliquid!")
    print("已连接到 Hyperliquid！")
```

### Custom Configuration / 自定义配置

You can also provide credentials explicitly:

您也可以显式提供凭证：

```python
from src.trading.hyperliquid_client import HyperliquidClient

# Initialize with explicit credentials
# 使用显式凭证初始化
client = HyperliquidClient(
    api_key="your_api_key",
    api_secret="your_api_secret",
    testnet=True,  # Use testnet / 使用测试网
    symbol="ETH/USDT:USDT"  # Optional trading symbol / 可选交易对
)
```

### Testnet vs Mainnet / 测试网与主网

**Testnet / 测试网**:
- URL: `https://api.hyperliquid-testnet.xyz`
- Use for testing and development
- 用于测试和开发

**Mainnet / 主网**:
- URL: `https://api.hyperliquid.xyz`
- Use for live trading
- 用于实盘交易

```python
# Testnet connection / 测试网连接
testnet_client = HyperliquidClient(testnet=True)

# Mainnet connection / 主网连接
mainnet_client = HyperliquidClient(testnet=False)
```

---

## API Reference / API 参考

### Initialization / 初始化

```python
HyperliquidClient(
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    testnet: Optional[bool] = None,
    symbol: Optional[str] = None
)
```

**Parameters / 参数**:
- `api_key` (optional): API key. Defaults to `HYPERLIQUID_API_KEY` environment variable.
- `api_secret` (optional): API secret. Defaults to `HYPERLIQUID_API_SECRET` environment variable.
- `testnet` (optional): Use testnet. Defaults to `HYPERLIQUID_TESTNET` environment variable.
- `symbol` (optional): Trading symbol. Defaults to `SYMBOL` from config.

**Raises / 抛出异常**:
- `AuthenticationError`: If API credentials are missing or invalid
- `ConnectionError`: If connection to Hyperliquid API fails

### Properties / 属性

| Property / 属性 | Type / 类型 | Description / 描述 |
|----------------|------------|-------------------|
| `is_connected` | `bool` | Connection status / 连接状态 |
| `base_url` | `str` | API base URL / API 基础 URL |
| `symbol` | `str` | Current trading symbol / 当前交易对 |
| `testnet` | `bool` | Whether using testnet / 是否使用测试网 |
| `api_key` | `str` | API key (masked in logs) / API 密钥（日志中已掩码） |

### Methods / 方法

HyperliquidClient implements the same interface as BinanceClient. Key methods include:

HyperliquidClient 实现与 BinanceClient 相同的接口。关键方法包括：

#### Data Fetching / 数据获取

```python
# Fetch market data / 获取市场数据
market_data = client.fetch_market_data()
# Returns: {"best_bid": float, "best_ask": float, "mid_price": float, "timestamp": int}

# Fetch funding rate / 获取资金费率
funding_rate = client.fetch_funding_rate()
# Returns: float (e.g., 0.0001)

# Fetch account data / 获取账户数据
account_data = client.fetch_account_data()
# Returns: {"position_amt": float, "entry_price": float, "available_balance": float}
```

#### Order Management / 订单管理

```python
# Place orders / 下单
orders = [
    {"side": "buy", "price": 1000.0, "quantity": 0.01},
    {"side": "sell", "price": 1002.0, "quantity": 0.01}
]
placed_orders = client.place_orders(orders)

# Fetch open orders / 获取未平仓订单
open_orders = client.fetch_open_orders()

# Cancel orders / 取消订单
canceled = client.cancel_orders(["order_id_1", "order_id_2"])
```

#### Symbol Management / 交易对管理

```python
# Set trading symbol / 设置交易对
client.set_symbol("BTC/USDT:USDT")

# Set leverage / 设置杠杆
client.set_leverage(5)  # 5x leverage / 5倍杠杆
```

---

## Error Handling / 错误处理

### Authentication Errors / 认证错误

If API credentials are missing or invalid:

如果 API 凭证缺失或无效：

```python
from src.trading.hyperliquid_client import HyperliquidClient, AuthenticationError

try:
    client = HyperliquidClient()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    print(f"认证失败：{e.message}")
    # Error message is bilingual / 错误消息是双语的
```

**Error Message Example / 错误消息示例**:
```
Missing API credentials. Please set HYPERLIQUID_API_KEY and HYPERLIQUID_API_SECRET environment variables.
缺少 API 凭证。请设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET 环境变量。
```

### Connection Errors / 连接错误

If connection to Hyperliquid API fails:

如果连接到 Hyperliquid API 失败：

```python
from src.trading.hyperliquid_client import HyperliquidClient, ConnectionError

try:
    client = HyperliquidClient()
except ConnectionError as e:
    print(f"Connection failed: {e.message}")
    print(f"连接失败：{e.message}")
```

### Retry Mechanism / 重试机制

HyperliquidClient automatically retries failed requests with exponential backoff:

HyperliquidClient 会自动使用指数退避重试失败的请求：

- **Max Retries / 最大重试次数**: 3
- **Retry Delays / 重试延迟**: 1s, 2s, 4s (exponential backoff / 指数退避)

---

## Integration Examples / 集成示例

### With StrategyInstance / 与 StrategyInstance 集成

HyperliquidClient can be used as a drop-in replacement for BinanceClient:

HyperliquidClient 可以作为 BinanceClient 的直接替代品使用：

```python
from src.trading.strategy_instance import StrategyInstance
from src.trading.hyperliquid_client import HyperliquidClient

# Create strategy instance with Hyperliquid exchange
# 使用 Hyperliquid 交易所创建策略实例
# Note: Currently StrategyInstance uses BinanceClient by default
# 注意：目前 StrategyInstance 默认使用 BinanceClient
# This is a future enhancement for exchange selection
# 这是未来交易所选择功能的增强
```

### Interface Compatibility / 接口兼容性

Both HyperliquidClient and BinanceClient implement the same interface:

HyperliquidClient 和 BinanceClient 都实现相同的接口：

```python
from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.exchange import BinanceClient

# Both clients have the same methods
# 两个客户端都有相同的方法
hyperliquid = HyperliquidClient()
binance = BinanceClient()

# Same interface / 相同接口
market_data_hl = hyperliquid.fetch_market_data()
market_data_bn = binance.fetch_market_data()

# Both return the same structure
# 两者返回相同的结构
assert "mid_price" in market_data_hl
assert "mid_price" in market_data_bn
```

---

## Best Practices / 最佳实践

### 1. Use Testnet for Development / 开发时使用测试网

Always test with testnet before using mainnet:

在使用主网之前，始终使用测试网进行测试：

```python
# Development / 开发
dev_client = HyperliquidClient(testnet=True)

# Production / 生产
prod_client = HyperliquidClient(testnet=False)
```

### 2. Handle Errors Gracefully / 优雅处理错误

Always wrap initialization in try-except:

始终在 try-except 中包装初始化：

```python
try:
    client = HyperliquidClient()
    if client.is_connected:
        # Proceed with trading operations
        # 继续交易操作
        pass
except (AuthenticationError, ConnectionError) as e:
    # Log error and handle appropriately
    # 记录错误并适当处理
    logger.error(f"Failed to connect: {e.message}")
```

### 3. Check Connection Status / 检查连接状态

Verify connection before performing operations:

在执行操作之前验证连接：

```python
client = HyperliquidClient()

if not client.is_connected:
    raise RuntimeError("Not connected to Hyperliquid")
    # 未连接到 Hyperliquid

# Safe to proceed / 可以安全继续
market_data = client.fetch_market_data()
```

### 4. Environment Variable Security / 环境变量安全

Never hardcode API credentials in code:

永远不要在代码中硬编码 API 凭证：

```python
# ❌ Bad / 错误
client = HyperliquidClient(
    api_key="hardcoded_key",  # Don't do this / 不要这样做
    api_secret="hardcoded_secret"
)

# ✅ Good / 正确
# Use environment variables / 使用环境变量
client = HyperliquidClient()  # Reads from env vars / 从环境变量读取
```

---

## Troubleshooting / 故障排除

### Issue: Authentication Fails / 问题：认证失败

**Symptoms / 症状**:
- `AuthenticationError` raised during initialization
- 初始化时抛出 `AuthenticationError`

**Solutions / 解决方案**:
1. Verify API credentials are set correctly:
   验证 API 凭证是否正确设置：
   ```bash
   echo $HYPERLIQUID_API_KEY
   echo $HYPERLIQUID_API_SECRET
   ```

2. Check credentials are valid on Hyperliquid:
   检查凭证在 Hyperliquid 上是否有效：
   - Testnet: https://app.hyperliquid-testnet.xyz
   - Mainnet: https://app.hyperliquid.xyz

3. Ensure no extra spaces in environment variables:
   确保环境变量中没有多余空格：
   ```bash
   export HYPERLIQUID_API_KEY="your_key"  # No spaces / 无空格
   ```

### Issue: Connection Timeout / 问题：连接超时

**Symptoms / 症状**:
- `ConnectionError` raised
- Network timeout errors

**Solutions / 解决方案**:
1. Check internet connection:
   检查互联网连接

2. Verify Hyperliquid API is accessible:
   验证 Hyperliquid API 是否可访问：
   ```bash
   curl https://api.hyperliquid.xyz/info
   ```

3. Check firewall settings:
   检查防火墙设置

### Issue: Testnet vs Mainnet Confusion / 问题：测试网与主网混淆

**Symptoms / 症状**:
- Connected to wrong environment
- 连接到错误的环境

**Solutions / 解决方案**:
1. Verify `HYPERLIQUID_TESTNET` environment variable:
   验证 `HYPERLIQUID_TESTNET` 环境变量：
   ```bash
   echo $HYPERLIQUID_TESTNET  # Should be "true" or "false"
   ```

2. Check `client.testnet` property:
   检查 `client.testnet` 属性：
   ```python
   client = HyperliquidClient()
   print(f"Using testnet: {client.testnet}")
   print(f"Base URL: {client.base_url}")
   ```

---

## Related Documentation / 相关文档

- **Specification / 规范**: `docs/specs/trading/CORE-004.md`
- **User Story / 用户故事**: `docs/stories/trading/US-CORE-004-A.md`
- **Interface Contract / 接口契约**: `contracts/trading.json#HyperliquidClient`
- **Unit Tests / 单元测试**: `tests/unit/trading/test_hyperliquid_connection.py`
- **Integration Tests / 集成测试**: `tests/integration/test_hyperliquid_integration.py`
- **Smoke Tests / 冒烟测试**: `tests/smoke/test_hyperliquid_connection.py`

---

## Support / 支持

For issues or questions, please refer to:
如有问题或疑问，请参考：

- Project Issues: GitHub Issues
- Documentation: `docs/` directory
- Code: `src/trading/hyperliquid_client.py`

---

**Last Updated / 最后更新**: 2025-12-01  
**Owner / 负责人**: Agent QA  
**Feature / 功能**: US-CORE-004-A

