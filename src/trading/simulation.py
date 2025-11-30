"""
Market Simulator Module / 市场模拟模块

Simulates market conditions for strategy testing.
模拟市场条件用于策略测试。

Owner: Agent TRADING
"""

import random
from typing import Any, Dict

from src.trading.performance import PerformanceTracker
from src.trading.strategies.fixed_spread import FixedSpreadStrategy


class MarketSimulator:
    """Simulates market conditions for strategy testing."""

    def __init__(self, strategy=None):
        """
        Initialize simulator.

        Args:
            strategy: Strategy instance to test (defaults to FixedSpreadStrategy)
        """
        self.strategy = strategy or FixedSpreadStrategy()
        self.performance = PerformanceTracker()
        self.current_price = 2000.0
        self.position = 0.0

    def generate_market_data(self) -> Dict[str, float]:
        """Generate simulated market data."""
        # Random walk
        change = random.gauss(0, 2)
        self.current_price += change

        # Create spread around mid price
        spread = 0.5  # Tight market spread
        best_bid = self.current_price - spread / 2
        best_ask = self.current_price + spread / 2

        return {
            "mid_price": self.current_price,
            "best_bid": best_bid,
            "best_ask": best_ask,
        }

    def run(self, steps: int = 100) -> Dict[str, Any]:
        """
        Run simulation for specified number of steps.

        Args:
            steps: Number of simulation steps

        Returns:
            Performance statistics
        """
        for _ in range(steps):
            market_data = self.generate_market_data()
            orders = self.strategy.calculate_target_orders(market_data)

            # Simple fill logic: if price moves through our orders
            for order in orders:
                if order["side"] == "buy":
                    if order["price"] >= market_data["best_bid"]:
                        self.position += order["quantity"]
                        self.performance.update_position(
                            self.position, market_data["mid_price"]
                        )
                elif order["side"] == "sell":
                    if order["price"] <= market_data["best_ask"]:
                        self.position -= order["quantity"]
                        self.performance.update_position(
                            self.position, market_data["mid_price"]
                        )

        return self.performance.get_stats()


if __name__ == "__main__":
    strategy = FixedSpreadStrategy()
    sim = MarketSimulator(strategy)
    stats = sim.run(1000)
    print("Simulation Results:", stats)

