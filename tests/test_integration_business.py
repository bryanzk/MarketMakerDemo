import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from alphaloop.main import AlphaLoop
from alphaloop.strategies.funding import FundingRateStrategy


class TestBusinessLogicIntegration:
    """Integration tests for business logic and edge cases"""

    @pytest.fixture
    def mock_exchange(self):
        """Create a mock exchange with basic functionality"""
        exchange = Mock()
        exchange.symbol = "ETH/USDT:USDT"
        exchange.fetch_market_data.return_value = {
            "best_bid": 1000.0,
            "best_ask": 1002.0,
            "mid_price": 1001.0,
            "timestamp": time.time() * 1000,  # Current time in ms
        }
        exchange.fetch_funding_rate.return_value = 0.0001
        exchange.fetch_open_orders.return_value = []
        exchange.cancel_orders.return_value = []
        exchange.place_orders.return_value = []
        exchange.set_symbol.return_value = True
        return exchange

    def test_strategy_switch_clears_orders(self, mock_exchange):
        """Verify old orders are treated as needing reset when strategy changes"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Simulate active orders
            mock_exchange.fetch_open_orders.return_value = [
                {"id": "order1", "side": "buy", "price": 999.0, "amount": 0.01},
                {"id": "order2", "side": "sell", "price": 1003.0, "amount": 0.01},
            ]

            # Switch strategy
            result = bot.set_strategy("funding_rate")
            assert result is True
            assert bot.strategy_switched is True
            assert isinstance(bot.strategy, FundingRateStrategy)

            # Run a cycle - should force full reset
            mock_exchange.place_orders.return_value = [
                {"id": "new1", "side": "buy", "price": 990.0, "amount": 0.01},
                {"id": "new2", "side": "sell", "price": 1010.0, "amount": 0.01},
            ]

            bot.run_cycle()

            # Verify flag was cleared and orders were synced
            assert bot.strategy_switched is False
            # Should have called place_orders with new orders
            assert mock_exchange.place_orders.called

    def test_order_sync_minimizes_changes(self, mock_exchange):
        """Verify OrderManager correctly identifies what needs to change"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Current orders at good prices
            current_orders = [
                {"id": "ord1", "side": "buy", "price": 999.5, "amount": 0.01},
                {"id": "ord2", "side": "sell", "price": 1002.5, "amount": 0.01},
            ]

            # Target orders with SAME prices (within tolerance)
            target_orders = [
                {"side": "buy", "price": 999.5, "quantity": 0.01},
                {"side": "sell", "price": 1002.5, "quantity": 0.01},
            ]

            to_cancel, to_place = bot.om.sync_orders(current_orders, target_orders)

            # No changes needed
            assert len(to_cancel) == 0
            assert len(to_place) == 0

    def test_order_sync_detects_price_change(self, mock_exchange):
        """Verify OrderManager detects when price moves beyond tolerance"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Current orders
            current_orders = [
                {"id": "ord1", "side": "buy", "price": 999.0, "amount": 0.01},
                {"id": "ord2", "side": "sell", "price": 1002.0, "amount": 0.01},
            ]

            # Target orders with DIFFERENT prices (outside tolerance)
            target_orders = [
                {"side": "buy", "price": 995.0, "quantity": 0.01},  # Moved >$1
                {"side": "sell", "price": 1005.0, "quantity": 0.01},  # Moved >$1
            ]

            to_cancel, to_place = bot.om.sync_orders(current_orders, target_orders)

            # Both should be updated
            assert len(to_cancel) == 2
            assert len(to_place) == 2

    def test_stale_data_protection(self, mock_exchange):
        """Verify cycle aborts if market data is old"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Return stale data (10 seconds old)
            stale_time = (time.time() - 10) * 1000
            mock_exchange.fetch_market_data.return_value = {
                "best_bid": 1000.0,
                "best_ask": 1002.0,
                "mid_price": 1001.0,
                "timestamp": stale_time,
            }

            # Run cycle - should abort
            bot.run_cycle()

            # Should NOT have placed orders
            assert not mock_exchange.place_orders.called

    def test_fresh_data_accepted(self, mock_exchange):
        """Verify cycle proceeds with fresh data"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Return fresh data
            fresh_time = time.time() * 1000
            mock_exchange.fetch_market_data.return_value = {
                "best_bid": 1000.0,
                "best_ask": 1002.0,
                "mid_price": 1001.0,
                "timestamp": fresh_time,
            }

            mock_exchange.place_orders.return_value = [
                {"id": "ord1", "side": "buy", "price": 999.0, "amount": 0.01}
            ]

            # Run cycle - should succeed
            bot.run_cycle()

            # Should have placed orders
            assert mock_exchange.place_orders.called

    def test_strategy_switch_preserves_params(self, mock_exchange):
        """Verify strategy switch preserves spread, quantity, leverage"""
        with patch("alphaloop.main.BinanceClient", return_value=mock_exchange):
            bot = AlphaLoop()

            # Set custom params
            bot.strategy.spread = 0.005
            bot.strategy.quantity = 0.1
            bot.strategy.leverage = 10

            # Switch strategy
            bot.set_strategy("funding_rate")

            # Verify params preserved
            assert bot.strategy.spread == 0.005
            assert bot.strategy.quantity == 0.1
            assert bot.strategy.leverage == 10
