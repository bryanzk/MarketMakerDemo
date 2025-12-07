from unittest.mock import Mock

from src.trading.engine import AlphaLoop


def test_engine_hyperliquid_only_creates_hl_instance():
    hl_exchange = Mock()
    hl_exchange.symbol = "ETHUSDC"

    engine = AlphaLoop(hyperliquid_only=True, hyperliquid_exchange=hl_exchange)

    assert "hyperliquid" in engine.strategy_instances
    inst = engine.strategy_instances["hyperliquid"]
    assert inst.exchange is hl_exchange
    assert inst.running is True
    assert engine.strategy is inst.strategy
