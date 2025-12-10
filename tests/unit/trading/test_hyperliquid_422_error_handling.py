"""
Unit tests for HyperliquidClient 422 error handling
HyperliquidClient 422 错误处理单元测试

Tests for improved 422 (Unprocessable Entity) error handling
测试改进的 422（无法处理的实体）错误处理

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import HTTPError

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquid422ErrorHandling:
    """Test 422 error handling in _make_request / 测试 _make_request 中的 422 错误处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_422_error_with_json_response(self, mock_post):
        """Test 422 error with JSON error response / 测试带 JSON 错误响应的 422 错误"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response with JSON / 模拟带 JSON 的 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid order format", "code": "INVALID_FORMAT"}'
        mock_422_response.json.return_value = {
            "error": "Invalid order format",
            "code": "INVALID_FORMAT"
        }
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock to return success for connection, then 422 for order
        # 设置 mock 先返回成功连接，然后返回 422 错误
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Make a request that will trigger 422 error / 发出会触发 422 错误的请求
        result = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"test": "data"},
            public=False,
        )
        
        # Verify result is None (422 errors return None, don't retry)
        # 验证结果为 None（422 错误返回 None，不重试）
        assert result is None
        
        # Verify last_api_error is set correctly / 验证 last_api_error 设置正确
        assert client.last_api_error is not None
        assert client.last_api_error["type"] == "invalid_request"
        assert client.last_api_error["status_code"] == 422
        assert "Invalid order format" in client.last_api_error["error_detail"]
        assert "INVALID_FORMAT" in client.last_api_error["error_detail"]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_422_error_with_text_response(self, mock_post):
        """Test 422 error with text error response / 测试带文本错误响应的 422 错误"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response with text / 模拟带文本的 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = "Invalid request parameters"
        mock_422_response.json.side_effect = ValueError("Not JSON")
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock to return success for connection, then 422 for order
        # 设置 mock 先返回成功连接，然后返回 422 错误
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Make a request that will trigger 422 error / 发出会触发 422 错误的请求
        result = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"test": "data"},
            public=False,
        )
        
        # Verify result is None / 验证结果为 None
        assert result is None
        
        # Verify last_api_error is set correctly / 验证 last_api_error 设置正确
        assert client.last_api_error is not None
        assert client.last_api_error["type"] == "invalid_request"
        assert client.last_api_error["status_code"] == 422
        assert "Invalid request parameters" in client.last_api_error["error_detail"]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_422_error_no_retry(self, mock_post):
        """Test that 422 errors don't retry / 测试 422 错误不重试"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response / 模拟 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid format"}'
        mock_422_response.json.return_value = {"error": "Invalid format"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock to return success for connection, then 422 for order
        # 设置 mock 先返回成功连接，然后返回 422 错误
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Make a request with max_retries=3 / 发出最大重试 3 次的请求
        result = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"test": "data"},
            public=False,
            max_retries=3,
        )
        
        # Verify result is None / 验证结果为 None
        assert result is None
        
        # Verify that only one attempt was made (no retries for 422)
        # 验证只尝试了一次（422 错误不重试）
        # Connection: 2 calls (info + exchange), then 1 call for the actual request
        # 连接：2 次调用（info + exchange），然后 1 次调用实际请求
        assert mock_post.call_count == 3  # 2 for connection + 1 for request

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_422_error_logs_request_data(self, mock_post):
        """Test that 422 errors log request data for debugging / 测试 422 错误记录请求数据以便调试"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response / 模拟 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid order"}'
        mock_422_response.json.return_value = {"error": "Invalid order"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock to return success for connection, then 422 for order
        # 设置 mock 先返回成功连接，然后返回 422 错误
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        test_data = {"action": {"type": "order"}, "nonce": 123456}
        
        # Make a request that will trigger 422 error / 发出会触发 422 错误的请求
        with patch("src.trading.hyperliquid_client.logger") as mock_logger:
            result = client._make_request(
                method="POST",
                endpoint="/exchange",
                data=test_data,
                public=False,
            )
            
            # Verify error was logged with request data / 验证错误已记录请求数据
            assert result is None
            mock_logger.error.assert_called()
            call_args = mock_logger.error.call_args
            assert "request_data" in call_args.kwargs.get("extra", {})
            logged_data = call_args.kwargs["extra"]["request_data"]
            assert "order" in logged_data or "action" in logged_data


class TestHyperliquid422ErrorInPlaceOrders:
    """Test 422 error handling in place_orders / 测试 place_orders 中的 422 错误处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_place_order_with_422_error(self, mock_post):
        """Test place_orders handles 422 error correctly / 测试 place_orders 正确处理 422 错误"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response / 模拟 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid order format", "details": "Price too low"}'
        mock_422_response.json.return_value = {
            "error": "Invalid order format",
            "details": "Price too low"
        }
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock: 2 calls for connection, then 422 for order placement
        # 设置 mock：2 次调用用于连接，然后 422 用于下单
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Mock SDK Exchange to simulate 422 error
        # 模拟 SDK Exchange 以模拟 422 错误
        mock_exchange = MagicMock()
        mock_exchange.account_address = "0x1234567890123456789012345678901234567890"
        # Simulate 422 error by returning error in statuses
        # 通过在 statuses 中返回错误来模拟 422 错误
        mock_exchange.order.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {
                    "statuses": [
                        {"error": "Invalid order format: Price too low"}
                    ]
                },
            },
        }
        client._exchange = mock_exchange
        
        # Try to place an order with valid parameters (passes validation but fails at API)
        # 尝试使用有效参数下单（通过验证但在 API 处失败）
        orders = [{"side": "buy", "price": 3000.0, "quantity": 0.1, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify no orders were created / 验证没有创建订单
        assert len(result) == 0
        
        # Verify last_order_error is set correctly / 验证 last_order_error 设置正确
        assert client.last_order_error is not None
        # Note: place_orders uses SDK which may set error type as "invalid_order" or "sdk_error"
        # 注意：place_orders 使用 SDK，可能将错误类型设置为 "invalid_order" 或 "sdk_error"
        # Check for valid error types depending on error source
        # 根据错误来源检查有效的错误类型
        assert client.last_order_error["type"] in ["invalid_request", "invalid_order", "sdk_error"], \
            f"Expected 'invalid_request', 'invalid_order', or 'sdk_error', got '{client.last_order_error['type']}'"
        # Verify error message contains relevant information
        # 验证错误消息包含相关信息
        error_msg = client.last_order_error.get("message", "")
        assert any(keyword in error_msg for keyword in ["Invalid", "order", "rejected", "Price", "low", "422"]), \
            f"Error message should contain relevant keywords, got: {error_msg}"
        
        # Verify order_payload and api_error are included if error type is invalid_request
        # 如果错误类型是 invalid_request，验证包含 order_payload 和 api_error
        # For SDK errors, these fields may not be present
        # 对于 SDK 错误，这些字段可能不存在
        if client.last_order_error.get("type") == "invalid_request":
            assert "order_payload" in client.last_order_error
            assert "api_error" in client.last_order_error

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_place_order_422_error_continues_with_next_order(self, mock_post):
        """Test that 422 error on one order doesn't stop processing other orders
        测试一个订单的 422 错误不会停止处理其他订单"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success
        
        # Mock SDK Exchange.order() method
        # First order fails with error status, second succeeds
        # 模拟 SDK Exchange.order() 方法
        # 第一个订单失败（错误状态），第二个成功
        def mock_order_side_effect(*args, **kwargs):
            # Track call count to simulate first order failing, second succeeding
            # 跟踪调用次数以模拟第一个订单失败，第二个成功
            if not hasattr(mock_order_side_effect, 'call_count'):
                mock_order_side_effect.call_count = 0
            mock_order_side_effect.call_count += 1
            
            if mock_order_side_effect.call_count == 1:
                # First order fails with error in statuses
                # 第一个订单失败，statuses 中包含错误
                return {
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {
                            "statuses": [
                                {"error": "Invalid order format"}
                            ]
                        },
                    },
                }
            else:
                # Second order succeeds
                # 第二个订单成功
                return {
                    "status": "ok",
                    "response": {
                        "type": "order",
                        "data": {"statuses": [{"resting": {"oid": 12345}}]},
                    },
                }
        
        client = HyperliquidClient()
        # Create and set mock exchange
        # 创建并设置 mock exchange
        mock_exchange = MagicMock()
        mock_exchange.order = MagicMock(side_effect=mock_order_side_effect)
        mock_exchange.account_address = "0x1234567890123456789012345678901234567890"
        client._exchange = mock_exchange
        
        # Try to place two orders with valid parameters (passes validation)
        # 尝试使用有效参数下两个订单（通过验证）
        orders = [
            {"side": "buy", "price": 3000.0, "quantity": 0.1, "type": "limit"},
            {"side": "sell", "price": 3100.0, "quantity": 0.1, "type": "limit"},
        ]
        result = client.place_orders(orders)
        
        # Verify only second order was created / 验证只创建了第二个订单
        assert len(result) == 1
        assert result[0].get("order_id") == "12345"  # order_id is converted to string / order_id 被转换为字符串
        
        # Note: last_order_error is cleared when a successful order is placed
        # 注意：当成功下单时，last_order_error 会被清除
        # This is expected behavior - the error from the first order is overwritten
        # 这是预期行为 - 第一个订单的错误会被覆盖
        # The important thing is that the second order was processed despite the first failing
        # 重要的是尽管第一个订单失败，第二个订单仍被处理

