from unittest.mock import Mock

from src.trading.engine import AlphaLoop
from src.trading.strategy_instance import StrategyInstance
from src.trading.exchange import BinanceClient


def test_engine_skips_non_hyperliquid_exchange_order_cycle():
    # Create engine without running AlphaLoop.__init__ to avoid side effects
    engine = object.__new__(AlphaLoop)
    engine.error_history = []
    engine.order_history = []

    instance = Mock(spec=StrategyInstance)
    instance.strategy_id = "default"
    instance.strategy_type = "fixed_spread"
    instance.exchange = Mock(spec=BinanceClient)
    instance.refresh_data.return_value = True
    instance.latest_market_data = {}
    instance.latest_funding_rate = 0.0
    instance.strategy_switched = False
    instance.tracked_order_ids = set()
    instance.order_history = []
    instance.error_history = []
    instance.calculate_target_orders.return_value = []
    instance.clear_tracked_orders = Mock()
    instance.sync_orders.return_value = (["oid-1"], [{"side": "buy", "price": 1.0, "quantity": 1.0}])
    instance.remove_tracked_order = Mock()
    instance.add_tracked_order = Mock()

    engine._run_strategy_instance_cycle(instance)

    instance.exchange.fetch_open_orders.assert_not_called()
    instance.exchange.cancel_orders.assert_not_called()
    instance.exchange.place_orders.assert_not_called()
