"""
Smoke Test for HyperliquidClient 422 error handling
HyperliquidClient 422 错误处理冒烟测试

Smoke tests verify critical paths for 422 error handling without full integration.
冒烟测试验证 422 错误处理的关键路径，无需完整集成。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.exceptions import HTTPError

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquid422ErrorSmoke:
    """
    Smoke tests for 422 error handling.
    422 错误处理的冒烟测试。
    
    These tests verify the critical path without full integration.
    这些测试验证关键路径，无需完整集成。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_smoke_422_error_handling(self, mock_post):
        """
        Smoke Test: 422 error is handled gracefully without crashing
        冒烟测试：422 错误被优雅处理，不会崩溃
        
        This is the most critical path - if 422 errors crash the system, trading cannot continue.
        这是最关键路径 - 如果 422 错误导致系统崩溃，交易无法继续。
        """
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response / 模拟 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid request"}'
        mock_422_response.json.return_value = {"error": "Invalid request"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock: 2 calls for connection, then 422 for request
        # 设置 mock：2 次调用用于连接，然后 422 用于请求
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Make a request that will trigger 422 error / 发出会触发 422 错误的请求
        # This should not raise an exception / 这不应该抛出异常
        result = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"test": "data"},
            public=False,
        )
        
        # Verify result is None (not an exception) / 验证结果为 None（不是异常）
        assert result is None
        
        # Verify error is stored for API endpoints / 验证错误已存储供 API 端点使用
        assert client.last_api_error is not None
        assert client.last_api_error["status_code"] == 422

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_smoke_place_order_422_error_does_not_crash(self, mock_post):
        """
        Smoke Test: 422 error during order placement doesn't crash the system
        冒烟测试：下单期间的 422 错误不会导致系统崩溃
        
        This is critical - order placement failures should be handled gracefully.
        这很关键 - 订单下单失败应该被优雅处理。
        """
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error response / 模拟 422 错误响应
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid order format"}'
        mock_422_response.json.return_value = {"error": "Invalid order format"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock: 2 calls for connection, then 422 for order
        # 设置 mock：2 次调用用于连接，然后 422 用于订单
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Try to place an order / 尝试下单
        # This should not raise an exception / 这不应该抛出异常
        orders = [{"side": "buy", "price": 100.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify no orders were created, but no exception was raised
        # 验证没有创建订单，但没有抛出异常
        assert len(result) == 0
        
        # Verify error information is available / 验证错误信息可用
        assert client.last_order_error is not None
        assert "422" in client.last_order_error["message"]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_smoke_422_error_includes_detailed_message(self, mock_post):
        """
        Smoke Test: 422 error includes detailed error message for debugging
        冒烟测试：422 错误包含详细的错误消息以便调试
        
        Error messages should be informative to help diagnose issues.
        错误消息应该信息丰富，以帮助诊断问题。
        """
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error with detailed message / 模拟带详细消息的 422 错误
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Price validation failed", "field": "price", "value": -100}'
        mock_422_response.json.return_value = {
            "error": "Price validation failed",
            "field": "price",
            "value": -100
        }
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock: 2 calls for connection, then 422 for request
        # 设置 mock：2 次调用用于连接，然后 422 用于请求
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        
        # Make a request that will trigger 422 error / 发出会触发 422 错误的请求
        result = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"test": "data"},
            public=False,
        )
        
        # Verify error detail is captured / 验证错误详情已捕获
        assert result is None
        assert client.last_api_error is not None
        assert "Price validation failed" in client.last_api_error["error_detail"]
        assert "price" in client.last_api_error["error_detail"]
        assert "-100" in client.last_api_error["error_detail"]

