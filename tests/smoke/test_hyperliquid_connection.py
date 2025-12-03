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

from src.trading.hyperliquid_client import HyperliquidClient, AuthenticationError


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

