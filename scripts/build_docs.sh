#!/bin/bash
# Build API documentation using pdoc

set -e

# Set PYTHONPATH to current directory so pdoc can find alphaloop module
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "🔨 Building API documentation..."

# Remove old docs
rm -rf docs/api

# Generate new docs
pdoc alphaloop \
  --output-dir docs/api \
  --logo "https://raw.githubusercontent.com/bryanzk/MarketMakerDemo/main/docs/logo.png" \
  --logo-link "/" \
  --footer-text "AlphaLoop Market Maker - Automated Trading System"

echo "✅ Documentation generated successfully in docs/api/"
echo "📖 View locally: open docs/api/index.html"

