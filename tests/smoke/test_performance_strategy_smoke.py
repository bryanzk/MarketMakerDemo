import time
from unittest.mock import MagicMock, Mock, patch

from fastapi.testclient import TestClient

import server


def _make_mock_bot_engine() -> MagicMock:
    mock_bot = MagicMock()
    mock_bot.data = MagicMock()
    now = time.time()
    mock_bot.data.trade_history = [
        {
            "pnl": 10.0,
            "timestamp": now - 10,
            "strategy_type": "fixed_spread",
            "strategy_id": "fixed_spread",
            "symbol": "ETH/USDT:USDT",
        },
        {
            "pnl": -5.0,
            "timestamp": now - 5,
            "strategy_type": "funding_rate",
            "strategy_id": "funding_rate",
            "symbol": "ETH/USDT:USDT",
        },
    ]
    mock_bot.data.price_history = []
    mock_bot.data.registry = MagicMock()
    mock_bot.data.registry.calculate_all.return_value = {"sharpe_ratio": 1.0}
    return mock_bot


class TestStrategyPerformanceSmoke:
    """
    Smoke tests for /api/performance/strategy endpoint.
    冒烟测试：/api/performance/strategy 端点。
    """

    def test_smoke_strategy_performance_endpoint_exists(self):
        mock_bot = _make_mock_bot_engine()
        mock_exchange = Mock()

        with patch.object(server, "bot_engine", mock_bot), patch.object(
            server, "get_default_exchange", return_value=mock_exchange
        ):
            client = TestClient(server.app)

            resp = client.get(
                "/api/performance/strategy",
                params={"strategy_type": "fixed_spread"},
            )

            assert resp.status_code == 200
            data = resp.json()

            # Basic structure checks
            assert "realized_pnl" in data
            assert "total_trades" in data
            assert "pnl_history" in data
            assert data["strategy_type"] == "fixed_spread"
