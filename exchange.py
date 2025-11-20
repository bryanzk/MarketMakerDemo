import ccxt
import logging
from config import API_KEY, API_SECRET, SYMBOL, LEVERAGE

logger = logging.getLogger(__name__)

class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binanceusdm({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True,
            'verbose': True,
            'options': {
                'defaultType': 'future',
            }
        })
        self.exchange.has['fetchCurrencies'] = False
        # self.exchange.set_sandbox_mode(True)  # Deprecated in recent CCXT
        
        # Manually override URLs for Testnet
        self.exchange.urls['api'] = {
            'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
            'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
            'fapiPrivateV2': 'https://testnet.binancefuture.com/fapi/v2',
            'fapiPrivateV3': 'https://testnet.binancefuture.com/fapi/v1',
            'public': 'https://testnet.binancefuture.com/fapi/v1',
            'private': 'https://testnet.binancefuture.com/fapi/v1',
            'sapi': 'https://testnet.binancefuture.com/fapi/v1',
        }
        self.exchange.urls['test'] = {
            'fapiPublic': 'https://testnet.binancefuture.com/fapi/v1',
            'fapiPrivate': 'https://testnet.binancefuture.com/fapi/v1',
            'fapiPrivateV2': 'https://testnet.binancefuture.com/fapi/v2',
            'fapiPrivateV3': 'https://testnet.binancefuture.com/fapi/v1',
            'public': 'https://testnet.binancefuture.com/fapi/v1',
            'private': 'https://testnet.binancefuture.com/fapi/v1',
            'sapi': 'https://testnet.binancefuture.com/fapi/v1',
        }
        self.symbol = SYMBOL
        self.market = self.exchange.load_markets()[self.symbol]
        
        # Set initial leverage
        self.set_leverage(LEVERAGE)

    def get_leverage(self):
        """
        Gets the current leverage for the symbol.
        """
        try:
            # Fetch position info which includes leverage
            positions = self.exchange.fapiPrivateV2GetPositionRisk({'symbol': self.market['id']})
            for pos in positions:
                if pos['symbol'] == self.market['id']:
                    return int(pos['leverage'])
            return None
        except Exception as e:
            logger.error(f"Error fetching leverage: {e}")
            return None

    def set_leverage(self, leverage):
        """
        Sets the leverage for the symbol.
        """
        try:
            result = self.exchange.fapiPrivatePostLeverage({
                'symbol': self.market['id'],
                'leverage': leverage
            })
            logger.info(f"Leverage set to {leverage}x for {self.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            return False

    def fetch_market_data(self):
        """
        Fetches top 5 order book and calculates mid price.
        Returns: dict with 'bid', 'ask', 'mid'
        """
        try:
            orderbook = self.exchange.fetch_order_book(self.symbol, limit=5)
            best_bid = orderbook['bids'][0][0] if orderbook['bids'] else None
            best_ask = orderbook['asks'][0][0] if orderbook['asks'] else None
            
            if best_bid and best_ask:
                mid_price = (best_bid + best_ask) / 2
            else:
                mid_price = None

            return {
                'best_bid': best_bid,
                'best_ask': best_ask,
                'mid_price': mid_price
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

    def fetch_account_data(self):
        """
        Fetches position and balance using V2 Account endpoint.
        Returns: dict with 'position_amt', 'entry_price', 'balance'
        """
        try:
            # Use V2 Account endpoint which returns both balance and positions
            # This avoids the V1 endpoint issue and reduces API calls
            account_info = self.exchange.fapiPrivateV2GetAccount()
            
            # Parse Balance
            usdt_balance = 0.0
            for asset in account_info['assets']:
                if asset['asset'] == 'USDT':
                    usdt_balance = float(asset['availableBalance'])
                    break

            # Parse Position
            position_amt = 0.0
            entry_price = 0.0
            
            # Note: symbol in account info might be 'ETHUSDT' (no slash)
            # We need to match it against our symbol.
            # CCXT usually handles symbol conversion, but raw API returns raw symbols.
            # ETH/USDT:USDT -> ETHUSDT usually.
            target_symbol = self.market['id'] # 'ETHUSDT'
            
            for pos in account_info['positions']:
                if pos['symbol'] == target_symbol:
                    position_amt = float(pos['positionAmt'])
                    entry_price = float(pos['entryPrice'])
                    break

            return {
                'position_amt': position_amt,
                'entry_price': entry_price,
                'balance': usdt_balance
            }
        except Exception as e:
            logger.error(f"Error fetching account data: {e}")
            return None

    def fetch_open_orders(self):
        """
        Fetches current open orders for the symbol.
        """
        try:
            return self.exchange.fetch_open_orders(self.symbol)
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    def place_orders(self, orders):
        """
        Places a batch of orders.
        orders: list of dicts {'side': 'buy'/'sell', 'price': float, 'quantity': float}
        """
        created_orders = []
        for order in orders:
            try:
                # Using create_order instead of create_orders (batch) for simplicity in MVP
                # Batch is supported but requires specific structure
                res = self.exchange.create_order(
                    symbol=self.symbol,
                    type='limit',
                    side=order['side'],
                    amount=order['quantity'],
                    price=order['price'],
                    params={'timeInForce': 'GTX'}  # Post Only
                )
                created_orders.append(res)
                logger.info(f"Placed {order['side']} order at {order['price']}")
            except Exception as e:
                logger.error(f"Error placing order {order}: {e}")
        return created_orders

    def cancel_orders(self, order_ids):
        """
        Cancels a list of order IDs.
        """
        for oid in order_ids:
            try:
                self.exchange.cancel_order(oid, self.symbol)
                logger.info(f"Canceled order {oid}")
            except Exception as e:
                logger.error(f"Error canceling order {oid}: {e}")

    def cancel_all_orders(self):
        """
        Cancels all open orders for the symbol.
        """
        try:
            # Try using ccxt's cancel_all_orders if supported
            if hasattr(self.exchange, 'cancel_all_orders'):
                self.exchange.cancel_all_orders(self.symbol)
                logger.info(f"Canceled all orders for {self.symbol}")
            else:
                # Fallback: fetch and cancel one by one
                open_orders = self.fetch_open_orders()
                order_ids = [o['id'] for o in open_orders]
                self.cancel_orders(order_ids)
                logger.info(f"Canceled {len(order_ids)} orders")
        except Exception as e:
            logger.error(f"Error canceling all orders: {e}")

    def fetch_realized_pnl(self, start_time=None):
        """
        Fetches total realized PnL from transaction history.
        :param start_time: Timestamp in ms to start calculating PnL from.
        """
        try:
            # Fetch income history (REALIZED_PNL)
            # Use raw API call since fetch_income might be missing in some ccxt versions
            # Endpoint: /fapi/v1/income
            params = {
                'symbol': self.symbol.replace('/', '').split(':')[0], # Convert ETH/USDT:USDT -> ETHUSDT
                'incomeType': 'REALIZED_PNL',
                'limit': 1000
            }
            if start_time:
                params['startTime'] = start_time
                
            income_history = self.exchange.fapiPrivateGetIncome(params)
            
            # Sum up 'income' field
            total_pnl = sum(float(item['income']) for item in income_history)
            return total_pnl
        except Exception as e:
            logger.error(f"Error fetching realized PnL: {e}")
            return 0.0
