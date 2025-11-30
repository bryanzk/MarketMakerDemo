"""
Exchange Client Module / 交易所客户端模块

Binance Futures exchange client using CCXT.
使用 CCXT 的币安期货交易所客户端。

Owner: Agent TRADING
"""

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

from src.shared.config import API_KEY, API_SECRET, LEVERAGE, SYMBOL

logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance Futures exchange client."""

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
        # Ensure TLS verification uses an accessible CA bundle
        ca_bundle = certifi.where()
        os.environ.setdefault("SSL_CERT_FILE", ca_bundle)
        os.environ.setdefault("REQUESTS_CA_BUNDLE", ca_bundle)
        if hasattr(self.exchange, "session"):
            self.exchange.session.verify = ca_bundle

        # Guard has access for test mocks
        try:
            if hasattr(self.exchange, "has") and isinstance(
                getattr(self.exchange, "has"), dict
            ):
                self.exchange.has["fetchCurrencies"] = False
        except TypeError:
            pass

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
        """Updates the trading symbol."""
        try:
            if symbol not in self.exchange.markets:
                self.exchange.load_markets()

            if symbol not in self.exchange.markets:
                logger.error(f"Symbol {symbol} not found in markets.")
                return False

            self.symbol = symbol
            self.market = self.exchange.markets[self.symbol]
            self.last_order_error = None
            self.last_api_error = None
            logger.info(f"Switched exchange client to symbol: {self.symbol}")
            return True
        except Exception as e:
            logger.error(f"Error setting symbol {symbol}: {e}")
            return False

    def get_leverage(self):
        """Gets the current leverage for the symbol."""
        try:
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
        """Sets the leverage for the symbol."""
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
        """Gets the maximum leverage for the symbol."""
        try:
            if "limits" in self.market and "leverage" in self.market["limits"]:
                return self.market["limits"]["leverage"]["max"]

            brackets = self.exchange.fapiPrivateGetLeverageBracket(
                {"symbol": self.market["id"]}
            )
            if brackets:
                for b in brackets:
                    if b["symbol"] == self.market["id"]:
                        return b["brackets"][0]["initialLeverage"]
            return 20
        except Exception as e:
            logger.error(f"Error fetching max leverage: {e}")
            return 20

    def get_symbol_limits(self):
        """Gets trading limits for the symbol."""
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
                    if limits["minNotional"] == 5.0:
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
        """Fetches top 5 order book and calculates mid price."""
        try:
            orderbook = self.exchange.fetch_order_book(self.symbol, limit=5)
            best_bid = orderbook["bids"][0][0] if orderbook["bids"] else None
            best_ask = orderbook["asks"][0][0] if orderbook["asks"] else None

            if best_bid and best_ask:
                mid_price = (best_bid + best_ask) / 2
            else:
                mid_price = None

            tick_size = None
            step_size = None
            if self.market:
                if "precision" in self.market:
                    precision = self.market["precision"]
                    if "price" in precision:
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
                "timestamp": orderbook.get("timestamp", time.time() * 1000),
                "tick_size": tick_size,
                "step_size": step_size,
            }
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return None

    def fetch_funding_rate(self):
        """Fetches the funding rate signal for the symbol."""
        try:
            info = self.exchange.fapiPublicGetPremiumIndex(
                {"symbol": self.market["id"]}
            )

            predicted = info.get("predictedFundingRate")
            last = info.get("lastFundingRate")

            predicted_val = float(predicted) if predicted is not None else None
            last_val = float(last) if last is not None else 0.0

            return predicted_val if predicted_val is not None else last_val
        except Exception as e:
            logger.error(f"Error fetching funding rate: {e}")
            return 0.0

    def fetch_funding_rate_for_symbol(self, symbol):
        """Fetches the funding rate for a specific symbol."""
        try:
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
        """Fetches funding rates for multiple symbols efficiently."""
        try:
            all_rates = self.exchange.fapiPublicGetPremiumIndex()

            if not self.exchange.markets:
                self.exchange.load_markets()

            id_to_symbol = {
                self.exchange.markets[sym]["id"]: sym
                for sym in symbols
                if sym in self.exchange.markets
            }

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

            for symbol in symbols:
                if symbol not in result:
                    result[symbol] = 0.0

            return result
        except Exception as e:
            logger.error(f"Error fetching bulk funding rates: {e}")
            return {symbol: 0.0 for symbol in symbols}

    def fetch_ticker_stats(self):
        """Fetches 24h ticker statistics."""
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
        """Fetches position and balance using V2 Account endpoint."""
        try:
            account_info = self.exchange.fapiPrivateV2GetAccount()

            wallet_balance = 0.0
            available_balance = 0.0
            for asset in account_info["assets"]:
                if asset["asset"] == "USDT":
                    wallet_balance = float(asset["walletBalance"])
                    available_balance = float(asset["availableBalance"])
                    break

            position_amt = 0.0
            entry_price = 0.0
            liquidation_price = 0.0

            target_symbol = self.market["id"]

            for pos in account_info["positions"]:
                if pos["symbol"] == target_symbol:
                    position_amt = float(pos["positionAmt"])
                    entry_price = float(pos["entryPrice"])
                    liquidation_price = float(pos.get("liquidationPrice", 0.0))
                    break

            return {
                "position_amt": position_amt,
                "entry_price": entry_price,
                "balance": wallet_balance,
                "available_balance": available_balance,
                "liquidation_price": liquidation_price,
            }
        except Exception as e:
            logger.error(f"Error fetching account data: {e}")
            return None

    def fetch_open_orders(self):
        """Fetches current open orders for the symbol."""
        try:
            return self.exchange.fetch_open_orders(self.symbol)
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    def place_orders(self, orders):
        """Places a batch of orders."""
        created_orders = []
        limits = self.get_symbol_limits()
        min_qty = limits["minQty"]
        min_notional = limits["minNotional"]
        step_size = limits["stepSize"]

        self.last_order_error = None

        for order in orders:
            try:
                qty = order["quantity"]
                price = order["price"]

                if price is None or price <= 0:
                    logger.error(f"Invalid price {price} for order, skipping...")
                    self.last_order_error = {
                        "type": "invalid_price",
                        "message": f"Invalid price: {price}. Cannot place order.",
                        "symbol": self.symbol,
                        "order": order,
                    }
                    continue

                if qty is None or qty <= 0:
                    logger.error(f"Invalid quantity {qty} for order, skipping...")
                    self.last_order_error = {
                        "type": "invalid_quantity",
                        "message": f"Invalid quantity: {qty}. Cannot place order.",
                        "symbol": self.symbol,
                        "order": order,
                    }
                    continue

                if qty < min_qty:
                    logger.warning(f"Quantity {qty} below min {min_qty}, adjusting...")
                    qty = min_qty

                notional = qty * price
                if notional < min_notional:
                    qty = (min_notional / price) * 1.1
                    logger.warning(
                        f"Notional {notional} below min {min_notional}, adjusting qty to {qty}..."
                    )

                if step_size:
                    qty = round(qty / step_size) * step_size
                    if qty < min_qty:
                        qty = min_qty

                res = self.exchange.create_order(
                    symbol=self.symbol,
                    type="limit",
                    side=order["side"],
                    amount=qty,
                    price=order["price"],
                    params={"timeInForce": "GTX"},
                )
                created_orders.append(res)
                logger.info(
                    f"Placed {order['side']} order at {order['price']} qty {qty}"
                )
                self.last_order_error = None
            except InsufficientFunds as e:
                error_msg = (
                    f"Insufficient balance to place {order['side']} order: {str(e)}"
                )
                logger.error(error_msg)
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
                time.sleep(1)
            except NetworkError as e:
                error_msg = f"Network error placing order: {str(e)}"
                logger.error(error_msg)
                self.last_order_error = {
                    "type": "network_error",
                    "message": error_msg,
                    "symbol": self.symbol,
                }
            except ExchangeError as e:
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
        """Cancels a list of order IDs."""
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
        """Cancels all open orders for the symbol."""
        try:
            if hasattr(self.exchange, "cancel_all_orders"):
                self.exchange.cancel_all_orders(self.symbol)
                logger.info(f"Canceled all orders for {self.symbol}")
            else:
                open_orders = self.fetch_open_orders()
                order_ids = [o["id"] for o in open_orders]
                self.cancel_orders(order_ids)
                logger.info(f"Canceled {len(order_ids)} orders")
        except Exception as e:
            logger.error(f"Error canceling all orders: {e}")

    def fetch_realized_pnl(self, start_time=None):
        """Fetches total realized PnL from transaction history."""
        try:
            params = {
                "symbol": self.symbol.replace("/", "").split(":")[0],
                "incomeType": "REALIZED_PNL",
                "limit": 1000,
            }
            if start_time:
                params["startTime"] = start_time

            income_history = self.exchange.fapiPrivateGetIncome(params)
            total_pnl = sum(float(item["income"]) for item in income_history)
            return total_pnl
        except Exception as e:
            logger.error(f"Error fetching realized PnL: {e}")
            return 0.0

    def fetch_commission(self, start_time=None):
        """Fetches total trading commission/fees from transaction history."""
        try:
            params = {
                "symbol": self.symbol.replace("/", "").split(":")[0],
                "incomeType": "COMMISSION",
                "limit": 1000,
            }
            if start_time:
                params["startTime"] = start_time

            income_history = self.exchange.fapiPrivateGetIncome(params)
            total_commission = sum(float(item["income"]) for item in income_history)
            return abs(total_commission)
        except Exception as e:
            logger.error(f"Error fetching commission: {e}")
            return 0.0

    def fetch_pnl_and_fees(self, start_time=None):
        """Fetches both realized PnL and commission fees in a single call."""
        try:
            base_params = {
                "symbol": self.symbol.replace("/", "").split(":")[0],
                "limit": 1000,
            }
            if start_time:
                base_params["startTime"] = start_time

            pnl_params = {**base_params, "incomeType": "REALIZED_PNL"}
            pnl_history = self.exchange.fapiPrivateGetIncome(pnl_params)
            total_pnl = sum(float(item["income"]) for item in pnl_history)

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

