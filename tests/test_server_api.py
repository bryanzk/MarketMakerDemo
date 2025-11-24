import time
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

import server


class DummyStrategy:
    def __init__(self, spread: float, quantity: float, leverage: int, skew_factor: float = None):
        self.spread = spread
        self.quantity = quantity
        self.leverage = leverage
        # Only Funding strategy will have skew_factor
        if skew_factor is not None:
            self.skew_factor = skew_factor


class DummyBotEngine:
    def __init__(self, strategy: Any, orders: List[Dict[str, Any]]):
        self.strategy = strategy
        self.current_stage = "Idle"
        self.alert = None
        self._status_base = {
            "active": False,
            "symbol": "ETH/USDT:USDT",
            "mid_price": 2000.0,
            "funding_rate": 0.0,
            "position": 0.0,
            "pnl": 0.0,
            "alert": None,
            "orders": [],
            "logs": [],
            "error": None,
        }
        self.order_history = orders

    def get_status(self) -> Dict[str, Any]:
        # Return shallow copy so handlers can mutate
        return dict(self._status_base)


@pytest.fixture
def client_fixed_strategy(monkeypatch):
    """Test client with a dummy Fixed Spread strategy bot engine."""
    strategy = DummyStrategy(spread=0.002, quantity=0.1, leverage=3)
    dummy_bot = DummyBotEngine(
        strategy=strategy,
        orders=[
            {
                "id": "ord1",
                "symbol": "ETH/USDT:USDT",
                "side": "buy",
                "price": 2000.0,
                "quantity": 0.1,
                "status": "placed",
                "timestamp": time.time(),
                "strategy_type": "fixed_spread",
            },
            {
                "id": "ord2",
                "symbol": "ETH/USDT:USDT",
                "side": "sell",
                "price": 2010.0,
                "quantity": 0.1,
                "status": "placed",
                "timestamp": time.time(),
                "strategy_type": "funding_rate",
            },
        ],
    )

    monkeypatch.setattr(server, "bot_engine", dummy_bot)
    monkeypatch.setattr(server, "is_running", False)

    return TestClient(server.app)


@pytest.fixture
def client_funding_strategy(monkeypatch):
    """Test client with a dummy Funding Rate strategy bot engine."""
    strategy = DummyStrategy(spread=0.003, quantity=0.2, leverage=5, skew_factor=150.0)
    dummy_bot = DummyBotEngine(strategy=strategy, orders=[])

    monkeypatch.setattr(server, "bot_engine", dummy_bot)
    monkeypatch.setattr(server, "is_running", True)

    return TestClient(server.app)


def test_status_includes_core_config_fixed(client_fixed_strategy):
    """GET /api/status should expose spread/quantity/leverage and fixed_spread strategy_type."""
    resp = client_fixed_strategy.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()

    # Values from DummyStrategy
    assert data["spread"] == pytest.approx(0.002)
    assert data["quantity"] == pytest.approx(0.1)
    assert data["leverage"] == 3
    assert data["strategy_type"] == "fixed_spread"
    # Active flag should reflect global is_running
    assert data["active"] is False


def test_status_includes_core_config_funding(client_funding_strategy):
    """GET /api/status should expose skew_factor when using FundingRateStrategy."""
    resp = client_funding_strategy.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()

    assert data["spread"] == pytest.approx(0.003)
    assert data["quantity"] == pytest.approx(0.2)
    assert data["leverage"] == 5
    assert data["strategy_type"] == "funding_rate"
    # skew_factor should be present for funding strategy
    assert data["skew_factor"] == pytest.approx(150.0)
    assert data["active"] is True


def test_order_history_filters_by_symbol_and_strategy_type(client_fixed_strategy):
    """GET /api/order-history should filter by symbol & strategy_type."""
    # Only the funding_rate order for ETH/USDT:USDT should be returned
    resp = client_fixed_strategy.get(
        "/api/order-history",
        params={"symbol": "ETH/USDT:USDT", "strategy_type": "funding_rate"},
    )
    assert resp.status_code == 200
    orders = resp.json()

    assert len(orders) == 1
    ord0 = orders[0]
    assert ord0["symbol"] == "ETH/USDT:USDT"
    assert ord0["strategy_type"] == "funding_rate"

