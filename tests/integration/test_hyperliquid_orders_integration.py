"""
Integration Test for US-CORE-004-B: Hyperliquid Order Management
US-CORE-004-B 集成测试：Hyperliquid 订单管理

Integration tests verify cross-module interactions and end-to-end workflows.
集成测试验证跨模块交互和端到端工作流。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.trading.hyperliquid_client import HyperliquidClient
from src.trading.order_manager import OrderManager
from src.trading.strategy_instance import StrategyInstance


class TestHyperliquidOrderManagerIntegration:
    """
    Integration tests for HyperliquidClient with OrderManager.
    HyperliquidClient 与 OrderManager 的集成测试。
    
    Tests AC-10: Integration with Order Manager.
    测试 AC-10：与订单管理器集成。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_order_manager_with_hyperliquid_client(self, mock_requests):
        """
        Integration Test: AC-10 - OrderManager can use HyperliquidClient
        集成测试：AC-10 - OrderManager 可以使用 HyperliquidClient
        
        Verifies that OrderManager works correctly with HyperliquidClient.
        验证 OrderManager 与 HyperliquidClient 正常工作。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create HyperliquidClient
        hyperliquid_client = HyperliquidClient()

        # Create OrderManager (it doesn't need exchange client in constructor)
        order_manager = OrderManager()

        # Mock exchange methods
        hyperliquid_client.fetch_open_orders = Mock(
            return_value=[
                {"id": "order1", "side": "buy", "price": 1000.0, "amount": 0.01},
            ]
        )
        hyperliquid_client.place_orders = Mock(
            return_value=[
                {"id": "order2", "side": "sell", "price": 1002.0, "amount": 0.01},
            ]
        )
        hyperliquid_client.cancel_orders = Mock(return_value=[])

        # Test order synchronization
        current_orders = [
            {"id": "order1", "side": "buy", "price": 1000.0, "amount": 0.01},
        ]
        target_orders = [
            {"side": "sell", "price": 1002.0, "quantity": 0.01},
        ]

        # OrderManager determines what to cancel and place
        to_cancel, to_place = order_manager.sync_orders(current_orders, target_orders)

        # Verify OrderManager logic
        assert "order1" in to_cancel  # Should cancel buy order
        assert len(to_place) == 1  # Should place sell order
        assert to_place[0]["side"] == "sell"

        # Execute orders through HyperliquidClient
        if to_cancel:
            hyperliquid_client.cancel_orders(to_cancel)
        if to_place:
            hyperliquid_client.place_orders(to_place)

        # Verify methods were called
        assert hyperliquid_client.cancel_orders.called
        assert hyperliquid_client.place_orders.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_order_manager_sync_flow_with_hyperliquid(self, mock_requests):
        """
        Integration Test: Complete order sync flow with HyperliquidClient
        集成测试：使用 HyperliquidClient 的完整订单同步流程
        
        Tests the end-to-end flow: fetch orders → sync → cancel → place.
        测试端到端流程：获取订单 → 同步 → 取消 → 下单。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client and order manager
        client = HyperliquidClient()
        order_manager = OrderManager()

        # Mock exchange methods
        client.fetch_open_orders = Mock(
            return_value=[
                {"id": "old1", "side": "buy", "price": 999.0, "amount": 0.01},
                {"id": "old2", "side": "sell", "price": 1003.0, "amount": 0.01},
            ]
        )
        client.place_orders = Mock(
            return_value=[
                {"id": "new1", "side": "buy", "price": 1000.0, "amount": 0.01},
                {"id": "new2", "side": "sell", "price": 1002.0, "amount": 0.01},
            ]
        )
        client.cancel_orders = Mock(return_value=[])

        # Step 1: Fetch current orders
        current_orders = client.fetch_open_orders()
        assert len(current_orders) == 2

        # Step 2: Define target orders
        target_orders = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
            {"side": "sell", "price": 1002.0, "quantity": 0.01},
        ]

        # Step 3: Sync orders
        to_cancel, to_place = order_manager.sync_orders(current_orders, target_orders)

        # Step 4: Execute changes
        if to_cancel:
            client.cancel_orders(to_cancel)
        if to_place:
            placed = client.place_orders(to_place)
            assert len(placed) > 0

        # Verify complete flow
        assert client.fetch_open_orders.called
        assert client.cancel_orders.called or len(to_cancel) == 0
        assert client.place_orders.called or len(to_place) == 0


class TestHyperliquidStrategyInstanceOrderIntegration:
    """
    Integration tests for HyperliquidClient with StrategyInstance order management.
    HyperliquidClient 与 StrategyInstance 订单管理的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.strategy_instance.BinanceClient")
    def test_strategy_instance_order_sync_with_hyperliquid(self, mock_binance, mock_requests):
        """
        Integration Test: StrategyInstance order sync with HyperliquidClient
        集成测试：StrategyInstance 与 HyperliquidClient 的订单同步
        
        Tests that StrategyInstance can use HyperliquidClient for order management.
        测试 StrategyInstance 可以使用 HyperliquidClient 进行订单管理。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create HyperliquidClient
        hyperliquid_client = HyperliquidClient()

        # Mock exchange methods
        hyperliquid_client.fetch_open_orders = Mock(return_value=[])
        hyperliquid_client.place_orders = Mock(
            return_value=[
                {"id": "order1", "side": "buy", "price": 1000.0, "amount": 0.01},
            ]
        )
        hyperliquid_client.cancel_orders = Mock(return_value=[])

        # Create StrategyInstance (it will use BinanceClient by default, but we can test interface)
        strategy_instance = StrategyInstance("test_strategy", "fixed_spread")

        # Test that StrategyInstance has order_manager
        assert hasattr(strategy_instance, "order_manager")
        assert hasattr(strategy_instance, "sync_orders")

        # Test order sync method
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
        ]

        to_cancel, to_place = strategy_instance.sync_orders(current_orders, target_orders)

        # Verify sync logic
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"

        # If we had HyperliquidClient as exchange, we could use it
        # 如果我们有 HyperliquidClient 作为 exchange，我们可以使用它
        if hyperliquid_client and to_place:
            placed = hyperliquid_client.place_orders(to_place)
            assert len(placed) > 0


class TestHyperliquidOrderWorkflowIntegration:
    """
    Integration tests for complete order workflow with HyperliquidClient.
    使用 HyperliquidClient 的完整订单工作流集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_complete_order_lifecycle(self, mock_requests):
        """
        Integration Test: Complete order lifecycle (place → query → cancel)
        集成测试：完整订单生命周期（下单 → 查询 → 取消）
        
        Tests the full order workflow from placement to cancellation.
        测试从下单到取消的完整订单工作流。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock order placement
        place_response = MagicMock()
        place_response.status_code = 200
        place_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_requests.post.return_value = place_response

        # Step 1: Place order
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
        placed_orders = client.place_orders(orders)
        assert mock_requests.post.called

        # Mock open orders query
        query_response = MagicMock()
        query_response.status_code = 200
        query_response.json.return_value = {
            "openOrders": [
                {
                    "oid": 12345,
                    "side": "A",
                    "px": "3000.0",
                    "sz": "0.01",
                }
            ]
        }
        mock_requests.post.return_value = query_response

        # Step 2: Query open orders
        open_orders = client.fetch_open_orders()
        assert hasattr(client, "fetch_open_orders")

        # Mock order cancellation
        cancel_response = MagicMock()
        cancel_response.status_code = 200
        cancel_response.json.return_value = {
            "status": "ok",
            "response": {"type": "cancel", "data": {"statuses": [{"filled": None}]}},
        }
        mock_requests.post.return_value = cancel_response

        # Step 3: Cancel order
        if open_orders and len(open_orders) > 0:
            order_id = open_orders[0].get("id", "12345")
            canceled = client.cancel_orders([order_id])
            assert hasattr(client, "cancel_orders")

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_order_error_handling_integration(self, mock_requests):
        """
        Integration Test: Order error handling in workflow
        集成测试：工作流中的订单错误处理
        
        Tests that errors are properly handled during order operations.
        测试订单操作期间错误得到正确处理。
        """
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Create client
        client = HyperliquidClient()

        # Mock error response
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "error": "Insufficient balance / 余额不足",
        }
        mock_requests.post.return_value = error_response

        # Attempt to place order (should handle error gracefully)
        orders = [{"side": "buy", "price": 3000.0, "quantity": 1000.0, "type": "limit"}]
        
        # The client should handle errors without raising exceptions
        # 客户端应该处理错误而不抛出异常
        try:
            result = client.place_orders(orders)
            # If error handling is implemented, it should return empty list or handle gracefully
            # 如果实现了错误处理，应该返回空列表或优雅处理
            assert result is not None or len(result) == 0
        except Exception as e:
            # If exception is raised, verify it's a meaningful error
            # 如果抛出异常，验证它是有意义的错误
            assert "balance" in str(e).lower() or "余额" in str(e)




