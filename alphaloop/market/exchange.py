import logging
import os
import time

import ccxt
import certifi
from ccxt import (
    AuthenticationError,
    ExchangeError,
    InsufficientFunds,
    InvalidOrder,
    NetworkError,
    OrderNotFound,
    RateLimitExceeded,
)

from alphaloop.core.config import API_KEY, API_SECRET, LEVERAGE, SYMBOL

logger = logging.getLogger(__name__)


class BinanceClient:
    def __init__(self):
        self.exchange = ccxt.binanceusdm(
            {
                "apiKey": API_KEY,
                "secret": API_SECRET,
                "enableRateLimit": True,
                "verbose": True,
                "options": {
                    "defaultType": "future",
                },
            }
        )
        # Ensure TLS verification uses an accessible CA bundle (e.g., when system certs are restricted)
        ca_bundle = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE", ca_bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)
        if hasattr(self.exchange, "session"):
            self.exchange.session.verify = ca_bundle
        # Some ccxt mocks used in tests may not fully implement mapping protocol for `has`,
        # so guard this access to avoid TypeError while keeping real behaviour unchanged.
        try:
            if hasattr(self.exchange, "has") and isinstance(
                getattr(self.exchange, "has"), dict
            ):
                self.exchange.has["fetchCurrencies"] = False
        except TypeError:
            # In test environments `has` can be a Mock; safe to ignore this optimisation.
            pass
        # self.exchange.set_sandbox_mode(True)  # Deprecated in recent CCXT

        # Manually override URLs for Testnet
        self.exchange.urls["api"] = {
            "fapiPublic": "https://testnet.binancefuture.com/fapi/v1",
            "fapiPrivate": "https://testnet.binancefuture.com/fapi/v1",
            "fapiPrivateV2": "https://testnet.binancefuture.com/fapi/v2",
            "fapiPrivateV3": "https://testnet.binancefuture.com/fapi/v1",
            "public": "https://testnet.binancefuture.com/fapi/v1",
            "private": "https://testnet.binancefuture.com/fapi/v1",
            "sapi": "https://testnet.binancefuture.com/fapi/v1",
        }
        self.exchange.urls["test"] = {
            "fapiPublic": "https://testnet.binancefuture.com/fapi/v1",
            "fapiPrivate": "https://testnet.binancefuture.com/fapi/v1",
            "fapiPrivateV2": "https://testnet.binancefuture.com/fapi/v2",
            "fapiPrivateV3": "https://testnet.binancefuture.com/fapi/v1",
            "public": "https://testnet.binancefuture.com/fapi/v1",
            "private": "https://testnet.binancefuture.com/fapi/v1",
            "sapi": "https://testnet.binancefuture.com/fapi/v1",
        }
        self.symbol = SYMBOL
        self.market = self.exchange.load_markets()[self.symbol]

        # Set initial leverage
        self.set_leverage(LEVERAGE)

        # Track latest errors for UI display
        self.last_order_error = None
        self.last_api_error = None

    def set_symbol(self, symbol):
        """
        Updates the trading symbol.
        """
        try:
            if symbol not in self.exchange.markets:
                self.exchange.load_markets()

            if symbol not in self.exchange.markets:
                logger.error(f"Symbol {symbol} not found in markets.")
                return False

            self.symbol = symbol
            self.market = self.exchange.markets[self.symbol]
            # Clear old errors when switching symbol
            self.last_order_error = None
            self.last_api_error = None
            logger.info(f"Switched exchange client to symbol: {self.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting symbol {symbol}: {e}")
            return False

    def get_leverage(self):
        """
        Gets the current leverage for the symbol.
        """
        try:
            # Fetch position info which includes leverage
            positions = self.exchange.fapiPrivateV2GetPositionRisk(
                {"symbol": self.market["id"]}
            )
            for pos in positions:
                if pos["symbol"] == self.market["id"]:
                    return int(pos["leverage"])
            return None
        except Exception as e:
            logger.error(f"Error fetching leverage: {e}")
            return None

    def set_leverage(self, leverage):
        """
        Sets the leverage for the symbol.
        """
        try:
            result = self.exchange.fapiPrivatePostLeverage(
                {"symbol": self.market["id"], "leverage": leverage}
            )
            logger.info(f"Leverage set to {leverage}x for {self.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting leverage: {e}")
            return False

    def get_max_leverage(self):
        """
        Gets the maximum leverage for the symbol.
        """
        try:
            # Check if limits are available in market info
            if "limits" in self.market and "leverage" in self.market["limits"]:
                return self.market["limits"]["leverage"]["max"]

            # Fallback: fetch leverage brackets
            brackets = self.exchange.fapiPrivateGetLeverageBracket(
                {"symbol": self.market["id"]}
            )
            if brackets:
                # Brackets is a list, usually one item if symbol specified
                # Or list of all symbols.
                for b in brackets:
                    if b["symbol"] == self.market["id"]:
                        # Brackets are usually sorted by leverage, max leverage is the highest bracket's initialLeverage?
                        # Actually brackets define max leverage for notional value ranges.
                        # The highest leverage is usually the first bracket.
                        return b["brackets"][0]["initialLeverage"]
            return 20  # Default fallback
        except Exception as e:
            logger.error(f"Error fetching max leverage: {e}")
            return 20

    def get_symbol_limits(self):
        """
        Gets trading limits for the symbol.
        Returns: dict with minQty, maxQty, stepSize, minNotional
        """
        try:
            limits = {
                "minQty": 0.001,
                "maxQty": 100000,
                "stepSize": 0.001,
                "minNotional": 5.0,
            }

            if "limits" in self.market:
                m_limits = self.market["limits"]
                if "amount" in m_limits:
                    limits["minQty"] = m_limits["amount"]["min"]
                    limits["maxQty"] = m_limits["amount"]["max"]
                if "market" in m_limits:
                    limits["minNotional"] = m_limits["market"]["min"]
                if "cost" in m_limits:
                    # Some exchanges use cost for minNotional
                    if limits["minNotional"] == 5.0:  # If not set by market
                        limits["minNotional"] = m_limits["cost"]["min"]

            if "precision" in self.market:
                if "amount" in self.market["precision"]:
                    limits["stepSize"] = self.market["precision"]["amount"]

            return limits
        except Exception as e:
            logger.error(f"Error fetching symbol limits: {e}")
            return {
                "minQty": 0.001,
                "maxQty": 100000,
                "stepSize": 0.001,
                "minNotional": 5.0,
            }

    def fetch_market_data(self):
        """
        Fetches top 5 order book and calculates mid price.
        Returns: dict with 'bid', 'ask', 'mid', 'timestamp', 'tick_size', 'step_size'
        """
        try:
            orderbook = self.exchange.fetch_order_book(self.symbol, limit=5)
            best_bid = orderbook["bids"][0][0] if orderbook["bids"] else None
            best_ask = orderbook["asks"][0][0] if orderbook["asks"] else None

            if best_bid and best_ask:
                mid_price = (best_bid + best_ask) / 2
            else:
                mid_price = None

            # Get precision info from market
            tick_size = None
            step_size = None
            if self.market:
                # Try to get tick_size from market precision
                if "precision" in self.market:
                    precision = self.market["precision"]
                    if "price" in precision:
                        # Some exchanges return number of decimals, others return the actual tick size
                        price_precision = precision["price"]
                        if isinstance(price_precision, int) and price_precision > 0:
                            tick_size = 10 ** (-price_precision)
                        elif isinstance(price_precision, float) and price_precision < 1:
                            tick_size = price_precision
                    if "amount" in precision:
                        amount_precision = precision["amount"]
                        if isinstance(amount_precision, int) and amount_precision > 0:
                            step_size = 10 ** (-amount_precision)
                        elif (
                            isinstance(amount_precision, float) and amount_precision < 1
                        ):
                            step_size = amount_precision

            return {
                "best_bid": best_bid,
                "best_ask": best_ask,
                "mid_price": mid_price,
                "timestamp": orderbook.get("timestamp", time.time() * 1000),  # ms
                "tick_size": tick_size,
                "step_size": step_size,
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

    def fetch_funding_rate(self):
        """
        Fetches the funding rate signal for the symbol.

        Prefer the **predicted funding rate for the next interval** (Binance "Funding (8h)"),
        and fall back to the last funding rate if prediction is not available.

        Returns: float (e.g., 0.0001 for 0.01%)
        """
        try:
            # Use raw premium index endpoint so we can read both predictedFundingRate and lastFundingRate
            # https://binance-docs.github.io/apidocs/futures/en/#mark-price-and-funded-rate
            info = self.exchange.fapiPublicGetPremiumIndex(
                {"symbol": self.market["id"]}
            )

            predicted = info.get("predictedFundingRate")
            last = info.get("lastFundingRate")

            # Binance returns strings, normalise to float
            predicted_val = float(predicted) if predicted is not None else None
            last_val = float(last) if last is not None else 0.0

            # Strategy should react to the upcoming funding environment,
            # so we use predicted if available, otherwise last as a safe fallback.
            return predicted_val if predicted_val is not None else last_val
        except Exception as e:
            logger.error(f"Error fetching funding rate: {e}")
            return 0.0

    def fetch_funding_rate_for_symbol(self, symbol):
        """
        Fetches the funding rate for a specific symbol without changing current symbol.

        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT:USDT')

        Returns: float (e.g., 0.0001 for 0.01%)
        """
        try:
            # Convert CCXT symbol to Binance format (e.g., 'BTC/USDT:USDT' -> 'BTCUSDT')
            if symbol not in self.exchange.markets:
                self.exchange.load_markets()

            if symbol not in self.exchange.markets:
                logger.error(f"Symbol {symbol} not found in markets")
                return 0.0

            market_id = self.exchange.markets[symbol]["id"]

            info = self.exchange.fapiPublicGetPremiumIndex({"symbol": market_id})

            predicted = info.get("predictedFundingRate")
            last = info.get("lastFundingRate")

            predicted_val = float(predicted) if predicted is not None else None
            last_val = float(last) if last is not None else 0.0

            return predicted_val if predicted_val is not None else last_val
        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol}: {e}")
            return 0.0

    def fetch_bulk_funding_rates(self, symbols):
        """
        Fetches funding rates for multiple symbols efficiently.

        Args:
            symbols: List of trading symbols (e.g., ['BTC/USDT:USDT', 'ETH/USDT:USDT'])

        Returns: dict mapping symbol to funding rate
        """
        try:
            # Fetch all funding rates at once (no symbol parameter = all symbols)
            all_rates = self.exchange.fapiPublicGetPremiumIndex()

            # Ensure markets are loaded
            if not self.exchange.markets:
                self.exchange.load_markets()

            # Build reverse mapping: market_id -> symbol
            id_to_symbol = {
                self.exchange.markets[sym]["id"]: sym
                for sym in symbols
                if sym in self.exchange.markets
            }

            # Extract rates for requested symbols
            result = {}
            for rate_info in all_rates:
                market_id = rate_info.get("symbol")
                if market_id in id_to_symbol:
                    symbol = id_to_symbol[market_id]
                    predicted = rate_info.get("predictedFundingRate")
                    last = rate_info.get("lastFundingRate")

                    predicted_val = float(predicted) if predicted is not None else None
                    last_val = float(last) if last is not None else 0.0

                    result[symbol] = (
                        predicted_val if predicted_val is not None else last_val
                    )

            # Fill in 0.0 for any missing symbols
            for symbol in symbols:
                if symbol not in result:
                    result[symbol] = 0.0

            return result
        except Exception as e:
            logger.error(f"Error fetching bulk funding rates: {e}")
            # Return 0.0 for all symbols on error
            return {symbol: 0.0 for symbol in symbols}

    def fetch_ticker_stats(self):
        """
        Fetches 24h ticker statistics.
        Returns: dict with 'percentage' (24h change %), 'quoteVolume'
        """
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return {
                "percentage": ticker["percentage"],
                "quoteVolume": ticker["quoteVolume"],
            }
        except Exception as e:
            logger.error(f"Error fetching ticker stats: {e}")
            return None

    def fetch_account_data(self):
        """
        Fetches position and balance using V2 Account endpoint.
        Returns: dict with 'position_amt', 'entry_price', 'balance', 'available_balance'
        """
        try:
            # Use V2 Account endpoint which returns both balance and positions
            # This avoids the V1 endpoint issue and reduces API calls
            account_info = self.exchange.fapiPrivateV2GetAccount()

            # Parse Balance
            # walletBalance = Total wallet balance (matches Binance UI)
            # availableBalance = Available for new trades (excludes margin)
            wallet_balance = 0.0
            available_balance = 0.0
            for asset in account_info["assets"]:
                if asset["asset"] == "USDT":
                    wallet_balance = float(asset["walletBalance"])
                    available_balance = float(asset["availableBalance"])
                    break

            # Parse Position
            position_amt = 0.0
            entry_price = 0.0
            liquidation_price = 0.0

            # Note: symbol in account info might be 'ETHUSDT' (no slash)
            # We need to match it against our symbol.
            # CCXT usually handles symbol conversion, but raw API returns raw symbols.
            # ETH/USDT:USDT -> ETHUSDT usually.
            target_symbol = self.market["id"]  # 'ETHUSDT'

            for pos in account_info["positions"]:
                if pos["symbol"] == target_symbol:
                    position_amt = float(pos["positionAmt"])
                    entry_price = float(pos["entryPrice"])
                    # Binance provides liquidation price in position data
                    liquidation_price = float(pos.get("liquidationPrice", 0.0))
                    break

            return {
                "position_amt": position_amt,
                "entry_price": entry_price,
                "balance": wallet_balance,  # Total wallet balance (matches Binance UI)
                "available_balance": available_balance,  # Available for trading
                "liquidation_price": liquidation_price,  # Forced liquidation price
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

        Returns:
            list: Successfully placed orders
        Note:
            Errors are recorded in self.last_order_error (last error encountered).
            Each order is processed independently - if one fails, others continue.
        """
        created_orders = []
        limits = self.get_symbol_limits()
        min_qty = limits["minQty"]
        min_notional = limits["minNotional"]
        step_size = limits["stepSize"]

        # Clear previous error at start
        self.last_order_error = None

        for order in orders:
            try:
                # Validate and correct quantity
                qty = order["quantity"]
                price = order["price"]

                # Validate price is positive to avoid division by zero
                if price is None or price <= 0:
                    logger.error(f"Invalid price {price} for order, skipping...")
                    self.last_order_error = {
                        "type": "invalid_price",
                        "message": f"Invalid price: {price}. Cannot place order.",
                        "symbol": self.symbol,
                        "order": order,
                    }
                    continue

                # Validate quantity is positive
                if qty is None or qty <= 0:
                    logger.error(f"Invalid quantity {qty} for order, skipping...")
                    self.last_order_error = {
                        "type": "invalid_quantity",
                        "message": f"Invalid quantity: {qty}. Cannot place order.",
                        "symbol": self.symbol,
                        "order": order,
                    }
                    continue

                # Check minimum quantity
                if qty < min_qty:
                    logger.warning(f"Quantity {qty} below min {min_qty}, adjusting...")
                    qty = min_qty

                # Check minimum notional
                notional = qty * price
                if notional < min_notional:
                    qty = (min_notional / price) * 1.1  # 10% buffer
                    logger.warning(
                        f"Notional {notional} below min {min_notional}, adjusting qty to {qty}..."
                    )

                # Round to step size
                if step_size:
                    qty = round(qty / step_size) * step_size
                    # Ensure we didn't round down below minimum
                    if qty < min_qty:
                        qty = min_qty

                # Using create_order instead of create_orders (batch) for simplicity in MVP
                # Batch is supported but requires specific structure
                res = self.exchange.create_order(
                    symbol=self.symbol,
                    type="limit",
                    side=order["side"],
                    amount=qty,
                    price=order["price"],
                    params={"timeInForce": "GTX"},  # Post Only
                )
                created_orders.append(res)
                logger.info(
                    f"Placed {order['side']} order at {order['price']} qty {qty}"
                )
                # Clear error on success
                self.last_order_error = None
            except InsufficientFunds as e:
                error_msg = (
                    f"Insufficient balance to place {order['side']} order: {str(e)}"
                )
                logger.error(error_msg)
                # Record error but continue with other orders
                self.last_order_error = {
                    "type": "insufficient_funds",
                    "message": error_msg,
                    "symbol": self.symbol,
                    "order": order,
                    "details": {
                        "side": order.get("side"),
                        "price": order.get("price"),
                        "quantity": order.get("quantity"),
                        "raw_error": str(e),
                    },
                }
                # Continue to next order - don't stop the batch
                continue
            except InvalidOrder as e:
                error_msg = f"Invalid order rejected by Binance: {str(e)}"
                logger.error(error_msg)
                self.last_order_error = {
                    "type": "invalid_order",
                    "message": error_msg,
                    "symbol": self.symbol,
                    "order": order,
                    "details": str(e),
                }
            except RateLimitExceeded as e:
                logger.warning(f"Rate limit hit, skipping order: {e}")
                self.last_order_error = {
                    "type": "rate_limit",
                    "message": f"Rate limit exceeded: {str(e)}",
                    "symbol": self.symbol,
                }
                time.sleep(1)  # Brief pause before continuing
            except NetworkError as e:
                error_msg = f"Network error placing order: {str(e)}"
                logger.error(error_msg)
                self.last_order_error = {
                    "type": "network_error",
                    "message": error_msg,
                    "symbol": self.symbol,
                }
            except ExchangeError as e:
                # Generic Binance API error - log with full details
                error_msg = f"Binance API error placing order: {str(e)}"
                logger.error(error_msg)
                logger.debug(f"Full exception details: {e.__dict__}")
                self.last_order_error = {
                    "type": "exchange_error",
                    "message": error_msg,
                    "symbol": self.symbol,
                    "order": order,
                }
            except Exception as e:
                # Unexpected error - log with traceback
                logger.error(
                    f"Unexpected error placing order {order}: {e}", exc_info=True
                )
                self.last_order_error = {
                    "type": "unknown_error",
                    "message": str(e),
                    "symbol": self.symbol,
                    "order": order,
                }
        return created_orders

    def cancel_orders(self, order_ids):
        """
        Cancels a list of order IDs.
        """
        for oid in order_ids:
            try:
                self.exchange.cancel_order(oid, self.symbol)
                logger.info(f"Canceled order {oid}")
            except OrderNotFound as e:
                logger.warning(
                    f"Order {oid} not found (may be already filled/canceled): {e}"
                )
            except NetworkError as e:
                logger.error(f"Network error canceling order {oid}: {e}")
                self.last_api_error = {
                    "type": "network_error",
                    "message": f"Failed to cancel order {oid}: {str(e)}",
                }
            except ExchangeError as e:
                logger.error(f"Exchange error canceling order {oid}: {e}")
                self.last_api_error = {
                    "type": "exchange_error",
                    "message": f"Failed to cancel order {oid}: {str(e)}",
                }
            except Exception as e:
                logger.error(f"Error canceling order {oid}: {e}", exc_info=True)

    def cancel_all_orders(self):
        """
        Cancels all open orders for the symbol.
        """
        try:
            # Try using ccxt's cancel_all_orders if supported
            if hasattr(self.exchange, "cancel_all_orders"):
                self.exchange.cancel_all_orders(self.symbol)
                logger.info(f"Canceled all orders for {self.symbol}")
            else:
                # Fallback: fetch and cancel one by one
                open_orders = self.fetch_open_orders()
                order_ids = [o["id"] for o in open_orders]
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
                "symbol": self.symbol.replace("/", "").split(":")[
                    0
                ],  # Convert ETH/USDT:USDT -> ETHUSDT
                "incomeType": "REALIZED_PNL",
                "limit": 1000,
            }
            if start_time:
                params["startTime"] = start_time

            income_history = self.exchange.fapiPrivateGetIncome(params)

            # Sum up 'income' field
            total_pnl = sum(float(item["income"]) for item in income_history)
            return total_pnl
        except Exception as e:
            logger.error(f"Error fetching realized PnL: {e}")
            return 0.0

    def fetch_commission(self, start_time=None):
        """
        Fetches total trading commission/fees from transaction history.
        :param start_time: Timestamp in ms to start calculating from.
        :return: Total commission paid (positive number, as fees are deducted)
        """
        try:
            params = {
                "symbol": self.symbol.replace("/", "").split(":")[
                    0
                ],  # Convert ETH/USDT:USDT -> ETHUSDT
                "incomeType": "COMMISSION",
                "limit": 1000,
            }
            if start_time:
                params["startTime"] = start_time

            income_history = self.exchange.fapiPrivateGetIncome(params)

            # Commission is returned as negative values, so we sum and negate
            # to get the total fees paid as a positive number
            total_commission = sum(float(item["income"]) for item in income_history)
            return abs(total_commission)
        except Exception as e:
            logger.error(f"Error fetching commission: {e}")
            return 0.0

    def fetch_pnl_and_fees(self, start_time=None):
        """
        Fetches both realized PnL and commission fees in a single call.
        More efficient than calling fetch_realized_pnl and fetch_commission separately.

        :param start_time: Timestamp in ms to start calculating from.
        :return: dict with 'realized_pnl', 'commission', 'net_pnl'
        """
        try:
            base_params = {
                "symbol": self.symbol.replace("/", "").split(":")[0],
                "limit": 1000,
            }
            if start_time:
                base_params["startTime"] = start_time

            # Fetch REALIZED_PNL
            pnl_params = {**base_params, "incomeType": "REALIZED_PNL"}
            pnl_history = self.exchange.fapiPrivateGetIncome(pnl_params)
            total_pnl = sum(float(item["income"]) for item in pnl_history)

            # Fetch COMMISSION
            comm_params = {**base_params, "incomeType": "COMMISSION"}
            comm_history = self.exchange.fapiPrivateGetIncome(comm_params)
            total_commission = abs(sum(float(item["income"]) for item in comm_history))

            return {
                "realized_pnl": total_pnl,
                "commission": total_commission,
                "net_pnl": total_pnl - total_commission,
            }
        except Exception as e:
            logger.error(f"Error fetching PnL and fees: {e}")
            return {
                "realized_pnl": 0.0,
                "commission": 0.0,
                "net_pnl": 0.0,
            }
