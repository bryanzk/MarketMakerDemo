"""
Smoke Test for HyperliquidClient 422 error handling and signature
HyperliquidClient 422 错误处理和签名冒烟测试

Smoke tests verify critical paths for 422 error handling and signature generation without full integration.
冒烟测试验证 422 错误处理和签名生成的关键路径，无需完整集成。

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
        
        # Set symbol to avoid symbol_not_set error / 设置交易对以避免 symbol_not_set 错误
        client.symbol = "ETH/USDT:USDT"
        
        # Mock _exchange to simulate SDK availability and return 422 error
        # Mock _exchange 以模拟 SDK 可用性并返回 422 错误
        mock_exchange = MagicMock()
        # SDK order() method returns dict with status="err" for errors
        # SDK order() 方法在错误时返回 status="err" 的字典
        mock_exchange.order.return_value = {
            "status": "err",
            "response": "Invalid order format (422 validation error)"
        }
        client._exchange = mock_exchange
        
        # Try to place an order with sufficient value to pass validation
        # 尝试下单，使用足够的价值以通过验证
        # Order value: 1000.0 * 0.01 = $10.0 (meets minimum requirement)
        # 订单价值: 1000.0 * 0.01 = $10.0（满足最小要求）
        orders = [{"side": "buy", "price": 1000.0, "quantity": 0.01, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify no orders were created, but no exception was raised
        # 验证没有创建订单，但没有抛出异常
        assert len(result) == 0
        
        # Verify error information is available / 验证错误信息可用
        assert client.last_order_error is not None
        # Check for 422 or validation error in message
        # 检查消息中是否包含 422 或验证错误
        error_message = client.last_order_error["message"]
        assert "422" in error_message or "validation" in error_message.lower() or "Invalid order" in error_message

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

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid private key format
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_smoke_signature_in_order_payload(self, mock_post):
        """
        Smoke Test: Order payload includes signature field
        冒烟测试：订单负载包含签名字段
        
        Verifies that signature is included in order payload when eth_account is available.
        验证 eth_account 可用时订单负载包含签名。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        order = {
            "side": "buy",
            "type": "limit",
            "price": 100.0,
            "quantity": 1.0,
        }

        payload = client._build_order_payload(order)

        # Verify payload includes signature if account is available / 验证账户可用时负载包含签名
        assert "action" in payload
        assert "nonce" in payload
        if client._account is not None:
            assert "signature" in payload
            assert payload["signature"] is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_smoke_connect_without_empty_exchange_request(self, mock_post):
        """
        Smoke Test: Connection does not send empty POST to /exchange
        冒烟测试：连接不发送空 POST 到 /exchange
        
        Verifies that _connect_and_authenticate no longer sends empty {} to /exchange.
        验证 _connect_and_authenticate 不再发送空 {} 到 /exchange。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success

        client = HyperliquidClient()

        # Verify client is connected / 验证客户端已连接
        assert client.is_connected is True

        # Verify only /info endpoint was called (not /exchange with empty body)
        # 验证只调用了 /info 端点（没有用空 body 调用 /exchange）
        # Check that mock_post was called, but not with empty json={}
        # 检查 mock_post 被调用，但不是用空的 json={}
        calls = mock_post.call_args_list
        # Should have at least one call to /info
        # 应该至少有一次对 /info 的调用
        assert len(calls) > 0
        # Verify no call was made with empty json={} to /exchange
        # 验证没有用空的 json={} 调用 /exchange
        for call in calls:
            args, kwargs = call
            url = args[0] if args else kwargs.get("url", "")
            json_data = kwargs.get("json", {})
            # If it's a call to /exchange, json should not be empty {}
            # 如果是对 /exchange 的调用，json 不应该是空的 {}
            if "/exchange" in url:
                assert json_data != {}, "Empty {} should not be sent to /exchange"

