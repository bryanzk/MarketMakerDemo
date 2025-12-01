# Shared Module - Common utilities for all modules
# Owner: Agent ARCH

"""
Shared utilities:
- config: Configuration management
- logger: Logging utilities
- utils: Common helper functions
"""

from src.shared.config import (
    API_KEY,
    API_SECRET,
    LEVERAGE,
    LOG_LEVEL,
    MAX_POSITION,
    METRICS_CONFIG,
    QUANTITY,
    REFRESH_INTERVAL,
    RISK_LIMITS,
    SKEW_FACTOR,
    SPREAD_PCT,
    STRATEGY_TYPE,
    SYMBOL,
)
from src.shared.logger import JsonFormatter, setup_logger
from src.shared.utils import round_step_size, round_tick_size

__all__ = [
    # Config
    "API_KEY",
    "API_SECRET",
    "SYMBOL",
    "QUANTITY",
    "SPREAD_PCT",
    "MAX_POSITION",
    "LEVERAGE",
    "SKEW_FACTOR",
    "STRATEGY_TYPE",
    "REFRESH_INTERVAL",
    "LOG_LEVEL",
    "RISK_LIMITS",
    "METRICS_CONFIG",
    # Logger
    "setup_logger",
    "JsonFormatter",
    # Utils
    "round_step_size",
    "round_tick_size",
]
