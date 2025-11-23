import random
from alphaloop.strategies.strategy import FixedSpreadStrategy
from alphaloop.market.performance import PerformanceTracker


class MarketSimulator:
    def __init__(self, strategy):
        self.strategy = strategy
        self.performance = PerformanceTracker()
        self.current_price = 2000.0
        self.position = 0.0

    def generate_market_data(self):
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

    def run(self, steps=100):
        # print(f"Starting simulation with spread: {self.strategy.spread}") # Removed noisy print
        for _ in range(steps):
            market_data = self.generate_market_data()
            orders = self.strategy.calculate_target_orders(market_data)

            # Simple fill logic: if price moves through our orders
            # For this mock, we'll assume 50% fill rate if we are inside the spread
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
