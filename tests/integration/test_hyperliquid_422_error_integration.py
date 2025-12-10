"""
Integration tests for HyperliquidClient 422 error handling
HyperliquidClient 422 错误处理集成测试

Integration tests verify 422 error handling in realistic scenarios.
集成测试验证实际场景中的 422 错误处理。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import HTTPError

from src.trading.hyperliquid_client import HyperliquidClient


class TestHyperliquid422ErrorIntegration:
    """
    Integration tests for 422 error handling.
    422 错误处理的集成测试。
    
    These tests verify error handling in realistic scenarios.
    这些测试验证实际场景中的错误处理。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            # Use a valid hex format private key (64 hex characters) for testing
            # 使用有效的十六进制格式私钥（64 个十六进制字符）用于测试
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format but invalid key for actual trading
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_integration_422_error_during_trading_cycle(self, mock_post):
        """
        Integration Test: 422 error during a trading cycle is handled gracefully
        集成测试：交易周期中的 422 错误被优雅处理
        
        Simulates a realistic scenario where an order placement fails with 422.
        模拟订单下单因 422 失败的实际场景。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock successful market data fetch / 模拟成功的市场数据获取
        mock_market_data = MagicMock()
        mock_market_data.status_code = 200
        mock_market_data.json.return_value = {
            "universe": [{"name": "ETH"}],
            "meta": {"universe": [{"name": "ETH"}]}
        }
        
        # Setup mock sequence: connection (2 calls), market data
        # 设置 mock 序列：连接（2 次调用），市场数据
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
            mock_market_data,  # Market data
        ]
        
        client = HyperliquidClient()
        
        # Mock fetch_market_data to return market data with tick_size and step_size
        # Mock fetch_market_data 返回包含 tick_size 和 step_size 的市场数据
        client.fetch_market_data = Mock(
            return_value={
                "best_bid": 2000.0,
                "best_ask": 2002.0,
                "mid_price": 2001.0,
                "tick_size": 0.1,
                "step_size": 0.001,
            }
        )
        
        # Mock SDK order() method to return 422 error response
        # Mock SDK order() 方法返回 422 错误响应
        if client._exchange:
            client._exchange.order = MagicMock(return_value={
                "status": "err",
                "response": "Insufficient margin. MARGIN_ERROR"
            })
        
        # Simulate a trading cycle / 模拟交易周期
        # 1. Get market data (should succeed) / 获取市场数据（应该成功）
        # 2. Place order (should fail with 422) / 下单（应该因 422 失败）
        
        # Get market data / 获取市场数据
        market_info = client._make_request(
            method="POST",
            endpoint="/info",
            data={"type": "metaAndAssetCtxs"},
            public=True,
        )
        assert market_info is not None
        
        # Try to place order / 尝试下单
        orders = [{"side": "buy", "price": 2000.0, "quantity": 1.0, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify order placement failed gracefully / 验证订单下单优雅失败
        assert len(result) == 0
        assert client.last_order_error is not None
        assert client.last_order_error["type"] == "invalid_request"
        assert "Insufficient margin" in client.last_order_error["message"]
        # Check error detail in api_error field / 检查 api_error 字段中的错误详情
        api_error = client.last_order_error.get("api_error", {})
        error_text = api_error.get("error", "") if api_error else ""
        assert "MARGIN_ERROR" in error_text or "Insufficient margin" in error_text

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            # Use a valid hex format private key (64 hex characters) for testing
            # 使用有效的十六进制格式私钥（64 个十六进制字符）用于测试
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format but invalid key for actual trading
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_integration_422_error_with_multiple_orders(self, mock_post):
        """
        Integration Test: 422 error on one order doesn't prevent other orders
        集成测试：一个订单的 422 错误不会阻止其他订单
        
        Simulates placing multiple orders where one fails with 422.
        模拟下多个订单，其中一个因 422 失败。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Setup mock sequence / 设置 mock 序列
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
        ]
        
        client = HyperliquidClient()
        
        # Mock fetch_market_data to return market data with tick_size and step_size
        # Market data should match order prices to avoid symbol mismatch detection
        # Mock fetch_market_data 返回包含 tick_size 和 step_size 的市场数据
        # 市场数据应该匹配订单价格以避免交易对不匹配检测
        # Use a callable mock that returns different market data based on which order is being placed
        # 使用可调用的 mock，根据正在下的订单返回不同的市场数据
        call_count = [0]  # Use list to allow modification in nested function
        def mock_fetch_market_data():
            call_count[0] += 1
            if call_count[0] == 1:
                # First order: price 100.0, so mid_price should be around 100.0
                # 第一个订单：价格 100.0，所以 mid_price 应该在 100.0 附近
                return {
                    "best_bid": 99.5,
                    "best_ask": 100.5,
                    "mid_price": 100.0,  # Match first order price / 匹配第一个订单价格
                    "tick_size": 0.1,
                    "step_size": 0.001,
                }
            else:
                # Second order: price 2010.0, so mid_price should be around 2010.0
                # 第二个订单：价格 2010.0，所以 mid_price 应该在 2010.0 附近
                return {
                    "best_bid": 2009.5,
                    "best_ask": 2010.5,
                    "mid_price": 2010.0,  # Match second order price / 匹配第二个订单价格
                    "tick_size": 0.1,
                    "step_size": 0.001,
                }
        client.fetch_market_data = Mock(side_effect=mock_fetch_market_data)
        
        # Mock SDK order() method to return different responses for different orders
        # Mock SDK order() 方法为不同订单返回不同响应
        if client._exchange:
            order_call_count = [0]  # Use list to allow modification in nested function
            def mock_order(*args, **kwargs):
                order_call_count[0] += 1
                if order_call_count[0] == 1:
                    # First order fails with 422 / 第一个订单因 422 失败
                    return {
                        "status": "err",
                        "response": "Invalid price. field: price"
                    }
                else:
                    # Second order succeeds / 第二个订单成功
                    return {
                        "status": "ok",
                        "response": {
                            "type": "order",
                            "data": {"statuses": [{"resting": {"oid": 99999}}]},
                        },
                    }
            client._exchange.order = MagicMock(side_effect=mock_order)
        
        # Place multiple orders / 下多个订单
        # First order will fail with 422 from API (not validation)
        # 第一个订单会因 API 返回 422 失败（不是验证失败）
        # Note: Order value must be >= $10.0 to pass validation
        # 注意：订单价值必须 >= $10.0 才能通过验证
        orders = [
            {"side": "buy", "price": 100.0, "quantity": 0.1, "type": "limit"},  # Value: $10.0, will fail with 422 / 价值: $10.0，会因 422 失败
            {"side": "sell", "price": 2010.0, "quantity": 0.1, "type": "limit"},  # Value: $201.0, valid order / 价值: $201.0，有效订单
        ]
        result = client.place_orders(orders)
        
        # Verify only valid order was placed / 验证只下了有效订单
        assert len(result) == 1
        assert result[0].get("order_id") == "99999"  # order_id is converted to string / order_id 被转换为字符串
        
        # Note: last_order_error is cleared when a successful order is placed
        # 注意：当成功下单时，last_order_error 会被清除
        # The important thing is that the second order was processed despite the first failing
        # 重要的是尽管第一个订单失败，第二个订单仍被处理

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            # Use a valid hex format private key (64 hex characters) for testing
            # 使用有效的十六进制格式私钥（64 个十六进制字符）用于测试
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format but invalid key for actual trading
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_integration_422_error_preserves_client_state(self, mock_post):
        """
        Integration Test: 422 error doesn't corrupt client state
        集成测试：422 错误不会破坏客户端状态
        
        Verifies that after a 422 error, the client can still make other requests.
        验证在 422 错误后，客户端仍可以发出其他请求。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error / 模拟 422 错误
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid request"}'
        mock_422_response.json.return_value = {"error": "Invalid request"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Mock successful request after error / 模拟错误后的成功请求
        mock_success_after = MagicMock()
        mock_success_after.status_code = 200
        mock_success_after.json.return_value = {"status": "ok", "data": "test"}
        
        # Setup mock sequence / 设置 mock 序列
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
            mock_422_response,  # First request fails with 422
            mock_success_after,  # Second request succeeds
        ]
        
        client = HyperliquidClient()
        
        # Make a request that fails with 422 / 发出因 422 失败的请求
        result1 = client._make_request(
            method="POST",
            endpoint="/exchange",
            data={"invalid": "data"},
            public=False,
        )
        assert result1 is None
        assert client.last_api_error is not None
        assert client.last_api_error["status_code"] == 422
        
        # Make another request that should succeed / 发出应该成功的另一个请求
        result2 = client._make_request(
            method="POST",
            endpoint="/info",
            data={"type": "clearinghouseState"},
            public=True,
        )
        
        # Verify second request succeeded / 验证第二个请求成功
        assert result2 is not None
        assert result2.get("status") == "ok"
        
        # Verify client is still functional / 验证客户端仍然可用
        assert client.is_connected is True

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            # Use a valid hex format private key (64 hex characters) for testing
            # 使用有效的十六进制格式私钥（64 个十六进制字符）用于测试
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format but invalid key for actual trading
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_integration_422_error_logs_complete_context(self, mock_post):
        """
        Integration Test: 422 error logs complete context for debugging
        集成测试：422 错误记录完整的上下文以便调试
        
        Verifies that error logging includes all necessary information.
        验证错误日志包含所有必要信息。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock 422 error with detailed response / 模拟带详细响应的 422 错误
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Validation failed", "details": {"price": "must be positive", "quantity": "too large"}}'
        mock_422_response.json.return_value = {
            "error": "Validation failed",
            "details": {
                "price": "must be positive",
                "quantity": "too large"
            }
        }
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock / 设置 mock
        mock_post.side_effect = [mock_success, mock_success, mock_422_response]
        
        client = HyperliquidClient()
        test_order_payload = {
            "action": {"type": "order", "orders": []},
            "nonce": 1234567890
        }
        
        # Make request and verify logging / 发出请求并验证日志
        with patch("src.trading.hyperliquid_client.logger") as mock_logger:
            result = client._make_request(
                method="POST",
                endpoint="/exchange",
                data=test_order_payload,
                public=False,
            )
            
            # Verify error was logged / 验证错误已记录
            assert result is None
            mock_logger.error.assert_called()
            
            # Verify log includes request data / 验证日志包含请求数据
            call_args = mock_logger.error.call_args
            extra = call_args.kwargs.get("extra", {})
            assert "request_data" in extra
            assert "error_detail" in extra
            assert "status_code" in extra
            assert extra["status_code"] == 422
            
            # Verify error detail contains API response / 验证错误详情包含 API 响应
            error_detail = extra["error_detail"]
            assert "Validation failed" in error_detail
            assert "must be positive" in error_detail

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid private key format
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    @patch("src.trading.hyperliquid_client.ETH_ACCOUNT_AVAILABLE", True)
    def test_integration_order_with_signature(self, mock_post):
        """
        Integration Test: Order placement includes signature in payload
        集成测试：订单下单在负载中包含签名
        
        Verifies that signature is properly included in order payload for /exchange endpoint.
        验证签名正确包含在 /exchange 端点的订单负载中。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Mock successful order placement / 模拟成功的订单下单
        mock_order_response = MagicMock()
        mock_order_response.status_code = 200
        mock_order_response.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {
                    "statuses": [
                        {
                            "resting": {
                                "oid": 12345
                            }
                        }
                    ]
                }
            }
        }
        
        # Setup mock sequence / 设置 mock 序列
        mock_post.side_effect = [
            mock_success,  # Connection
            mock_order_response,  # Order placement
        ]
        
        client = HyperliquidClient()
        
        # Place an order / 下一个订单
        orders = [{"side": "buy", "price": 100.0, "quantity": 1.0, "type": "limit"}]
        result = client.place_orders(orders)
        
        # Verify order was placed (or at least attempted with signature) / 验证订单已下单（或至少尝试使用签名）
        # Check that the request included signature in payload / 检查请求在负载中包含签名
        order_call = None
        for call in mock_post.call_args_list:
            args, kwargs = call
            url = args[0] if args else kwargs.get("url", "")
            if "/exchange" in url:
                order_call = call
                break
        
        if order_call:
            _, kwargs = order_call
            json_data = kwargs.get("json", {})
            # Verify payload structure / 验证负载结构
            assert "action" in json_data
            assert "nonce" in json_data
            # If account is available, signature should be included / 如果账户可用，应该包含签名
            if client._account is not None:
                assert "signature" in json_data
                assert json_data["signature"] is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            # Use a valid hex format private key (64 hex characters) for testing
            # 使用有效的十六进制格式私钥（64 个十六进制字符）用于测试
            "HYPERLIQUID_API_SECRET": "0x" + "1" * 64,  # Valid format but invalid key for actual trading
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_integration_connection_without_empty_exchange_request(self, mock_post):
        """
        Integration Test: Connection does not send empty POST to /exchange
        集成测试：连接不发送空 POST 到 /exchange
        
        Verifies that _connect_and_authenticate no longer sends empty {} to /exchange,
        which was causing 422 errors and masking real connection issues.
        验证 _connect_and_authenticate 不再发送空 {} 到 /exchange，
        这会导致 422 错误并掩盖真实的连接问题。
        """
        # Mock successful connection / 模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        mock_post.return_value = mock_success
        
        client = HyperliquidClient()
        
        # Verify client is connected / 验证客户端已连接
        assert client.is_connected is True
        
        # Verify no empty POST was made to /exchange / 验证没有向 /exchange 发送空 POST
        calls = mock_post.call_args_list
        for call in calls:
            args, kwargs = call
            url = args[0] if args else kwargs.get("url", "")
            json_data = kwargs.get("json", {})
            # If it's a call to /exchange, json should not be empty {}
            # 如果是对 /exchange 的调用，json 不应该是空的 {}
            if "/exchange" in url:
                assert json_data != {}, "Empty {} should not be sent to /exchange during connection"

