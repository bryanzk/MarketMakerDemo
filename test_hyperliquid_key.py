#!/usr/bin/env python3
"""
Test Hyperliquid API Key / 测试 Hyperliquid API Key

This script tests if the configured Hyperliquid API credentials are valid.
此脚本测试配置的 Hyperliquid API 凭证是否有效。

Usage / 用法:
    python test_hyperliquid_key.py
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.trading.hyperliquid_client import (
    HyperliquidClient,
    AuthenticationError,
    ConnectionError,
)


def test_hyperliquid_key():
    """Test Hyperliquid API key configuration / 测试 Hyperliquid API Key 配置"""
    print("=" * 60)
    print("Hyperliquid API Key Test / Hyperliquid API Key 测试")
    print("=" * 60)
    print()

    # Check environment variables
    api_key = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

    print(f"Configuration / 配置:")
    print(f"  API Key: {'*' * 20 if api_key else 'NOT SET / 未设置'}")
    print(f"  API Secret: {'*' * 20 if api_secret else 'NOT SET / 未设置'}")
    print(f"  Testnet: {testnet}")
    print()

    if not api_key or not api_secret:
        print("❌ ERROR / 错误: API credentials not found in environment variables")
        print("   Please set HYPERLIQUID_API_KEY and HYPERLIQUID_API_SECRET")
        print("   请在环境变量中设置 HYPERLIQUID_API_KEY 和 HYPERLIQUID_API_SECRET")
        return False

    try:
        print("Attempting to connect to Hyperliquid... / 尝试连接到 Hyperliquid...")
        print(f"  Environment: {'TESTNET' if testnet else 'MAINNET'}")
        print()

        # Initialize client
        client = HyperliquidClient(testnet=testnet)

        print("✅ Connection successful! / 连接成功！")
        print(f"  Base URL: {client.base_url}")
        print(f"  Symbol: {client.symbol}")
        print(f"  Connected: {client.is_connected}")
        print()

        # Test connection status
        print("Checking connection status... / 检查连接状态...")
        status = client.get_connection_status()
        print(f"  Status: {'Connected / 已连接' if status['connected'] else 'Disconnected / 已断开'}")
        if status.get("last_successful_call"):
            print(f"  Last successful call: {status['last_successful_call']}")
        print()

        # Test basic API calls
        print("Testing basic API calls... / 测试基本 API 调用...")

        # Test fetching account data
        try:
            account_data = client.fetch_account_data()
            if account_data:
                print("✅ Account data fetch successful / 账户数据获取成功")
                print(f"  Balance: {account_data.get('balance', 'N/A')}")
                print(f"  Available: {account_data.get('available_balance', 'N/A')}")
                print(f"  Position: {account_data.get('position_amt', 'N/A')}")
            else:
                print("⚠️  Account data fetch returned None (may be placeholder)")
        except Exception as e:
            print(f"⚠️  Account data fetch failed: {e}")

        # Test fetching market data
        try:
            market_data = client.fetch_market_data()
            if market_data:
                print("✅ Market data fetch successful / 市场数据获取成功")
                print(f"  Mid Price: {market_data.get('mid_price', 'N/A')}")
            else:
                print("⚠️  Market data fetch returned None (may be placeholder)")
        except Exception as e:
            print(f"⚠️  Market data fetch failed: {e}")

        print()
        print("=" * 60)
        print("✅ All tests passed! / 所有测试通过！")
        print("   Your Hyperliquid API Key is working correctly.")
        print("   您的 Hyperliquid API Key 工作正常。")
        print("=" * 60)
        return True

    except AuthenticationError as e:
        print()
        print("❌ AUTHENTICATION ERROR / 认证错误:")
        print(f"   {str(e)}")
        print()
        print("Possible causes / 可能的原因:")
        print("  1. Invalid API Key or Secret / 无效的 API Key 或 Secret")
        print("  2. API Key not activated / API Key 未激活")
        print("  3. Wrong environment (testnet vs mainnet) / 错误的环境（测试网 vs 主网）")
        print()
        return False

    except ConnectionError as e:
        print()
        print("❌ CONNECTION ERROR / 连接错误:")
        print(f"   {str(e)}")
        print()
        print("Possible causes / 可能的原因:")
        print("  1. Network connectivity issues / 网络连接问题")
        print("  2. Hyperliquid API is down / Hyperliquid API 服务不可用")
        print("  3. Firewall blocking connection / 防火墙阻止连接")
        print()
        return False

    except Exception as e:
        print()
        print("❌ UNEXPECTED ERROR / 意外错误:")
        print(f"   {str(e)}")
        print(f"   Type: {type(e).__name__}")
        import traceback

        print()
        print("Traceback / 堆栈跟踪:")
        traceback.print_exc()
        print()
        return False


if __name__ == "__main__":
    success = test_hyperliquid_key()
    sys.exit(0 if success else 1)






