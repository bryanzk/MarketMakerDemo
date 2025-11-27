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
from alphaloop.market.strategy_instance import StrategyInstance
from alphaloop.strategies.funding import FundingRateStrategy
from alphaloop.strategies.strategy import FixedSpreadStrategy

logger = setup_logger("AlphaLoop")


class AlphaLoop:
    def __init__(self):
        # Multi-strategy support: list of StrategyInstance objects
        self.strategy_instances = {}  # Dict[strategy_id: str, StrategyInstance]

        # Backward compatibility: create default strategy instance
        default_strategy_id = "default"
        if STRATEGY_TYPE == "funding_rate":
            default_instance = StrategyInstance(default_strategy_id, "funding_rate")
            logger.info("Using Strategy: Funding Rate Skew")
        else:
            default_instance = StrategyInstance(default_strategy_id, "fixed_spread")
            logger.info("Using Strategy: Fixed Spread")
        self.strategy_instances[default_strategy_id] = default_instance
        # Ensure the legacy default strategy keeps running unless explicitly stopped
        default_instance.running = True

        # Legacy single strategy reference for backward compatibility
        self.strategy = default_instance.strategy

        # Shared agents and resources
        self.quant = QuantAgent()
        self.risk = RiskAgent()
        self.data = DataAgent()
        self.om = (
            OrderManager()
        )  # Legacy order manager (kept for backward compatibility)
        self.alert = (
            None  # Global alert (can be overridden by strategy-specific alerts)
        )
        self.current_stage = "Idle"
        self.active_orders = []  # Legacy: aggregated orders from all strategies
        self.system_logs = deque(maxlen=50)
        self.order_history = deque(maxlen=200)  # Legacy: aggregated order history
        self.error_history = deque(maxlen=200)  # Legacy: aggregated error history

        # Note: Each strategy instance now has its own exchange connection
        # No shared exchange at AlphaLoop level
        # 注意：每个策略实例现在都有自己的交易所连接
        # AlphaLoop 级别不再有共享的交易所

    def add_strategy_instance(
        self,
        strategy_id: str,
        strategy_type: str = "fixed_spread",
        symbol: str | None = None,
    ):
        """
        Add a new strategy instance.

        Args:
            strategy_id: Unique identifier for the strategy instance
            strategy_type: "fixed_spread" or "funding_rate"
            symbol: Optional trading symbol override

        Returns:
            bool: True if added successfully, False if strategy_id already exists
        """
        if strategy_id in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' already exists")
            return False

        instance = StrategyInstance(strategy_id, strategy_type, symbol=symbol)
        self.strategy_instances[strategy_id] = instance
        logger.info(f"Added strategy instance '{strategy_id}' ({strategy_type})")
        return True

    def remove_strategy_instance(self, strategy_id: str):
        """
        Remove a strategy instance and cancel all its orders.

        Args:
            strategy_id: Identifier of the strategy instance to remove

        Returns:
            bool: True if removed successfully, False if not found
        """
        if strategy_id not in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' not found")
            return False

        instance = self.strategy_instances[strategy_id]

        # Cancel all tracked orders for this strategy using its own exchange
        if (
            instance.use_real_exchange
            and instance.exchange
            and instance.tracked_order_ids
        ):
            try:
                instance.exchange.cancel_orders(list(instance.tracked_order_ids))
                logger.info(
                    f"Cancelled {len(instance.tracked_order_ids)} orders for strategy '{strategy_id}'"
                )
            except Exception as e:
                logger.error(
                    f"Error cancelling orders for strategy '{strategy_id}': {e}"
                )

        del self.strategy_instances[strategy_id]
        logger.info(f"Removed strategy instance '{strategy_id}'")
        return True

    def get_strategy_instance(self, strategy_id: str):
        """Get a strategy instance by ID."""
        return self.strategy_instances.get(strategy_id)

    def set_strategy(self, strategy_type):
        """
        Switch the default strategy at runtime (backward compatibility).
        For multi-strategy, use add_strategy_instance instead.
        """
        # Update default strategy instance
        default_id = "default"
        if default_id not in self.strategy_instances:
            # Create default if it doesn't exist
            self.add_strategy_instance(default_id, strategy_type)
        else:
            # Preserve current settings and running state
            current_instance = self.strategy_instances[default_id]
            current_spread = current_instance.strategy.spread
            current_quantity = current_instance.strategy.quantity
            current_leverage = current_instance.strategy.leverage
            current_running = current_instance.running  # Preserve running state
            current_alert = current_instance.alert  # Preserve alert

            # Create new instance
            new_instance = StrategyInstance(default_id, strategy_type)
            new_instance.strategy.spread = current_spread
            new_instance.strategy.quantity = current_quantity
            new_instance.strategy.leverage = current_leverage
            new_instance.running = current_running  # Restore running state
            new_instance.alert = current_alert  # Restore alert

            self.strategy_instances[default_id] = new_instance
            self.strategy = new_instance.strategy  # Update legacy reference
            new_instance.strategy_switched = True
            logger.info(
                f"Switched default strategy to: {strategy_type} (running={current_running})"
            )

        return True

    def set_symbol(self, symbol, strategy_id: str = "default"):
        """
        Update the trading symbol for a specific strategy instance.

        Args:
            symbol: Trading symbol to set
            strategy_id: Strategy instance ID (defaults to "default")

        Returns:
            bool: True if symbol updated successfully
        """
        if strategy_id not in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' not found")
            return False

        instance = self.strategy_instances[strategy_id]
        return instance.set_symbol(symbol)

    def set_stage(self, stage_name):
        self.current_stage = stage_name
        timestamp = time.strftime("%H:%M:%S")
        self.system_logs.append({"timestamp": timestamp, "stage": stage_name})

    def get_status(self):
        # Get status for each strategy instance (each has its own data)
        strategy_statuses = {}
        for strategy_id, instance in self.strategy_instances.items():
            strategy_statuses[strategy_id] = instance.get_status()

        # Legacy: Get default strategy for backward compatibility
        default_instance = self.strategy_instances.get("default")
        if default_instance:
            default_status = default_instance.get_status()
            current_symbol = default_status.get("symbol", "ETH/USDT:USDT")
            mid_price = default_status.get("mid_price", 2000.0)
            funding_rate = default_status.get("funding_rate", 0.0)
            position = default_status.get("position", 0.0)
            pnl = default_status.get("pnl", 0.0)
            default_strategy_type = default_instance.strategy_type
        else:
            current_symbol = "ETH/USDT:USDT"
            mid_price = 2000.0
            funding_rate = 0.0
            position = 0.0
            pnl = 0.0
            default_strategy_type = "fixed_spread"

        # Get last error from any strategy instance (for backward compatibility)
        last_error = None
        for instance in self.strategy_instances.values():
            if instance.exchange and hasattr(instance.exchange, "last_order_error"):
                if instance.exchange.last_order_error:
                    last_error = instance.exchange.last_order_error
                    break

        return {
            "active": True,
            "symbol": current_symbol,  # From default instance
            "mid_price": mid_price,  # From default instance
            "funding_rate": funding_rate,  # From default instance
            "position": position,  # From default instance
            "pnl": pnl,  # From default instance
            "strategy_type": default_strategy_type,  # Legacy field
            "spread": (
                getattr(default_instance.strategy, "spread", None)
                if default_instance
                else None
            ),  # Legacy
            "quantity": (
                getattr(default_instance.strategy, "quantity", None)
                if default_instance
                else None
            ),  # Legacy
            "leverage": (
                getattr(default_instance.strategy, "leverage", None)
                if default_instance
                else None
            ),  # Legacy
            "alert": self.alert,  # Global alert
            "orders": self.active_orders,  # Aggregated orders
            "logs": list(self.system_logs),
            "last_error": last_error,  # From any strategy instance
            "error": None,
            # Multi-strategy support
            "strategy_instances": strategy_statuses,
            "strategy_count": len(self.strategy_instances),
        }

    def _get_error_suggestion(self, error_type: str, error_details: dict) -> str:
        """
        Get user-friendly suggestion based on error type.

        Args:
            error_type: Type of error (e.g., "insufficient_funds", "invalid_order")
            error_details: Error details dict

        Returns:
            Suggestion string
        """
        suggestions = {
            "insufficient_funds": (
                "Check your account balance and margin. "
                "Consider reducing order quantity or closing existing positions. "
                "For sell orders, ensure you have sufficient position size."
            ),
            "invalid_order": (
                "Order parameters may be invalid. "
                "Check price, quantity, and symbol settings. "
                "Verify order limits (min quantity, min notional)."
            ),
            "exchange_error": (
                "Exchange API error occurred. "
                "This may be temporary - the system will retry in the next cycle. "
                "If it persists, check Binance API status."
            ),
        }
        return suggestions.get(
            error_type, "Please check your strategy settings and try again."
        )

    def _run_strategy_instance_cycle(self, instance: StrategyInstance):
        """
        Run a single strategy instance cycle using its own exchange connection.

        Args:
            instance: StrategyInstance to execute (has its own exchange)
        """
        try:
            # Refresh data for this strategy instance using its own exchange
            if not instance.refresh_data():
                instance.alert = {
                    "type": "error",
                    "message": "Failed to refresh exchange data.",
                    "suggestion": "Check Binance connectivity / API credentials.",
                }
                return

            market_data = instance.latest_market_data
            funding_rate = instance.latest_funding_rate

            # Calculate target orders for this strategy instance
            target_orders = instance.calculate_target_orders(market_data, funding_rate)

            # Get current orders for this strategy (filtered by tracked IDs)
            if instance.strategy_switched:
                logger.info(
                    f"Strategy '{instance.strategy_id}' was switched - forcing full order reset"
                )
                current_orders = []
                instance.clear_tracked_orders()
                instance.strategy_switched = False
            else:
                # Fetch all open orders using this instance's exchange
                all_orders = instance.exchange.fetch_open_orders()
                current_orders = [
                    o for o in all_orders if o.get("id") in instance.tracked_order_ids
                ]

            # Sync orders for this strategy instance
            to_cancel_ids, to_place = instance.sync_orders(
                current_orders, target_orders
            )

            # Cancel orders that need updating
            if to_cancel_ids:
                for order_id in to_cancel_ids:
                    instance.remove_tracked_order(order_id)
                    # Update history
                    for hist_order in instance.order_history:
                        if hist_order.get("id") == order_id:
                            hist_order["status"] = "cancelled"
                instance.exchange.cancel_orders(to_cancel_ids)

            # Place new/updated orders
            if to_place:
                placed_orders = instance.exchange.place_orders(to_place)
                for order in placed_orders:
                    order_id = order.get("id")
                    if order_id:
                        instance.add_tracked_order(order_id)

                    # Record in strategy-specific history
                    instance.order_history.append(
                        {
                            "id": order_id or "unknown",
                            "symbol": instance.exchange.symbol,
                            "side": order.get("side"),
                            "price": order.get("price"),
                            "quantity": order.get("amount", order.get("quantity")),
                            "status": "placed",
                            "timestamp": time.time(),
                            "strategy_id": instance.strategy_id,
                            "strategy_type": instance.strategy_type,
                        }
                    )

                    # Also add to global history for backward compatibility
                    self.order_history.append(
                        {
                            "id": order_id or "unknown",
                            "symbol": instance.exchange.symbol,
                            "side": order.get("side"),
                            "price": order.get("price"),
                            "quantity": order.get("amount", order.get("quantity")),
                            "status": "placed",
                            "timestamp": time.time(),
                            "strategy_id": instance.strategy_id,
                            "strategy_type": instance.strategy_type,
                        }
                    )

                # Handle errors using this instance's exchange
                if hasattr(instance.exchange, "last_order_error") and getattr(
                    instance.exchange, "last_order_error"
                ):
                    err = instance.exchange.last_order_error
                    error_type = err.get("type", "unknown")
                    error_message = err.get("message", "")

                    # Record error in history
                    error_record = {
                        "timestamp": time.time(),
                        "symbol": err.get("symbol", instance.exchange.symbol),
                        "type": error_type,
                        "message": error_message,
                        "details": err.get("details"),
                        "strategy_id": instance.strategy_id,
                        "strategy_type": instance.strategy_type,
                    }
                    instance.error_history.append(error_record)
                    self.error_history.append(error_record)

                    # Set alert for critical errors (insufficient funds, invalid orders, etc.)
                    if error_type in [
                        "insufficient_funds",
                        "invalid_order",
                        "exchange_error",
                    ]:
                        instance.alert = {
                            "type": (
                                "error"
                                if error_type == "insufficient_funds"
                                else "warning"
                            ),
                            "message": error_message,
                            "suggestion": self._get_error_suggestion(error_type, err),
                        }
                        logger.warning(
                            f"Strategy '{instance.strategy_id}' error: {error_type} - {error_message}"
                        )

                # Update active orders for this instance using its own exchange
                all_orders = instance.exchange.fetch_open_orders()
                instance.active_orders = [
                    o for o in all_orders if o.get("id") in instance.tracked_order_ids
                ]
                for order in instance.active_orders:
                    if "amount" not in order:
                        order["amount"] = order.get("quantity", 0)
            else:
                instance.active_orders = []

        except Exception as e:
            logger.error(
                f"Error in strategy instance '{instance.strategy_id}' cycle: {e}"
            )
            instance.error_history.append(
                {
                    "timestamp": time.time(),
                    "symbol": (
                        instance.exchange.symbol if instance.exchange else "unknown"
                    ),
                    "type": "cycle_error",
                    "message": str(e),
                    "details": None,
                    "strategy_id": instance.strategy_id,
                    "strategy_type": instance.strategy_type,
                }
            )
            instance.alert = {
                "type": "error",
                "message": f"Strategy '{instance.strategy_id}' error: {e}",
                "suggestion": "Check logs or retry.",
            }

    def run_cycle(self):
        logger.info(
            f"Starting AlphaLoop Cycle with {len(self.strategy_instances)} strategy instance(s)"
        )

        active_instances = [
            (strategy_id, instance)
            for strategy_id, instance in self.strategy_instances.items()
            if instance.use_real_exchange and instance.running
        ]
        has_real_exchange = any(
            inst.use_real_exchange for inst in self.strategy_instances.values()
        )

        if has_real_exchange and not active_instances:
            self.set_stage("Idle (no active strategies)")
            self.active_orders = []
            stats = {"realized_pnl": 0.0, "win_rate": 0.0}
        elif active_instances:
            self.set_stage("Execution")
            try:
                # Execute each running strategy instance independently
                for strategy_id, instance in active_instances:
                    logger.info(
                        f"Executing strategy instance: {strategy_id} (symbol: {instance.symbol})"
                    )
                    self._run_strategy_instance_cycle(instance)

                # Aggregate active orders from running strategies (legacy compatibility)
                self.active_orders = []
                for _, instance in active_instances:
                    self.active_orders.extend(instance.active_orders)

                # Use aggregated stats from all strategies (placeholder until fills tracked)
                stats = {
                    "realized_pnl": 0.0,
                    "win_rate": 0.0,
                }
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
                self.error_history.append(
                    {
                        "timestamp": time.time(),
                        "symbol": "unknown",
                        "type": "cycle_error",
                        "message": str(e),
                        "details": None,
                        "strategy_type": "system",
                    }
                )
                self.alert = {
                    "type": "error",
                    "message": f"Cycle error: {e}",
                    "suggestion": "Check logs or retry. This may be a temporary issue.",
                }
                self.set_stage("Idle (cycle error)")
                return
        else:
            self.set_stage("Market Simulation")
            # Simulation Mode: Use default strategy for backward compatibility
            default_instance = self.strategy_instances.get("default")
            if default_instance:
                sim = MarketSimulator(default_instance.strategy)
                stats = sim.run(steps=500)
                mock_market = sim.generate_market_data()
                self.active_orders = default_instance.calculate_target_orders(
                    mock_market
                )
                for i, o in enumerate(self.active_orders):
                    o["id"] = f"ord_{int(time.time())}_{i}"
                    o["amount"] = o.get("quantity", 0)

        # Data Ingestion & Analysis (shared across all strategies)
        self.set_stage("Data: Analyzing Market")
        self.data.ingest_data({"price": 1000}, [])  # Mock ingestion
        metrics = self.data.calculate_metrics()

        volatility = metrics.get("volatility", 0)
        sharpe = metrics.get("sharpe_ratio", 0)
        self.set_stage(f"Data: Volatility {volatility:.2%}, Sharpe {sharpe:.2f}")

        logger.info(
            f"Cycle Performance",
            extra={"extra_data": {"pnl": stats["realized_pnl"], "metrics": metrics}},
        )

        # Quant Analysis & Proposal for each strategy instance independently
        for strategy_id, instance in self.strategy_instances.items():
            if not instance.running:
                continue

            current_config = {"spread": instance.strategy.spread}
            strategy_status = instance.get_status()
            strategy_metrics = {
                "strategy_id": strategy_id,
                "strategy_type": instance.strategy_type,
                "mid_price": strategy_status.get("mid_price"),
                "position": strategy_status.get("position"),
                "strategy_pnl": strategy_status.get("pnl"),
                "funding_rate": strategy_status.get("funding_rate"),
            }
            proposal = self.quant.analyze_and_propose(
                current_config, {**stats, **metrics, **strategy_metrics}
            )

            if not proposal:
                logger.info(
                    f"No changes proposed for strategy '{strategy_id}'. Skipping."
                )
                continue

            logger.info(
                f"Quant proposing spread {proposal['spread']:.2%} for strategy '{strategy_id}'"
            )

            # Risk Validation
            approved, reason = self.risk.validate_proposal(proposal)

            if approved:
                logger.info(
                    f"Applying new config for strategy '{strategy_id}'",
                    extra={"extra_data": {"proposal": proposal}},
                )
                instance.strategy.spread = proposal["spread"]
                instance.alert = None
            else:
                logger.warning(
                    f"Proposal rejected for strategy '{strategy_id}': {reason}"
                )

                # Auto-fallback to safe defaults
                safe_defaults = instance.reset_to_safe_defaults()
                logger.info(
                    f"Auto-fallback to safe defaults for strategy '{strategy_id}'",
                    extra={"extra_data": {"safe_defaults": safe_defaults}},
                )

                instance.alert = {
                    "type": "warning",
                    "message": f"Risk Rejection: {reason}",
                    "suggestion": f"Auto-fallback to safe defaults (Spread: {safe_defaults['spread']*100:.2f}%).",
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
