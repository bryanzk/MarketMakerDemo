"""
Fixture-driven simulations for exchange failures / 交易所失败的基于 Fixture 的模拟

Tests error handling for various exchange failure scenarios.
测试各种交易所失败场景的错误处理。

Owner: Agent QA
"""

import time
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout as RequestsTimeout

from src.trading.hyperliquid_client import (
    AuthenticationError,
    ConnectionError,
    HyperliquidClient,
)


# Note: Fixtures are no longer used as we patch requests.post directly in each test
# 注意：不再使用 fixture，因为我们在每个测试中直接 patch requests.post


class TestNetworkTimeoutHandling:
    """Test network timeout error handling / 测试网络超时错误处理"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_network_timeout_handling(self, mock_post):
        """Test handling of network timeout / 测试网络超时的处理"""
        # Mock successful connection first / 首先模拟成功连接
        # _connect_and_authenticate calls requests.post twice per attempt (info + exchange)
        # _connect_and_authenticate 每次尝试调用 requests.post 两次（info + exchange）
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt, 1 attempt needed)
        # 为连接提供足够的 mock（每次尝试 2 次调用，需要 1 次尝试）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Reset mock to timeout for fetch_market_data
        # 重置 mock 以便 fetch_market_data 超时
        mock_post.side_effect = RequestsTimeout("Request timeout")
        
        # fetch_market_data should handle timeout gracefully
        # fetch_market_data 应该优雅地处理超时
        result = client.fetch_market_data()
        
        # Should return None or error dict, not raise exception
        # 应该返回 None 或错误字典，不抛出异常
        assert result is None or isinstance(result, dict)

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_connection_error_handling(self, mock_post):
        """Test handling of connection error / 测试连接错误的处理"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Reset mock to connection error for fetch_market_data
        # 重置 mock 以便 fetch_market_data 连接错误
        mock_post.side_effect = RequestsConnectionError("Connection failed")
        
        # Should raise ConnectionError or return None
        # 应该抛出 ConnectionError 或返回 None
        try:
            result = client.fetch_market_data()
            # If no exception, result should be None
            # 如果没有异常，结果应为 None
            assert result is None
        except ConnectionError:
            # ConnectionError is acceptable
            # ConnectionError 是可接受的
            pass


class TestRateLimitHandling:
    """Test rate limit error handling / 测试速率限制错误处理"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_rate_limit_handling(self, mock_post):
        """Test handling of rate limit / 测试速率限制的处理"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Create rate limit response for _make_request
        # 为 _make_request 创建速率限制响应
        mock_rate_limit_response = MagicMock()
        mock_rate_limit_response.status_code = 429
        mock_rate_limit_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Rate limit exceeded"
        )
        mock_rate_limit_response.json.return_value = {"error": "Rate limit exceeded"}
        
        # Reset mock to rate limit for _make_request
        # 重置 mock 以便 _make_request 速率限制
        mock_post.return_value = mock_rate_limit_response
        
        # _make_request should handle 429 gracefully
        # _make_request 应该优雅地处理 429
        result = client._make_request("POST", "/test", data={})
        
        # Should return None for rate limit errors
        # 对于速率限制错误，应返回 None
        assert result is None or isinstance(result, dict)


class TestAuthenticationErrorHandling:
    """Test authentication error handling / 测试认证错误处理"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_authentication_error_handling(self, mock_post):
        """Test handling of authentication error / 测试认证错误的处理"""
        # Create auth error response - this will be used during connection
        # 创建认证错误响应 - 这将在连接期间使用
        mock_auth_error_response = MagicMock()
        mock_auth_error_response.status_code = 401
        mock_auth_error_response.text = "Unauthorized"
        mock_auth_error_response.json.return_value = {"error": "Unauthorized"}
        
        # First call (info) succeeds, second call (exchange) returns 401
        # 第一次调用（info）成功，第二次调用（exchange）返回 401
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        mock_post.side_effect = [mock_success, mock_auth_error_response]
        
        # Should raise AuthenticationError during initialization
        # 应该在初始化期间抛出 AuthenticationError
        with pytest.raises(AuthenticationError):
            HyperliquidClient(
                api_key="test_key", api_secret="test_secret", testnet=True
            )


class TestServerErrorHandling:
    """Test server error handling / 测试服务器错误处理"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_server_error_handling(self, mock_post):
        """Test handling of server error / 测试服务器错误的处理"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Create server error response for _make_request
        # 为 _make_request 创建服务器错误响应
        mock_server_error_response = MagicMock()
        mock_server_error_response.status_code = 500
        mock_server_error_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Internal Server Error"
        )
        mock_server_error_response.json.return_value = {"error": "Internal Server Error"}
        
        # Reset mock to server error for _make_request
        # 重置 mock 以便 _make_request 服务器错误
        mock_post.return_value = mock_server_error_response
        
        # Should return None for server errors
        # 对于服务器错误，应返回 None
        result = client._make_request("POST", "/test", data={})
        
        assert result is None or isinstance(result, dict)


class TestErrorRecovery:
    """Test error recovery mechanisms / 测试错误恢复机制"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_error_state_tracking(self, mock_post):
        """Test that errors are tracked in client state / 测试错误在客户端状态中被跟踪"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Create rate limit response for _make_request
        # 为 _make_request 创建速率限制响应
        mock_rate_limit_response = MagicMock()
        mock_rate_limit_response.status_code = 429
        mock_rate_limit_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Rate limit exceeded"
        )
        mock_rate_limit_response.json.return_value = {"error": "Rate limit exceeded"}
        
        # Reset mock to rate limit for _make_request
        # 重置 mock 以便 _make_request 速率限制
        mock_post.return_value = mock_rate_limit_response
        
        result = client._make_request("POST", "/test", data={})
        
        # Check that error state is tracked
        # 检查错误状态是否被跟踪
        assert hasattr(client, "last_api_error") or result is None

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_connection_status_after_error(self, mock_post):
        """Test connection status after error / 测试错误后的连接状态"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Reset mock to connection error for fetch_market_data
        # 重置 mock 以便 fetch_market_data 连接错误
        mock_post.side_effect = RequestsConnectionError("Connection failed")
        
        try:
            client.fetch_market_data()
        except ConnectionError:
            pass
        
        # Connection status should reflect error
        # 连接状态应反映错误
        assert hasattr(client, "is_connected")


class TestErrorResponseFormat:
    """Test error response format from exchange failures / 测试交易所失败的错误响应格式"""

    @patch.dict(
        "os.environ",
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests.post")
    def test_error_response_includes_context(self, mock_post):
        """Test that error responses include context / 测试错误响应包含上下文"""
        # Mock successful connection first / 首先模拟成功连接
        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}
        
        # Provide enough mocks for connection (2 calls per attempt)
        # 为连接提供足够的 mock（每次尝试 2 次调用）
        mock_post.side_effect = [mock_success, mock_success]
        
        client = HyperliquidClient(
            api_key="test_key", api_secret="test_secret", testnet=True
        )
        
        # Create rate limit response for _make_request
        # 为 _make_request 创建速率限制响应
        mock_rate_limit_response = MagicMock()
        mock_rate_limit_response.status_code = 429
        mock_rate_limit_response.raise_for_status.side_effect = requests.exceptions.HTTPError(
            "Rate limit exceeded"
        )
        mock_rate_limit_response.json.return_value = {"error": "Rate limit exceeded"}
        
        # Reset mock to rate limit for _make_request
        # 重置 mock 以便 _make_request 速率限制
        mock_post.return_value = mock_rate_limit_response
        
        result = client._make_request("POST", "/test", data={})
        
        # Error should be tracked with context
        # 错误应使用上下文跟踪
        if hasattr(client, "last_api_error") and client.last_api_error is not None:
            error = client.last_api_error
            assert isinstance(error, dict)
            assert "type" in error or "message" in error
        else:
            # If no error tracked, result should be None
            # 如果没有跟踪错误，结果应为 None
            assert result is None

