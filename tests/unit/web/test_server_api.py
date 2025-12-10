import asyncio
import time
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient

import server
from src.trading.strategies.funding_rate import FundingRateStrategy
from src.ai.evaluation.schemas import (
    AggregatedResult,
    EvaluationResult,
    ParameterStatistics,
    SimulationResult,
    StrategyConsensus,
    StrategyProposal,
)


class DummyStrategy:
    def __init__(
        self, spread: float, quantity: float, leverage: int, skew_factor: float = None
    ):
        self.spread = spread
        self.quantity = quantity
        self.leverage = leverage
        # Only Funding strategy will have skew_factor
        if skew_factor is not None:
            self.skew_factor = skew_factor


class DummyBotEngine:
    def __init__(
        self,
        strategy: Any,
        orders: List[Dict[str, Any]],
        errors: List[Dict[str, Any]] = None,
    ):
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
            "strategy_instances": {},
            "strategy_count": 0,
        }
        self.order_history = orders
        self.error_history = errors or []
        # Add strategy_instances attribute for new architecture compatibility
        self.strategy_instances = {}

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
        errors=[
            {
                "timestamp": time.time(),
                "symbol": "ETH/USDT:USDT",
                "type": "invalid_price",
                "message": "Invalid price: None. Cannot place order.",
                "strategy_type": "fixed_spread",
            },
            {
                "timestamp": time.time(),
                "symbol": "ETH/USDT:USDT",
                "type": "invalid_quantity",
                "message": "Invalid quantity: 0. Cannot place order.",
                "strategy_type": "funding_rate",
            },
        ],
    )

    monkeypatch.setattr(server, "bot_engine", dummy_bot)
    monkeypatch.setattr(server, "is_running", False)
    monkeypatch.setattr(server, "get_default_exchange", lambda: None)

    return TestClient(server.app)


@pytest.fixture
def client_funding_strategy(monkeypatch):
    """Test client with a FundingRateStrategy bot engine to ensure strategy_type is correct."""
    strategy = FundingRateStrategy()
    strategy.spread = 0.003
    strategy.quantity = 0.2
    strategy.leverage = 5
    strategy.skew_factor = 150.0

    dummy_bot = DummyBotEngine(strategy=strategy, orders=[])

    monkeypatch.setattr(server, "bot_engine", dummy_bot)
    monkeypatch.setattr(server, "is_running", True)
    monkeypatch.setattr(server, "get_default_exchange", lambda: None)

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


def test_error_history_filters_by_type(client_fixed_strategy):
    """GET /api/error-history should filter by error_type."""
    resp = client_fixed_strategy.get(
        "/api/error-history",
        params={"error_type": "invalid_quantity"},
    )
    assert resp.status_code == 200
    errors = resp.json()

    assert len(errors) == 1
    err0 = errors[0]
    assert err0["type"] == "invalid_quantity"
    assert err0["symbol"] == "ETH/USDT:USDT"


@pytest.fixture
def client_with_evaluation(monkeypatch):
    """Test client with mocked evaluation environment."""

    class DummyExchange:
        symbol = "ETHUSDT"

        def fetch_market_data(self):
            return {
                "symbol": "ETHUSDT",
                "mid_price": 2000.0,
                "best_bid": 1999.5,
                "best_ask": 2000.5,
                "funding_rate": 0.0001,
            }

        def fetch_account_data(self):
            return {
                "position_amt": 0.1,
                "unrealizedProfit": 5.0,
                "balance": 1000.0,
                "leverage": 3,
            }

    monkeypatch.setattr(server, "get_default_exchange", lambda: DummyExchange())
    monkeypatch.setattr(server, "create_all_providers", lambda: ["mock"])

    proposal1 = StrategyProposal(
        recommended_strategy="FundingRate",
        spread=0.012,
        skew_factor=120.0,
        quantity=0.15,
        leverage=2.5,
        reasoning="Positive funding rate.",
        confidence=0.85,
        provider_name="Gemini (mock)",
    )
    proposal2 = StrategyProposal(
        recommended_strategy="FixedSpread",
        spread=0.015,
        skew_factor=100.0,
        quantity=0.10,
        leverage=1.5,
        reasoning="Volatility suggests wider spread.",
        confidence=0.75,
        provider_name="OpenAI (mock)",
    )

    sim1 = SimulationResult(
        realized_pnl=180.0,
        total_trades=45,
        winning_trades=26,
        win_rate=0.58,
        sharpe_ratio=2.1,
        simulation_steps=500,
    )
    sim2 = SimulationResult(
        realized_pnl=120.0,
        total_trades=38,
        winning_trades=20,
        win_rate=0.52,
        sharpe_ratio=1.5,
        simulation_steps=500,
    )

    eval_results = [
        EvaluationResult(
            provider_name="Gemini (mock)",
            proposal=proposal1,
            simulation=sim1,
            score=85.0,
            rank=1,
            latency_ms=1200,
        ),
        EvaluationResult(
            provider_name="OpenAI (mock)",
            proposal=proposal2,
            simulation=sim2,
            score=72.0,
            rank=2,
            latency_ms=980,
        ),
    ]

    aggregated = AggregatedResult(
        strategy_consensus=StrategyConsensus(
            consensus_strategy="FundingRate",
            consensus_level="majority",
            consensus_ratio=0.67,
            consensus_count=2,
            total_models=3,
            strategy_votes={"FundingRate": 2, "FixedSpread": 1},
            strategy_percentages={"FundingRate": 0.67, "FixedSpread": 0.33},
            providers_by_strategy={
                "FundingRate": ["Gemini (mock)", "Claude (mock)"],
                "FixedSpread": ["OpenAI (mock)"],
            },
        ),
        parameter_stats=ParameterStatistics(
            spread_mean=0.0123,
            spread_median=0.012,
            spread_min=0.01,
            spread_max=0.015,
            spread_std=0.001,
            skew_mean=135.0,
            skew_median=135.0,
            quantity_mean=0.125,
            quantity_median=0.125,
            leverage_mean=2.0,
            leverage_median=2.0,
            confidence_mean=0.80,
            confidence_min=0.75,
            confidence_max=0.85,
        ),
        consensus_confidence=0.85,
        confidence_breakdown={},
        consensus_proposal=StrategyProposal(
            recommended_strategy="FundingRate",
            spread=0.012,
            skew_factor=135.0,
            quantity=0.12,
            leverage=2.0,
            reasoning="Consensus reasoning.",
            confidence=0.85,
            provider_name="Consensus",
        ),
        individual_results=eval_results,
        successful_evaluations=2,
        failed_evaluations=0,
        avg_pnl=150.0,
        avg_sharpe=1.8,
        avg_win_rate=0.55,
        avg_latency_ms=1090.0,
    )

    class FakeEvaluator:
        def __init__(self, *args, **kwargs):
            pass

        def evaluate(self, context):
            return eval_results

        def aggregate_results(self, results):
            return aggregated

        @staticmethod
        def generate_comparison_table(results):
            return "mock table"

        @staticmethod
        def generate_consensus_summary(aggregated_result):
            return {"summary": "mock consensus"}

    async def immediate_to_thread(func, *args, **kwargs):
        return func(*args, **kwargs)

    monkeypatch.setattr(server, "MultiLLMEvaluator", FakeEvaluator)
    monkeypatch.setattr(asyncio, "to_thread", immediate_to_thread)

    strategy = DummyStrategy(spread=0.002, quantity=0.1, leverage=3)
    dummy_bot = DummyBotEngine(strategy=strategy, orders=[])
    monkeypatch.setattr(server, "bot_engine", dummy_bot)

    return TestClient(server.app)


def test_run_evaluation_returns_results(client_with_evaluation):
    resp = client_with_evaluation.post("/api/evaluation/run", json={"symbol": "BTCUSDT"})
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["individual_results"]) == 2
    assert data["individual_results"][0]["provider_name"] == "Gemini (mock)"
    assert data["aggregated"]["strategy_consensus"]["consensus_strategy"] == "FundingRate"
    assert "comparison_table" in data
    assert "consensus_report" in data


def test_apply_evaluation_consensus(client_with_evaluation, monkeypatch):
    client_with_evaluation.post("/api/evaluation/run", json={"symbol": "ETHUSDT"})

    captured = {}

    async def fake_update_config(config):
        captured["config"] = config
        return {"status": "updated"}

    async def fake_update_leverage(leverage):
        captured["leverage"] = leverage
        return {"status": "updated"}

    monkeypatch.setattr(server, "update_config", fake_update_config)
    monkeypatch.setattr(server, "update_leverage", fake_update_leverage)

    resp = client_with_evaluation.post("/api/evaluation/apply", json={"source": "consensus"})
    assert resp.status_code == 200
    assert captured["config"].strategy_type == "funding_rate"
    assert captured["config"].spread == pytest.approx(1.2)  # percentage
    assert captured["leverage"] == 2


def test_apply_evaluation_individual_provider(client_with_evaluation, monkeypatch):
    client_with_evaluation.post("/api/evaluation/run", json={"symbol": "ETHUSDT"})

    captured = {}

    async def fake_update_config(config):
        captured["config"] = config
        return {"status": "updated"}

    async def fake_update_leverage(leverage):
        captured["leverage"] = leverage
        return {"status": "updated"}

    monkeypatch.setattr(server, "update_config", fake_update_config)
    monkeypatch.setattr(server, "update_leverage", fake_update_leverage)

    resp = client_with_evaluation.post(
        "/api/evaluation/apply",
        json={"source": "individual", "provider_name": "Gemini (mock)"},
    )
    assert resp.status_code == 200
    assert captured["config"].strategy_type == "funding_rate"
    assert captured["config"].spread == pytest.approx(1.2)
    assert captured["leverage"] == 2


def test_apply_individual_provider_not_found(client_with_evaluation):
    client_with_evaluation.post("/api/evaluation/run", json={"symbol": "ETHUSDT"})
    resp = client_with_evaluation.post(
        "/api/evaluation/apply",
        json={"source": "individual", "provider_name": "Unknown"},
    )
    assert resp.status_code == 200
    assert resp.json()["error"].startswith("Provider Unknown not found")

class TestErrorHistoryAPI:
    """Comprehensive tests for /api/error-history endpoint."""

    @pytest.fixture
    def client_with_errors(self, monkeypatch):
        """Test client with multiple error entries for filtering tests."""
        now = time.time()
        strategy = DummyStrategy(spread=0.002, quantity=0.1, leverage=3)
        dummy_bot = DummyBotEngine(
            strategy=strategy,
            orders=[],
            errors=[
                {
                    "timestamp": now - 100,
                    "symbol": "ETH/USDT:USDT",
                    "type": "invalid_price",
                    "message": "Invalid price: None",
                    "strategy_type": "fixed_spread",
                },
                {
                    "timestamp": now - 50,
                    "symbol": "BTC/USDT:USDT",
                    "type": "invalid_quantity",
                    "message": "Invalid quantity: 0",
                    "strategy_type": "funding_rate",
                },
                {
                    "timestamp": now - 10,
                    "symbol": "ETH/USDT:USDT",
                    "type": "insufficient_funds",
                    "message": "Not enough balance",
                    "strategy_type": "funding_rate",
                },
                {
                    "timestamp": now,
                    "symbol": "SOL/USDT:USDT",
                    "type": "invalid_price",
                    "message": "Invalid price: -100",
                    "strategy_type": "fixed_spread",
                },
            ],
        )

        monkeypatch.setattr(server, "bot_engine", dummy_bot)
        monkeypatch.setattr(server, "is_running", False)

        return TestClient(server.app), now

    def test_error_history_returns_all(self, client_with_errors):
        """GET /api/error-history without filters returns all errors."""
        client, _ = client_with_errors
        resp = client.get("/api/error-history")
        assert resp.status_code == 200
        errors = resp.json()
        assert len(errors) == 4

    def test_error_history_sorted_by_timestamp_descending(self, client_with_errors):
        """GET /api/error-history returns errors sorted newest first."""
        client, now = client_with_errors
        resp = client.get("/api/error-history")
        errors = resp.json()

        # First error should have the highest timestamp
        assert errors[0]["symbol"] == "SOL/USDT:USDT"
        assert errors[-1]["symbol"] == "ETH/USDT:USDT"
        assert errors[-1]["type"] == "invalid_price"

        # Verify descending order
        timestamps = [e["timestamp"] for e in errors]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_error_history_filter_by_symbol(self, client_with_errors):
        """GET /api/error-history filters by symbol."""
        client, _ = client_with_errors
        resp = client.get("/api/error-history", params={"symbol": "ETH/USDT:USDT"})
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 2
        for err in errors:
            assert err["symbol"] == "ETH/USDT:USDT"

    def test_error_history_filter_by_strategy_type(self, client_with_errors):
        """GET /api/error-history filters by strategy_type."""
        client, _ = client_with_errors
        resp = client.get(
            "/api/error-history", params={"strategy_type": "funding_rate"}
        )
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 2
        for err in errors:
            assert err["strategy_type"] == "funding_rate"

    def test_error_history_filter_by_from_time(self, client_with_errors):
        """GET /api/error-history filters by from_time."""
        client, now = client_with_errors
        # Only errors from last 60 seconds
        resp = client.get("/api/error-history", params={"from_time": now - 60})
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 3  # Excludes the one at now - 100
        for err in errors:
            assert err["timestamp"] >= now - 60

    def test_error_history_filter_by_to_time(self, client_with_errors):
        """GET /api/error-history filters by to_time."""
        client, now = client_with_errors
        # Only errors older than 30 seconds
        resp = client.get("/api/error-history", params={"to_time": now - 30})
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 2  # now - 100 and now - 50
        for err in errors:
            assert err["timestamp"] <= now - 30

    def test_error_history_filter_by_time_range(self, client_with_errors):
        """GET /api/error-history filters by from_time and to_time together."""
        client, now = client_with_errors
        # Errors between 60 and 20 seconds ago
        resp = client.get(
            "/api/error-history",
            params={"from_time": now - 60, "to_time": now - 20},
        )
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 1  # Only now - 50
        assert errors[0]["symbol"] == "BTC/USDT:USDT"

    def test_error_history_combined_filters(self, client_with_errors):
        """GET /api/error-history combines multiple filters."""
        client, _ = client_with_errors
        # invalid_price errors in fixed_spread strategy
        resp = client.get(
            "/api/error-history",
            params={"error_type": "invalid_price", "strategy_type": "fixed_spread"},
        )
        assert resp.status_code == 200
        errors = resp.json()

        assert len(errors) == 2
        for err in errors:
            assert err["type"] == "invalid_price"
            assert err["strategy_type"] == "fixed_spread"

    def test_error_history_no_match(self, client_with_errors):
        """GET /api/error-history returns empty list when no matches."""
        client, _ = client_with_errors
        resp = client.get(
            "/api/error-history",
            params={"symbol": "DOGE/USDT:USDT"},
        )
        assert resp.status_code == 200
        errors = resp.json()
        assert errors == []

    def test_error_history_empty_when_no_errors(self, monkeypatch):
        """GET /api/error-history returns empty list when error_history is empty."""
        strategy = DummyStrategy(spread=0.002, quantity=0.1, leverage=3)
        dummy_bot = DummyBotEngine(strategy=strategy, orders=[], errors=[])

        monkeypatch.setattr(server, "bot_engine", dummy_bot)
        monkeypatch.setattr(server, "is_running", False)

        client = TestClient(server.app)
        resp = client.get("/api/error-history")
        assert resp.status_code == 200
        assert resp.json() == []
