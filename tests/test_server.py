from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_exchange():
    """Create a mock exchange instance"""
    exchange = Mock()
    exchange.set_leverage = Mock(return_value=True)
    exchange.fetch_pnl_and_fees = Mock(
        return_value={"realized_pnl": 0.0, "commission": 0.0, "net_pnl": 0.0}
    )
    exchange.fetch_account_data = Mock(return_value={"balance": 10000.0})
    exchange.get_symbol_limits = Mock(
        return_value={
            "minQty": 0.001,
            "maxQty": 100.0,
            "stepSize": 0.001,
            "minNotional": 5.0,
        }
    )
    exchange.last_order_error = None
    return exchange


@pytest.fixture
def mock_strategy_instance(mock_exchange):
    """Create a mock strategy instance"""
    instance = Mock()
    instance.exchange = mock_exchange
    instance.use_real_exchange = True
    instance.strategy = Mock()
    instance.strategy.spread = 0.002
    instance.strategy.quantity = 0.02
    instance.strategy.leverage = 5
    instance.strategy.skew_factor = 100.0
    type(instance.strategy).__name__ = "FixedSpreadStrategy"
    instance.strategy_type = "fixed_spread"
    instance.running = False
    instance.alert = None
    instance.refresh_data = Mock(return_value=True)
    instance.get_status = Mock(
        return_value={
            "symbol": "ETH/USDT:USDT",
            "mid_price": 3000.0,
            "position": 0.1,
            "pnl": 5.0,
        }
    )
    return instance


@pytest.fixture
def mock_bot(mock_strategy_instance):
    """Create a mock bot_engine instance with new architecture"""
    mock = MagicMock()
    mock.get_status.return_value = {
        "symbol": "ETH/USDT:USDT",
        "mid_price": 3000.0,
        "position": 0.1,
        "balance": 10000.0,
        "orders": [],
        "pnl": 5.0,
        "leverage": 5,
        "active": False,
        "error": None,
        "strategy_instances": {"default": mock_strategy_instance.get_status()},
        "strategy_count": 1,
    }
    mock.start = Mock()
    mock.stop = Mock()
    mock.alert = None
    mock.current_stage = "Idle"

    # Legacy strategy reference
    mock.strategy = mock_strategy_instance.strategy
    type(mock.strategy).__name__ = "FixedSpreadStrategy"

    # Strategy instances (new architecture)
    mock.strategy_instances = {"default": mock_strategy_instance}

    mock.set_symbol = Mock(return_value=True)
    mock.add_strategy_instance = Mock(return_value=True)

    # Agents
    mock.data = Mock()
    mock.data.calculate_metrics.return_value = {}
    mock.data.trade_history = []

    mock.risk = Mock()
    mock.risk.validate_proposal.return_value = (True, "Approved")
    mock.risk.risk_limits = {"MIN_SPREAD": 0.001, "MAX_SPREAD": 0.05}

    mock.order_history = []
    mock.error_history = []

    return mock


class TestServer:
    """Test cases for FastAPI server endpoints"""

    def test_root_endpoint(self, mock_bot, mock_exchange):
        """Test that root endpoint returns HTML"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)
            response = client.get("/")

            assert response.status_code == 200
            assert "text/html" in response.headers["content-type"]

    def test_get_status_bot_stopped(self, mock_bot, mock_exchange):
        """Test /api/status when bot is stopped"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ), patch("server.is_running", False):
            from server import app

            client = TestClient(app)

            response = client.get("/api/status")

            assert response.status_code == 200
            data = response.json()
            assert data["symbol"] == "ETH/USDT:USDT"
            assert data["active"] is False

    def test_get_status_bot_running(self, mock_bot, mock_exchange):
        """Test /api/status when bot is running"""
        mock_bot.get_status.return_value = {
            "symbol": "ETH/USDT:USDT",
            "mid_price": 3000.0,
            "position": 0.1,
            "balance": 10000.0,
            "orders": [],
            "pnl": 5.0,
            "leverage": 5,
            "active": True,
            "error": None,
            "strategy_instances": {},
            "strategy_count": 1,
        }

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ), patch("server.is_running", True):
            from server import app

            client = TestClient(app)

            response = client.get("/api/status")

            assert response.status_code == 200
            data = response.json()
            assert data["active"] is True

    def test_get_status_with_error(self, mock_bot, mock_exchange):
        """Test /api/status when there's an error"""
        mock_bot.get_status.return_value["error"] = "Connection failed"

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.get("/api/status")

            assert response.status_code == 200
            data = response.json()
            assert data["error"] == "Connection failed"

    def test_control_start_success(self, mock_bot, mock_exchange):
        """Test POST /api/control with action=start"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/control?action=start")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "started"

    def test_control_stop_success(self, mock_bot, mock_exchange):
        """Test POST /api/control with action=stop"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/control?action=stop")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "stopped"

    def test_control_invalid_action(self, mock_bot, mock_exchange):
        """Test POST /api/control with invalid action"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/control?action=invalid")

            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_update_config_success(self, mock_bot, mock_exchange):
        """Test POST /api/config with valid parameters"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            payload = {"spread": 0.5, "quantity": 0.05}  # 0.5% in UI

            response = client.post("/api/config", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            # Verify spread was converted from percentage to decimal
            assert mock_bot.strategy.spread == 0.005  # 0.5% -> 0.005
            assert mock_bot.strategy.quantity == 0.05

    def test_update_config_scopes_to_target_strategy(self, mock_bot, mock_exchange):
        """Ensure updating one strategy instance does not mutate the default instance"""
        funding_instance = Mock()
        funding_instance.strategy = Mock()
        funding_instance.strategy.spread = 0.001
        funding_instance.strategy.quantity = 0.01
        funding_instance.strategy.skew_factor = 50.0
        funding_instance.strategy_type = "funding_rate"
        funding_instance.strategy_id = "funding_rate"
        mock_bot.strategy_instances["funding_rate"] = funding_instance

        original_default_spread = mock_bot.strategy.spread

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            payload = {
                "spread": 0.3,
                "quantity": 0.02,
                "strategy_type": "funding_rate",
                "strategy_id": "funding_rate",
            }

            response = client.post("/api/config", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            assert funding_instance.strategy.spread == 0.003
            assert funding_instance.strategy.quantity == 0.02
            # Default strategy should remain unchanged
            assert mock_bot.strategy.spread == original_default_spread

    def test_update_leverage_success(self, mock_bot, mock_exchange):
        """Test POST /api/leverage with valid value"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/leverage?leverage=10")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            assert data["leverage"] == 10
            mock_exchange.set_leverage.assert_called_with(10)

    def test_update_leverage_too_low(self, mock_bot, mock_exchange):
        """Test POST /api/leverage with value below range"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/leverage?leverage=0")

            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "1 and 125" in data["error"]

    def test_update_leverage_too_high(self, mock_bot, mock_exchange):
        """Test POST /api/leverage with value above range"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/leverage?leverage=150")

            assert response.status_code == 200
            data = response.json()
            assert "error" in data
            assert "1 and 125" in data["error"]

    def test_update_leverage_exchange_error(self, mock_bot, mock_exchange):
        """Test POST /api/leverage when exchange returns error"""
        mock_exchange.set_leverage.return_value = False

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            response = client.post("/api/leverage?leverage=10")

            # Should return error when set_leverage fails
            assert response.status_code == 200
            data = response.json()
            assert "error" in data

    def test_update_pair_success(self, mock_bot, mock_exchange, mock_strategy_instance):
        """Test POST /api/pair with valid symbol"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            payload = {"symbol": "BTC/USDT:USDT"}

            response = client.post("/api/pair", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "updated"
            assert data["symbol"] == "BTC/USDT:USDT"
            mock_bot.set_symbol.assert_called_with(
                "BTC/USDT:USDT", strategy_id="default"
            )

    def test_update_pair_supports_strategy_id(self, mock_bot, mock_exchange):
        """Test POST /api/pair can target specific strategy instance"""
        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            payload = {"symbol": "BTC/USDT:USDT", "strategy_id": "funding_rate"}

            response = client.post("/api/pair", json=payload)

            assert response.status_code == 200
            mock_bot.set_symbol.assert_called_with(
                "BTC/USDT:USDT", strategy_id="funding_rate"
            )

    def test_update_pair_failure(self, mock_bot, mock_exchange):
        """Test POST /api/pair with invalid symbol"""
        mock_bot.set_symbol.return_value = False

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            from server import app

            client = TestClient(app)

            payload = {"symbol": "INVALID/USDT:USDT"}

            response = client.post("/api/pair", json=payload)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"

    def test_get_performance_stats(self, mock_bot, mock_exchange):
        """Test GET /api/performance endpoint with detailed dashboard metrics"""
        # server.py uses bot_engine.data.trade_history
        mock_bot.data.trade_history = [
            {"pnl": 10.0, "timestamp": 1600000000},
            {"pnl": -5.0, "timestamp": 1600000060},
            {"pnl": 20.0, "timestamp": 1600000120},
        ]
        mock_bot.data.calculate_metrics.return_value = {
            "sharpe_ratio": 1.5,
            "tick_to_trade_latency": 5.0,
            "slippage_bps": 1.2,
            "fill_rate": 0.95,
        }

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            # Set session start time before test trades (1600000000 = 2020-09-13)
            import server

            server.session_start_time_ms = 1500000000 * 1000  # Earlier than test trades

            from server import app

            client = TestClient(app)

            response = client.get("/api/performance")

            assert response.status_code == 200
            data = response.json()

            # Check basic stats
            assert data["total_trades"] == 3
            assert data["realized_pnl"] == 25.0
            assert data["winning_trades"] == 2
            assert data["losing_trades"] == 1
            assert abs(data["win_rate"] - 66.66) < 0.01

            # Check metrics
            assert data["metrics"]["sharpe_ratio"] == 1.5
            assert data["metrics"]["tick_to_trade_latency"] == 5.0

            # Check PnL history structure
            assert len(data["pnl_history"]) == 4  # Initial point + 3 trades
            # Initial point
            assert data["pnl_history"][0][1] == 0
            # Last point
            assert data["pnl_history"][-1][1] == 25.0

    def test_get_performance_with_commission(self, mock_bot, mock_exchange):
        """Test GET /api/performance endpoint includes commission data"""
        mock_bot.data.trade_history = [
            {"pnl": 10.0, "timestamp": 1600000000},
        ]
        mock_bot.data.calculate_metrics.return_value = {}

        # Mock exchange with commission data
        mock_exchange.fetch_pnl_and_fees.return_value = {
            "realized_pnl": 100.0,
            "commission": 2.5,
            "net_pnl": 97.5,
        }

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            # Set session start time before test trades (1600000000 = 2020-09-13)
            import server

            server.session_start_time_ms = 1500000000 * 1000  # Earlier than test trades

            from server import app

            client = TestClient(app)

            response = client.get("/api/performance")

            assert response.status_code == 200
            data = response.json()

            # Check commission fields are present
            assert "commission" in data
            assert "net_pnl" in data
            assert data["commission"] == 2.5
            assert data["net_pnl"] == 97.5
            # realized_pnl should use exchange value
            assert data["realized_pnl"] == 100.0

    def test_get_performance_commission_fallback(self, mock_bot, mock_exchange):
        """Test GET /api/performance falls back gracefully when exchange fails"""
        mock_bot.data.trade_history = [
            {"pnl": 15.0, "timestamp": 1600000000},
        ]
        mock_bot.data.calculate_metrics.return_value = {}

        # Mock exchange that raises exception
        mock_exchange.fetch_pnl_and_fees.side_effect = Exception("API Error")

        with patch("server.bot_engine", mock_bot), patch(
            "server.get_default_exchange", return_value=mock_exchange
        ):
            # Set session start time before test trades (1600000000 = 2020-09-13)
            import server

            server.session_start_time_ms = 1500000000 * 1000  # Earlier than test trades

            from server import app

            client = TestClient(app)

            response = client.get("/api/performance")

            assert response.status_code == 200
            data = response.json()

            # Should still return data with local calculation
            assert data["realized_pnl"] == 15.0
            assert data["commission"] == 0.0
            assert data["net_pnl"] == 15.0
