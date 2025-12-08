#!/bin/bash
# Update HYPERLIQUID_API_KEY in .env file
# 更新 .env 文件中的 HYPERLIQUID_API_KEY

ADDRESS="0x662097117457B21F935E187cAff2d4E30D708627"

if [ -f .env ]; then
    # Remove old HYPERLIQUID_API_KEY lines
    sed -i.bak '/^HYPERLIQUID_API_KEY=/d' .env
    # Add new one
    echo "HYPERLIQUID_API_KEY=$ADDRESS" >> .env
    echo "✅ Updated HYPERLIQUID_API_KEY to $ADDRESS"
else
    echo "HYPERLIQUID_API_KEY=$ADDRESS" > .env
    echo "✅ Created .env with HYPERLIQUID_API_KEY=$ADDRESS"
fi
