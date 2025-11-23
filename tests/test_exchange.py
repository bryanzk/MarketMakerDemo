import pytest
from unittest.mock import Mock, MagicMock, patch
from alphaloop.market.exchange import BinanceClient


class TestBinanceClient:
    """Test cases for BinanceClient class"""
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_init_success(self, mock_binance):
        """Test successful initialization of BinanceClient"""
        # Setup mock
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_binance.return_value = mock_exchange
        
        # Create client
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Verify
        assert client.symbol == 'ETH/USDT:USDT'
        assert client.market['id'] == 'ETHUSDT'
        mock_exchange.load_markets.assert_called_once()
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_set_symbol_success(self, mock_binance):
        """Test setting a new symbol successfully"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'},
            'BTC/USDT:USDT': {'id': 'BTCUSDT', 'symbol': 'BTC/USDT:USDT'}
        }
        mock_exchange.markets = mock_exchange.load_markets.return_value
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Change symbol
        result = client.set_symbol('BTC/USDT:USDT')
        
        assert result is True
        assert client.symbol == 'BTC/USDT:USDT'
        assert client.market['id'] == 'BTCUSDT'
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_set_symbol_not_found(self, mock_binance):
        """Test setting a symbol that doesn't exist"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.markets = mock_exchange.load_markets.return_value
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Try to set invalid symbol
        result = client.set_symbol('INVALID/USDT:USDT')
        
        assert result is False
        assert client.symbol == 'ETH/USDT:USDT'  # Should remain unchanged
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_set_symbol_exception(self, mock_binance):
        """Test exception handling in set_symbol"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.markets = {}
        # Don't set side_effect here, it will break init
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
            # Set side effect after init
            client.exchange.load_markets.side_effect = Exception("API Error")
            # Ensure symbol is not in markets so it triggers load_markets
            client.exchange.markets = {}
        
        result = client.set_symbol('BTC/USDT:USDT')
        
        assert result is False

    # Removed test_fetch_order_book_success as method does not exist

    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_fetch_market_data_empty_orderbook(self, mock_binance):
        """Test market data extraction with empty orderbook"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fetch_order_book.return_value = {
            'bids': [],
            'asks': []
        }
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        market_data = client.fetch_market_data()
        
        assert market_data['best_bid'] is None
        assert market_data['best_ask'] is None
        assert market_data['mid_price'] is None
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_success(self, mock_binance):
        """Test successful realized PnL fetch"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = [
            {'incomeType': 'REALIZED_PNL', 'income': '10.5'},
            {'incomeType': 'REALIZED_PNL', 'income': '5.3'}
            # Removed COMMISSION as API filters it out
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 15.8
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_with_start_time(self, mock_binance):
        """Test realized PnL fetch with start time filter"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = [
            {'incomeType': 'REALIZED_PNL', 'income': '10.5'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        start_time = 1700000000000
        pnl = client.fetch_realized_pnl(start_time=start_time)
        
        mock_exchange.fapiPrivateGetIncome.assert_called_with({
            'symbol': 'ETHUSDT',
            'incomeType': 'REALIZED_PNL',
            'startTime': start_time,
            'limit': 1000
        })
        assert pnl == 10.5
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_no_records(self, mock_binance):
        """Test realized PnL fetch with no records"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = []
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 0.0
    
    @patch('alphaloop.market.exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_error(self, mock_binance):
        """Test realized PnL fetch error handling"""
        mock_exchange = MagicMock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.side_effect = Exception("API Error")
        mock_binance.return_value = mock_exchange
        
        with patch('alphaloop.market.exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 0.0
