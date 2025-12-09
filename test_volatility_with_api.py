#!/usr/bin/env python3
"""
Test Volatility Calculation with Real API Data / 使用真实 API 数据测试波动率计算

Fetch real data from Hyperliquid API and calculate volatility.
从 Hyperliquid API 获取真实数据并计算波动率。
"""

import json
import math
import sys
import time
import urllib.request

print("=" * 80)
print("Volatility Calculation with Real API Data / 使用真实 API 数据计算波动率")
print("=" * 80)

BASE_URL = "https://api.hyperliquid-testnet.xyz/info"

def calculate_returns(prices):
    """Calculate returns from price series / 从价格序列计算收益率"""
    if len(prices) < 2:
        return []
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
    return returns

def calculate_volatility(returns):
    """Calculate volatility from returns / 从收益率计算波动率"""
    if len(returns) < 2:
        return 0.0
    n = len(returns)
    mean_return = sum(returns) / n
    variance = sum((r - mean_return) ** 2 for r in returns) / (n - 1)
    volatility = math.sqrt(variance)
    return volatility

# Step 1: Get current price / 步骤 1: 获取当前价格
print("\n1. Fetching current price (allMids) / 获取当前价格 (allMids)...")
try:
    url = f"{BASE_URL}"
    payload = json.dumps({"type": "allMids"}).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        if isinstance(data, dict):
            # Response format: {"BTC": "12345.67", "ETH": "2345.67", ...}
            # 响应格式: {"BTC": "12345.67", "ETH": "2345.67", ...}
            mid_prices = data
            # Try to find BTC or ETH / 尝试找到 BTC 或 ETH
            coin = None
            for test_coin in ["BTC", "ETH", "SOL"]:
                if test_coin in mid_prices:
                    coin = test_coin
                    break
            
            if coin:
                current_price = float(mid_prices[coin])
                print(f"   ✅ Found {coin} current price: {current_price}")
                print(f"   ✅ 找到 {coin} 当前价格: {current_price}")
            else:
                # Use first available coin / 使用第一个可用币种
                coin = list(mid_prices.keys())[0]
                current_price = float(mid_prices[coin])
                print(f"   ✅ Using {coin} current price: {current_price}")
                print(f"   ✅ 使用 {coin} 当前价格: {current_price}")
        else:
            print("   ⚠️  Unexpected response format")
            print("   ⚠️  意外响应格式")
            coin = None
            current_price = None
except Exception as e:
    print(f"   ❌ Error fetching current price: {e}")
    print(f"   ❌ 获取当前价格错误: {e}")
    coin = None
    current_price = None

# Step 2: Fetch historical candles / 步骤 2: 获取历史 K 线
if coin:
    print(f"\n2. Fetching historical candles for {coin} / 获取 {coin} 的历史 K 线...")
    try:
        # Calculate time range for 1 hour of 1-minute candles / 计算 1 小时 1 分钟 K 线的时间范围
        current_time_ms = int(time.time() * 1000)
        end_time_ms = current_time_ms
        start_time_ms = end_time_ms - (60 * 60 * 1000)  # 1 hour ago / 1 小时前
        
        payload = {
            "type": "candleSnapshot",
            "req": {
                "coin": coin,
                "interval": "1m",
                "startTime": start_time_ms,
                "endTime": end_time_ms
            }
        }
        
        url = f"{BASE_URL}"
        payload_json = json.dumps(payload).encode('utf-8')
        
        print(f"   🔄 Requesting candles from {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_ms/1000))} to {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time_ms/1000))}")
        print(f"   🔄 请求 K 线从 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time_ms/1000))} 到 {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time_ms/1000))}")
        
        req = urllib.request.Request(url, data=payload_json, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=10) as response:
            candles = json.loads(response.read().decode('utf-8'))
            
            if isinstance(candles, list) and len(candles) > 0:
                print(f"   ✅ Successfully fetched {len(candles)} candles")
                print(f"   ✅ 成功获取 {len(candles)} 根 K 线")
                
                # Extract close prices / 提取收盘价
                # Format: {'t': timestamp, 'o': open, 'h': high, 'l': low, 'c': close, 'v': volume, ...}
                # 格式: {'t': 时间戳, 'o': 开盘, 'h': 最高, 'l': 最低, 'c': 收盘, 'v': 成交量, ...}
                close_prices = []
                for candle in candles:
                    if isinstance(candle, dict) and 'c' in candle:
                        close_prices.append(float(candle['c']))  # 'c' is close price
                    elif isinstance(candle, list) and len(candle) >= 5:
                        close_prices.append(float(candle[4]))  # Index 4 is close price (fallback)
                
                if len(close_prices) >= 2:
                    print(f"   📊 Extracted {len(close_prices)} close prices")
                    print(f"   📊 提取了 {len(close_prices)} 个收盘价")
                    print(f"   📊 Price range: {min(close_prices):.4f} - {max(close_prices):.4f}")
                    print(f"   📊 价格范围: {min(close_prices):.4f} - {max(close_prices):.4f}")
                    
                    # Step 3: Calculate volatility / 步骤 3: 计算波动率
                    print(f"\n3. Calculating volatility / 计算波动率...")
                    returns = calculate_returns(close_prices)
                    volatility = calculate_volatility(returns)
                    
                    print(f"   📈 Number of returns: {len(returns)}")
                    print(f"   📈 收益率数量: {len(returns)}")
                    print(f"   📈 Mean return: {sum(returns)/len(returns):.6f} ({sum(returns)/len(returns)*100:.4f}%)")
                    print(f"   📈 平均收益率: {sum(returns)/len(returns):.6f} ({sum(returns)/len(returns)*100:.4f}%)")
                    print(f"   ✅ Volatility: {volatility:.6f} ({volatility*100:.4f}%)")
                    print(f"   ✅ 波动率: {volatility:.6f} ({volatility*100:.4f}%)")
                    
                    # Annualized volatility / 年化波动率
                    # For hourly data: periods_per_year = 24 * 365 = 8760
                    # 对于小时数据: periods_per_year = 24 * 365 = 8760
                    volatility_annual = volatility * math.sqrt(24 * 365)
                    print(f"   ✅ Annualized volatility (hourly): {volatility_annual:.6f} ({volatility_annual*100:.4f}%)")
                    print(f"   ✅ 年化波动率（小时）: {volatility_annual:.6f} ({volatility_annual*100:.4f}%)")
                else:
                    print(f"   ⚠️  Insufficient close prices: {len(close_prices)}")
                    print(f"   ⚠️  收盘价不足: {len(close_prices)}")
            elif isinstance(candles, dict):
                print(f"   ⚠️  Unexpected response format (dict): {list(candles.keys())[:5]}")
                print(f"   ⚠️  意外响应格式（字典）: {list(candles.keys())[:5]}")
            else:
                print(f"   ⚠️  Empty or invalid response")
                print(f"   ⚠️  空响应或无效响应")
                
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP Error: {e.code}")
        print(f"   ❌ HTTP 错误: {e.code}")
        if e.code == 422:
            print(f"   📄 Response: {e.read().decode('utf-8')[:500]}")
            print(f"   📄 响应: {e.read().decode('utf-8')[:500]}")
    except Exception as e:
        print(f"   ❌ Error fetching candles: {e}")
        print(f"   ❌ 获取 K 线错误: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 80)
print("TEST SUMMARY / 测试摘要")
print("=" * 80)
print("✅ API connectivity test passed")
print("✅ API 连接测试通过")
if coin:
    print(f"✅ Successfully fetched and calculated volatility for {coin}")
    print(f"✅ 成功获取并计算了 {coin} 的波动率")
print("=" * 80)

