import os
from dotenv import load_dotenv
from eth_account import Account
from hyperliquid.exchange import Exchange

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

    testnet = os.environ.get("HYPERLIQUID_TESTNET", "true").lower() == "true"
    base_url = (
        "https://api.hyperliquid-testnet.xyz"
        if testnet
        else "https://api.hyperliquid.xyz"
    )

    # Order parameters (override via env if needed)
    coin = os.environ.get("HYPERLIQUID_ORDER_COIN", "ETH")
    is_buy = os.environ.get("HYPERLIQUID_ORDER_SIDE", "buy").lower() == "buy"
    size = float(os.environ.get("HYPERLIQUID_ORDER_SIZE", "0.001"))
    price = float(os.environ.get("HYPERLIQUID_ORDER_PRICE", "3000"))

    # Build wallet and client
    wallet = Account.from_key(priv_key)
    exchange = Exchange(wallet, base_url=base_url, timeout=15.0)

    # Place limit order (GTC)
    order_type = {"limit": {"tif": "Gtc"}}
    print(
        f"Placing {'BUY' if is_buy else 'SELL'} {coin} "
        f"size={size} price={price} on {'testnet' if testnet else 'mainnet'}..."
    )
    result = exchange.order(
        name=coin,
        is_buy=is_buy,
        sz=size,
        limit_px=price,
        order_type=order_type,
        reduce_only=False,
    )
    print("Response:", result)


if __name__ == "__main__":
    main()
