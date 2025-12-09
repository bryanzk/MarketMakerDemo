# 422 错误调用堆栈图示 / 422 Error Call Stack Diagram

## 错误信息 / Error Message

```
Hyperliquid invalid request (422) for /info. 
Request summary: {'action_type': None, 'nonce': None, 'has_signature': False, 'vaultAddress': None}, 
Response: HTTPError: 422 Client Error: Unprocessable Entity for url: https://api.hyperliquid-testnet.xyz/info.

Historical candle data not available for BTC. 
Using current price from allMids endpoint as fallback.
```

## 调用堆栈图示 / Call Stack Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 前端 / Frontend                                                              │
│ (Browser / API Client)                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ POST /api/evaluation/run
                              │ { "symbol": "BTC/USDC:USDC", "exchange": "hyperliquid" }
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. FastAPI Endpoint Handler                                                 │
│    server.py:2394                                                           │
│    @app.post("/api/evaluation/run")                                          │
│    async def run_evaluation(request: EvaluationRunRequest)                   │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用 calculate_volatility_1h_24h
                              │ server.py:2562
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Volatility Calculation Entry Point                                       │
│    src/trading/volatility.py:266                                            │
│    def calculate_volatility_1h_24h(                                        │
│        exchange, symbol: str, calculator: Optional[VolatilityCalculator]   │
│    ) -> Tuple[float, float]                                                 │
│                                                                              │
│    ├─ volatility_1h = fetch_and_calculate_volatility(                      │
│    │      exchange, symbol, hours=1, default=0.01, calculator=calculator     │
│    │  )                                                                      │
│    │                                                                         │
│    └─ volatility_24h = fetch_and_calculate_volatility(                   │
│          exchange, symbol, hours=24, default=0.03, calculator=calculator     │
│      )                                                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用 fetch_and_calculate_volatility
                              │ volatility.py:195
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Fetch and Calculate Volatility                                           │
│    src/trading/volatility.py:195                                            │
│    def fetch_and_calculate_volatility(                                     │
│        exchange, symbol: str, hours: int, default: float,                   │
│        calculator: Optional[VolatilityCalculator]                            │
│    ) -> float                                                                │
│                                                                              │
│    └─ prices = fetch_historical_prices(exchange, symbol, hours)              │
│       volatility.py:225                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用 fetch_historical_prices
                              │ volatility.py:145
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. Historical Prices Wrapper                                               │
│    src/trading/volatility.py:145                                            │
│    def fetch_historical_prices(                                             │
│        exchange, symbol: str, hours: int, interval_minutes: int = 1          │
│    ) -> List[float]                                                          │
│                                                                              │
│    └─ return exchange.fetch_historical_prices(symbol, hours, interval_minutes)│
│       volatility.py:167                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用 exchange.fetch_historical_prices
                              │ (HyperliquidClient 实例方法)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. HyperliquidClient.fetch_historical_prices                                │
│    src/trading/hyperliquid_client.py:1937                                   │
│    def fetch_historical_prices(                                              │
│        self, symbol: Optional[str] = None, hours: int = 24,                 │
│        interval_minutes: int = 1                                             │
│    ) -> List[float]                                                          │
│                                                                              │
│    策略 1: 尝试 SDK Info.candle_snapshot (失败)                              │
│    策略 2: 使用 REST API /info 端点 (candleSnapshot)                         │
│                                                                              │
│    └─ candle_payload = {                                                    │
│          "type": "candleSnapshot",                                          │
│          "req": {                                                            │
│              "coin": "BTC",                                                  │
│              "interval": "1m",                                               │
│              "n": 60                                                          │
│          }                                                                   │
│       }                                                                      │
│                                                                              │
│    └─ response = self._make_request(                                       │
│          method="POST",                                                      │
│          endpoint="/info",                                                  │
│          data=candle_payload,                                                │
│          public=True                                                        │
│      )                                                                      │
│      hyperliquid_client.py:2069                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 调用 _make_request
                              │ hyperliquid_client.py:2069
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. HyperliquidClient._make_request                                         │
│    src/trading/hyperliquid_client.py:950                                    │
│    def _make_request(                                                        │
│        self, method: str, endpoint: str, data: Optional[Dict] = None,      │
│        public: bool = False, max_retries: int = 3                            │
│    ) -> Optional[Dict]                                                       │
│                                                                              │
│    └─ requests.post(url, json=data, headers=headers, timeout=...)          │
│       hyperliquid_client.py:1000+                                           │
│                                                                              │
│    └─ 捕获 HTTPError (422)                                                  │
│       hyperliquid_client.py:1080+                                            │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPError: 422 Client Error
                              │ Unprocessable Entity
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 7. 422 错误处理 / 422 Error Handling                                        │
│    src/trading/hyperliquid_client.py:1080-1183                              │
│                                                                              │
│    ├─ 提取错误详情                                                          │
│    │   error_detail = e.response.json() 或 e.response.text                 │
│    │                                                                         │
│    ├─ 构建请求摘要 (隐藏敏感信息)                                            │
│    │   request_summary = {                                                   │
│    │       "action_type": None,  # candleSnapshot 没有 action.type          │
│    │       "nonce": None,       # 公共端点不需要 nonce                      │
│    │       "has_signature": False,  # 公共端点不需要签名                     │
│    │       "vaultAddress": None                                              │
│    │   }                                                                     │
│    │                                                                         │
│    └─ 记录错误日志                                                          │
│       logger.error(                                                          │
│           "Hyperliquid invalid request (422) for /info. "                   │
│           "Request summary: {request_summary}, "                             │
│           "Response: {error_detail}.",                                       │
│           extra={                                                            │
│               "request_data": {...},  # 清理后的请求数据                     │
│               "status_code": 422,                                            │
│               "error_detail": error_detail,                                   │
│               ...                                                             │
│           }                                                                  │
│       )                                                                      │
│       hyperliquid_client.py:1172                                            │
│                                                                              │
│    └─ return None  # 不重试 422 错误                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ _make_request 返回 None
                              │ (response is None)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 8. 回退到 allMids / Fallback to allMids                                     │
│    src/trading/hyperliquid_client.py:2097-2125                             │
│                                                                              │
│    if response is None:  # candleSnapshot 请求失败                          │
│        logger.warning(                                                        │
│            "Historical candle data not available for {coin}. "              │
│            "Using current price from allMids endpoint as fallback."           │
│        )                                                                     │
│        hyperliquid_client.py:2099                                           │
│                                                                              │
│        └─ mids_payload = {"type": "allMids"}                                │
│        └─ mids_response = self._make_request(                               │
│              method="POST",                                                  │
│              endpoint="/info",                                              │
│              data=mids_payload,                                             │
│              public=True                                                     │
│          )                                                                   │
│          hyperliquid_client.py:2106                                         │
│                                                                              │
│        └─ 如果成功，返回 [current_price] * num_points                        │
│        └─ 如果失败，使用 fetch_market_data() 作为最终回退                    │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 返回价格列表或空列表
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 9. 继续波动率计算 / Continue Volatility Calculation                        │
│    src/trading/volatility.py:225-263                                         │
│                                                                              │
│    └─ 如果 prices 为空或不足，使用默认值                                     │
│    └─ 否则计算波动率并返回                                                  │
│    └─ 返回 volatility_1h 和 volatility_24h                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                              │
                              │ 返回 (volatility_1h, volatility_24h)
                              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 10. 返回 API 响应 / Return API Response                                     │
│     server.py:2588-2606                                                      │
│                                                                              │
│     └─ context = MarketContext(                                             │
│           volatility_24h=volatility_24h,                                    │
│           volatility_1h=volatility_1h,                                     │
│           ...                                                                │
│       )                                                                      │
│                                                                              │
│     └─ 继续 LLM 评估流程                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 关键点说明 / Key Points

### 1. 错误发生位置 / Error Location
- **文件**: `src/trading/hyperliquid_client.py`
- **方法**: `_make_request` (line 2069 调用, line 1080-1183 处理)
- **端点**: `POST /info` with `candleSnapshot` type
- **错误码**: 422 Unprocessable Entity

### 2. 请求数据 / Request Data
```python
candle_payload = {
    "type": "candleSnapshot",
    "req": {
        "coin": "BTC",      # 从 symbol "BTC/USDC:USDC" 提取
        "interval": "1m",    # 从 interval_minutes=1 映射
        "n": 60             # hours * 60 // interval_minutes
    }
}
```

### 3. 为什么 request_summary 显示 None / Why request_summary Shows None
- `action_type: None` - `candleSnapshot` 请求没有 `action.type` 字段
- `nonce: None` - 公共端点 (`public=True`) 不需要 nonce
- `has_signature: False` - 公共端点不需要签名
- `vaultAddress: None` - 公共端点不需要 vaultAddress

### 4. 错误处理流程 / Error Handling Flow
1. **捕获 422 错误** - `except HTTPError as e` (line 1080)
2. **提取错误详情** - 从 `e.response.json()` 或 `e.response.text` 提取
3. **构建请求摘要** - 隐藏敏感信息，保留调试信息
4. **记录错误日志** - 包含完整的调试信息
5. **返回 None** - 不重试 422 错误（请求本身有问题）
6. **触发回退机制** - 使用 `allMids` 端点获取当前价格

### 5. 回退机制 / Fallback Mechanism
```
candleSnapshot 失败
    ↓
尝试 allMids 端点
    ↓
如果 allMids 也失败
    ↓
使用 fetch_market_data() 作为最终回退
    ↓
如果所有方法都失败
    ↓
返回空列表，使用默认波动率值
```

## 可能的原因 / Possible Causes

1. **交易对格式问题** / Symbol Format Issue
   - `coin` 提取可能不正确（例如 "BTC" vs "BTC/USDC:USDC"）
   - Hyperliquid 可能期望不同的 coin 名称格式

2. **间隔不支持** / Interval Not Supported
   - `interval_minutes=1` 映射到 `"1m"`，但可能不支持
   - 或者请求的 `n` 值超过限制

3. **API 端点变更** / API Endpoint Change
   - Hyperliquid API 可能已更新，`candleSnapshot` 格式已变更
   - 或者测试网 (`hyperliquid-testnet.xyz`) 的行为与主网不同

4. **网络/认证问题** / Network/Auth Issue
   - 虽然 `public=True`，但可能仍需要某些认证
   - 或者测试网环境配置问题

## 建议的调试步骤 / Recommended Debugging Steps

1. **检查请求格式** / Check Request Format
   ```python
   # 在 _make_request 中添加详细日志
   logger.debug(f"Request payload: {json.dumps(data, indent=2)}")
   ```

2. **验证 coin 名称** / Verify Coin Name
   ```python
   # 检查 coin 提取逻辑
   coin = symbol_base.replace("USDT", "").replace("/", "").replace(":", "").upper()
   # 可能需要使用 meta 响应中的确切 coin 名称
   ```

3. **测试官方 SDK** / Test Official SDK
   ```python
   # 确保 SDK Info.candle_snapshot 方法正确调用
   if hasattr(self._info, 'candle_snapshot'):
       candles = self._info.candle_snapshot(coin, official_interval, num_candles)
   ```

4. **检查 Hyperliquid 文档** / Check Hyperliquid Docs
   - 确认 `candleSnapshot` 请求格式是否最新
   - 验证测试网是否支持该端点

