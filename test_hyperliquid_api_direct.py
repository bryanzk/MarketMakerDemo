#!/usr/bin/env python3
"""
Direct Hyperliquid API Test / 直接 Hyperliquid API 测试

Test if we can fetch data directly from Hyperliquid API.
测试是否可以直接从 Hyperliquid API 获取数据。
"""

import json
import sys
import time

try:
    import requests
except ImportError:
    print("❌ Error: requests module not found. Install with: pip install requests")
    print("❌ 错误: 未找到 requests 模块。使用以下命令安装: pip install requests")
    sys.exit(1)

print("=" * 80)
print("Testing Hyperliquid API Direct Access / 测试 Hyperliquid API 直接访问")
print("=" * 80)

# Test endpoints / 测试端点
BASE_URL_TESTNET = "https://api.hyperliquid-testnet.xyz"
BASE_URL_MAINNET = "https://api.hyperliquid.xyz"

# Test 1: Public info endpoint (allMids) / 测试 1: 公共信息端点 (allMids)
print("\n1. Testing public info endpoint (allMids) / 测试公共信息端点 (allMids)...")
try:
    url = f"{BASE_URL_TESTNET}/info"
    payload = {"type": "allMids"}
    
    print(f"   🔄 Requesting: POST {url}")
    print(f"   🔄 请求: POST {url}")
    print(f"   📦 Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"   📊 Status Code: {response.status_code}")
    print(f"   📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success! Response keys: {list(data.keys()) if isinstance(data, dict) else 'List'}")
        print(f"   ✅ 成功！响应键: {list(data.keys()) if isinstance(data, dict) else 'List'}")
        
        if isinstance(data, dict) and "mid_prices" in data:
            mid_prices = data["mid_prices"]
            print(f"   📊 Available coins: {list(mid_prices.keys())[:5]}...")
            print(f"   📊 可用币种: {list(mid_prices.keys())[:5]}...")
            if "BTC" in mid_prices:
                print(f"   📊 BTC mid price: {mid_prices['BTC']}")
                print(f"   📊 BTC 中间价: {mid_prices['BTC']}")
    else:
        print(f"   ⚠️  Unexpected status code: {response.status_code}")
        print(f"   ⚠️  意外状态码: {response.status_code}")
        print(f"   📄 Response: {response.text[:200]}")
        print(f"   📄 响应: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Candle snapshot endpoint / 测试 2: K 线快照端点
print("\n2. Testing candle snapshot endpoint / 测试 K 线快照端点...")
try:
    url = f"{BASE_URL_TESTNET}/info"
    
    # Calculate time range for 1 hour of 1-minute candles / 计算 1 小时 1 分钟 K 线的时间范围
    current_time_ms = int(time.time() * 1000)
    end_time_ms = current_time_ms
    start_time_ms = end_time_ms - (60 * 60 * 1000)  # 1 hour ago / 1 小时前
    
    payload = {
        "type": "candleSnapshot",
        "req": {
            "coin": "BTC",
            "interval": "1m",
            "startTime": start_time_ms,
            "endTime": end_time_ms
        }
    }
    
    print(f"   🔄 Requesting: POST {url}")
    print(f"   🔄 请求: POST {url}")
    print(f"   📦 Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"   📊 Status Code: {response.status_code}")
    print(f"   📊 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            print(f"   ✅ Success! Received {len(data)} candles")
            print(f"   ✅ 成功！收到 {len(data)} 根 K 线")
            print(f"   📊 First candle: {data[0]}")
            print(f"   📊 第一根 K 线: {data[0]}")
            print(f"   📊 Last candle: {data[-1]}")
            print(f"   📊 最后一根 K 线: {data[-1]}")
            
            # Extract close prices / 提取收盘价
            if len(data[0]) >= 5:
                close_prices = [candle[4] for candle in data if len(candle) >= 5]
                print(f"   📊 Close prices: {len(close_prices)} values")
                print(f"   📊 收盘价: {len(close_prices)} 个值")
                if close_prices:
                    print(f"   📊 First close: {close_prices[0]}")
                    print(f"   📊 第一个收盘价: {close_prices[0]}")
                    print(f"   📊 Last close: {close_prices[-1]}")
                    print(f"   📊 最后一个收盘价: {close_prices[-1]}")
        else:
            print(f"   ⚠️  Empty response or unexpected format")
            print(f"   ⚠️  空响应或意外格式")
            print(f"   📄 Response: {str(data)[:200]}")
    elif response.status_code == 422:
        print(f"   ⚠️  422 Unprocessable Entity - Request format issue")
        print(f"   ⚠️  422 无法处理的实体 - 请求格式问题")
        try:
            error_data = response.json()
            print(f"   📄 Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   📄 Response: {response.text[:500]}")
    else:
        print(f"   ⚠️  Unexpected status code: {response.status_code}")
        print(f"   ⚠️  意外状态码: {response.status_code}")
        print(f"   📄 Response: {response.text[:200]}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("TEST SUMMARY / 测试摘要")
print("=" * 80)
print("✅ API connectivity test completed")
print("✅ API 连接测试完成")
print("=" * 80)

