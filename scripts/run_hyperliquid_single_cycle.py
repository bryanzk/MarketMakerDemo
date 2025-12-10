"""
Manual one-cycle runner for Hyperliquid to sanity-check price alignment with SDK.

Usage:
    HL_SYMBOL=ETH/USDT:USDT HL_QTY=0.01 HL_SPREAD_BP=20 venv/bin/python3 scripts/run_hyperliquid_single_cycle.py

Environment:
    HL_SYMBOL      Trading pair (default: ETH/USDT:USDT)
    HL_QTY         Order size in base coin (default: 0.01)
    HL_SPREAD_BP   Total spread in basis points (default: 20bp => +/-10bp around mid)

This script:
1) Initializes HyperliquidClient (uses your existing env vars for keys/base_url).
2) Fetches market data and resolves tick_size.
3) Builds one buy & one sell limit order around mid, rounded to tick_size.
4) Sends via SDK and prints the responses.

If network is unavailable or SDK fails, it will print the error and exit non-zero.
"""

import json
import os
import sys
from decimal import Decimal

from src.shared.utils import round_tick_size
from src.trading.hyperliquid_client import HyperliquidClient


def main():
    symbol = os.getenv("HL_SYMBOL", "ETH/USDT:USDT")
    qty = float(os.getenv("HL_QTY", "0.01"))
    spread_bp = float(os.getenv("HL_SPREAD_BP", "20.0"))  # total spread in bps

    print(f"== Running single-cycle sanity check for {symbol} ==")
    client = HyperliquidClient(symbol=symbol)

    market = client.fetch_market_data()
    if not market or not market.get("mid_price"):
        print("Market data unavailable; aborting.", file=sys.stderr)
        sys.exit(1)

    mid = float(market["mid_price"])
    tick_size = market.get("tick_size") or client._resolve_tick_size(
        symbol.split("/")[0], market
    )
    spread_fraction = spread_bp / 10000.0

    # symmetric prices around mid
    bid_raw = mid * (1 - spread_fraction / 2)
    ask_raw = mid * (1 + spread_fraction / 2)
    bid_px = round_tick_size(bid_raw, tick_size)
    ask_px = round_tick_size(ask_raw, tick_size)

    print(
        json.dumps(
            {
                "mid": mid,
                "tick_size": tick_size,
                "bid_raw": bid_raw,
                "bid_px": bid_px,
                "ask_raw": ask_raw,
                "ask_px": ask_px,
                "qty": qty,
            },
            indent=2,
        )
    )

    orders = [
        {"side": "buy", "price": bid_px, "quantity": qty, "type": "limit"},
        {"side": "sell", "price": ask_px, "quantity": qty, "type": "limit"},
    ]

    try:
        placed = client.place_orders(orders)
        print("Order placement result:")
        print(json.dumps(placed, indent=2))
    except Exception as e:
        print(f"Order placement failed: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
