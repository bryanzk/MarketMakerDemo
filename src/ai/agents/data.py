"""
Data Agent / 数据代理

Ingests market data and calculates metrics.
摄取市场数据并计算指标。

Owner: Agent AI
"""

import numpy as np

from src.shared.config import METRICS_CONFIG
from src.shared.logger import setup_logger
from src.shared.metrics.definitions import (
    FillRate,
    SharpeRatio,
    Slippage,
    TickToTradeLatency,
)
from src.shared.metrics.registry import MetricsRegistry

logger = setup_logger("DataAgent")


class DataAgent:
    """Agent for data ingestion and metrics calculation."""

    def __init__(self):
        self.trade_history = []
        self.price_history = []
        self.registry = MetricsRegistry()
        self._register_metrics()

    def _register_metrics(self):
        """Register configured metrics."""
        # Layer 1
        l1_conf = METRICS_CONFIG.get("layer_1_infrastructure", {})
        self.registry.register(
            TickToTradeLatency(
                "tick_to_trade_latency", l1_conf.get("tick_to_trade_latency", {})
            )
        )

        # Layer 2
        l2_conf = METRICS_CONFIG.get("layer_2_execution", {})
        self.registry.register(
            Slippage("slippage_bps", l2_conf.get("slippage_bps", {}))
        )
        self.registry.register(FillRate("fill_rate", l2_conf.get("fill_rate", {})))

        # Layer 4
        l4_conf = METRICS_CONFIG.get("layer_4_strategy", {})
        self.registry.register(
            SharpeRatio("sharpe_ratio", l4_conf.get("sharpe_ratio", {}))
        )

    def ingest_data(self, market_data, trades):
        """
        Ingests market data and trades for analysis.

        Args:
            market_data: Dict with 'price' key
            trades: List of trade dicts
        """
        self.price_history.append(market_data["price"])
        self.trade_history.extend(trades)

    def calculate_metrics(self):
        """
        Calculates metrics using the registry.

        Returns:
            Dict of metric names to values
        """
        data_context = {"trades": self.trade_history, "prices": self.price_history}

        metrics = self.registry.calculate_all(data_context)
        logger.info("Calculated Metrics", extra={"extra_data": metrics})
        return metrics
