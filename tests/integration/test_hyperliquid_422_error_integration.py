"""
Integration tests for HyperliquidClient 422 error handling
HyperliquidClient 422 错误处理集成测试

Integration tests verify 422 error handling in realistic scenarios.
集成测试验证实际场景中的 422 错误处理。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, patch

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
            "HYPERLIQUID_API_SECRET": "test_secret",
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
        
        # Mock 422 error for order placement / 模拟订单下单的 422 错误
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Insufficient margin", "code": "MARGIN_ERROR"}'
        mock_422_response.json.return_value = {
            "error": "Insufficient margin",
            "code": "MARGIN_ERROR"
        }
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Setup mock sequence: connection (2 calls), market data, then 422 for order
        # 设置 mock 序列：连接（2 次调用），市场数据，然后订单 422
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
            mock_market_data,  # Market data
            mock_422_response,  # Order placement fails
        ]
        
        client = HyperliquidClient()
        
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
        assert "MARGIN_ERROR" in client.last_order_error.get("api_error", {}).get("error_detail", "")

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
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
        
        # Mock 422 error for first order / 模拟第一个订单的 422 错误
        mock_422_response = MagicMock()
        mock_422_response.status_code = 422
        mock_422_response.text = '{"error": "Invalid price", "field": "price"}'
        mock_422_response.json.return_value = {"error": "Invalid price", "field": "price"}
        mock_422_response.raise_for_status.side_effect = HTTPError(
            response=mock_422_response
        )
        
        # Mock success for second order / 模拟第二个订单成功
        mock_success_order = MagicMock()
        mock_success_order.status_code = 200
        mock_success_order.json.return_value = {
            "status": "ok",
            "response": {
                "type": "order",
                "data": {"statuses": [{"resting": {"oid": 99999}}]},
            },
        }
        
        # Setup mock sequence / 设置 mock 序列
        mock_post.side_effect = [
            mock_success,  # Connection call 1
            mock_success,  # Connection call 2
            mock_422_response,  # First order fails
            mock_success_order,  # Second order succeeds
        ]
        
        client = HyperliquidClient()
        
        # Place multiple orders / 下多个订单
        # First order will fail with 422 from API (not validation)
        # 第一个订单会因 API 返回 422 失败（不是验证失败）
        orders = [
            {"side": "buy", "price": 100.0, "quantity": 0.01, "type": "limit"},  # Will fail with 422 / 会因 422 失败
            {"side": "sell", "price": 2010.0, "quantity": 0.01, "type": "limit"},  # Valid order / 有效订单
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
            "HYPERLIQUID_API_SECRET": "test_secret",
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
            "HYPERLIQUID_API_SECRET": "test_secret",
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

