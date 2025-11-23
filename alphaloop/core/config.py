import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Credentials
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# Trading Parameters
SYMBOL = "ETH/USDT:USDT"  # Trading pair (CCXT Unified format for linear swap)
QUANTITY = 0.02  # Order quantity in base asset (e.g., ETH)
SPREAD_PCT = 0.2 / 100  # 0.2% spread (converted to decimal: 0.002)
MAX_POSITION = 0.5  # Max absolute position size (ETH)
LEVERAGE = 5  # Leverage multiplier

# System Parameters
REFRESH_INTERVAL = 2  # Seconds between loops
LOG_LEVEL = "INFO"

# Risk Limits
RISK_LIMITS = {
    "MIN_SPREAD": 0.001,  # 0.1%
    "MAX_SPREAD": 0.05,  # 5%
    "MAX_POSITION": MAX_POSITION,
}

# Metrics Configuration (Pluggable)
METRICS_CONFIG = {
    "layer_1_infrastructure": {
        "tick_to_trade_latency": {"enabled": True, "target_ms": 5},
        "websocket_sequence_gap": {"enabled": True, "target": 0},
    },
    "layer_2_execution": {
        "slippage_bps": {"enabled": True, "target_bps": 2},
        "fill_rate": {"enabled": True, "target_pct": 80},
    },
    "layer_3_risk": {
        "liquidation_buffer": {"enabled": True, "target_pct": 20},
        "funding_yield": {"enabled": False, "target_apy": 10},  # Disabled example
    },
    "layer_4_strategy": {
        "sharpe_ratio": {"enabled": True, "target": 2.0},
        "sortino_ratio": {"enabled": True, "target": 3.0},
    },
}
