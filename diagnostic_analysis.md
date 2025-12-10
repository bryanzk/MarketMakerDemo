# Trading Strategy Analysis / 交易策略分析

**Generated / 生成时间**: 2025-12-10  
**Analysis Based On / 分析依据**: diagnostic_report.md, diagnostic_post_fix.md, diagnostic_summary.md, server.log

---

## 问题 1: 为什么下单总是很难成交？/ Why Are Orders Hard to Fill?

### 根本原因分析 / Root Cause Analysis

#### 1.1 价差设置过大 / Spread Too Wide

**当前配置 / Current Configuration**:
- `SPREAD_PCT = 1.5%` (0.015)
- 买入价距离中间价: **0.75%** (spread / 2)
- 卖出价距离中间价: **0.75%** (spread / 2)
- 总价差: **1.5%**

**实际订单价格 / Actual Order Prices** (从诊断报告):
- 中间价: **3368.15 USDC**
- 买入订单: **3354.1** (低于中间价 14.05，约 **0.42%**)
- 卖出订单: **3371.5** (高于中间价 3.35，约 **0.10%**)
- 订单价差: **17.4** (约 **0.52%**)

**问题 / Problem**:
1. **价差过大**: 1.5% 的价差对于做市策略来说太大了
   - 市场价格需要波动 **0.75%** 才能触及买入价
   - 市场价格需要波动 **0.75%** 才能触及卖出价
   - 在低波动市场中，这种波动可能很少发生

2. **限价单成交机制 / Limit Order Fill Mechanism**:
   - 限价单只有在市场价格**达到或超过**订单价格时才会成交
   - 买入限价单：需要市场价格**下跌**到订单价格或更低
   - 卖出限价单：需要市场价格**上涨**到订单价格或更高
   - 如果价差太大，市场价格可能永远不会触及订单价格

3. **市场波动不足 / Insufficient Market Volatility**:
   - 从日志看，市场价格在 3368.15 附近波动
   - 没有触及买入价（3354.1）或卖出价（3371.5）
   - 这是**正常现象**，但价差过大导致成交率低

#### 1.2 订单价格设置不够激进 / Order Prices Not Aggressive Enough

**当前策略 / Current Strategy**:
```python
bid_price = mid_price * (1 - self.spread / 2)  # 买入价 = 中间价 * (1 - 0.75%)
ask_price = mid_price * (1 + self.spread / 2)   # 卖出价 = 中间价 * (1 + 0.75%)
```

**问题 / Problem**:
- 订单价格距离中间价太远
- 对于做市策略，应该更接近市场价格以提高成交率
- 建议价差: **0.1% - 0.3%** (而不是 1.5%)

#### 1.3 订单同步逻辑的稳定性窗口 / Order Stability Window

**当前配置 / Current Configuration**:
- `MIN_ORDER_AGE_SECONDS = 30` (订单最小存活时间 30 秒)
- `PRICE_THRESHOLD_PCT = 0.001` (0.1% 价格差异阈值)
- `QTY_THRESHOLD_PCT = 0.01` (1% 数量差异阈值)

**影响 / Impact**:
- 订单在 30 秒内不会被取消，即使价格已经偏离目标
- 如果市场价格快速变化，订单可能长时间停留在错误的价格上
- 这可能导致订单无法成交，因为价格已经不再合理

---

## 问题 2: 为什么允许单边订单成交？/ Why Allow Single-Side Orders?

### 根本原因分析 / Root Cause Analysis

#### 2.1 订单同步逻辑的设计 / Order Sync Logic Design

**代码位置 / Code Location**: `src/trading/order_manager.py`

**当前逻辑 / Current Logic**:
```python
def sync_orders(self, current_orders, target_orders, mid_price):
    # 分别处理买入和卖出订单
    # Process buy and sell orders separately
    
    # Compare Buy
    if tgt_buy:
        if curr_buy:
            if self._should_cancel_order(curr_buy, tgt_buy, mid_price):
                to_cancel.append(curr_buy["id"])
                to_place.append(tgt_buy)
        else:
            to_place.append(tgt_buy)  # 没有当前买入订单，直接下单
    else:
        if curr_buy:
            to_cancel.append(curr_buy["id"])  # 没有目标买入订单，取消当前订单
    
    # Compare Sell (同样的逻辑)
    # ...
```

**问题 / Problem**:
1. **独立处理买入和卖出订单**:
   - 买入订单和卖出订单是**独立处理**的
   - 如果只有买入订单需要更新，就只下单买入
   - 如果只有卖出订单需要更新，就只下单卖出
   - **没有强制要求双边下单**

2. **订单同步的增量更新 / Incremental Order Sync**:
   - 订单同步是**增量更新**的，只更新需要变更的订单
   - 如果当前有买入订单，目标也有买入订单，但价格差异在阈值内，就不会更新
   - 如果当前有卖出订单，但目标没有卖出订单（或卖出订单被取消），就会只下单买入

3. **策略设计意图 / Strategy Design Intent**:
   - `FixedSpreadStrategy.calculate_target_orders()` **总是返回双边订单**
   - 但订单同步逻辑允许**单边更新**
   - 这导致在某些情况下，只有一边的订单被下单

#### 2.2 实际日志证据 / Actual Log Evidence

从 server.log 可以看到：
```
Placing 1 order(s) for strategy 'hyperliquid'. Buy orders: 1, Sell orders: 0.
Placing 1 order(s) for strategy 'hyperliquid'. Buy orders: 0, Sell orders: 1.
```

**原因分析 / Cause Analysis**:
1. **订单失败导致单边 / Order Failure Causes Single-Side**:
   - 如果双边订单下单时，一边失败，另一边成功
   - 系统会继续运行，导致只有一边的订单存在

2. **订单同步的增量更新 / Incremental Sync**:
   - 如果当前只有买入订单，目标需要卖出订单
   - 系统会只下单卖出，不会强制取消买入订单（如果买入订单在稳定性窗口内）

3. **订单取消逻辑 / Order Cancellation Logic**:
   - 订单只有在价格差异超过阈值时才会被取消
   - 如果买入订单价格合理，但卖出订单需要更新，系统会只下单卖出

---

## 解决方案 / Solutions

### 解决方案 1: 减小价差以提高成交率 / Reduce Spread to Improve Fill Rate

**建议 / Recommendation**:
1. **减小 SPREAD_PCT**:
   - 从 `1.5%` 减小到 `0.2% - 0.5%`
   - 对于 ETH (价格 ~$3000)，0.2% 价差 = $6
   - 对于 BTC (价格 ~$90k)，0.2% 价差 = $180

2. **动态价差调整 / Dynamic Spread Adjustment**:
   - 根据市场波动率动态调整价差
   - 高波动时增大价差，低波动时减小价差
   - 根据成交率调整价差（成交率低时减小价差）

3. **更激进的价格设置 / More Aggressive Price Setting**:
   - 买入价更接近 best_bid
   - 卖出价更接近 best_ask
   - 提高成交率，但可能降低利润

### 解决方案 2: 强制双边下单 / Force Both-Side Order Placement

**建议 / Recommendation**:
1. **修改订单同步逻辑 / Modify Order Sync Logic**:
   ```python
   # 在 sync_orders 方法中，确保总是双边下单
   # Ensure both-side orders are always placed
   
   if len(target_orders) == 2:  # 策略应该总是返回双边订单
       # 如果只有一边的订单需要更新，也要确保另一边存在
       # If only one side needs update, ensure the other side exists
       if tgt_buy and not curr_buy:
           to_place.append(tgt_buy)
       if tgt_sell and not curr_sell:
           to_place.append(tgt_sell)
       
       # 如果目标订单是双边，但当前只有单边，取消单边订单
       # If target is both-side but current is single-side, cancel single-side
       if tgt_buy and tgt_sell:
           if curr_buy and not curr_sell:
               # 检查买入订单是否应该保留
               # Check if buy order should be kept
               if not self._should_cancel_order(curr_buy, tgt_buy, mid_price):
                   # 买入订单合理，只下单卖出
                   # Buy order is reasonable, only place sell
                   to_place.append(tgt_sell)
               else:
                   # 买入订单也需要更新，取消并重新下单双边
                   # Buy order also needs update, cancel and place both
                   to_cancel.append(curr_buy["id"])
                   to_place.extend([tgt_buy, tgt_sell])
   ```

2. **添加双边订单验证 / Add Both-Side Order Validation**:
   ```python
   # 在 _run_strategy_instance_cycle 中，验证目标订单是双边
   # In _run_strategy_instance_cycle, verify target orders are both-side
   
   if len(target_orders) != 2:
       logger.warning(
           f"Strategy should return 2 orders (buy + sell), but got {len(target_orders)}. "
           f"策略应该返回 2 个订单（买入 + 卖出），但得到 {len(target_orders)} 个。"
       )
   
   # 确保下单时总是双边
   # Ensure both-side when placing orders
   if to_place:
       buy_orders = [o for o in to_place if o.get("side") == "buy"]
       sell_orders = [o for o in to_place if o.get("side") == "sell"]
       
       if buy_orders and not sell_orders:
           # 只有买入订单，检查是否有目标卖出订单
           # Only buy orders, check if target sell order exists
           tgt_sell = next((o for o in target_orders if o.get("side") == "sell"), None)
           if tgt_sell:
               to_place.append(tgt_sell)
       
       if sell_orders and not buy_orders:
           # 只有卖出订单，检查是否有目标买入订单
           # Only sell orders, check if target buy order exists
           tgt_buy = next((o for o in target_orders if o.get("side") == "buy"), None)
           if tgt_buy:
               to_place.append(tgt_buy)
   ```

3. **订单失败后的恢复逻辑 / Recovery Logic After Order Failure**:
   ```python
   # 如果下单失败，检查是否是单边失败
   # If order placement fails, check if it's single-side failure
   
   if len(placed_orders) < len(to_place):
       failed_sides = target_sides - placed_sides
       if failed_sides:
           # 如果一边失败，取消另一边以确保双边一致性
           # If one side fails, cancel the other side to ensure both-side consistency
           logger.warning(
               f"Single-side order failure detected: {failed_sides}. "
               f"Cancelling opposite side to maintain both-side consistency. "
               f"检测到单边订单失败: {failed_sides}。"
               f"取消另一边以保持双边一致性。"
           )
           # 取消已成功下单的订单
           # Cancel successfully placed orders
           for order in placed_orders:
               instance.exchange.cancel_orders([order.get("id")])
   ```

---

## 总结 / Summary

### 问题 1: 成交率低 / Low Fill Rate

**根本原因 / Root Cause**:
- 价差设置过大 (1.5%)
- 订单价格距离中间价太远
- 市场波动不足

**解决方案 / Solution**:
- 减小价差到 0.2% - 0.5%
- 动态调整价差
- 更激进的价格设置

### 问题 2: 允许单边订单 / Single-Side Orders Allowed

**根本原因 / Root Cause**:
- 订单同步逻辑独立处理买入和卖出订单
- 增量更新导致单边更新
- 订单失败后没有恢复逻辑

**解决方案 / Solution**:
- ✅ **已实现**: 强制双边下单（方案 1）
- ✅ **已实现**: 在 `order_manager.py` 中添加 `enforce_both_side` 参数
- ✅ **已实现**: 在 `strategy_instance.py` 中添加 `_requires_both_side_orders` 方法
- ✅ **已实现**: 可扩展设计，支持未来其他策略类型

**实现细节 / Implementation Details**:
1. **`order_manager.py`**: 
   - 添加 `enforce_both_side` 参数到 `sync_orders` 方法
   - 在订单同步后检查并强制双边下单
   - 如果只有买入订单，自动添加卖出订单
   - 如果只有卖出订单，自动添加买入订单

2. **`strategy_instance.py`**:
   - 添加 `_requires_both_side_orders` 方法判断策略是否需要双边订单
   - 支持基于策略类型的判断（`fixed_spread`, `funding_rate`）
   - 支持基于目标订单的回退判断（如果策略返回双边订单，则认为是做市策略）
   - 可扩展：未来新策略可以重写此方法或添加策略类型

3. **扩展性设计 / Extensibility**:
   - 策略类型判断：当前支持 `fixed_spread` 和 `funding_rate`
   - 回退机制：如果策略返回双边订单，自动识别为做市策略
   - 未来扩展：新策略可以：
     - 在 `_requires_both_side_orders` 中添加策略类型
     - 重写 `_requires_both_side_orders` 方法
     - 返回双边订单以自动启用强制双边逻辑

---

**Report Generated by / 报告生成者**: Agent TRADING  
**Status / 状态**: ✅ Analysis Complete / 分析完成  
**Implementation Status / 实现状态**: ✅ Implemented (Solution 1) / 已实现（方案 1）

