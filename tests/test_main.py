import pytest
import time
import threading
from unittest.mock import Mock, MagicMock, patch, PropertyMock
from main import BotEngine


class TestBotEngine:
    """Test cases for BotEngine class"""
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_init_success(self, mock_client, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test successful BotEngine initialization"""
        # Setup mocks
        mock_client.return_value = Mock()
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        # Create engine
        engine = BotEngine()
        
        # Verify
        assert engine.running is False
        assert engine.thread is None
        assert engine.status['active'] is False
        assert engine.status['error'] is None
        assert engine.client is not None
        assert engine.strategy is not None
        assert engine.risk is not None
        assert engine.om is not None
    
    @patch('main.BinanceClient')
    def test_init_failure(self, mock_client):
        """Test BotEngine initialization failure"""
        mock_client.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception):
            BotEngine()
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_start_success(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test successful bot start"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.start()
        
        # Verify
        assert engine.running is True
        assert engine.thread is not None
        assert engine.status['error'] is None
        
        # Cleanup
        engine.stop()
        time.sleep(0.1)
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_start_connection_check_failure(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test bot start with connection check failure"""
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {}  # Empty data
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.start()
        
        # Verify
        assert engine.running is False
        assert engine.status['error'] == "Connection failed"
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_start_connection_exception(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test bot start with connection exception"""
        mock_client = Mock()
        mock_client.fetch_account_data.side_effect = Exception("API Error")
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.start()
        
        # Verify
        assert engine.running is False
        assert "API Error" in engine.status['error']
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_start_already_running(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test preventing double start"""
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.start()
        
        # Try to start again
        engine.start()
        
        # Should still be running with only one thread
        assert engine.running is True
        
        # Cleanup
        engine.stop()
        time.sleep(0.1)
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_stop_success(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test successful bot stop"""
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        mock_client.cancel_all_orders = Mock()
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.start()
        time.sleep(0.1)
        
        engine.stop()
        
        # Verify
        assert engine.running is False
        mock_client.cancel_all_orders.assert_called_once()
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_stop_not_running(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test stop when bot is not running"""
        mock_client_cls.return_value = Mock()
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        engine.stop()
        
        # Should handle gracefully
        assert engine.running is False
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    @patch('main.time.sleep')  # Mock sleep to speed up test
    def test_run_loop_single_iteration(self, mock_sleep, mock_client_cls, mock_strategy_cls, 
                                      mock_risk_cls, mock_om_cls, mock_perf_cls):
        """Test one iteration of the main loop"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {
            'balance': 10000.0, 
            'position': 0.1,
            'entry_price': 3000.0,
            'pnl': 5.0,
            'available': 9500.0
        }
        mock_client.fetch_market_data.return_value = {
            'mid_price': 3005.0,
            'best_bid': 3004.0,
            'best_ask': 3006.0
        }
        mock_client.fetch_open_orders.return_value = []
        mock_client.get_leverage.return_value = 5
        mock_client.fetch_realized_pnl.return_value = 10.0
        mock_client.place_orders.return_value = []
        mock_client.cancel_orders.return_value = None
        mock_client_cls.return_value = mock_client
        
        mock_strategy = Mock()
        mock_strategy.calculate_target_orders.return_value = [
            {'side': 'buy', 'price': 3000.0, 'quantity': 0.1}
        ]
        mock_strategy_cls.return_value = mock_strategy
        
        mock_risk = Mock()
        mock_risk.check_position_limits.return_value = [
            {'side': 'buy', 'price': 3000.0, 'quantity': 0.1}
        ]
        mock_risk_cls.return_value = mock_risk
        
        mock_om = Mock()
        mock_om.sync_orders.return_value = ([], [{'side': 'buy', 'price': 3000.0, 'quantity': 0.1}])
        mock_om_cls.return_value = mock_om
        
        mock_perf = Mock()
        mock_perf.update_position.return_value = None
        mock_perf.get_stats.return_value = {}
        mock_perf_cls.return_value = mock_perf
        
        # Create engine and run for a short time
        engine = BotEngine()
        engine.start()
        time.sleep(0.2)
        engine.stop()
        
        # Verify all major methods were called
        assert mock_client.fetch_market_data.called
        assert mock_client.fetch_account_data.called
        assert mock_strategy.calculate_target_orders.called
        assert mock_risk.check_position_limits.called
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_get_status(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test get_status method"""
        mock_client_cls.return_value = Mock()
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        status = engine.get_status()
        
        # Verify status structure
        assert 'symbol' in status
        assert 'mid_price' in status
        assert 'position' in status
        assert 'balance' in status
        assert 'active' in status
        assert 'error' in status
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    def test_switch_pair_success(self, mock_client_cls, mock_strategy, mock_risk, mock_om, mock_perf):
        """Test switch_pair method"""
        mock_client = Mock()
        mock_client.set_symbol.return_value = True
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        mock_client_cls.return_value = mock_client
        mock_strategy.return_value = Mock()
        mock_risk.return_value = Mock()
        mock_om.return_value = Mock()
        mock_perf.return_value = Mock()
        
        engine = BotEngine()
        
        # Switch symbol
        result = engine.switch_pair('BTC/USDT:USDT')
        
        # Verify
        assert result is True
        mock_client.set_symbol.assert_called_with('BTC/USDT:USDT')
        assert engine.status['symbol'] == 'BTC/USDT:USDT'
    
    @patch('main.PerformanceTracker')
    @patch('main.OrderManager')
    @patch('main.RiskManager')
    @patch('main.FixedSpreadStrategy')
    @patch('main.BinanceClient')
    @patch('main.time.sleep')
    def test_run_loop_exception_handling(self, mock_sleep, mock_client_cls, mock_strategy_cls,
                                        mock_risk_cls, mock_om_cls, mock_perf_cls):
        """Test that exceptions in run loop are caught and bot stops"""
        # Setup mocks
        mock_client = Mock()
        mock_client.fetch_account_data.return_value = {'balance': 10000.0}
        # Make fetch_market_data raise an exception
        mock_client.fetch_market_data.side_effect = Exception("Test error")
        mock_client.cancel_all_orders = Mock()
        mock_client_cls.return_value = mock_client
        
        mock_strategy = Mock()
        mock_strategy_cls.return_value = mock_strategy
        mock_risk = Mock()
        mock_risk_cls.return_value = mock_risk
        mock_om = Mock()
        mock_om_cls.return_value = mock_om
        mock_perf = Mock()
        mock_perf_cls.return_value = mock_perf
        
        # Mock sleep to allow exception to propagate 
        call_count = [0]
        def sleep_side_effect(seconds):
            call_count[0] += 1
            if call_count[0] > 3:
                return
            time.sleep(0.05)
        mock_sleep.side_effect = sleep_side_effect
        
        engine = BotEngine()
        engine.start()
        time.sleep(0.25)
        
        # Verify bot caught exception and stopped
        assert engine.running is False
        # Error should be set
        assert engine.status['error'] is not None
        mock_client.cancel_all_orders.assert_called()
