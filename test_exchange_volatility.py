#!/usr/bin/env python3
"""
Test Exchange Volatility Calculator / 测试交易所波动率计算器

Simple test to verify exchange data fetching works.
简单测试以验证交易所数据获取是否正常工作。
"""

import os
import sys

# Add project root to path / 将项目根目录添加到路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 80)
print("Testing Exchange Volatility Calculator / 测试交易所波动率计算器")
print("=" * 80)

try:
    print("\n1. Testing imports / 测试导入...")
    from src.trading.volatility import (
        calculate_volatility_1h_24h,
        fetch_and_calculate_volatility,
        VolatilityCalculator,
    )
    print("   ✅ Volatility module imported successfully")
    print("   ✅ 波动率模块导入成功")
    
    print("\n2. Testing HyperliquidClient import / 测试 HyperliquidClient 导入...")
    from src.trading.hyperliquid_client import HyperliquidClient
    print("   ✅ HyperliquidClient imported successfully")
    print("   ✅ HyperliquidClient 导入成功")
    
    print("\n3. Testing client initialization / 测试客户端初始化...")
    # Try to initialize with minimal config / 尝试使用最小配置初始化
    try:
        client = HyperliquidClient(symbol="BTC/USDC:USDC", testnet=True)
        print(f"   ✅ Client initialized: {type(client).__name__}")
        print(f"   ✅ 客户端已初始化: {type(client).__name__}")
        print(f"   📊 Symbol: {client.symbol}")
        print(f"   📊 交易对: {client.symbol}")
        print(f"   🌐 Base URL: {client.base_url}")
        print(f"   🌐 基础 URL: {client.base_url}")
    except Exception as e:
        print(f"   ⚠️  Client initialization warning: {e}")
        print(f"   ⚠️  客户端初始化警告: {e}")
        print("   ℹ️  This is OK if API keys are not configured")
        print("   ℹ️  如果未配置 API 密钥，这是正常的")
        client = None
    
    if client:
        print("\n4. Testing historical price fetching / 测试历史价格获取...")
        try:
            # Try to fetch 1 hour of data with 1-minute interval / 尝试获取 1 小时数据，1 分钟间隔
            print("   🔄 Fetching 1 hour of historical prices (1-minute interval)...")
            print("   🔄 获取 1 小时历史价格（1 分钟间隔）...")
            prices = client.fetch_historical_prices("BTC/USDC:USDC", hours=1, interval_minutes=1)
            
            if prices and len(prices) > 0:
                print(f"   ✅ Successfully fetched {len(prices)} price points")
                print(f"   ✅ 成功获取 {len(prices)} 个价格点")
                print(f"   📊 First price: {prices[0]:.4f}")
                print(f"   📊 第一个价格: {prices[0]:.4f}")
                print(f"   📊 Last price: {prices[-1]:.4f}")
                print(f"   📊 最后一个价格: {prices[-1]:.4f}")
                
                print("\n5. Testing volatility calculation / 测试波动率计算...")
                try:
                    calculator = VolatilityCalculator(cache_ttl=300)
                    volatility = fetch_and_calculate_volatility(
                        client, "BTC/USDC:USDC", hours=1, default=0.02, calculator=calculator
                    )
                    
                    print(f"   ✅ Volatility calculated: {volatility:.6f} ({volatility*100:.4f}%)")
                    print(f"   ✅ 波动率已计算: {volatility:.6f} ({volatility*100:.4f}%)")
                    
                    print("\n6. Testing 1h and 24h volatility / 测试 1 小时和 24 小时波动率...")
                    try:
                        volatility_1h, volatility_24h = calculate_volatility_1h_24h(
                            client, "BTC/USDC:USDC", calculator=calculator
                        )
                        print(f"   ✅ 1-hour volatility: {volatility_1h:.6f} ({volatility_1h*100:.4f}%)")
                        print(f"   ✅ 1 小时波动率: {volatility_1h:.6f} ({volatility_1h*100:.4f}%)")
                        print(f"   ✅ 24-hour volatility: {volatility_24h:.6f} ({volatility_24h*100:.4f}%)")
                        print(f"   ✅ 24 小时波动率: {volatility_24h:.6f} ({volatility_24h*100:.4f}%)")
                    except Exception as e:
                        print(f"   ⚠️  1h/24h calculation warning: {e}")
                        print(f"   ⚠️  1 小时/24 小时计算警告: {e}")
                    
                except Exception as e:
                    print(f"   ⚠️  Volatility calculation warning: {e}")
                    print(f"   ⚠️  波动率计算警告: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"   ⚠️  No prices fetched (empty result)")
                print(f"   ⚠️  未获取到价格（空结果）")
                print("   ℹ️  This might be OK if API is unavailable or rate-limited")
                print("   ℹ️  如果 API 不可用或受到速率限制，这可能是正常的")
        except Exception as e:
            print(f"   ⚠️  Price fetching error: {e}")
            print(f"   ⚠️  价格获取错误: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY / 测试摘要")
    print("=" * 80)
    print("✅ All imports successful / 所有导入成功")
    print("✅ 所有导入成功")
    if client:
        print("✅ Client initialized / 客户端已初始化")
        print("✅ 客户端已初始化")
    print("=" * 80)
    
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    print(f"❌ 导入错误: {e}")
    print("\nMissing dependencies. Try installing:")
    print("缺少依赖。尝试安装:")
    print("  pip install python-dotenv requests certifi")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

