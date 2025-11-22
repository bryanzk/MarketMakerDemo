import pytest
from alphaloop.agents.data import DataAgent
from alphaloop.core.config import METRICS_CONFIG

class TestDataAgent:
    def setup_method(self):
        self.agent = DataAgent()
        
    def test_initialization(self):
        assert len(self.agent.trade_history) == 0
        assert len(self.agent.price_history) == 0
        assert self.agent.registry is not None
        
    def test_ingest_data(self):
        market_data = {'price': 100, 'best_bid': 99, 'best_ask': 101}
        trades = [{'price': 100, 'quantity': 1, 'pnl': 10}]
        
        self.agent.ingest_data(market_data, trades)
        
        assert len(self.agent.price_history) == 1
        assert len(self.agent.trade_history) == 1
        assert self.agent.price_history[0] == 100
        
    def test_calculate_metrics_empty(self):
        metrics = self.agent.calculate_metrics()
        # Should return metrics even if empty, with default values or 0
        assert 'sharpe_ratio' in metrics
        assert metrics['sharpe_ratio'] == 0.0
        
    def test_calculate_metrics_with_data(self):
        # Ingest enough data to calculate metrics
        for i in range(20):
            self.agent.ingest_data({'price': 100}, [{'price': 100, 'quantity': 1, 'pnl': i}])
            
        metrics = self.agent.calculate_metrics()
        assert 'sharpe_ratio' in metrics
        assert 'slippage_bps' in metrics
