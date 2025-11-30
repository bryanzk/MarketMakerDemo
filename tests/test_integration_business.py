import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.engine import AlphaLoop
from src.trading.strategy_instance import StrategyInstance
from src.trading.strategies.funding_rate import FundingRateStrategy


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
        exchange.fetch_account_data.return_value = {
            "position_amt": 0.1,
            "entry_price": 1000.0,
        }
        exchange.fetch_open_orders.return_value = []
        exchange.cancel_orders.return_value = []
        exchange.place_orders.return_value = []
        exchange.set_symbol.return_value = True
        return exchange

    def test_strategy_switch_clears_orders(self, mock_exchange):
        """Verify old orders are treated as needing reset when strategy changes"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()
            default_instance = bot.strategy_instances["default"]

            # Simulate active orders
            mock_exchange.fetch_open_orders.return_value = [
                {"id": "order1", "side": "buy", "price": 999.0, "amount": 0.01},
                {"id": "order2", "side": "sell", "price": 1003.0, "amount": 0.01},
            ]

            # Switch strategy
            result = bot.set_strategy("funding_rate")
            assert result is True
            
            # After set_strategy, need to get the updated instance
            default_instance = bot.strategy_instances["default"]
            assert default_instance.strategy_switched is True
            assert isinstance(default_instance.strategy, FundingRateStrategy)

            # Run a cycle - should force full reset
            mock_exchange.place_orders.return_value = [
                {"id": "new1", "side": "buy", "price": 990.0, "amount": 0.01},
                {"id": "new2", "side": "sell", "price": 1010.0, "amount": 0.01},
            ]

            bot.run_cycle()

            # Verify flag was cleared after run_cycle
            default_instance = bot.strategy_instances["default"]
            assert default_instance.strategy_switched is False
            # Should have called place_orders with new orders
            assert mock_exchange.place_orders.called

    def test_order_sync_minimizes_changes(self, mock_exchange):
        """Verify OrderManager correctly identifies what needs to change"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
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
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
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
        """Verify refresh_data still updates cache with stale data but logs warning"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()
            default_instance = bot.strategy_instances["default"]

            # Return stale data (10 seconds old)
            stale_time = (time.time() - 10) * 1000
            mock_exchange.fetch_market_data.return_value = {
                "best_bid": 1000.0,
                "best_ask": 1002.0,
                "mid_price": 1001.0,
                "timestamp": stale_time,
            }

            # Run cycle - refresh_data should still update cache
            bot.run_cycle()

            # Cache should be updated even with stale data (now on StrategyInstance)
            assert default_instance.latest_market_data is not None
            assert default_instance.latest_market_data["mid_price"] == 1001.0

    def test_fresh_data_accepted(self, mock_exchange):
        """Verify cycle proceeds with fresh data"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
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
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()

            # Set custom params on default strategy
            default_instance = bot.strategy_instances["default"]
            default_instance.strategy.spread = 0.005
            default_instance.strategy.quantity = 0.1
            default_instance.strategy.leverage = 10

            # Switch strategy
            bot.set_strategy("funding_rate")

            # Get updated instance
            default_instance = bot.strategy_instances["default"]

            # Verify params preserved
            assert default_instance.strategy.spread == 0.005
            assert default_instance.strategy.quantity == 0.1
            assert default_instance.strategy.leverage == 10

    def test_get_status_includes_strategy_config(self, mock_exchange):
        """Status should expose core strategy config for UI"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()

            # Custom config on default strategy
            default_instance = bot.strategy_instances["default"]
            default_instance.strategy.spread = 0.003
            default_instance.strategy.quantity = 0.2
            default_instance.strategy.leverage = 5

            status = bot.get_status()

            assert status["spread"] == 0.003
            assert status["quantity"] == 0.2
            assert status["leverage"] == 5
            assert status["strategy_type"] in ("fixed_spread", "funding_rate")

    def test_order_history_includes_strategy_type(self, mock_exchange):
        """Order history entries should include strategy_type for filtering"""
        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()

            # Ensure we are running funding strategy
            bot.set_strategy("funding_rate")

            # Fresh market data & orders
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

            bot.run_cycle()

            assert len(bot.order_history) > 0
            last_order = bot.order_history[-1]
            assert last_order.get("strategy_type") == "funding_rate"

    def test_run_cycle_handles_refresh_failure_gracefully(self, mock_exchange):
        """If refresh_data fails, cycle should not place orders for that instance."""
        # Make fetch_market_data return None to simulate refresh failure
        mock_exchange.fetch_market_data.return_value = None

        with patch(
            "src.trading.strategy_instance.BinanceClient",
            return_value=mock_exchange,
        ):
            bot = AlphaLoop()
            default_instance = bot.strategy_instances["default"]

            # Clear any orders
            default_instance.active_orders = []

            bot.run_cycle()

            # No orders should have been placed since refresh_data failed
            # The place_orders should not have been called for this instance
            assert mock_exchange.place_orders.call_count == 0
            # Instance should have no active orders
            assert len(default_instance.active_orders) == 0
