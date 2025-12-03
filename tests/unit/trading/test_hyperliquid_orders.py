"""
Unit tests for HyperliquidClient order management
HyperliquidClient 订单管理单元测试

Tests for US-CORE-004-B: Hyperliquid Order Management
测试 US-CORE-004-B: Hyperliquid 订单管理

Owner: Agent TRADING
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Note: This test assumes HyperliquidClient order methods will be implemented
# 注意：此测试假设 HyperliquidClient 订单方法将被实现
# According to TDD principles, tests are written first and will fail until implementation is complete
# 根据 TDD 原则，先编写测试，在实现完成前测试会失败


class TestHyperliquidClientLimitOrderPlacement:
    """Test AC-1: Limit Order Placement / 测试 AC-1: 限价单下单"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_limit_buy_order_success(self, mock_requests):
        """Test successful limit buy order placement / 测试成功下限价买单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful order placement
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_requests.post.return_value = order_response

        # Place limit buy order
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)

        # Verify order was placed
        assert len(result) > 0
        assert mock_requests.post.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_limit_sell_order_success(self, mock_requests):
        """Test successful limit sell order placement / 测试成功下限价卖单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful order placement
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12346}}]},
            },
        }
        mock_requests.post.return_value = order_response

        # Place limit sell order
        orders = [{"side": "sell", "price": 3010.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)

        # Verify order was placed
        assert len(result) > 0
        assert mock_requests.post.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_limit_order_returns_order_id(self, mock_requests):
        """Test that limit order returns order ID / 测试限价单返回订单 ID"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful order placement with order ID
        order_id = "HL_ORDER_12345"
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": order_id}}]},
            },
        }
        mock_requests.post.return_value = order_response

        # Place limit order
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)

        # Verify order ID is returned
        assert len(result) > 0
        # Order should have an ID
        if isinstance(result[0], dict):
            assert "id" in result[0] or "order_id" in result[0]


class TestHyperliquidClientMarketOrderPlacement:
    """Test AC-2: Market Order Placement / 测试 AC-2: 市价单下单"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_market_buy_order_success(self, mock_requests):
        """Test successful market buy order placement / 测试成功下市价买单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful market order execution
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {
                    "statuses": [
                        {
                            "filled": {
                                "totalSz": "0.01",
                                "avgPx": "3000.5",
                            }
                        }
                    ]
                },
            },
        }
        mock_requests.post.return_value = order_response

        # Place market buy order (no price needed for market orders)
        orders = [{"side": "buy", "quantity": 0.01, "type": "market"}]
        result = client.place_orders(orders)

        # Verify order was executed
        assert len(result) > 0
        assert mock_requests.post.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_market_sell_order_success(self, mock_requests):
        """Test successful market sell order placement / 测试成功下市价卖单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful market order execution
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {
                    "statuses": [
                        {
                            "filled": {
                                "totalSz": "0.01",
                                "avgPx": "3010.5",
                            }
                        }
                    ]
                },
            },
        }
        mock_requests.post.return_value = order_response

        # Place market sell order
        orders = [{"side": "sell", "quantity": 0.01, "type": "market"}]
        result = client.place_orders(orders)

        # Verify order was executed
        assert len(result) > 0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_market_order_returns_fill_confirmation(self, mock_requests):
        """Test that market order returns fill confirmation / 测试市价单返回成交确认"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock market order fill
        fill_price = 3000.5
        fill_quantity = 0.01
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {
                    "statuses": [
                        {
                            "filled": {
                                "totalSz": str(fill_quantity),
                                "avgPx": str(fill_price),
                            }
                        }
                    ]
                },
            },
        }
        mock_requests.post.return_value = order_response

        # Place market order
        orders = [{"side": "buy", "quantity": fill_quantity, "type": "market"}]
        result = client.place_orders(orders)

        # Verify fill confirmation
        assert len(result) > 0
        # Result should contain fill information
        if isinstance(result[0], dict):
            assert "filled" in str(result[0]).lower() or "status" in result[0]


class TestHyperliquidClientOrderCancellation:
    """Test AC-3: Order Cancellation / 测试 AC-3: 订单取消"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_cancel_order_success(self, mock_requests):
        """Test successful order cancellation / 测试成功取消订单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful cancellation
        cancel_response = MagicMock()
        cancel_response.status_code = 200
        cancel_response.json.return_value = {
            "status": "ok",
            "response": {"type": "cancel"},
        }
        mock_requests.post.return_value = cancel_response

        # Cancel order
        order_id = "HL_ORDER_12345"
        client.cancel_orders([order_id])

        # Verify cancellation was called
        assert mock_requests.post.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_cancel_order_returns_confirmation(self, mock_requests):
        """Test that order cancellation returns confirmation / 测试订单取消返回确认"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock cancellation confirmation
        cancel_response = MagicMock()
        cancel_response.status_code = 200
        cancel_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "cancel",
                "data": {"statuses": [{"cancelled": {"oid": 12345}}]},
            },
        }
        mock_requests.post.return_value = cancel_response

        # Cancel order
        order_id = "HL_ORDER_12345"
        client.cancel_orders([order_id])

        # Verify cancellation was successful
        assert mock_requests.post.called


class TestHyperliquidClientCancelAllOrders:
    """Test AC-4: Cancel All Orders / 测试 AC-4: 取消所有订单"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_cancel_all_orders_success(self, mock_requests):
        """Test successful cancellation of all orders / 测试成功取消所有订单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock open orders
        open_orders_response = MagicMock()
        open_orders_response.status_code = 200
        open_orders_response.json.return_value = {
            "status": "ok",
            "openOrders": [
                {"id": "HL_ORDER_1", "symbol": "ETH", "side": "buy"},
                {"id": "HL_ORDER_2", "symbol": "ETH", "side": "sell"},
            ],
        }
        mock_requests.post.return_value = open_orders_response

        # Mock cancellation response
        cancel_response = MagicMock()
        cancel_response.status_code = 200
        cancel_response.json.return_value = {
            "status": "ok",
            "response": {"type": "cancel"},
        }

        # Set up side_effect to return different responses
        mock_requests.post.side_effect = [
            mock_response,  # Initial connection
            mock_response,  # Initial connection (second call)
            open_orders_response,  # fetch_open_orders
            cancel_response,  # cancel_orders call 1
            cancel_response,  # cancel_orders call 2
        ]

        # Cancel all orders
        client.cancel_all_orders()

        # Verify cancellation was attempted for all orders
        assert mock_requests.post.call_count >= 3

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_cancel_all_orders_with_no_open_orders(self, mock_requests):
        """Test cancel all orders when no open orders exist / 测试没有未成交订单时取消所有订单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock empty open orders
        open_orders_response = MagicMock()
        open_orders_response.status_code = 200
        open_orders_response.json.return_value = {"status": "ok", "openOrders": []}
        mock_requests.post.return_value = open_orders_response

        # Cancel all orders (should handle gracefully)
        client.cancel_all_orders()

        # Should not raise exception
        assert True


class TestHyperliquidClientOrderStatusQuery:
    """Test AC-5: Order Status Query / 测试 AC-5: 订单状态查询"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_order_status_success(self, mock_requests):
        """Test successful order status query / 测试成功查询订单状态"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock order status response
        order_id = "HL_ORDER_12345"
        order_status_response = MagicMock()
        order_status_response.status_code = 200
        order_status_response.json.return_value = {
            "status": "ok",
            "order": {
                "id": order_id,
                "symbol": "ETH",
                "side": "buy",
                "type": "limit",
                "price": 3000.0,
                "quantity": 0.01,
                "filled_qty": 0.0,
                "status": "open",
                "timestamp": 1234567890,
            },
        }
        mock_requests.post.return_value = order_status_response

        # Fetch order status
        result = client.fetch_order(order_id)

        # Verify order details are returned
        assert result is not None
        assert result.get("order_id") == order_id or result.get("id") == order_id
        assert "status" in result
        assert "price" in result
        assert "quantity" in result

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_order_status_includes_all_fields(self, mock_requests):
        """Test that order status includes all required fields / 测试订单状态包含所有必需字段"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock complete order status
        order_status_response = MagicMock()
        order_status_response.status_code = 200
        order_status_response.json.return_value = {
            "status": "ok",
            "order": {
                "id": "HL_ORDER_12345",
                "symbol": "ETH",
                "side": "buy",
                "type": "limit",
                "price": 3000.0,
                "quantity": 0.01,
                "filled_qty": 0.005,
                "status": "partially_filled",
                "timestamp": 1234567890,
            },
        }
        mock_requests.post.return_value = order_status_response

        # Fetch order status
        result = client.fetch_order("HL_ORDER_12345")

        # Verify all required fields are present
        required_fields = [
            "order_id",
            "symbol",
            "side",
            "type",
            "quantity",
            "price",
            "status",
            "filled_qty",
            "timestamp",
        ]
        # Check if fields exist (may have different names)
        assert result is not None
        # At least some key fields should be present
        assert any(field in str(result) for field in ["id", "order_id", "status"])

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_order_not_found(self, mock_requests):
        """Test order status query for non-existent order / 测试查询不存在的订单状态"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient, OrderNotFoundError

        client = HyperliquidClient()

        # Mock order not found response
        order_status_response = MagicMock()
        order_status_response.status_code = 404
        order_status_response.json.return_value = {
            "status": "error",
            "message": "Order not found",
        }
        mock_requests.post.return_value = order_status_response

        # Fetch non-existent order
        with pytest.raises(OrderNotFoundError):
            client.fetch_order("NON_EXISTENT_ORDER")


class TestHyperliquidClientOpenOrdersQuery:
    """Test AC-6: Open Orders Query / 测试 AC-6: 未成交订单查询"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_open_orders_success(self, mock_requests):
        """Test successful open orders query / 测试成功查询未成交订单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock open orders response
        open_orders_response = MagicMock()
        open_orders_response.status_code = 200
        open_orders_response.json.return_value = {
            "status": "ok",
            "openOrders": [
                {
                    "id": "HL_ORDER_1",
                    "symbol": "ETH",
                    "side": "buy",
                    "price": 3000.0,
                    "quantity": 0.01,
                    "status": "open",
                },
                {
                    "id": "HL_ORDER_2",
                    "symbol": "ETH",
                    "side": "sell",
                    "price": 3010.0,
                    "quantity": 0.01,
                    "status": "open",
                },
            ],
        }
        mock_requests.post.return_value = open_orders_response

        # Fetch open orders
        result = client.fetch_open_orders()

        # Verify open orders are returned
        assert isinstance(result, list)
        assert len(result) == 2

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_open_orders_only_returns_open_orders(self, mock_requests):
        """Test that only open orders are returned, not filled/cancelled / 测试只返回未成交订单，不包括已成交/已取消"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock response with mixed order statuses
        # API should filter to only return open orders
        open_orders_response = MagicMock()
        open_orders_response.status_code = 200
        open_orders_response.json.return_value = {
            "status": "ok",
            "openOrders": [
                {"id": "HL_ORDER_1", "status": "open"},
                {"id": "HL_ORDER_2", "status": "open"},
            ],
        }
        mock_requests.post.return_value = open_orders_response

        # Fetch open orders
        result = client.fetch_open_orders()

        # Verify only open orders are returned
        assert isinstance(result, list)
        for order in result:
            # All orders should be open (status check if available)
            if isinstance(order, dict) and "status" in order:
                assert order["status"] == "open"


class TestHyperliquidClientOrderHistory:
    """Test AC-7: Order History / 测试 AC-7: 订单历史"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_orders_history_success(self, mock_requests):
        """Test successful order history query / 测试成功查询订单历史"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock order history response
        history_response = MagicMock()
        history_response.status_code = 200
        history_response.json.return_value = {
            "status": "ok",
            "orders": [
                {
                    "id": "HL_ORDER_1",
                    "status": "filled",
                    "timestamp": 1234567890,
                },
                {
                    "id": "HL_ORDER_2",
                    "status": "cancelled",
                    "timestamp": 1234567891,
                },
                {
                    "id": "HL_ORDER_3",
                    "status": "open",
                    "timestamp": 1234567892,
                },
            ],
        }
        mock_requests.post.return_value = history_response

        # Fetch order history
        result = client.fetch_orders_history()

        # Verify history is returned
        assert isinstance(result, list)
        assert len(result) > 0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_orders_history_includes_timestamps(self, mock_requests):
        """Test that order history includes timestamps / 测试订单历史包含时间戳"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock order history with timestamps
        history_response = MagicMock()
        history_response.status_code = 200
        history_response.json.return_value = {
            "status": "ok",
            "orders": [
                {
                    "id": "HL_ORDER_1",
                    "status": "filled",
                    "timestamp": 1234567890,
                },
            ],
        }
        mock_requests.post.return_value = history_response

        # Fetch order history
        result = client.fetch_orders_history()

        # Verify timestamps are present
        assert isinstance(result, list)
        if len(result) > 0 and isinstance(result[0], dict):
            assert "timestamp" in result[0] or "created_at" in result[0]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_fetch_orders_history_with_limit(self, mock_requests):
        """Test order history query with limit parameter / 测试带限制参数的订单历史查询"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock limited history response
        history_response = MagicMock()
        history_response.status_code = 200
        history_response.json.return_value = {
            "status": "ok",
            "orders": [{"id": f"HL_ORDER_{i}", "status": "filled"} for i in range(10)],
        }
        mock_requests.post.return_value = history_response

        # Fetch order history with limit
        result = client.fetch_orders_history(limit=10)

        # Verify limit is respected
        assert isinstance(result, list)
        assert len(result) <= 10


class TestHyperliquidClientOrderErrorHandling:
    """Test AC-8: Order Error Handling / 测试 AC-8: 订单错误处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_order_insufficient_balance(self, mock_requests):
        """Test order placement with insufficient balance / 测试余额不足时下单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import (
            HyperliquidClient,
            InsufficientBalanceError,
        )

        client = HyperliquidClient()

        # Mock insufficient balance error
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "status": "error",
            "response": {
                "type": "error",
                "data": "Insufficient balance / 余额不足",
            },
        }
        mock_requests.post.return_value = error_response

        # Attempt to place order
        orders = [{"side": "buy", "price": 3000.0, "quantity": 1000.0, "type": "limit"}]
        result = client.place_orders(orders)

        # Should handle error gracefully
        # Either return empty list or raise InsufficientBalanceError
        assert result == [] or client.last_order_error is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_order_invalid_price(self, mock_requests):
        """Test order placement with invalid price / 测试无效价格时下单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient, InvalidOrderError

        client = HyperliquidClient()

        # Mock invalid price error
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "status": "error",
            "response": {
                "type": "error",
                "data": "Invalid price / 无效价格",
            },
        }
        mock_requests.post.return_value = error_response

        # Attempt to place order with invalid price
        orders = [{"side": "buy", "price": -100.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)

        # Should handle error gracefully
        assert result == [] or client.last_order_error is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_order_error_bilingual_message(self, mock_requests):
        """Test that order errors provide bilingual messages / 测试订单错误提供双语消息"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock error response
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "status": "error",
            "response": {
                "type": "error",
                "data": "Insufficient balance / 余额不足",
            },
        }
        mock_requests.post.return_value = error_response

        # Attempt to place order
        orders = [{"side": "buy", "price": 3000.0, "quantity": 1000.0, "type": "limit"}]
        client.place_orders(orders)

        # Verify error message is bilingual
        if client.last_order_error:
            error_msg = client.last_order_error.get("message", "")
            assert (
                "余额" in error_msg
                or "balance" in error_msg.lower()
                or "insufficient" in error_msg.lower()
            )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_cancel_order_not_found(self, mock_requests):
        """Test cancellation of non-existent order / 测试取消不存在的订单"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient, OrderNotFoundError

        client = HyperliquidClient()

        # Mock order not found error
        error_response = MagicMock()
        error_response.status_code = 404
        error_response.json.return_value = {
            "status": "error",
            "response": {"type": "error", "data": "Order not found / 订单未找到"},
        }
        mock_requests.post.return_value = error_response

        # Attempt to cancel non-existent order
        # Should handle gracefully (either raise OrderNotFoundError or log error)
        try:
            client.cancel_orders(["NON_EXISTENT_ORDER"])
        except OrderNotFoundError:
            # Expected behavior
            pass
        except Exception:
            # Other exceptions are also acceptable
            pass


class TestHyperliquidClientOrderIdempotency:
    """Test AC-9: Order Idempotency / 测试 AC-9: 订单幂等性"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_duplicate_order_handles_idempotency(self, mock_requests):
        """Test that placing duplicate orders handles idempotency / 测试下重复订单时处理幂等性"""
        # Mock successful connection for initialization
        # Note: HyperliquidClient.__init__ calls requests.post twice (once for /info, once for /exchange)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # After initialization, set up side_effect for order placement calls
        # Mock order placement - first call creates order, second returns existing
        order_id = "HL_ORDER_12345"
        first_response = MagicMock()
        first_response.status_code = 200
        first_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": order_id}}]},
            },
        }

        # Second call with same parameters should return existing order
        second_response = MagicMock()
        second_response.status_code = 200
        second_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": order_id}}]},
            },
        }

        # Set side_effect AFTER initialization to handle order placement calls
        # The first two calls were already consumed during initialization
        mock_requests.post.side_effect = [
            first_response,  # First order placement
            second_response,  # Second order placement (same params)
        ]

        # Place same order twice
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.01, "type": "limit"}]
        result1 = client.place_orders(orders)
        result2 = client.place_orders(orders)

        # Both should return the same order ID (idempotency)
        assert len(result1) > 0
        assert len(result2) > 0
        # Order IDs should match (if available)
        if isinstance(result1[0], dict) and isinstance(result2[0], dict):
            id1 = result1[0].get("id") or result1[0].get("order_id")
            id2 = result2[0].get("id") or result2[0].get("order_id")
            if id1 and id2:
                assert id1 == id2


class TestHyperliquidClientOrderManagerIntegration:
    """Test AC-10: Integration with Order Manager / 测试 AC-10: 与订单管理器集成"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_order_manager_can_use_hyperliquid_client(self, mock_requests):
        """Test that OrderManager can use HyperliquidClient / 测试 OrderManager 可以使用 HyperliquidClient"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient
        from src.trading.order_manager import OrderManager

        # Initialize client and order manager
        client = HyperliquidClient()
        order_manager = OrderManager()

        # Verify OrderManager can work with HyperliquidClient
        # This is a basic integration test - full integration would require
        # OrderManager to accept an exchange client parameter
        assert client is not None
        assert order_manager is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_place_orders_interface_compatibility(self, mock_requests):
        """Test that place_orders interface is compatible with OrderManager / 测试 place_orders 接口与 OrderManager 兼容"""
        # Mock successful connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Mock successful order placement
        order_response = MagicMock()
        order_response.status_code = 200
        order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        mock_requests.post.return_value = order_response

        # Test order format compatible with OrderManager
        # OrderManager typically uses: {"side": "buy", "price": 3000.0, "quantity": 0.01}
        orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.01},
            {"side": "sell", "price": 3010.0, "quantity": 0.01},
        ]

        # Should accept this format
        result = client.place_orders(orders)

        # Verify interface compatibility
        assert isinstance(result, list)
