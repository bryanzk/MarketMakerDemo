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
        
        # Try to place an order / 尝试下单
        orders = [{"side": "buy", "price": 100.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify no orders were created / 验证没有创建订单
        assert len(result) == 0
        
        # Verify last_order_error is set correctly / 验证 last_order_error 设置正确
        assert client.last_order_error is not None
        assert client.last_order_error["type"] == "invalid_request"
        assert "Invalid order format" in client.last_order_error["message"]
        assert "Price too low" in client.last_order_error["message"]
        assert "422" in client.last_order_error["message"]
        
        # Verify order_payload is included in error / 验证错误中包含 order_payload
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
        
        # Mock 422 error for first order, success for second / 模拟第一个订单 422 错误，第二个成功
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid order"}'
        mock_422_response.json.return_value = {"error": "Invalid order"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        mock_success_order = MagicMock()
        mock_success_order.status_code = 200
        mock_success_order.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 12345}}]},
            },
        }
        
        # Setup mock: 2 calls for connection, then 422, then success
        # 设置 mock：2 次调用用于连接，然后 422，然后成功
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
            mock_422_response,  # First order fails
            mock_success_order,  # Second order succeeds
        ]
        
        client = HyperliquidClient()
        
        # Try to place two orders / 尝试下两个订单
        orders = [
            {"side": "buy", "price": 100.0, "quantity": 0.01, "type": "limit"},
            {"side": "sell", "price": 101.0, "quantity": 0.01, "type": "limit"},
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

