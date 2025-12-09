# Symbol Mismatch Fix / 交易对不匹配修复

## Problem / 问题

When placing orders for BTC, the reference price shows ETC price (3340.30) instead of BTC price (~93000).
当为 BTC 下单时，参考价格显示的是 ETC 价格（3340.30）而不是 BTC 价格（~93000）。

**Error Example / 错误示例**:
```
Order price 93045.9 is 2685.56% away from reference price 3340.30.
订单价格 93045.9 与参考价格 3340.30 相差 2685.56%。
```

This indicates that `fetch_market_data()` was called with the wrong symbol.
这表明 `fetch_market_data()` 使用了错误的交易对调用。

## Root Cause Analysis / 根本原因分析

### Data Flow / 数据流

```
Frontend (UI)
    │
    │ POST /api/hyperliquid/pair (update symbol)
    │ { "symbol": "BTC/USDC:USDC" }
    ▼
Backend API Handler
    server.py: update_hyperliquid_pair()
    │
    │ Updates instance.symbol
    │ Updates instance.exchange.symbol (direct assignment)
    ▼
StrategyInstance
    instance.symbol = "BTC/USDC:USDC"
    instance.exchange.symbol = "BTC/USDC:USDC" (may not trigger internal updates)
    │
    │ refresh_data() called
    │
    │ instance.exchange.set_symbol(instance.symbol) ✅ (if exchange connected)
    │ OR
    │ instance.exchange.symbol = instance.symbol ❌ (if not connected - no internal update)
    ▼
HyperliquidClient
    self.symbol = "BTC/USDC:USDC" (may be set)
    BUT: _asset_index_map, _meta_cache may not be updated
    │
    │ place_orders() called
    │
    │ fetch_market_data() uses self.symbol
    │ BUT: self.symbol may still be "ETC/USDC:USDC" ❌
    ▼
fetch_market_data()
    Extracts coin from self.symbol
    If self.symbol = "ETC/USDC:USDC" → coin = "ETC" ❌
    Fetches market data for ETC instead of BTC ❌
```

## Fixes Applied / 已应用的修复

### 1. Enhanced Symbol Update in API Handler / 增强 API 处理程序中的交易对更新

**File**: `server.py:1309-1315`

**Before / 之前**:
```python
if hasattr(instance.exchange, 'symbol'):
    instance.exchange.symbol = pair.symbol  # Direct assignment - may not update internal state
```

**After / 之后**:
```python
# Always call set_symbol to ensure internal state is updated
# 始终调用 set_symbol 以确保内部状态已更新
if hasattr(instance.exchange, 'set_symbol'):
    success = instance.exchange.set_symbol(pair.symbol)
    if not success:
        logger.warning("Failed to set symbol on exchange, but instance symbol updated.")
elif hasattr(instance.exchange, 'symbol'):
    # Fallback: direct assignment if set_symbol not available
    instance.exchange.symbol = pair.symbol
```

### 2. Enhanced Logging in place_orders / 增强 place_orders 中的日志

**File**: `src/trading/hyperliquid_client.py:2790-2796`

**Added / 添加**:
- Log current symbol at start of `place_orders`
- Log symbol and coin before fetching market data
- Log market data result (symbol, coin, mid_price)

### 3. Enhanced Logging in fetch_market_data / 增强 fetch_market_data 中的日志

**File**: `src/trading/hyperliquid_client.py:1550-1564`

**Added / 添加**:
- Log current symbol when `fetch_market_data` is called
- Log extracted coin name from symbol
- This helps identify if wrong symbol is being used

### 4. Symbol Mismatch Detection / 交易对不匹配检测

**File**: `src/trading/hyperliquid_client.py:2967-2981`

**Added / 添加**:
- Detect when order price and reference price ratio is > 10x or < 0.1x
- This indicates market data was fetched for wrong coin
- Log error and skip order placement if mismatch detected

### 5. Enhanced set_symbol Logging / 增强 set_symbol 日志

**File**: `src/trading/hyperliquid_client.py:1485-1497`

**Added / 添加**:
- Log old symbol → new symbol transition
- This helps track symbol updates

## Verification Steps / 验证步骤

### Step 1: Check Symbol Update Flow / 步骤 1: 检查交易对更新流程

1. Frontend updates symbol via `/api/hyperliquid/pair`
2. Backend updates `instance.symbol` and calls `exchange.set_symbol()`
3. `HyperliquidClient.set_symbol()` updates `self.symbol` and calls `_initialize_symbol()`

### Step 2: Check place_orders Flow / 步骤 2: 检查 place_orders 流程

1. `place_orders()` logs current `self.symbol`
2. Before `fetch_market_data()`, logs symbol and coin
3. `fetch_market_data()` logs symbol and extracted coin
4. After `fetch_market_data()`, logs mid_price
5. If price ratio > 10x or < 0.1x, detects mismatch and skips order

### Step 3: Monitor Logs / 步骤 3: 监控日志

Look for these log messages:
查找以下日志消息：

```
✅ place_orders called with N order(s). Current client symbol: BTC/USDC:USDC.
✅ fetch_market_data called. Current client symbol: BTC/USDC:USDC.
✅ Extracted coin from symbol. Symbol: BTC/USDC:USDC, Coin: BTC.
✅ Market data fetched. Symbol: BTC/USDC:USDC, Coin: BTC, Mid price: 93000.0.
```

If you see:
如果看到：

```
⚠️  SYMBOL MISMATCH DETECTED!
Order price 93045.9 vs reference price 3340.30 (ratio: 27.85).
Client symbol: ETC/USDC:USDC, Coin extracted: ETC.
```

This indicates `self.symbol` was not updated correctly.
这表明 `self.symbol` 没有正确更新。

## Testing / 测试

1. **Update symbol via API / 通过 API 更新交易对**:
   ```bash
   curl -X POST http://localhost:8000/api/hyperliquid/pair \
     -H "Content-Type: application/json" \
     -d '{"symbol": "BTC/USDC:USDC"}'
   ```

2. **Check logs / 检查日志**:
   ```bash
   tail -f server.log | grep -E "symbol|Symbol|SYMBOL"
   ```

3. **Start bot and place orders / 启动 bot 并下单**:
   - Check that `place_orders` logs show correct symbol
   - Check that `fetch_market_data` logs show correct coin
   - Verify no symbol mismatch errors

## Expected Behavior / 预期行为

1. ✅ Frontend updates symbol → Backend updates instance and exchange symbol
2. ✅ `set_symbol()` is called to update internal state
3. ✅ `place_orders()` uses correct symbol
4. ✅ `fetch_market_data()` fetches data for correct coin
5. ✅ Price validation uses correct reference price
6. ✅ Orders are placed successfully

## Known Issues / 已知问题

- If exchange is not connected when symbol is updated, `set_symbol()` may not be called
- If `set_symbol()` fails, internal state may not be updated
- Symbol mismatch detection may not catch all cases (e.g., if prices are similar)

## Next Steps / 下一步

1. Monitor logs after restart to verify symbol updates correctly
2. Test with different symbols (BTC, ETH, SOL) to ensure correct behavior
3. If issues persist, add more validation in `place_orders` to verify symbol before fetching market data

