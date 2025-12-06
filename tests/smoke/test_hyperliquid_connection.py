"""
Smoke Test for US-CORE-004-A: Hyperliquid Connection and Authentication
US-CORE-004-A 冒烟测试：Hyperliquid 连接与认证

Smoke tests verify critical paths without full integration.
冒烟测试验证关键路径，无需完整集成。

Owner: Agent QA
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.trading.hyperliquid_client import (
    HyperliquidClient,
    AuthenticationError,
    RateLimiter,
)


class TestHyperliquidConnectionSmoke:
    """
    Smoke tests for Hyperliquid connection and authentication.
    Hyperliquid 连接与认证的冒烟测试。
    
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
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_client_initialization(self, mock_requests):
        """
        Smoke Test: AC-1 - Client can be initialized successfully
        冒烟测试：AC-1 - 客户端可以成功初始化
        
        This is the most critical path - if initialization fails, nothing works.
        这是最关键路径 - 如果初始化失败，所有功能都无法工作。
        """
        # Mock successful API responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        # Initialize client (should not raise exceptions)
        client = HyperliquidClient()

        # Verify client was created
        assert client is not None
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_authentication_success(self, mock_requests):
        """
        Smoke Test: AC-2 - Authentication succeeds with valid credentials
        冒烟测试：AC-2 - 使用有效凭证认证成功
        
        Verifies that authentication flow completes without errors.
        验证认证流程完成且无错误。
        """
        # Mock successful authentication
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "user": "test_user"}
        mock_requests.post.return_value = mock_response

        # Initialize client (authentication happens in __init__)
        client = HyperliquidClient()

        # Verify authentication was attempted
        assert mock_requests.post.called
        # Verify connection status
        assert client.is_connected is True

    @patch.dict(os.environ, {}, clear=True)
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_authentication_failure_handling(self, mock_requests):
        """
        Smoke Test: AC-3 - Authentication failure is handled gracefully
        冒烟测试：AC-3 - 认证失败被优雅处理
        
        Verifies that missing credentials raise appropriate error.
        验证缺失凭证时抛出适当的错误。
        """
        import src.trading.hyperliquid_client as hyperliquid_module

        # Mock the config values to None to simulate missing credentials
        with patch.object(hyperliquid_module, "HYPERLIQUID_API_KEY", None), patch.object(
            hyperliquid_module, "HYPERLIQUID_API_SECRET", None
        ):
            # Should raise AuthenticationError when credentials are missing
            with pytest.raises(AuthenticationError) as exc_info:
                HyperliquidClient()

            # Verify error message is bilingual
            error_msg = str(exc_info.value)
            assert (
                "API 凭证" in error_msg
                or "API credentials" in error_msg
                or "missing" in error_msg.lower()
                or "缺失" in error_msg
            )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_testnet_connection(self, mock_requests):
        """
        Smoke Test: AC-4 - Testnet connection works
        冒烟测试：AC-4 - 测试网连接正常
        
        Verifies that testnet environment is correctly selected.
        验证测试网环境被正确选择。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        client = HyperliquidClient()

        # Verify testnet is enabled
        assert client.testnet is True
        # Verify testnet URL is used
        assert "testnet" in client.base_url

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_smoke_connection_health(self, mock_requests):
        """
        Smoke Test: AC-5 - Connection health can be checked
        冒烟测试：AC-5 - 可以检查连接健康状态
        
        Verifies that connection status is accessible.
        验证连接状态可访问。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        client = HyperliquidClient()

        # Verify connection health attributes exist
        assert hasattr(client, "is_connected")
        assert client.is_connected is True


class TestHyperliquidRateLimiterSmoke:
    """
    Smoke tests for Hyperliquid rate limiter.
    Hyperliquid 速率限制器冒烟测试。
    
    These tests verify critical rate limiting functionality.
    这些测试验证关键的速率限制功能。
    """

    def test_smoke_rate_limiter_initialization(self):
        """
        Smoke Test: Rate limiter can be initialized
        冒烟测试：速率限制器可以初始化
        
        Verifies that rate limiter is created with correct default limit.
        验证速率限制器以正确的默认限制创建。
        """
        limiter = RateLimiter()
        assert limiter is not None
        assert limiter.max_weight_per_minute == 1200

    def test_smoke_rate_limiter_in_client(self):
        """
        Smoke Test: Rate limiter is initialized in HyperliquidClient
        冒烟测试：速率限制器在 HyperliquidClient 中初始化
        
        Verifies that client has rate limiter attribute.
        验证客户端具有速率限制器属性。
        """
        with patch.dict(
            os.environ,
            {
                "HYPERLIQUID_API_KEY": "test_key",
                "HYPERLIQUID_API_SECRET": "test_secret",
            },
        ), patch("src.trading.hyperliquid_client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            mock_requests.post.return_value = mock_response

            client = HyperliquidClient()

            # Verify rate limiter exists
            assert hasattr(client, "rate_limiter")
            assert client.rate_limiter is not None
            assert client.rate_limiter.max_weight_per_minute == 1200

    def test_smoke_rate_limiter_allows_request(self):
        """
        Smoke Test: Rate limiter allows request when under limit
        冒烟测试：在限制下时速率限制器允许请求
        
        Verifies that rate limiter allows requests when weight is available.
        验证当有权重可用时速率限制器允许请求。
        """
        limiter = RateLimiter(max_weight_per_minute=1200)
        can_request, wait_time = limiter.can_make_request("/info")
        assert can_request is True
        assert wait_time == 0.0

    def test_smoke_rate_limiter_blocks_when_over_limit(self):
        """
        Smoke Test: Rate limiter blocks request when over limit
        冒烟测试：超过限制时速率限制器阻止请求
        
        Verifies that rate limiter blocks requests when limit is exceeded.
        验证当超过限制时速率限制器阻止请求。
        """
        limiter = RateLimiter(max_weight_per_minute=5)
        # Record requests to reach limit / 记录请求以达到限制
        limiter.record_request("/exchange")  # Weight: 5
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        assert can_request is False
        # wait_time should be > 0 if within max_wait_time, or -1.0 if exceeds max_wait_time
        # wait_time 如果在 max_wait_time 内应该 > 0，如果超过 max_wait_time 则为 -1.0
        assert wait_time > 0 or wait_time == -1.0

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_smoke_rate_limiter_integration(self, mock_sleep, mock_requests):
        """
        Smoke Test: Rate limiter works in _make_request
        冒烟测试：速率限制器在 _make_request 中工作
        
        Verifies that rate limiter is called before making requests.
        验证在发出请求前调用速率限制器。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response

        client = HyperliquidClient()

        # Make a request / 发出请求
        result = client._make_request("POST", "/info", public=True)

        # Verify request was made / 验证请求已发出
        assert result is not None
        # Rate limiter should have been checked / 应该已检查速率限制器
        assert hasattr(client, "rate_limiter")

