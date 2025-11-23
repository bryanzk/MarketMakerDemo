import pytest
from unittest.mock import Mock, MagicMock
from alphaloop.market.simulation import MarketSimulator

class TestMarketSimulator:
    def test_init(self):
        mock_strategy = Mock()
        sim = MarketSimulator(mock_strategy)
        assert sim.strategy == mock_strategy
        assert sim.current_price == 2000.0
        assert sim.position == 0.0
        
    def test_generate_market_data(self):
        mock_strategy = Mock()
        sim = MarketSimulator(mock_strategy)
        
        data = sim.generate_market_data()
        
        assert 'mid_price' in data
        assert 'best_bid' in data
        assert 'best_ask' in data
        # assert data['mid_price'] == 2000.0 # Price drifts, so exact match might fail
        
    def test_run_simulation(self):
        mock_strategy = Mock()
        mock_strategy.calculate_target_orders.return_value = [
            {'side': 'buy', 'price': 990, 'quantity': 1.0},
            {'side': 'sell', 'price': 1010, 'quantity': 1.0}
        ]
        
        sim = MarketSimulator(mock_strategy)
        stats = sim.run(steps=10)
        
        assert 'realized_pnl' in stats
        assert 'total_trades' in stats
        assert 'win_rate' in stats
        assert mock_strategy.calculate_target_orders.called
