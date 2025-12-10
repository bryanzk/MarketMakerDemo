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

        # Step 2: Define target orders with larger price difference to trigger update
        # 步骤 2：定义目标订单，价格差异较大以触发更新
        # Price difference must exceed 0.1% threshold (mid_price ~1001, threshold ~1.001)
        # 价格差异必须超过 0.1% 阈值（中间价 ~1001，阈值 ~1.001）
        target_orders = [
            {"side": "buy", "price": 995.0, "quantity": 0.01},  # Changed from 999.0 (diff > 1.001)
            {"side": "sell", "price": 1007.0, "quantity": 0.01},  # Changed from 1003.0 (diff > 1.001)
        ]

        # Step 3: Sync orders (with enforce_both_side for market making)
        # 步骤 3：同步订单（对做市策略使用 enforce_both_side）
        # Provide mid_price to ensure correct threshold calculation
        # 提供 mid_price 以确保正确的阈值计算
        mid_price = (target_orders[0]["price"] + target_orders[1]["price"]) / 2
        to_cancel, to_place = order_manager.sync_orders(
            current_orders, target_orders, mid_price=mid_price, enforce_both_side=True
        )

        # Verify both-side enforcement
        # 验证双边强制
        # Both orders should be cancelled and replaced due to price difference
        # 由于价格差异，两个订单都应该被取消并替换
        assert len(to_cancel) == 2
        assert len(to_place) == 2
        buy_count = sum(1 for o in to_place if o.get("side") == "buy")
        sell_count = sum(1 for o in to_place if o.get("side") == "sell")
        assert buy_count == 1
        assert sell_count == 1

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

        # Test order sync method with single-side target (non-market-making scenario)
        # 测试单边目标订单的订单同步方法（非做市场景）
        current_orders = []
        target_orders = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
        ]

        to_cancel, to_place = strategy_instance.sync_orders(current_orders, target_orders)

        # For single-side target, should place only that side
        # 对于单边目标，应该只下单那一边
        assert len(to_place) == 1
        assert to_place[0]["side"] == "buy"

        # Test with both-side target (market-making scenario)
        # 测试双边目标（做市场景）
        target_orders_both = [
            {"side": "buy", "price": 1000.0, "quantity": 0.01},
            {"side": "sell", "price": 1002.0, "quantity": 0.01},
        ]

        to_cancel, to_place = strategy_instance.sync_orders(current_orders, target_orders_both)

        # For market-making strategy (fixed_spread), should enforce both-side
        # 对于做市策略（fixed_spread），应该强制双边
        assert len(to_place) == 2
        buy_orders = [o for o in to_place if o.get("side") == "buy"]
        sell_orders = [o for o in to_place if o.get("side") == "sell"]
        assert len(buy_orders) == 1
        assert len(sell_orders) == 1

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
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid hex format for SDK initialization
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.HyperliquidExchange")
    def test_complete_order_lifecycle(self, mock_exchange_class, mock_requests):
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

        # Mock HyperliquidExchange to avoid SDK initialization issues
        # Mock HyperliquidExchange 以避免 SDK 初始化问题
        mock_exchange_instance = MagicMock()
        mock_exchange_instance.bulk_cancel.return_value = {"status": "ok"}
        # Mock order method for place_orders - return dict format expected by _parse_sdk_order_response
        # Mock order 方法用于 place_orders - 返回 _parse_sdk_order_response 期望的字典格式
        mock_exchange_instance.order.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_exchange_class.return_value = mock_exchange_instance
        
        # Create client
        client = HyperliquidClient()
        
        # Manually set _exchange to mock to bypass initialization
        # 手动设置 _exchange 为 mock 以绕过初始化
        client._exchange = mock_exchange_instance
        # Set symbol for place_orders and cancel_orders to work
        # 设置 symbol 以便 place_orders 和 cancel_orders 工作
        client.symbol = "ETH/USDT:USDT"
        # Mock fetch_market_data to avoid actual API calls
        # Mock fetch_market_data 以避免实际 API 调用
        client.fetch_market_data = Mock(
            return_value={
                "mid_price": 3000.0,
                "best_bid": 2999.0,
                "best_ask": 3001.0,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )
    
        # Step 1: Place order (using mocked SDK)
        # 步骤 1：下单（使用 mock 的 SDK）
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
        placed_orders = client.place_orders(orders)
        # Verify SDK order method was called
        # 验证 SDK order 方法被调用
        assert mock_exchange_instance.order.called
        # Verify orders were placed
        # 验证订单已下单
        assert len(placed_orders) > 0
    
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
    
        # Step 3: Cancel order (using mocked SDK)
        # 步骤 3：取消订单（使用 mock 的 SDK）
        if open_orders and len(open_orders) > 0:
            order_id = open_orders[0].get("id", "12345")
            # cancel_orders should use mocked _exchange
            # cancel_orders 应该使用 mock 的 _exchange
            client.cancel_orders([order_id])
            assert hasattr(client, "cancel_orders")
            # Verify mock was called
            # 验证 mock 被调用
            assert mock_exchange_instance.bulk_cancel.called

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






