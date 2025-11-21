import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Trading Parameters
SYMBOL = "ETH/USDT:USDT"  # Trading pair (CCXT Unified format for linear swap)
QUANTITY = 0.02     # Order quantity in base asset (e.g., ETH)
SPREAD_PCT = 0.002 / 100  # 0.002% spread (converted to decimal: 0.00002)
MAX_POSITION = 0.5  # Max absolute position size (ETH)
LEVERAGE = 5        # Leverage multiplier

# System Parameters
REFRESH_INTERVAL = 2  # Seconds between loops
LOG_LEVEL = "INFO"
