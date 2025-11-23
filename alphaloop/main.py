import sys
import time
from collections import deque

from alphaloop.agents.data import DataAgent
from alphaloop.agents.quant import QuantAgent
from alphaloop.agents.risk import RiskAgent
from alphaloop.core.logger import setup_logger
from alphaloop.market.exchange import BinanceClient
from alphaloop.market.simulation import MarketSimulator
from alphaloop.strategies.strategy import FixedSpreadStrategy

logger = setup_logger("AlphaLoop")


class AlphaLoop:
    def __init__(self):
        self.strategy = FixedSpreadStrategy()
        self.quant = QuantAgent()
        self.risk = RiskAgent()
        self.data = DataAgent()
        self.alert = None
        self.current_stage = "Idle"
        self.active_orders = []
        self.system_logs = deque(maxlen=50)
        self.order_history = deque(maxlen=200)  # Store last 200 orders
        # Initialize exchange
        try:
            self.exchange = BinanceClient()
            self.use_real_exchange = True
            logger.info("Exchange connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to exchange: {e}. Using simulation mode.")
            self.exchange = None
            self.use_real_exchange = False

    def set_symbol(self, symbol):
        """Update the trading symbol"""
        if self.exchange:
            success = self.exchange.set_symbol(symbol)
            if success:
                logger.info(f"Symbol updated to {symbol}")
                return True
            else:
                logger.error(f"Failed to update symbol to {symbol}")
                return False
        return False

    def set_stage(self, stage_name):
        self.current_stage = stage_name
        timestamp = time.strftime("%H:%M:%S")
        self.system_logs.append({"timestamp": timestamp, "stage": stage_name})

    def get_status(self):
        # Fetch real data if exchange is available
        mid_price = 2000.0
        position = 0.0
        pnl = 0.0
        current_symbol = "ETH/USDT:USDT"  # Default

        if self.use_real_exchange:
            try:
                current_symbol = self.exchange.symbol
                market_data = self.exchange.fetch_market_data()
                if market_data and market_data["mid_price"]:
                    mid_price = market_data["mid_price"]

                account_data = self.exchange.fetch_account_data()
                if account_data:
                    position = account_data["position_amt"]
                    # Calculate unrealized PnL if we have a position
                    if position != 0 and account_data["entry_price"] != 0:
                        pnl = (mid_price - account_data["entry_price"]) * position
            except Exception as e:
                logger.error(f"Error fetching real-time data: {e}")

        return {
            "active": True,
            "symbol": current_symbol,
            "mid_price": mid_price,
            "position": position,
            "pnl": pnl,
            "alert": self.alert,
            "orders": self.active_orders,
            "logs": list(self.system_logs),
            "error": None,
        }

    def run_cycle(self):
        logger.info("Starting AlphaLoop Cycle")

        if self.use_real_exchange:
            self.set_stage("Execution")
            # 1. Real Exchange Mode: Fetch market data and place orders
            try:
                # Fetch current market data
                market_data = self.exchange.fetch_market_data()
                if not market_data or not market_data["mid_price"]:
                    logger.error("Failed to fetch market data")
                    return

                # Calculate target orders based on current market
                target_orders = self.strategy.calculate_target_orders(market_data)

                # Cancel existing orders
                self.exchange.cancel_all_orders()

                # Place new orders
                if target_orders:
                    placed_orders = self.exchange.place_orders(target_orders)
                    # Record placed orders in history
                    for order in placed_orders:
                        self.order_history.append(
                            {
                                "id": order.get("id", "unknown"),
                                "symbol": self.exchange.symbol,
                                "side": order.get("side"),
                                "price": order.get("price"),
                                "quantity": order.get("amount", order.get("quantity")),
                                "status": "placed",
                                "timestamp": time.time(),
                            }
                        )
                    # Fetch updated open orders
                    self.active_orders = self.exchange.fetch_open_orders()
                    # Format for frontend
                    for order in self.active_orders:
                        if "amount" not in order:
                            order["amount"] = order.get("quantity", 0)
                else:
                    self.active_orders = []

                # Use market data for stats
                stats = {
                    "realized_pnl": 0.0,  # Would need to track fills
                    "win_rate": 0.0,
                }
            except Exception as e:
                logger.error(f"Error in real exchange cycle: {e}")
                return
        else:
            self.set_stage("Market Simulation")
            # 2. Simulation Mode (fallback)
            sim = MarketSimulator(self.strategy)
            stats = sim.run(steps=500)
            mock_market = sim.generate_market_data()
            self.active_orders = self.strategy.calculate_target_orders(mock_market)
            for i, o in enumerate(self.active_orders):
                o["id"] = f"ord_{int(time.time())}_{i}"
                o["amount"] = o["quantity"]

        # 2. Data Ingestion & Analysis
        self.set_stage("Data: Analyzing Market")
        # Assuming sim.run returns trades in stats for now, or we need to modify sim
        # For this prototype, we'll pass the aggregate stats as a mock
        self.data.ingest_data({"price": 1000}, [])  # Mock ingestion
        metrics = self.data.calculate_metrics()

        # Log Data Agent findings
        volatility = metrics.get("volatility", 0)
        sharpe = metrics.get("sharpe_ratio", 0)
        self.set_stage(f"Data: Volatility {volatility:.2%}, Sharpe {sharpe:.2f}")

        logger.info(
            f"Cycle Performance",
            extra={"extra_data": {"pnl": stats["realized_pnl"], "metrics": metrics}},
        )

        # 3. Quant Analysis & Proposal
        current_config = {"spread": self.strategy.spread}
        # Pass metrics to Quant instead of raw stats
        proposal = self.quant.analyze_and_propose(current_config, {**stats, **metrics})

        if not proposal:
            self.set_stage("Quant: No changes proposed")
            logger.info("No changes proposed. Cycle complete.")
            return

        self.set_stage(f"Quant: Proposing Spread {proposal['spread']:.2%}")

        # 3. Risk Validation
        approved, reason = self.risk.validate_proposal(proposal)

        if approved:
            self.set_stage("Risk: Approved Proposal")
            # 4. Deployment (Apply changes)
            logger.info(
                f"Applying new config", extra={"extra_data": {"proposal": proposal}}
            )
            self.strategy.spread = proposal["spread"]
            self.alert = None  # Clear alert on success
        else:
            self.set_stage(f"Risk: Rejected ({reason})")
            logger.warning(f"Proposal rejected: {reason}")
            self.alert = {
                "type": "warning",
                "message": f"Risk Rejection: {reason}",
                "suggestion": "Check your strategy settings or market volatility.",
            }

    def run_continuous(self, cycles=5):
        for i in range(cycles):
            logger.info(f"Iteration {i+1}")
            self.run_cycle()
            self.set_stage("Idle")
            time.sleep(1)


if __name__ == "__main__":
    loop = AlphaLoop()
    loop.run_continuous(cycles=3)
