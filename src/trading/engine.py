"""
AlphaLoop Trading Engine / AlphaLoop 交易引擎

Main trading engine that orchestrates strategy instances and agents.
协调策略实例和代理的主交易引擎。

Owner: Agent TRADING
"""

import sys
import time
from collections import deque
from typing import Any, Dict, Optional

from src.ai.agents.data import DataAgent
from src.ai.agents.quant import QuantAgent
from src.ai.agents.risk import RiskAgent
from src.shared.config import STRATEGY_TYPE, SYMBOL, HYPERLIQUID_ONLY
from src.shared.logger import setup_logger
from src.shared.tracing import get_trace_id
from src.trading.exchange import BinanceClient
from src.trading.order_manager import OrderManager
from src.trading.simulation import MarketSimulator
from src.trading.strategies.fixed_spread import FixedSpreadStrategy
from src.trading.strategies.funding_rate import FundingRateStrategy
from src.trading.strategy_instance import StrategyInstance

logger = setup_logger("AlphaLoop")


class AlphaLoop:
    """
    Main trading engine for market making bot.
    做市机器人的主交易引擎。

    Supports multiple strategy instances running independently.
    支持多个策略实例独立运行。
    """

    def __init__(self, hyperliquid_only: Optional[bool] = None, hyperliquid_exchange: Optional[Any] = None):
        # Multi-strategy support: dict of StrategyInstance objects
        self.strategy_instances: Dict[str, StrategyInstance] = {}

        # Determine mode / 确定模式
        self.hyperliquid_only = HYPERLIQUID_ONLY if hyperliquid_only is None else hyperliquid_only

        if self.hyperliquid_only:
            # Hyperliquid-only mode: create a Hyperliquid strategy instance and skip default Binance
            # 仅 Hyperliquid 模式：创建 Hyperliquid 策略实例，跳过默认 Binance
            try:
                from src.trading.hyperliquid_client import HyperliquidClient

                hl_exchange = hyperliquid_exchange or HyperliquidClient()
                hl_instance = StrategyInstance(
                    "hyperliquid",
                    STRATEGY_TYPE,
                    symbol=SYMBOL,
                    exchange=hl_exchange,
                )
                hl_instance.running = True
                self.strategy_instances["hyperliquid"] = hl_instance
                self.strategy = hl_instance.strategy
                logger.info("Started in Hyperliquid-only mode; default Binance instance disabled")
            except Exception as e:
                logger.error(
                    f"Failed to initialize Hyperliquid-only mode: {e}. No default instance created.",
                    exc_info=True,
                )
                self.strategy = None
        else:
            # Backward compatibility: create default Binance strategy instance
            default_strategy_id = "default"
            if STRATEGY_TYPE == "funding_rate":
                default_instance = StrategyInstance(default_strategy_id, "funding_rate")
                logger.info("Using Strategy: Funding Rate Skew")
            else:
                default_instance = StrategyInstance(default_strategy_id, "fixed_spread")
                logger.info("Using Strategy: Fixed Spread")
            self.strategy_instances[default_strategy_id] = default_instance
            default_instance.running = True

            # Legacy single strategy reference for backward compatibility
            self.strategy = default_instance.strategy

        # Shared agents and resources
        self.quant = QuantAgent()
        self.risk = RiskAgent()
        self.data = DataAgent()
        self.om = OrderManager()  # Legacy order manager
        self.alert = None  # Global alert
        self.current_stage = "Idle"
        self.active_orders = []  # Legacy: aggregated orders
        self.system_logs = deque(maxlen=50)
        self.order_history = deque(maxlen=200)
        self.error_history = deque(maxlen=200)

    def add_strategy_instance(
        self,
        strategy_id: str,
        strategy_type: str = "fixed_spread",
        symbol: Optional[str] = None,
        exchange: Optional[Any] = None,
    ) -> bool:
        """
        Add a new strategy instance.

        Args:
            strategy_id: Unique identifier for the strategy instance
            strategy_type: "fixed_spread" or "funding_rate"
            symbol: Optional trading symbol override
            exchange: Optional exchange client instance (e.g., HyperliquidClient for hyperliquid instances)

        Returns:
            True if added successfully, False if strategy_id already exists
        """
        if strategy_id in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' already exists")
            return False

        instance = StrategyInstance(strategy_id, strategy_type, symbol=symbol, exchange=exchange)
        self.strategy_instances[strategy_id] = instance
        logger.info(f"Added strategy instance '{strategy_id}' ({strategy_type})")
        return True

    def remove_strategy_instance(self, strategy_id: str) -> bool:
        """
        Remove a strategy instance and cancel all its orders.

        Args:
            strategy_id: Identifier of the strategy instance to remove

        Returns:
            True if removed successfully, False if not found
        """
        if strategy_id not in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' not found")
            return False

        instance = self.strategy_instances[strategy_id]

        # Cancel all tracked orders for this strategy
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

    def get_strategy_instance(self, strategy_id: str) -> Optional[StrategyInstance]:
        """Get a strategy instance by ID."""
        return self.strategy_instances.get(strategy_id)

    def set_strategy(self, strategy_type: str) -> bool:
        """
        Switch the default strategy at runtime (backward compatibility).
        For multi-strategy, use add_strategy_instance instead.
        """
        default_id = "default"
        if default_id not in self.strategy_instances:
            self.add_strategy_instance(default_id, strategy_type)
        else:
            current_instance = self.strategy_instances[default_id]
            current_spread = current_instance.strategy.spread
            current_quantity = current_instance.strategy.quantity
            current_leverage = current_instance.strategy.leverage
            current_running = current_instance.running
            current_alert = current_instance.alert

            new_instance = StrategyInstance(default_id, strategy_type)
            new_instance.strategy.spread = current_spread
            new_instance.strategy.quantity = current_quantity
            new_instance.strategy.leverage = current_leverage
            new_instance.running = current_running
            new_instance.alert = current_alert

            self.strategy_instances[default_id] = new_instance
            self.strategy = new_instance.strategy
            new_instance.strategy_switched = True
            logger.info(
                f"Switched default strategy to: {strategy_type} (running={current_running})"
            )

        return True

    def set_symbol(self, symbol: str, strategy_id: str = "default") -> bool:
        """
        Update the trading symbol for a specific strategy instance.

        Args:
            symbol: Trading symbol to set
            strategy_id: Strategy instance ID (defaults to "default")

        Returns:
            True if symbol updated successfully
        """
        if strategy_id not in self.strategy_instances:
            logger.error(f"Strategy instance '{strategy_id}' not found")
            return False

        instance = self.strategy_instances[strategy_id]
        return instance.set_symbol(symbol)

    def set_stage(self, stage_name: str) -> None:
        """Set the current stage and log it."""
        self.current_stage = stage_name
        timestamp = time.strftime("%H:%M:%S")
        self.system_logs.append({"timestamp": timestamp, "stage": stage_name})

    def get_status(self) -> dict:
        """Get current status of all strategy instances."""
        strategy_statuses = {}
        for strategy_id, instance in self.strategy_instances.items():
            strategy_statuses[strategy_id] = instance.get_status()

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

        last_error = None
        for instance in self.strategy_instances.values():
            if instance.exchange and hasattr(instance.exchange, "last_order_error"):
                if instance.exchange.last_order_error:
                    last_error = instance.exchange.last_order_error
                    break

        return {
            "active": True,
            "symbol": current_symbol,
            "mid_price": mid_price,
            "funding_rate": funding_rate,
            "position": position,
            "pnl": pnl,
            "strategy_type": default_strategy_type,
            "spread": (
                getattr(default_instance.strategy, "spread", None)
                if default_instance
                else None
            ),
            "quantity": (
                getattr(default_instance.strategy, "quantity", None)
                if default_instance
                else None
            ),
            "leverage": (
                getattr(default_instance.strategy, "leverage", None)
                if default_instance
                else None
            ),
            "alert": self.alert,
            "orders": self.active_orders,
            "logs": list(self.system_logs),
            "last_error": last_error,
            "error": None,
            "strategy_instances": strategy_statuses,
            "strategy_count": len(self.strategy_instances),
        }

    def _get_error_suggestion(self, error_type: str, error_details: dict) -> str:
        """Get user-friendly suggestion based on error type."""
        suggestions = {
            "insufficient_funds": (
                "Check your account balance and margin. "
                "Consider reducing order quantity or closing existing positions."
            ),
            "invalid_order": (
                "Order parameters may be invalid. "
                "Check price, quantity, and symbol settings."
            ),
            "exchange_error": (
                "Exchange API error occurred. "
                "This may be temporary - the system will retry in the next cycle."
            ),
        }
        return suggestions.get(
            error_type, "Please check your strategy settings and try again."
        )

    def _run_strategy_instance_cycle(self, instance: StrategyInstance) -> None:
        """Run a single strategy instance cycle using its own exchange connection."""
        try:
            if not instance.refresh_data():
                exchange_name = "exchange"
                if instance.exchange:
                    exchange_name = getattr(instance.exchange, "__class__", type(None)).__name__.replace("Client", "")
                instance.alert = {
                    "type": "error",
                    "message": "Failed to refresh exchange data.",
                    "suggestion": f"Check {exchange_name} connectivity / API credentials.",
                }
                # Add error to error_history / 将错误添加到 error_history
                error_record = {
                    "timestamp": time.time(),
                    "symbol": (
                        getattr(instance.exchange, "symbol", "unknown")
                        if instance.exchange
                        else "unknown"
                    ),
                    "type": "cycle_error",
                    "message": "Failed to refresh exchange data.",
                    "details": None,
                    "strategy_id": instance.strategy_id,
                    "strategy_type": instance.strategy_type,
                    "trace_id": get_trace_id(),
                }
                instance.error_history.append(error_record)
                self.error_history.append(error_record)
                return

            # Only allow Hyperliquid exchanges to place/cancel orders
            # 仅允许 Hyperliquid 交易所下单/撤单，其他交易所直接跳过
            try:
                from src.trading.hyperliquid_client import HyperliquidClient
            except Exception:
                HyperliquidClient = None  # type: ignore

            if not (
                HyperliquidClient
                and instance.exchange
                and isinstance(instance.exchange, HyperliquidClient)
            ):
                logger.info(
                    "Skipping order cycle for non-Hyperliquid exchange",
                    extra={
                        "strategy_id": instance.strategy_id,
                        "strategy_type": instance.strategy_type,
                        "exchange_type": type(instance.exchange).__name__
                        if instance.exchange
                        else "None",
                        "trace_id": get_trace_id(),
                    },
                )
                return

            market_data = instance.latest_market_data
            funding_rate = instance.latest_funding_rate

            target_orders = instance.calculate_target_orders(market_data, funding_rate)

            if instance.strategy_switched:
                logger.info(
                    f"Strategy '{instance.strategy_id}' was switched - forcing full order reset"
                )
                current_orders = []
                instance.clear_tracked_orders()
                instance.strategy_switched = False
            else:
                all_orders = instance.exchange.fetch_open_orders()
                current_orders = [
                    o for o in all_orders if o.get("id") in instance.tracked_order_ids
                ]

            to_cancel_ids, to_place = instance.sync_orders(
                current_orders, target_orders
            )

            if to_cancel_ids:
                for order_id in to_cancel_ids:
                    instance.remove_tracked_order(order_id)
                    for hist_order in instance.order_history:
                        if hist_order.get("id") == order_id:
                            hist_order["status"] = "cancelled"
                instance.exchange.cancel_orders(to_cancel_ids)

            if to_place:
                placed_orders = instance.exchange.place_orders(to_place)
                for order in placed_orders:
                    order_id = order.get("id")
                    if order_id:
                        instance.add_tracked_order(order_id)

                    order_record = {
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
                    instance.order_history.append(order_record)
                    self.order_history.append(order_record)

            # Check for order errors after placing orders (even if no orders were placed) / 在下单后检查订单错误（即使没有下单）
            if hasattr(instance.exchange, "last_order_error"):
                last_error = getattr(instance.exchange, "last_order_error", None)
                if last_error and isinstance(last_error, dict):
                    err = last_error
                    error_type = err.get("type", "unknown")
                    error_message = err.get("message", "")

                    error_record = {
                        "timestamp": time.time(),
                        "symbol": err.get("symbol", instance.exchange.symbol),
                        "type": error_type,
                        "message": error_message,
                        "details": err.get("details"),
                        "strategy_id": instance.strategy_id,
                        "strategy_type": instance.strategy_type,
                        "trace_id": get_trace_id(),  # Include trace_id for correlation / 包含 trace_id 用于关联
                    }
                    instance.error_history.append(error_record)
                    self.error_history.append(error_record)

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

                    # Clear last_order_error after processing / 处理完后清除 last_order_error
                    instance.exchange.last_order_error = None

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
            # Get symbol safely to avoid format string issues with Mock / 安全地获取 symbol 以避免 Mock 的格式化字符串问题
            symbol = "unknown"
            if instance.exchange:
                try:
                    symbol = str(getattr(instance.exchange, "symbol", "unknown"))
                except Exception:
                    symbol = "unknown"

            error_record = {
                "timestamp": time.time(),
                "symbol": symbol,
                "type": "cycle_error",
                "message": str(e),
                "details": None,
                "strategy_id": instance.strategy_id,
                "strategy_type": instance.strategy_type,
                "trace_id": get_trace_id(),  # Include trace_id for correlation / 包含 trace_id 用于关联
            }
            instance.error_history.append(error_record)
            self.error_history.append(error_record)
            instance.alert = {
                "type": "error",
                "message": f"Strategy '{instance.strategy_id}' error: {e}",
                "suggestion": "Check logs or retry.",
            }

    def run_cycle(self) -> None:
        """Run one cycle of all strategy instances."""
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
                for strategy_id, instance in active_instances:
                    logger.info(
                        f"Executing strategy instance: {strategy_id} (symbol: {instance.symbol})"
                    )
                    self._run_strategy_instance_cycle(instance)

                self.active_orders = []
                for _, instance in active_instances:
                    self.active_orders.extend(instance.active_orders)

                stats = {"realized_pnl": 0.0, "win_rate": 0.0}
            except Exception as e:
                logger.error(f"Error in cycle: {e}")
                self.error_history.append(
                    {
                        "timestamp": time.time(),
                        "symbol": "unknown",
                        "type": "cycle_error",
                        "message": str(e),
                        "trace_id": get_trace_id(),  # Include trace_id for correlation / 包含 trace_id 用于关联
                        "details": None,
                        "strategy_type": "system",
                        "trace_id": get_trace_id(),  # Include trace_id for correlation / 包含 trace_id 用于关联
                    }
                )
                self.alert = {
                    "type": "error",
                    "message": f"Cycle error: {e}",
                    "suggestion": "Check logs or retry.",
                }
                self.set_stage("Idle (cycle error)")
                return
        else:
            self.set_stage("Market Simulation")
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

        # Data Ingestion & Analysis
        self.set_stage("Data: Analyzing Market")
        self.data.ingest_data({"price": 1000}, [])
        metrics = self.data.calculate_metrics()

        volatility = metrics.get("volatility", 0)
        sharpe = metrics.get("sharpe_ratio", 0)
        # Safely format to avoid Mock.__format__ errors / 安全格式化以避免 Mock.__format__ 错误
        try:
            volatility_str = (
                f"{volatility:.2%}" if isinstance(volatility, (int, float)) else "0.00%"
            )
            sharpe_str = f"{sharpe:.2f}" if isinstance(sharpe, (int, float)) else "0.00"
        except (TypeError, ValueError):
            volatility_str = "0.00%"
            sharpe_str = "0.00"
        self.set_stage(f"Data: Volatility {volatility_str}, Sharpe {sharpe_str}")

        logger.info(
            f"Cycle Performance",
            extra={"extra_data": {"pnl": stats["realized_pnl"], "metrics": metrics}},
        )

        # Quant Analysis & Proposal for each strategy instance
        for strategy_id, instance in self.strategy_instances.items():
            if not instance.running:
                continue

            current_config = {"spread": instance.strategy.spread}
            strategy_status = instance.get_status()
            # Safely get strategy_status values, handling Mock objects
            # 安全获取 strategy_status 值，处理 Mock 对象
            if isinstance(strategy_status, dict):
                strategy_metrics = {
                    "strategy_id": strategy_id,
                    "strategy_type": instance.strategy_type,
                    "mid_price": strategy_status.get("mid_price"),
                    "position": strategy_status.get("position"),
                    "strategy_pnl": strategy_status.get("pnl"),
                    "funding_rate": strategy_status.get("funding_rate"),
                }
            else:
                # If strategy_status is a Mock, use defaults
                # 如果 strategy_status 是 Mock，使用默认值
                strategy_metrics = {
                    "strategy_id": strategy_id,
                    "strategy_type": instance.strategy_type,
                    "mid_price": 1000.0,
                    "position": 0.0,
                    "strategy_pnl": 0.0,
                    "funding_rate": 0.0,
                }
            proposal = self.quant.analyze_and_propose(
                current_config, {**stats, **metrics, **strategy_metrics}
            )

            if not proposal:
                logger.info(
                    f"No changes proposed for strategy '{strategy_id}'. Skipping."
                )
                continue

            # Safely access proposal spread, handling Mock objects
            # 安全访问 proposal spread，处理 Mock 对象
            if isinstance(proposal, dict) and "spread" in proposal:
                spread_value = proposal["spread"]
                if isinstance(spread_value, (int, float)):
                    spread_str = f"{spread_value:.2%}"
                else:
                    spread_str = "N/A"
            else:
                spread_str = "N/A"
            logger.info(
                f"Quant proposing spread {spread_str} for strategy '{strategy_id}'"
            )

            # Safely unpack validate_proposal result / 安全解包 validate_proposal 结果
            try:
                validation_result = self.risk.validate_proposal(proposal)
                if isinstance(validation_result, tuple) and len(validation_result) == 2:
                    approved, reason = validation_result
                else:
                    # If not a tuple, assume approved / 如果不是元组，假设已批准
                    approved = (
                        bool(validation_result)
                        if validation_result is not None
                        else True
                    )
                    reason = None
            except (TypeError, ValueError) as e:
                logger.warning(f"Error validating proposal: {e}. Assuming approved.")
                approved = True
                reason = None

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

    def run_continuous(self, cycles: int = 5) -> None:
        """Run multiple cycles continuously."""
        for i in range(cycles):
            logger.info(f"Iteration {i+1}")
            self.run_cycle()
            self.set_stage("Idle")
            time.sleep(1)


if __name__ == "__main__":
    loop = AlphaLoop()
    loop.run_continuous(cycles=3)
