import numpy as np
from alphaloop.metrics.base import Metric


class SharpeRatio(Metric):
    def calculate(self, data):
        trades = data.get("trades", [])
        if len(trades) < 10:
            return 0.0

        pnls = [t["pnl"] for t in trades]
        returns = np.diff(pnls)

        if len(returns) > 0 and np.std(returns) > 0:
            return float(np.mean(returns) / np.std(returns) * np.sqrt(365 * 24 * 60))
        return 0.0


class Slippage(Metric):
    def calculate(self, data):
        # Mock implementation
        return 0.5  # 0.5 bps


class FillRate(Metric):
    def calculate(self, data):
        # Mock implementation
        return 0.85  # 85%


class TickToTradeLatency(Metric):
    def calculate(self, data):
        # Mock implementation
        return 3.5  # ms
