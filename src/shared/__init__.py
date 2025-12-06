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
    HYPERLIQUID_API_KEY,
    HYPERLIQUID_API_SECRET,
    HYPERLIQUID_TESTNET,
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
from src.shared.error_mapper import ErrorMapper, map_exception
from src.shared.errors import (
    ErrorSeverity,
    ErrorType,
    StandardErrorResponse,
)
from src.shared.exchange_metrics import (
    ExchangeName,
    MetricsCollector,
    OperationType,
    metrics_collector,
    track_exchange_operation,
)
from src.shared.logger import JsonFormatter, setup_logger
from src.shared.utils import round_step_size, round_tick_size

__all__ = [
    # Config - Binance
    "API_KEY",
    "API_SECRET",
    # Config - Hyperliquid
    "HYPERLIQUID_API_KEY",
    "HYPERLIQUID_API_SECRET",
    "HYPERLIQUID_TESTNET",
    # Config - Trading Parameters
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
    # Error Handling
    "ErrorSeverity",
    "ErrorType",
    "StandardErrorResponse",
    "ErrorMapper",
    "map_exception",
    # Metrics
    "ExchangeName",
    "OperationType",
    "MetricsCollector",
    "metrics_collector",
    "track_exchange_operation",
]
