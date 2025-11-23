import pytest
from unittest.mock import Mock, MagicMock, patch
from exchange import BinanceClient


class TestBinanceClient:
    """Test cases for BinanceClient class"""
    
    @patch('exchange.ccxt.binanceusdm')
    def test_init_success(self, mock_binance):
        """Test successful initialization of BinanceClient"""
        # Setup mock
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_binance.return_value = mock_exchange
        
        # Create client
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Verify
        assert client.symbol == 'ETH/USDT:USDT'
        assert client.market['id'] == 'ETHUSDT'
        mock_exchange.load_markets.assert_called_once()
    
    @patch('exchange.ccxt.binanceusdm')
    def test_set_symbol_success(self, mock_binance):
        """Test setting a new symbol successfully"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'},
            'BTC/USDT:USDT': {'id': 'BTCUSDT', 'symbol': 'BTC/USDT:USDT'}
        }
        mock_exchange.markets = mock_exchange.load_markets.return_value
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Change symbol
        result = client.set_symbol('BTC/USDT:USDT')
        
        assert result is True
        assert client.symbol == 'BTC/USDT:USDT'
        assert client.market['id'] == 'BTCUSDT'
    
    @patch('exchange.ccxt.binanceusdm')
    def test_set_symbol_not_found(self, mock_binance):
        """Test setting a symbol that doesn't exist"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.markets = mock_exchange.load_markets.return_value
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        # Try to set invalid symbol
        result = client.set_symbol('INVALID/USDT:USDT')
        
        assert result is False
        assert client.symbol == 'ETH/USDT:USDT'  # Should remain unchanged
    
    @patch('exchange.ccxt.binanceusdm')
    def test_set_symbol_exception(self, mock_binance):
        """Test exception handling in set_symbol"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.markets = {}
        mock_exchange.load_markets.side_effect = Exception("API Error")
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
            # Re-mock after init to test the method
            client.exchange.markets = {}
            client.exchange.load_markets.side_effect = Exception("API Error")
        
        result = client.set_symbol('BTC/USDT:USDT')
        
        assert result is False
    
    @patch('exchange.ccxt.binanceusdm')
    def test_get_leverage_success(self, mock_binance):
        """Test successful leverage retrieval"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateV2GetPositionRisk.return_value = [
            {'symbol': 'ETHUSDT', 'leverage': '10'},
            {'symbol': 'BTCUSDT', 'leverage': '5'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        leverage = client.get_leverage()
        
        assert leverage == 10
    
    @patch('exchange.ccxt.binanceusdm')
    def test_get_leverage_not_found(self, mock_binance):
        """Test leverage retrieval when symbol not in positions"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateV2GetPositionRisk.return_value = [
            {'symbol': 'BTCUSDT', 'leverage': '5'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        leverage = client.get_leverage()
        
        assert leverage is None
    
    @patch('exchange.ccxt.binanceusdm')
    def test_get_leverage_error(self, mock_binance):
        """Test leverage retrieval error handling"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateV2GetPositionRisk.side_effect = Exception("API Error")
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        leverage = client.get_leverage()
        
        assert leverage is None
    
    @patch('exchange.ccxt.binanceusdm')
    def test_set_leverage_success(self, mock_binance):
        """Test successful leverage setting"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivatePostLeverage.return_value = {'leverage': 10}
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        result = client.set_leverage(10)
        
        assert result is True
        mock_exchange.fapiPrivatePostLeverage.assert_called_with({
            'symbol': 'ETHUSDT',
            'leverage': 10
        })
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_order_book_success(self, mock_binance):
        """Test successful orderbook fetch"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fetch_order_book.return_value = {
            'bids': [[3000.0, 10.0], [2999.5, 5.0]],
            'asks': [[3001.0, 8.0], [3001.5, 12.0]]
        }
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        orderbook = client.fetch_order_book()
        
        assert orderbook['bids'][0][0] == 3000.0
        assert orderbook['asks'][0][0] == 3001.0
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_market_data_success(self, mock_binance):
        """Test successful market data extraction"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fetch_order_book.return_value = {
            'bids': [[3000.0, 10.0]],
            'asks': [[3001.0, 8.0]]
        }
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        market_data = client.fetch_market_data()
        
        assert market_data['best_bid'] == 3000.0
        assert market_data['best_ask'] == 3001.0
        assert market_data['mid_price'] == 3000.5
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_market_data_empty_orderbook(self, mock_binance):
        """Test market data extraction with empty orderbook"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fetch_order_book.return_value = {
            'bids': [],
            'asks': []
        }
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        market_data = client.fetch_market_data()
        
        assert market_data == {}
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_account_data_success(self, mock_binance):
        """Test successful account data fetch"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateV2GetAccount.return_value = {
            'totalWalletBalance': '10000.0',
            'availableBalance': '9500.0',
            'positions': [
                {
                    'symbol': 'ETHUSDT',
                    'positionAmt': '0.5',
                    'entryPrice': '3000.0',
                    'unrealizedProfit': '50.0'
                }
            ]
        }
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        account_data = client.fetch_account_data()
        
        assert account_data['balance'] == 10000.0
        assert account_data['available'] == 9500.0
        assert account_data['position'] == 0.5
        assert account_data['entry_price'] == 3000.0
        assert account_data['pnl'] == 50.0
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_account_data_no_position(self, mock_binance):
        """Test account data when no position exists"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateV2GetAccount.return_value = {
            'totalWalletBalance': '10000.0',
            'availableBalance': '10000.0',
            'positions': []
        }
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        account_data = client.fetch_account_data()
        
        assert account_data['position'] == 0.0
        assert account_data['entry_price'] == 0.0
        assert account_data['pnl'] == 0.0
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_open_orders_success(self, mock_binance):
        """Test successful open orders fetch"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fetch_open_orders.return_value = [
            {
                'id': '123',
                'symbol': 'ETH/USDT:USDT',
                'side': 'buy',
                'price': 3000.0,
                'amount': 0.1
            },
            {
                'id': '124',
                'symbol': 'ETH/USDT:USDT',
                'side': 'sell',
                'price': 3010.0,
                'amount': 0.1
            }
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        orders = client.fetch_open_orders()
        
        assert len(orders) == 2
        assert orders[0]['id'] == '123'
        assert orders[1]['side'] == 'sell'
    
    @patch('exchange.ccxt.binanceusdm')
    def test_place_orders_success(self, mock_binance):
        """Test successful order placement"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.create_limit_order.return_value = {'id': '12345'}
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        orders_to_place = [
            {'side': 'buy', 'price': 3000.0, 'quantity': 0.1}
        ]
        
        result = client.place_orders(orders_to_place)
        
        assert result == [{'id': '12345'}]
        mock_exchange.create_limit_order.assert_called_once()
    
    @patch('exchange.ccxt.binanceusdm')
    def test_place_orders_error(self, mock_binance):
        """Test order placement with error"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.create_limit_order.side_effect = Exception("Insufficient balance")
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        orders_to_place = [
            {'side': 'buy', 'price': 3000.0, 'quantity': 0.1}
        ]
        
        result = client.place_orders(orders_to_place)
        
        assert result == []
    
    @patch('exchange.ccxt.binanceusdm')
    def test_cancel_orders_success(self, mock_binance):
        """Test successful order cancellation"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.cancel_order.return_value = {'id': '123', 'status': 'canceled'}
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        order_ids = ['123', '124']
        client.cancel_orders(order_ids)
        
        assert mock_exchange.cancel_order.call_count == 2
    
    @patch('exchange.ccxt.binanceusdm')
    def test_cancel_all_orders_with_method(self, mock_binance):
        """Test cancel_all_orders when exchange has the method"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.cancel_all_orders = Mock()
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        client.cancel_all_orders()
        
        mock_exchange.cancel_all_orders.assert_called_once_with('ETH/USDT:USDT')
    
    @patch('exchange.ccxt.binanceusdm')
    def test_cancel_all_orders_fallback(self, mock_binance):
        """Test cancel_all_orders fallback mechanism"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        # Remove cancel_all_orders method
        delattr(type(mock_exchange), 'cancel_all_orders')
        mock_exchange.fetch_open_orders.return_value = [
            {'id': '123'}, {'id': '124'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        client.cancel_all_orders()
        
        assert mock_exchange.cancel_order.call_count == 2
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_success(self, mock_binance):
        """Test successful realized PnL fetch"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = [
            {'incomeType': 'REALIZED_PNL', 'income': '10.5'},
            {'incomeType': 'REALIZED_PNL', 'income': '5.3'},
            {'incomeType': 'COMMISSION', 'income': '-0.1'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 15.8
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_with_start_time(self, mock_binance):
        """Test realized PnL fetch with start time filter"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = [
            {'incomeType': 'REALIZED_PNL', 'income': '10.5'}
        ]
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        start_time = 1700000000000
        pnl = client.fetch_realized_pnl(start_time=start_time)
        
        mock_exchange.fapiPrivateGetIncome.assert_called_with({
            'symbol': 'ETHUSDT',
            'incomeType': 'REALIZED_PNL',
            'startTime': start_time
        })
        assert pnl == 10.5
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_no_records(self, mock_binance):
        """Test realized PnL fetch with no records"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.return_value = []
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 0.0
    
    @patch('exchange.ccxt.binanceusdm')
    def test_fetch_realized_pnl_error(self, mock_binance):
        """Test realized PnL fetch error handling"""
        mock_exchange = Mock()
        mock_exchange.load_markets.return_value = {
            'ETH/USDT:USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT:USDT'}
        }
        mock_exchange.fapiPrivateGetIncome.side_effect = Exception("API Error")
        mock_binance.return_value = mock_exchange
        
        with patch('exchange.LEVERAGE', 5):
            client = BinanceClient()
        
        pnl = client.fetch_realized_pnl()
        
        assert pnl == 0.0
