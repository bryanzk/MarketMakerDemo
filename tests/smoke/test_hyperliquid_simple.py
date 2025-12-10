#!/usr/bin/env python3
"""
Simple Hyperliquid API Test / 简单的 Hyperliquid API 测试

Directly test Hyperliquid API connectivity and authentication.
直接测试 Hyperliquid API 连接和认证。
"""

import json
import os
import sys

import requests

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_api_connectivity():
    """Test basic API connectivity / 测试基本 API 连接"""
    print("=" * 60)
    print("Hyperliquid API Connectivity Test / Hyperliquid API 连接测试")
    print("=" * 60)
    print()

    # Test mainnet endpoint
    print("Testing mainnet endpoint... / 测试主网端点...")
    try:
        url = "https://api.hyperliquid.xyz/info"
        # Hyperliquid uses POST for /info endpoint
        payload = {"type": "meta"}
        response = requests.post(url, json=payload, timeout=10)
        print(f"  Status Code: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Mainnet API is reachable / 主网 API 可达")
            data = response.json()
            print(f"  Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:5]}")
        else:
            print(f"  ⚠️  Unexpected status: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")

    print()

    # Test testnet endpoint
    print("Testing testnet endpoint... / 测试测试网端点...")
    try:
        url = "https://api.hyperliquid-testnet.xyz/info"
        payload = {"type": "meta"}
        response = requests.post(url, json=payload, timeout=10)
        print(f"  Status Code: {response.status_code}")
        if response.status_code == 200:
            print("  ✅ Testnet API is reachable / 测试网 API 可达")
            data = response.json()
            print(f"  Response type: {type(data)}")
            if isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:5]}")
        else:
            print(f"  ⚠️  Unexpected status: {response.text[:100]}")
    except Exception as e:
        print(f"  ❌ Connection failed: {e}")

    print()


def test_api_key():
    """Test API key authentication / 测试 API Key 认证"""
    print("=" * 60)
    print("Hyperliquid API Key Authentication Test / Hyperliquid API Key 认证测试")
    print("=" * 60)
    print()

    api_key = os.getenv("HYPERLIQUID_API_KEY")
    api_secret = os.getenv("HYPERLIQUID_API_SECRET")
    testnet = os.getenv("HYPERLIQUID_TESTNET", "false").lower() == "true"

    if not api_key or not api_secret:
        print("❌ API credentials not found in environment variables")
        print("   Please set HYPERLIQUID_API_KEY and HYPERLIQUID_API_SECRET")
        return False

    print(f"API Key: {'*' * 20}")
    print(f"Testnet: {testnet}")
    print()

    base_url = (
        "https://api.hyperliquid-testnet.xyz"
        if testnet
        else "https://api.hyperliquid.xyz"
    )

    # Note: Hyperliquid authentication requires signature generation
    # This is a simplified test - full implementation would need proper signing
    print("Note: Full authentication requires signature generation")
    print("      This test only verifies API endpoint connectivity")
    print("      注意：完整认证需要签名生成")
    print("      此测试仅验证 API 端点连接性")
    print()

    try:
        from src.trading.hyperliquid_client import HyperliquidClient

        print("Initializing HyperliquidClient... / 初始化 HyperliquidClient...")
        client = HyperliquidClient(testnet=testnet)

        print("✅ Client initialized successfully / 客户端初始化成功")
        print(f"  Base URL: {client.base_url}")
        print(f"  Connected: {client.is_connected}")

        status = client.get_connection_status()
        print(f"  Connection Status: {status}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_api_connectivity()
    print()
    test_api_key()

