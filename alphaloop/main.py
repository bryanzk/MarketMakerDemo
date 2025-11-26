import sys
import time
from collections import deque

from alphaloop.agents.data import DataAgent
from alphaloop.agents.quant import QuantAgent
from alphaloop.agents.risk import RiskAgent
from alphaloop.core.config import STRATEGY_TYPE
from alphaloop.core.logger import setup_logger
from alphaloop.market.exchange import BinanceClient
from alphaloop.market.order_manager import OrderManager
from alphaloop.market.simulation import MarketSimulator
from alphaloop.strategies.funding import FundingRateStrategy
from alphaloop.strategies.strategy import FixedSpreadStrategy

logger = setup_logger("AlphaLoop")


class AlphaLoop:
    def __init__(self):
        if STRATEGY_TYPE == "funding_rate":
            self.strategy = FundingRateStrategy()
            logger.info("Using Strategy: Funding Rate Skew")
        else:
            self.strategy = FixedSpreadStrategy()
            logger.info("Using Strategy: Fixed Spread")
        self.quant = QuantAgent()
        self.risk = RiskAgent()
        self.data = DataAgent()
        self.om = OrderManager()  # Smart order syncing
        self.strategy_switched = False  # Flag to track strategy changes
        self.alert = None
        self.current_stage = "Idle"
        self.active_orders = []
        self.system_logs = deque(maxlen=50)
        self.order_history = deque(maxlen=200)  # Store last 200 orders
        self.error_history = deque(maxlen=200)  # Store last 200 errors (order/exchange)
        # Initialize exchange
        try:
            self.exchange = BinanceClient()
            self.use_real_exchange = True
            logger.info("Exchange connected successfully")
        except Exception as e:
            logger.error(f"Failed to connect to exchange: {e}. Using simulation mode.")
            self.exchange = None
            self.use_real_exchange = False

        # Data Cache for Non-Blocking Status
        self.latest_market_data = None
        self.latest_funding_rate = 0.0
        self.latest_account_data = None

    def set_strategy(self, strategy_type):
        """Switch strategy at runtime, preserving common parameters."""
        # Preserve current settings
        current_spread = self.strategy.spread
        current_quantity = self.strategy.quantity
        current_leverage = self.strategy.leverage

        new_strategy = None
        if strategy_type == "funding_rate":
            new_strategy = FundingRateStrategy()
            logger.info("Switched to Strategy: Funding Rate Skew")
        elif strategy_type == "fixed_spread":
            new_strategy = FixedSpreadStrategy()
            logger.info("Switched to Strategy: Fixed Spread")
        else:
            logger.error(f"Unknown strategy type: {strategy_type}")
            return False

        # Restore settings
        new_strategy.spread = current_spread
        new_strategy.quantity = current_quantity
        new_strategy.leverage = current_leverage

        # If switching TO funding rate, we might want to ensure skew_factor is set from config or default
        # But FundingRateStrategy.__init__ already does that.

        self.strategy = new_strategy
        # Flag that strategy was switched - next cycle should do a full order reset
        self.strategy_switched = True
        return True

    def set_symbol(self, symbol):
        """Update the trading symbol"""
        if self.exchange:
            success = self.exchange.set_symbol(symbol)
            if success:
                logger.info(f"Symbol updated to {symbol}")
                # Invalidate cache to prevent stale data
                self.latest_market_data = None
                self.latest_funding_rate = 0.0
                self.latest_account_data = None
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
        # Use cached data to avoid blocking the API server
        mid_price = 2000.0
        position = 0.0
        pnl = 0.0
        current_symbol = "ETH/USDT:USDT"
        funding_rate = 0.0

        # Derive current strategy type for status & history
        strategy_type = (
            "funding_rate"
            if isinstance(self.strategy, FundingRateStrategy)
            else "fixed_spread"
        )

        if self.use_real_exchange:
            if self.exchange:
                current_symbol = self.exchange.symbol

            # Use Cached Data
            if self.latest_market_data and self.latest_market_data["mid_price"]:
                mid_price = self.latest_market_data["mid_price"]

            funding_rate = self.latest_funding_rate

            if self.latest_account_data:
                position = self.latest_account_data["position_amt"]
                # Calculate unrealized PnL if we have a position
                if position != 0 and self.latest_account_data["entry_price"] != 0:
                    pnl = (
                        mid_price - self.latest_account_data["entry_price"]
                    ) * position

        return {
            "active": True,
            "symbol": current_symbol,
            "mid_price": mid_price,
            "funding_rate": funding_rate,
            "position": position,
            "pnl": pnl,
            "strategy_type": strategy_type,
            "spread": getattr(self.strategy, "spread", None),
            "quantity": getattr(self.strategy, "quantity", None),
            "leverage": getattr(self.strategy, "leverage", None),
            "alert": self.alert,
            "orders": self.active_orders,
            "logs": list(self.system_logs),
            "last_error": (
                self.exchange.last_order_error
                if self.exchange and hasattr(self.exchange, "last_order_error")
                else None
            ),
            "error": None,
        }

    def run_cycle(self):
        logger.info("Starting AlphaLoop Cycle")

        if self.use_real_exchange:
            self.set_stage("Execution")
            # 1. Real Exchange Mode: Fetch market data and place orders

    def refresh_data(self):
        """Fetch fresh data from exchange and update cache."""
        if not self.use_real_exchange or not self.exchange:
            return False

        try:
            # Fetch current market data
            market_data = self.exchange.fetch_market_data()
            if not market_data or not market_data["mid_price"]:
                logger.error("Failed to fetch market data")
                return False

            # Validate data freshness (protect against stale data)
            current_time_ms = time.time() * 1000
            data_timestamp = market_data.get("timestamp", current_time_ms)
            data_age_seconds = (current_time_ms - data_timestamp) / 1000

            if data_age_seconds > 5.0:  # 5 second threshold
                logger.warning(f"Market data is stale ({data_age_seconds:.1f}s old).")
                # We still update cache but might want to warn caller

            # Fetch funding rate
            funding_rate = self.exchange.fetch_funding_rate()

            # Fetch Account Data (for PnL and Position)
            account_data = self.exchange.fetch_account_data()

            # Update Cache
            self.latest_market_data = market_data
            self.latest_funding_rate = funding_rate
            self.latest_account_data = account_data
            return True
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            return False

    def run_cycle(self):
        logger.info("Starting AlphaLoop Cycle")

        if self.use_real_exchange:
            self.set_stage("Execution")
            # 1. Real Exchange Mode: Fetch market data and place orders
            try:
                # Refresh Data
                if not self.refresh_data():
                    self.set_stage("Idle (refresh failed)")
                    if not self.alert or self.alert.get("type") != "error":
                        self.alert = {
                            "type": "error",
                            "message": "Failed to refresh exchange data.",
                            "suggestion": "Check Binance connectivity / API credentials.",
                        }
                    return

                market_data = self.latest_market_data
                funding_rate = self.latest_funding_rate

                # Calculate target orders based on current market and funding rate
                # FixedSpreadStrategy will ignore funding_rate if it doesn't accept it,
                # but we should handle that gracefully or ensure both accept it.
                # Since we didn't update FixedSpreadStrategy signature, we need to check.
                if (
                    hasattr(self.strategy.calculate_target_orders, "__code__")
                    and "funding_rate"
                    in self.strategy.calculate_target_orders.__code__.co_varnames
                ):
                    target_orders = self.strategy.calculate_target_orders(
                        market_data, funding_rate=funding_rate
                    )
                else:
                    target_orders = self.strategy.calculate_target_orders(market_data)

                # Use OrderManager to sync orders efficiently
                # If strategy was just switched, force a full reset
                if self.strategy_switched:
                    logger.info("Strategy was switched - forcing full order reset")
                    current_orders = []  # Treat as if no orders exist
                    self.strategy_switched = False  # Clear flag
                else:
                    current_orders = self.exchange.fetch_open_orders()

                to_cancel_ids, to_place = self.om.sync_orders(
                    current_orders, target_orders
                )

                # Cancel orders that need updating
                if to_cancel_ids:
                    # Update status in history
                    for order_id in to_cancel_ids:
                        for hist_order in self.order_history:
                            if hist_order["id"] == order_id:
                                hist_order["status"] = "cancelled"
                    # Batch cancel
                    self.exchange.cancel_orders(to_cancel_ids)

                # Place new/updated orders
                if to_place:
                    placed_orders = self.exchange.place_orders(to_place)
                    # Record placed orders in history
                    strategy_type = (
                        "funding_rate"
                        if isinstance(self.strategy, FundingRateStrategy)
                        else "fixed_spread"
                    )
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
                                "strategy_type": strategy_type,
                            }
                        )
                    # If the exchange recorded a last_order_error for any failed order,
                    # capture it into a rolling error history for UI inspection.
                    if hasattr(self.exchange, "last_order_error") and getattr(
                        self.exchange, "last_order_error"
                    ):
                        err = self.exchange.last_order_error
                        self.error_history.append(
                            {
                                "timestamp": time.time(),
                                "symbol": err.get("symbol", self.exchange.symbol),
                                "type": err.get("type", "unknown"),
                                "message": err.get("message", ""),
                                "details": err.get("details"),
                                "strategy_type": strategy_type,
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
                # Record the cycle error in error_history for UI display
                strategy_type = (
                    "funding_rate"
                    if isinstance(self.strategy, FundingRateStrategy)
                    else "fixed_spread"
                )
                self.error_history.append(
                    {
                        "timestamp": time.time(),
                        "symbol": self.exchange.symbol if self.exchange else "unknown",
                        "type": "cycle_error",
                        "message": str(e),
                        "details": None,
                        "strategy_type": strategy_type,
                    }
                )
                # Also set alert for immediate UI feedback
                self.alert = {
                    "type": "error",
                    "message": f"Exchange cycle error: {e}",
                    "suggestion": "Check logs or retry. This may be a temporary issue.",
                }
                self.set_stage("Idle (cycle error)")
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
