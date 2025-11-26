import numpy as np
import pytest

from alphaloop.metrics.definitions import FillRate, SharpeRatio, Slippage


class TestSharpeRatio:
    def test_calculate_empty(self):
        metric = SharpeRatio("sharpe", {})
        assert metric.calculate({"trades": []}) == 0.0

    def test_calculate_valid(self):
        metric = SharpeRatio("sharpe", {})
        # Create trades with varying returns
        trades = [
            {"pnl": 10},
            {"pnl": 20},
            {"pnl": 25},
            {"pnl": 40},
            {"pnl": 30},
            {"pnl": 60},
            {"pnl": 55},
            {"pnl": 80},
            {"pnl": 75},
            {"pnl": 100},
            {"pnl": 90},
        ]

        val = metric.calculate({"trades": trades})
        assert val > 0


class TestSlippage:
    def test_calculate(self):
        metric = Slippage("slippage", {})
        assert metric.calculate({}) == 0.5  # Mock value


class TestFillRate:
    def test_calculate(self):
        metric = FillRate("fill_rate", {})
        assert metric.calculate({}) == 0.85  # Mock value
