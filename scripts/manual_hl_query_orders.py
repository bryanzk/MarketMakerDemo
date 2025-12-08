#!/usr/bin/env python3
"""
Manual script to query open orders on Hyperliquid
手动查询 Hyperliquid 未成交订单的脚本

Usage / 用法:
    python scripts/manual_hl_query_orders.py
"""

import os
import sys
from dotenv import load_dotenv
from eth_account import Account
from hyperliquid.info import Info

# Load environment variables from .env file
load_dotenv()


def main():
    # Load credentials from environment
    priv_key = os.environ.get("HYPERLIQUID_API_SECRET")
    if not priv_key:
        raise SystemExit("Missing HYPERLIQUID_API_SECRET in environment.")

    # Normalize private key to 0x-prefixed hex
    if not priv_key.startswith("0x"):
        priv_key = f"0x{priv_key}"

    # Get wallet address from private key
    wallet = Account.from_key(priv_key)
    wallet_address = wallet.address

    # Get user address (may differ from wallet address in API wallet mode)
    user_address = os.environ.get("HYPERLIQUID_WALLET_ADDRESS") or wallet_address

    testnet = os.environ.get("HYPERLIQUID_TESTNET", "true").lower() == "true"
    base_url = (
        "https://api.hyperliquid-testnet.xyz"
        if testnet
        else "https://api.hyperliquid.xyz"
    )

    print("=" * 60)
    print("Hyperliquid Open Orders Query")
    print("Hyperliquid 未成交订单查询")
    print("=" * 60)
    print(f"\nConfiguration / 配置:")
    print(f"  Testnet: {testnet}")
    print(f"  Base URL: {base_url}")
    print(f"  Wallet Address (for signing): {wallet_address}")
    print(f"  User Address (for query): {user_address}")
    print(f"  钱包地址（用于签名）: {wallet_address}")
    print(f"  用户地址（用于查询）: {user_address}")

    # Initialize Info client
    info = Info(base_url, skip_ws=True, timeout=15.0)

    # Query open orders
    print(f"\n📋 Querying open orders for user: {user_address}")
    print(f"📋 正在查询用户 {user_address} 的未成交订单...")

    try:
        # Query open orders
        response = info.open_orders(user_address)

        print(f"\n✅ Query successful / 查询成功")
        print(f"✅ Response type: {type(response)}")
        print(f"✅ Response keys: {list(response.keys()) if isinstance(response, dict) else 'N/A'}")

        if isinstance(response, dict):
            orders = response.get("openOrders", [])
            print(f"\n📊 Found {len(orders)} open order(s) / 找到 {len(orders)} 个未成交订单")

            if len(orders) == 0:
                print("\n✅ No open orders / 没有未成交订单")
            else:
                print("\n" + "=" * 80)
                print(f"{'Coin':<10} {'Side':<6} {'Size':<15} {'Price':<15} {'Order ID':<20} {'Status':<10}")
                print("=" * 80)

                for order in orders:
                    coin = order.get("coin", "N/A")
                    side = "BUY" if order.get("side", {}).get("bids", []) else "SELL"
                    size = order.get("sz", "0")
                    price = order.get("limitPx", "N/A")
                    order_id = order.get("oid", "N/A")
                    status = order.get("status", "N/A")

                    print(f"{coin:<10} {side:<6} {str(size):<15} {str(price):<15} {str(order_id):<20} {str(status):<10}")

                print("=" * 80)

                # Print detailed JSON for debugging
                print("\n📄 Detailed order data / 详细订单数据:")
                import json
                print(json.dumps(response, indent=2, default=str))

        else:
            print(f"\n⚠️  Unexpected response format / 意外的响应格式:")
            print(f"Response: {response}")

    except Exception as e:
        print(f"\n❌ Error querying open orders / 查询未成交订单时出错:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

