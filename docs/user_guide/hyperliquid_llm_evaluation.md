# Hyperliquid LLM Evaluation Support Guide / Hyperliquid LLM 评估支持指南

## Overview / 概述

This guide explains how to use the Multi-LLM Evaluation API with Hyperliquid exchange. The API supports both Binance and Hyperliquid exchanges, allowing you to get AI-powered trading parameter suggestions for Hyperliquid trading pairs.

本指南介绍如何在 Hyperliquid 交易所上使用多 LLM 评估 API。API 支持 Binance 和 Hyperliquid 两个交易所，允许您获取 Hyperliquid 交易对的 AI 驱动交易参数建议。

**Code Location / 代码位置**: 
- API Endpoint: `server.py#run_evaluation`
- Exchange Client: `src/trading/hyperliquid_client.py#HyperliquidClient`
- Evaluator: `src/ai/evaluation/evaluator.py#MultiLLMEvaluator`

---

## Features / 功能特性

- ✅ **Multi-Exchange Support / 多交易所支持**: Use the same API for both Binance and Hyperliquid
- ✅ **Hyperliquid Market Data / Hyperliquid 市场数据**: Automatically fetches current market data from Hyperliquid
- ✅ **Exchange Context / 交易所上下文**: LLM receives Hyperliquid-specific context in evaluation prompts
- ✅ **Consistent Response Format / 一致的响应格式**: Same response structure as Binance evaluation
- ✅ **Error Handling / 错误处理**: Clear bilingual error messages for connection and data issues

---

## Prerequisites / 前置条件

Before using Hyperliquid LLM evaluation, ensure:

在使用 Hyperliquid LLM 评估之前，请确保：

1. **Hyperliquid Connection / Hyperliquid 连接**: HyperliquidClient must be connected and authenticated
   - See [Hyperliquid Connection Guide](./hyperliquid_connection.md) for setup instructions
   - 查看 [Hyperliquid 连接指南](./hyperliquid_connection.md) 了解设置说明

2. **LLM API Keys / LLM API 密钥**: At least one LLM provider must be configured
   - Gemini: `GEMINI_API_KEY`
   - OpenAI: `OPENAI_API_KEY`
   - Claude: `ANTHROPIC_API_KEY`
   - See [Multi-LLM Evaluation Guide](./multi_llm_evaluation.md) for LLM setup
   - 查看 [多 LLM 评估指南](./multi_llm_evaluation.md) 了解 LLM 设置

---

## API Usage / API 使用方法

### Endpoint / 端点

```
POST /api/evaluation/run
```

### Request Parameters / 请求参数

| Parameter / 参数 | Type / 类型 | Required / 必需 | Default / 默认值 | Description / 描述 |
|-----------------|------------|----------------|-----------------|-------------------|
| `symbol` | string | Yes / 是 | - | Trading pair symbol (e.g., "ETH/USDT:USDT") / 交易对符号（例如 "ETH/USDT:USDT"） |
| `exchange` | string | No / 否 | "binance" | Exchange name: "binance" or "hyperliquid" / 交易所名称："binance" 或 "hyperliquid" |
| `simulation_steps` | integer | No / 否 | 500 | Number of simulation steps for validation / 验证的模拟步数 |

### Request Example / 请求示例

#### Using Hyperliquid / 使用 Hyperliquid

```bash
curl -X POST http://localhost:8000/api/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ETH/USDT:USDT",
    "exchange": "hyperliquid",
    "simulation_steps": 500
  }'
```

#### Using Binance (Default) / 使用 Binance（默认）

```bash
curl -X POST http://localhost:8000/api/evaluation/run \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "ETH/USDT:USDT",
    "exchange": "binance",
    "simulation_steps": 500
  }'
```

### Response Format / 响应格式

The response format is consistent for both Binance and Hyperliquid:

响应格式对于 Binance 和 Hyperliquid 都是一致的：

```json
{
  "symbol": "ETHUSDT",
  "exchange": "hyperliquid",
  "individual_results": [
    {
      "provider_name": "Gemini",
      "rank": 1,
      "score": 85.5,
      "latency_ms": 1250,
      "proposal": {
        "recommended_strategy": "FundingRate",
        "spread": 0.012,
        "skew_factor": 120,
        "quantity": 0.1,
        "leverage": 5,
        "confidence": 0.85,
        "risk_level": "medium",
        "reasoning": "Based on Hyperliquid market conditions...",
        "parse_success": true
      },
      "simulation": {
        "realized_pnl": 150.0,
        "total_trades": 45,
        "win_rate": 0.62,
        "sharpe_ratio": 2.1,
        "simulation_steps": 500
      }
    }
  ],
  "aggregated": {
    "strategy_consensus": {
      "consensus_strategy": "FundingRate",
      "consensus_level": "majority",
      "consensus_ratio": 0.67,
      "consensus_count": 2,
      "total_models": 3,
      "strategy_votes": {
        "FundingRate": 2,
        "FixedSpread": 1
      },
      "strategy_percentages": {
        "FundingRate": 66.67,
        "FixedSpread": 33.33
      }
    },
    "consensus_confidence": 0.82,
    "consensus_proposal": {
      "recommended_strategy": "FundingRate",
      "spread": 0.012,
      "skew_factor": 120,
      "quantity": 0.1,
      "leverage": 5,
      "confidence": 0.82,
      "reasoning": "Consensus from multiple models..."
    },
    "avg_pnl": 145.5,
    "avg_sharpe": 2.05,
    "avg_win_rate": 0.60,
    "avg_latency_ms": 1350,
    "successful_evaluations": 3,
    "failed_evaluations": 0
  },
  "comparison_table": "Markdown formatted comparison table...",
  "consensus_report": {
    "summary": "Consensus recommendation summary..."
  },
  "market_data": {
    "symbol": "ETHUSDT",
    "mid_price": 3001.0,
    "best_bid": 3000.0,
    "best_ask": 3002.0,
    "funding_rate": 0.0001,
    "spread_bps": 6.66
  }
}
```

### Key Response Fields / 关键响应字段

- **`exchange`**: Indicates which exchange was used ("binance" or "hyperliquid") / 指示使用的交易所（"binance" 或 "hyperliquid"）
- **`market_data`**: Current market data from the specified exchange / 来自指定交易所的当前市场数据
- **`individual_results`**: Results from each LLM provider / 每个 LLM 提供商的结果
- **`aggregated`**: Consensus recommendation combining all models / 结合所有模型的共识建议

---

## Python API Usage / Python API 使用方法

### Basic Example / 基本示例

```python
import requests

# Run evaluation for Hyperliquid
# 为 Hyperliquid 运行评估
response = requests.post(
    "http://localhost:8000/api/evaluation/run",
    json={
        "symbol": "ETH/USDT:USDT",
        "exchange": "hyperliquid",
        "simulation_steps": 500
    }
)

data = response.json()

# Check exchange used
# 检查使用的交易所
print(f"Exchange: {data['exchange']}")  # Output: "hyperliquid"

# View consensus recommendation
# 查看共识建议
consensus = data["aggregated"]["consensus_proposal"]
print(f"Strategy: {consensus['recommended_strategy']}")
print(f"Spread: {consensus['spread']}")
print(f"Confidence: {consensus['confidence']}")

# View market data
# 查看市场数据
market_data = data["market_data"]
print(f"Mid Price: {market_data['mid_price']}")
print(f"Funding Rate: {market_data['funding_rate']}")
```

### Comparing Binance vs Hyperliquid / 比较 Binance 与 Hyperliquid

```python
import requests

def compare_exchanges(symbol):
    """Compare LLM recommendations for the same symbol on different exchanges"""
    """比较同一交易对在不同交易所上的 LLM 建议"""
    
    results = {}
    
    for exchange in ["binance", "hyperliquid"]:
        response = requests.post(
            "http://localhost:8000/api/evaluation/run",
            json={
                "symbol": symbol,
                "exchange": exchange,
                "simulation_steps": 500
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            consensus = data["aggregated"]["consensus_proposal"]
            results[exchange] = {
                "strategy": consensus["recommended_strategy"],
                "spread": consensus["spread"],
                "confidence": consensus["confidence"],
                "market_price": data["market_data"]["mid_price"]
            }
        else:
            print(f"Error for {exchange}: {response.json()}")
    
    # Compare results
    # 比较结果
    print(f"\nComparison for {symbol}:")
    print(f"{symbol} 的比较结果：")
    for exchange, result in results.items():
        print(f"\n{exchange.upper()}:")
        print(f"  Strategy: {result['strategy']}")
        print(f"  Spread: {result['spread']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Market Price: {result['market_price']}")

# Usage / 使用
compare_exchanges("ETH/USDT:USDT")
```

---

## Applying LLM Suggestions / 应用 LLM 建议

After running evaluation, you can apply the consensus recommendation to your strategy:

运行评估后，您可以将共识建议应用到策略：

### Apply Endpoint / 应用端点

```
POST /api/evaluation/apply
```

### Request Parameters / 请求参数

| Parameter / 参数 | Type / 类型 | Required / 必需 | Description / 描述 |
|-----------------|------------|----------------|-------------------|
| `source` | string | Yes / 是 | "consensus" or "individual" / "consensus" 或 "individual" |
| `provider_name` | string | No / 否 | Required if source="individual" / 如果 source="individual" 则必需 |
| `exchange` | string | No / 否 | "binance" or "hyperliquid" (default: same as evaluation) / "binance" 或 "hyperliquid"（默认：与评估相同） |

### Apply Example / 应用示例

```python
import requests

# Step 1: Run evaluation
# 步骤 1：运行评估
eval_response = requests.post(
    "http://localhost:8000/api/evaluation/run",
    json={
        "symbol": "ETH/USDT:USDT",
        "exchange": "hyperliquid",
        "simulation_steps": 500
    }
)

# Step 2: Apply consensus recommendation
# 步骤 2：应用共识建议
apply_response = requests.post(
    "http://localhost:8000/api/evaluation/apply",
    json={
        "source": "consensus",
        "exchange": "hyperliquid"
    }
)

if apply_response.status_code == 200:
    result = apply_response.json()
    print(f"Status: {result['status']}")
    print(f"Applied Config: {result['applied_config']}")
    print(f"Exchange: {result['exchange']}")
else:
    print(f"Error: {apply_response.json()}")
```

---

## Exchange-Specific Features / 交易所特定功能

### Hyperliquid-Specific Context / Hyperliquid 特定上下文

When using `exchange="hyperliquid"`, the LLM receives additional context:

当使用 `exchange="hyperliquid"` 时，LLM 会收到额外的上下文：

1. **Exchange Name in Symbol / 符号中的交易所名称**: Symbol includes "(HYPERLIQUID)" identifier
   - Example: "ETHUSDT (HYPERLIQUID)"
   - 示例："ETHUSDT (HYPERLIQUID)"

2. **Hyperliquid Market Data / Hyperliquid 市场数据**: 
   - Current funding rate from Hyperliquid
   - Real-time bid/ask prices
   - Position and leverage information
   - 来自 Hyperliquid 的当前资金费率
   - 实时买卖价格
   - 仓位和杠杆信息

3. **Exchange-Specific Parameters / 交易所特定参数**:
   - Hyperliquid leverage limits
   - Hyperliquid funding rate characteristics
   - Hyperliquid order types
   - Hyperliquid 杠杆限制
   - Hyperliquid 资金费率特征
   - Hyperliquid 订单类型

### Market Data Differences / 市场数据差异

The API automatically fetches market data from the specified exchange:

API 会自动从指定的交易所获取市场数据：

| Data Source / 数据源 | Binance | Hyperliquid |
|---------------------|---------|-------------|
| Price Data / 价格数据 | Binance API | Hyperliquid API |
| Funding Rate / 资金费率 | Binance funding rate | Hyperliquid funding rate |
| Account Data / 账户数据 | Binance account | Hyperliquid account |
| Position Info / 仓位信息 | Binance position | Hyperliquid position |

---

## Error Handling / 错误处理

### Common Errors / 常见错误

#### 1. Exchange Not Connected / 交易所未连接

**Error / 错误**:
```json
{
  "error": "Hyperliquid exchange not connected. Please connect to Hyperliquid first. / Hyperliquid 交易所未连接。请先连接到 Hyperliquid。"
}
```

**Solution / 解决方案**:
- Ensure HyperliquidClient is connected before running evaluation
- See [Hyperliquid Connection Guide](./hyperliquid_connection.md)
- 确保在运行评估之前 HyperliquidClient 已连接
- 查看 [Hyperliquid 连接指南](./hyperliquid_connection.md)

#### 2. Invalid Exchange Parameter / 无效的交易所参数

**Error / 错误**:
```json
{
  "error": "Invalid exchange parameter: invalid_exchange. Must be 'binance' or 'hyperliquid'. / 无效的交易所参数：invalid_exchange。必须是 'binance' 或 'hyperliquid'。"
}
```

**Solution / 解决方案**:
- Use only "binance" or "hyperliquid" as exchange parameter
- 仅使用 "binance" 或 "hyperliquid" 作为交易所参数

#### 3. Market Data Fetch Failure / 市场数据获取失败

**Error / 错误**:
```json
{
  "error": "Failed to fetch market data: Network error / 获取市场数据失败：网络错误"
}
```

**Solution / 解决方案**:
- Check network connection
- Verify exchange client is working
- Retry the request
- 检查网络连接
- 验证交易所客户端是否正常工作
- 重试请求

#### 4. No LLM Providers Available / 没有可用的 LLM 提供商

**Error / 错误**:
```json
{
  "error": "No LLM providers available. Please configure API keys."
}
```

**Solution / 解决方案**:
- Configure at least one LLM API key (Gemini, OpenAI, or Claude)
- See [Multi-LLM Evaluation Guide](./multi_llm_evaluation.md) for setup
- 配置至少一个 LLM API 密钥（Gemini、OpenAI 或 Claude）
- 查看 [多 LLM 评估指南](./multi_llm_evaluation.md) 了解设置

---

## Best Practices / 最佳实践

### 1. Connection Check / 连接检查

Always verify exchange connection before running evaluation:

在运行评估之前始终验证交易所连接：

```python
from src.trading.hyperliquid_client import HyperliquidClient

# Check connection
# 检查连接
client = HyperliquidClient()
if not client.is_connected:
    print("Please connect to Hyperliquid first")
    print("请先连接到 Hyperliquid")
    # Connect...
    # 连接...
```

### 2. Error Handling / 错误处理

Always handle errors gracefully:

始终优雅地处理错误：

```python
import requests

response = requests.post(
    "http://localhost:8000/api/evaluation/run",
    json={
        "symbol": "ETH/USDT:USDT",
        "exchange": "hyperliquid"
    }
)

if response.status_code == 200:
    data = response.json()
    # Process results...
    # 处理结果...
else:
    error = response.json()
    if isinstance(error, list) and len(error) > 0:
        error = error[0]
    print(f"Error: {error.get('error', 'Unknown error')}")
```

### 3. Exchange Selection / 交易所选择

Choose the exchange based on your trading needs:

根据您的交易需求选择交易所：

- **Use Binance** if:
  - You're already trading on Binance
  - You need Binance-specific features
  - 如果您已经在 Binance 上交易
  - 如果您需要 Binance 特定功能

- **Use Hyperliquid** if:
  - You're trading on Hyperliquid
  - You want to compare recommendations across exchanges
  - You need Hyperliquid-specific market data
  - 如果您在 Hyperliquid 上交易
  - 如果您想比较不同交易所的建议
  - 如果您需要 Hyperliquid 特定的市场数据

### 4. Simulation Steps / 模拟步数

Adjust simulation steps based on your needs:

根据您的需求调整模拟步数：

- **500 steps** (default): Good balance between accuracy and speed
- **1000+ steps**: More accurate but slower
- **100 steps**: Faster but less accurate (for quick testing)
- **500 步**（默认）：准确性和速度之间的良好平衡
- **1000+ 步**：更准确但更慢
- **100 步**：更快但不太准确（用于快速测试）

---

## Integration Examples / 集成示例

### Example 1: Automated Strategy Update / 示例 1：自动策略更新

```python
import requests
import time

def auto_update_strategy(symbol, exchange="hyperliquid", interval_minutes=60):
    """
    Automatically run evaluation and apply consensus recommendation
    自动运行评估并应用共识建议
    """
    while True:
        try:
            # Run evaluation
            # 运行评估
            eval_response = requests.post(
                "http://localhost:8000/api/evaluation/run",
                json={
                    "symbol": symbol,
                    "exchange": exchange,
                    "simulation_steps": 500
                }
            )
            
            if eval_response.status_code == 200:
                data = eval_response.json()
                consensus = data["aggregated"]["consensus_proposal"]
                
                # Apply if confidence is high
                # 如果置信度高则应用
                if consensus["confidence"] > 0.8:
                    apply_response = requests.post(
                        "http://localhost:8000/api/evaluation/apply",
                        json={
                            "source": "consensus",
                            "exchange": exchange
                        }
                    )
                    print(f"Applied strategy: {consensus['recommended_strategy']}")
                    print(f"已应用策略：{consensus['recommended_strategy']}")
            
        except Exception as e:
            print(f"Error: {e}")
        
        # Wait before next evaluation
        # 等待下一次评估
        time.sleep(interval_minutes * 60)

# Usage / 使用
auto_update_strategy("ETH/USDT:USDT", exchange="hyperliquid")
```

### Example 2: Multi-Exchange Comparison / 示例 2：多交易所比较

```python
import requests
import pandas as pd

def compare_exchange_recommendations(symbol):
    """
    Compare LLM recommendations across exchanges
    比较不同交易所的 LLM 建议
    """
    results = []
    
    for exchange in ["binance", "hyperliquid"]:
        try:
            response = requests.post(
                "http://localhost:8000/api/evaluation/run",
                json={
                    "symbol": symbol,
                    "exchange": exchange,
                    "simulation_steps": 500
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                consensus = data["aggregated"]["consensus_proposal"]
                market_data = data["market_data"]
                
                results.append({
                    "Exchange": exchange.upper(),
                    "Strategy": consensus["recommended_strategy"],
                    "Spread": consensus["spread"],
                    "Confidence": consensus["confidence"],
                    "Market Price": market_data["mid_price"],
                    "Funding Rate": market_data["funding_rate"]
                })
        except Exception as e:
            print(f"Error for {exchange}: {e}")
    
    # Create comparison DataFrame
    # 创建比较 DataFrame
    df = pd.DataFrame(results)
    print(df.to_string(index=False))
    
    return df

# Usage / 使用
compare_exchange_recommendations("ETH/USDT:USDT")
```

---

## Troubleshooting / 故障排除

### Issue: Evaluation returns error for Hyperliquid / 问题：Hyperliquid 评估返回错误

**Symptoms / 症状**:
- API returns error about exchange not connected
- API 返回关于交易所未连接的错误

**Solutions / 解决方案**:
1. Verify HyperliquidClient is initialized and connected
2. Check environment variables (HYPERLIQUID_API_KEY, HYPERLIQUID_API_SECRET)
3. Test connection separately before running evaluation
4. 验证 HyperliquidClient 已初始化并连接
5. 检查环境变量（HYPERLIQUID_API_KEY、HYPERLIQUID_API_SECRET）
6. 在运行评估之前单独测试连接

### Issue: Different recommendations for same symbol / 问题：同一交易对的不同建议

**Symptoms / 症状**:
- Binance and Hyperliquid return different recommendations for the same symbol
- Binance 和 Hyperliquid 对同一交易对返回不同的建议

**Explanation / 说明**:
- This is expected! Different exchanges have different market conditions
- Prices, funding rates, and liquidity can vary between exchanges
- LLM recommendations reflect these differences
- 这是预期的！不同交易所有不同的市场条件
- 价格、资金费率和流动性可能在交易所之间有所不同
- LLM 建议反映了这些差异

---

## Related Documentation / 相关文档

- [Multi-LLM Evaluation Guide](./multi_llm_evaluation.md) - General LLM evaluation usage
- [Hyperliquid Connection Guide](./hyperliquid_connection.md) - Setting up Hyperliquid connection
- [Hyperliquid Orders Guide](./hyperliquid_orders.md) - Hyperliquid order management
- [API Reference](../api_reference.md) - Complete API documentation
- [多 LLM 评估指南](./multi_llm_evaluation.md) - 一般 LLM 评估使用
- [Hyperliquid 连接指南](./hyperliquid_connection.md) - 设置 Hyperliquid 连接
- [Hyperliquid 订单指南](./hyperliquid_orders.md) - Hyperliquid 订单管理
- [API 参考](../api_reference.md) - 完整 API 文档

---

## Summary / 总结

The Hyperliquid LLM Evaluation API extends the Multi-LLM Evaluation System to support Hyperliquid exchange, allowing you to:

Hyperliquid LLM 评估 API 扩展了多 LLM 评估系统以支持 Hyperliquid 交易所，允许您：

1. ✅ Get AI-powered trading suggestions for Hyperliquid pairs
2. ✅ Compare recommendations across Binance and Hyperliquid
3. ✅ Use Hyperliquid-specific market data in LLM context
4. ✅ Apply suggestions directly to Hyperliquid strategies
5. ✅ 获取 Hyperliquid 交易对的 AI 驱动交易建议
6. ✅ 比较 Binance 和 Hyperliquid 的建议
7. ✅ 在 LLM 上下文中使用 Hyperliquid 特定的市场数据
8. ✅ 直接将建议应用到 Hyperliquid 策略

The API maintains consistency with Binance evaluation while providing exchange-specific context and data.

API 在提供交易所特定上下文和数据的同时，保持与 Binance 评估的一致性。



