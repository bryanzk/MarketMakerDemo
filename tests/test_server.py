import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock, patch


@pytest.fixture
def mock_bot():
    """Create a mock bot_engine instance"""
    mock = Mock()
    mock.get_status.return_value = {
        'symbol': 'ETH/USDT:USDT',
        'mid_price': 3000.0,
        'position': 0.1,
        'balance': 10000.0,
        'orders': [],
        'pnl': 5.0,
        'leverage': 5,
        'active': False,
        'error': None
    }
    mock.start = Mock()
    mock.stop = Mock()
    mock.strategy = Mock()
    mock.strategy.spread = 0.002
    mock.strategy.quantity = 0.02
    mock.client = Mock()
    mock.client.set_leverage = Mock(return_value=True)
    mock.switch_pair = Mock(return_value=True)
    mock.performance = Mock()
    mock.performance.get_stats.return_value = {}
    mock.performance.reset = Mock()
    return mock


class TestServer:
    """Test cases for FastAPI server endpoints"""
    
    def test_root_endpoint(self, mock_bot):
        """Test that root endpoint returns HTML"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            response = client.get("/")
            
            assert response.status_code == 200
            assert 'text/html' in response.headers['content-type']
    
    def test_get_status_bot_stopped(self, mock_bot):
        """Test /api/status when bot is stopped"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data['symbol'] == 'ETH/USDT:USDT'
            assert data['active'] is False
    
    def test_get_status_bot_running(self, mock_bot):
        """Test /api/status when bot is running"""
        mock_bot.get_status.return_value['active'] = True
        
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data['active'] is True
    
    def test_get_status_with_error(self, mock_bot):
        """Test /api/status when there's an error"""
        mock_bot.get_status.return_value['error'] = "Connection failed"
        
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data['error'] == "Connection failed"
    
    def test_get_status_no_bot(self):
        """Test /api/status when bot is not initialized"""
        with patch('main.bot_engine', None):
            from server import app
            client = TestClient(app)
            
            response = client.get("/api/status")
            
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
    
    def test_control_start_success(self, mock_bot):
        """Test POST /api/control with action=start"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/control?action=start")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'started'
            mock_bot.start.assert_called_once()
    
    def test_control_stop_success(self, mock_bot):
        """Test POST /api/control with action=stop"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/control?action=stop")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'stopped'
            mock_bot.stop.assert_called_once()
    
    def test_control_invalid_action(self, mock_bot):
        """Test POST /api/control with invalid action"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/control?action=invalid")
            
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
    
    def test_update_config_success(self, mock_bot):
        """Test POST /api/config with valid parameters"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            payload = {
                'spread': 0.5,  # 0.5% in UI
                'quantity': 0.05
            }
            
            response = client.post("/api/config", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'updated'
            # Verify spread was converted from percentage to decimal
            assert mock_bot.strategy.spread == 0.005  # 0.5% -> 0.005
            assert mock_bot.strategy.quantity == 0.05
    
    def test_update_leverage_success(self, mock_bot):
        """Test POST /api/leverage with valid value"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/leverage?leverage=10")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'updated'
            assert data['leverage'] == 10
            mock_bot.client.set_leverage.assert_called_with(10)
    
    def test_update_leverage_too_low(self, mock_bot):
        """Test POST /api/leverage with value below range"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/leverage?leverage=0")
            
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
            assert '1 and 125' in data['error']
    
    def test_update_leverage_too_high(self, mock_bot):
        """Test POST /api/leverage with value above range"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/leverage?leverage=150")
            
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
            assert '1 and 125' in data['error']
    
    def test_update_leverage_exchange_error(self, mock_bot):
        """Test POST /api/leverage when exchange returns error"""
        mock_bot.client.set_leverage.return_value = False
        
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/leverage?leverage=10")
            
            # Should return error when set_leverage fails
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
    
    def test_update_pair_success(self, mock_bot):
        """Test POST /api/pair with valid symbol"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            payload = {'symbol': 'BTC/USDT:USDT'}
            
            response = client.post("/api/pair", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'updated'
            assert data['symbol'] == 'BTC/USDT:USDT'
            mock_bot.switch_pair.assert_called_with('BTC/USDT:USDT')
    
    def test_update_pair_failure(self, mock_bot):
        """Test POST /api/pair with invalid symbol"""
        mock_bot.switch_pair.return_value = False
        
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            payload = {'symbol': 'INVALID/USDT:USDT'}
            
            response = client.post("/api/pair", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert 'error' in data
    
    def test_get_performance_stats(self, mock_bot):
        """Test GET /api/performance endpoint"""
        mock_bot.performance.get_stats.return_value = {
            'total_trades': 10,
            'win_rate': 0.6,
            'total_pnl': 100.0
        }
        
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.get("/api/performance")
            
            assert response.status_code == 200
            data = response.json()
            assert data['total_trades'] == 10
            assert data['win_rate'] == 0.6
    
    def test_reset_performance(self, mock_bot):
        """Test POST /api/performance/reset endpoint"""
        with patch('main.bot_engine', mock_bot):
            from server import app
            client = TestClient(app)
            
            response = client.post("/api/performance/reset")
            
            assert response.status_code == 200
            data = response.json()
            assert data['status'] == 'reset'
            mock_bot.performance.reset.assert_called_once()
