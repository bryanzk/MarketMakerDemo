# Metrics Module - Pluggable metrics framework
# Owner: Agent ARCH

"""
Metrics framework:
- base: Abstract metric class
- definitions: Concrete metric implementations
- registry: Metric registration and calculation
"""

from src.shared.metrics.base import Metric
from src.shared.metrics.definitions import (
    FillRate,
    SharpeRatio,
    Slippage,
    TickToTradeLatency,
)
from src.shared.metrics.registry import MetricsRegistry

__all__ = [
    "Metric",
    "SharpeRatio",
    "Slippage",
    "FillRate",
    "TickToTradeLatency",
    "MetricsRegistry",
]
