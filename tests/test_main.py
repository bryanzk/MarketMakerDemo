import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from alphaloop.main import AlphaLoop

class TestAlphaLoop:
    """Test cases for AlphaLoop class"""
    
    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_init_success(self, mock_strategy, mock_risk, mock_quant, mock_data, mock_client):
        """Test successful AlphaLoop initialization"""
        # Setup mocks
        mock_client_instance = Mock()
        mock_client_instance.fetch_market_data.return_value = {'mid_price': 100.0}
        mock_client.return_value = mock_client_instance
        
        mock_data.return_value = Mock()
        mock_quant.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_strategy.return_value = Mock()
        
        # Create engine
        engine = AlphaLoop()
        
        # Verify
        # Verify
        assert engine.get_status()['active'] is True # active is hardcoded to True in main.py
        assert engine.get_status()['error'] is None
        assert engine.exchange is not None
        assert engine.data is not None
        assert engine.quant is not None
        assert engine.risk is not None
        assert engine.strategy is not None
        
    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_run_cycle_flow(self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls):
        """Test the main execution cycle flow"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        mock_client.fetch_market_data.return_value = {'mid_price': 100.0} # Fixed key
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = []
        mock_client_cls.return_value = mock_client
        
        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {'volatility': 0.01}
        mock_data_cls.return_value = mock_data
        
        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = {'spread': 0.02}
        mock_quant_cls.return_value = mock_quant
        
        mock_risk = Mock()
        mock_risk.validate_proposal.return_value = (True, "Approved")
        mock_risk_cls.return_value = mock_risk
        
        mock_strategy = Mock()
        mock_strategy.spread = 0.01
        mock_strategy.calculate_target_orders.return_value = [{'side': 'buy', 'price': 99, 'quantity': 1}]
        mock_strategy_cls.return_value = mock_strategy
        
        engine = AlphaLoop()
        
        # Run one cycle manually
        engine.run_cycle()
        
        # Verify flow
        mock_client.fetch_market_data.assert_called()
        mock_data.ingest_data.assert_called()
        mock_quant.analyze_and_propose.assert_called()
        mock_risk.validate_proposal.assert_called()
        mock_strategy.calculate_target_orders.assert_called()
        mock_client.place_orders.assert_called()

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_risk_rejection(self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls):
        """Test that risk rejection prevents strategy update"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_market_data.return_value = {'mid_price': 100.0} # Needed to proceed
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = []
        mock_client_cls.return_value = mock_client
        
        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {'volatility': 0.01, 'sharpe_ratio': 1.5}
        mock_data_cls.return_value = mock_data
        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = {'spread': 0.05} # High spread
        mock_quant_cls.return_value = mock_quant
        
        mock_risk = Mock()
        mock_risk.validate_proposal.return_value = (False, "Spread too high")
        mock_risk_cls.return_value = mock_risk
        
        mock_strategy = Mock()
        mock_strategy.spread = 0.01
        mock_strategy.calculate_target_orders.return_value = [] # Return empty list to be iterable
        mock_strategy_cls.return_value = mock_strategy
        
        engine = AlphaLoop()
        engine.run_cycle()
        
        # Verify
        mock_risk.validate_proposal.assert_called()
        # Strategy spread should NOT have changed (mock object attribute wouldn't change automatically, 
        # but we can check that we didn't log "Applying new config" or similar if we could spy on logger)
        # Better: check that alert was set
        assert engine.alert is not None
        assert "Risk Rejection" in engine.alert['message']

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_set_symbol(self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls):
        """Test switching trading pair"""
        mock_client = Mock()
        mock_client.set_symbol.return_value = True
        mock_client_cls.return_value = mock_client
        
        engine = AlphaLoop()
        result = engine.set_symbol("BTC/USDT:USDT")
        
        assert result is True
        mock_client.set_symbol.assert_called_with("BTC/USDT:USDT")


class TestErrorHistory:
    """Test cases for error_history tracking in AlphaLoop"""

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_error_history_initialized_empty(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that error_history is initialized as empty deque"""
        mock_client_cls.return_value = Mock()
        mock_data_cls.return_value = Mock()
        mock_quant_cls.return_value = Mock()
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        engine = AlphaLoop()

        assert hasattr(engine, "error_history")
        assert len(engine.error_history) == 0
        assert engine.error_history.maxlen == 200

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_error_history_captures_order_error(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that order errors are captured in error_history during run_cycle"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.return_value = {
            "mid_price": 2000.0,
            "best_bid": 1999.0,
            "best_ask": 2001.0,
            "timestamp": time.time() * 1000,
        }
        mock_client.fetch_funding_rate.return_value = 0.0001
        mock_client.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "entry_price": 0.0,
            "balance": 1000.0,
        }
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = [
            {"id": "ord1", "side": "buy", "price": 1999.0, "amount": 0.01}
        ]
        # Simulate an order error
        mock_client.last_order_error = {
            "type": "invalid_price",
            "message": "Invalid price: None",
            "symbol": "ETH/USDT:USDT",
        }
        mock_client_cls.return_value = mock_client

        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {"volatility": 0.01, "sharpe_ratio": 1.5}
        mock_data_cls.return_value = mock_data

        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = None  # No proposal
        mock_quant_cls.return_value = mock_quant

        mock_risk = Mock()
        mock_risk_cls.return_value = mock_risk

        mock_strategy = Mock()
        mock_strategy.spread = 0.002
        mock_strategy.calculate_target_orders.return_value = [
            {"side": "buy", "price": 1999.0, "quantity": 0.01}
        ]
        mock_strategy_cls.return_value = mock_strategy

        engine = AlphaLoop()
        engine.run_cycle()

        # Verify error was captured
        assert len(engine.error_history) == 1
        error = engine.error_history[0]
        assert error["type"] == "invalid_price"
        assert error["symbol"] == "ETH/USDT:USDT"
        assert "timestamp" in error
        assert "message" in error

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_error_history_includes_strategy_type(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that error_history entries include strategy_type"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.return_value = {
            "mid_price": 2000.0,
            "best_bid": 1999.0,
            "best_ask": 2001.0,
            "timestamp": time.time() * 1000,
        }
        mock_client.fetch_funding_rate.return_value = 0.0001
        mock_client.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "entry_price": 0.0,
            "balance": 1000.0,
        }
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = [{"id": "ord1", "side": "buy"}]
        mock_client.last_order_error = {
            "type": "insufficient_funds",
            "message": "No balance",
            "symbol": "ETH/USDT:USDT",
        }
        mock_client_cls.return_value = mock_client

        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {}
        mock_data_cls.return_value = mock_data

        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = None
        mock_quant_cls.return_value = mock_quant

        mock_risk = Mock()
        mock_risk_cls.return_value = mock_risk

        mock_strategy = Mock()
        mock_strategy.spread = 0.002
        mock_strategy.calculate_target_orders.return_value = [
            {"side": "buy", "price": 1999.0, "quantity": 0.01}
        ]
        mock_strategy_cls.return_value = mock_strategy

        engine = AlphaLoop()
        engine.run_cycle()

        # Verify strategy_type is in error
        assert len(engine.error_history) == 1
        error = engine.error_history[0]
        assert "strategy_type" in error
        assert error["strategy_type"] == "fixed_spread"

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_error_history_no_error_when_order_succeeds(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that error_history is not updated when orders succeed"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.return_value = {
            "mid_price": 2000.0,
            "best_bid": 1999.0,
            "best_ask": 2001.0,
            "timestamp": time.time() * 1000,
        }
        mock_client.fetch_funding_rate.return_value = 0.0001
        mock_client.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "entry_price": 0.0,
            "balance": 1000.0,
        }
        mock_client.fetch_open_orders.return_value = []
        mock_client.place_orders.return_value = [{"id": "ord1", "side": "buy"}]
        mock_client.last_order_error = None  # No error
        mock_client_cls.return_value = mock_client

        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {}
        mock_data_cls.return_value = mock_data

        mock_quant = Mock()
        mock_quant.analyze_and_propose.return_value = None
        mock_quant_cls.return_value = mock_quant

        mock_risk = Mock()
        mock_risk_cls.return_value = mock_risk

        mock_strategy = Mock()
        mock_strategy.spread = 0.002
        mock_strategy.calculate_target_orders.return_value = [
            {"side": "buy", "price": 1999.0, "quantity": 0.01}
        ]
        mock_strategy_cls.return_value = mock_strategy

        engine = AlphaLoop()
        engine.run_cycle()

        # Verify no error was captured
        assert len(engine.error_history) == 0

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_refresh_data_failure_sets_alert(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that refresh_data failure sets an error alert and updates stage"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        # Return None to simulate refresh failure
        mock_client.fetch_market_data.return_value = None
        mock_client_cls.return_value = mock_client

        mock_data_cls.return_value = Mock()
        mock_quant_cls.return_value = Mock()
        mock_risk_cls.return_value = Mock()
        mock_strategy_cls.return_value = Mock()

        engine = AlphaLoop()
        engine.run_cycle()

        # Verify alert was set
        assert engine.alert is not None
        assert engine.alert["type"] == "error"
        assert "refresh" in engine.alert["message"].lower() or "data" in engine.alert["message"].lower()
        # Verify stage indicates failure
        assert "refresh failed" in engine.current_stage.lower() or "idle" in engine.current_stage.lower()

    @patch('alphaloop.main.BinanceClient')
    @patch('alphaloop.main.DataAgent')
    @patch('alphaloop.main.QuantAgent')
    @patch('alphaloop.main.RiskAgent')
    @patch('alphaloop.main.FixedSpreadStrategy')
    def test_cycle_exception_records_error_and_sets_alert(
        self, mock_strategy_cls, mock_risk_cls, mock_quant_cls, mock_data_cls, mock_client_cls
    ):
        """Test that exceptions in run_cycle are recorded in error_history and alert is set"""
        # Setup mocks
        mock_client = Mock()
        mock_client.symbol = "ETH/USDT:USDT"
        mock_client.fetch_market_data.return_value = {
            "mid_price": 2000.0,
            "best_bid": 1999.0,
            "best_ask": 2001.0,
            "timestamp": time.time() * 1000,
        }
        mock_client.fetch_funding_rate.return_value = 0.0001
        mock_client.fetch_account_data.return_value = {
            "position_amt": 0.0,
            "entry_price": 0.0,
            "balance": 1000.0,
        }
        mock_client.fetch_open_orders.return_value = []
        # Simulate exception during place_orders
        mock_client.place_orders.side_effect = Exception("Network timeout")
        mock_client_cls.return_value = mock_client

        mock_data = Mock()
        mock_data.calculate_metrics.return_value = {}
        mock_data_cls.return_value = mock_data

        mock_quant_cls.return_value = Mock()
        mock_risk_cls.return_value = Mock()

        mock_strategy = Mock()
        mock_strategy.spread = 0.002
        mock_strategy.calculate_target_orders.return_value = [
            {"side": "buy", "price": 1999.0, "quantity": 0.01}
        ]
        mock_strategy_cls.return_value = mock_strategy

        engine = AlphaLoop()
        engine.run_cycle()

        # Verify cycle_error was recorded
        assert len(engine.error_history) == 1
        error = engine.error_history[0]
        assert error["type"] == "cycle_error"
        assert "Network timeout" in error["message"]
        assert error["symbol"] == "ETH/USDT:USDT"
        assert "strategy_type" in error

        # Verify alert was set
        assert engine.alert is not None
        assert engine.alert["type"] == "error"
        assert "cycle error" in engine.alert["message"].lower() or "network timeout" in engine.alert["message"].lower()
