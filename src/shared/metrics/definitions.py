"""
Metric Definitions / 指标定义

Concrete implementations of various metrics.
各种指标的具体实现。

Owner: Agent ARCH
"""

from typing import Any, Dict, List, Optional

import numpy as np

from src.shared.metrics.base import Metric


class SharpeRatio(Metric):
    """Sharpe Ratio metric for risk-adjusted returns."""

    def calculate(self, data: Dict[str, Any]) -> float:
        trades: List[Dict] = data.get("trades", [])
        if len(trades) < 10:
            return 0.0

        pnls = [t["pnl"] for t in trades]
        returns = np.diff(pnls)

        if len(returns) > 0 and np.std(returns) > 0:
            return float(np.mean(returns) / np.std(returns) * np.sqrt(365 * 24 * 60))
        return 0.0


class Slippage(Metric):
    """Slippage metric in basis points."""

    def calculate(self, data: Dict[str, Any]) -> float:
        # Mock implementation
        return 0.5  # 0.5 bps


class FillRate(Metric):
    """Order fill rate metric."""

    def calculate(self, data: Dict[str, Any]) -> float:
        # Mock implementation
        return 0.85  # 85%


class TickToTradeLatency(Metric):
    """Tick-to-trade latency in milliseconds."""

    def calculate(self, data: Dict[str, Any]) -> float:
        # Mock implementation
        return 3.5  # ms

