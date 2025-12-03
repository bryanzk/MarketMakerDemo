"""
Unit tests for HyperliquidClient connection and authentication
HyperliquidClient 连接与认证单元测试

Tests for US-CORE-004-A: Hyperliquid Connection and Authentication
测试 US-CORE-004-A: Hyperliquid 连接与认证

Owner: Agent TRADING
"""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Note: This test assumes HyperliquidClient will be implemented in src/trading/hyperliquid_client.py
# 注意：此测试假设 HyperliquidClient 将在 src/trading/hyperliquid_client.py 中实现
# According to TDD principles, tests are written first and will fail until implementation is complete
# 根据 TDD 原则，先编写测试，在实现完成前测试会失败


class TestHyperliquidClientInitialization:
    """Test AC-1: Hyperliquid Client Implementation / 测试 AC-1: Hyperliquid 客户端实现"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_api_key",
            "HYPERLIQUID_API_SECRET": "test_api_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_init_with_testnet_config(self, mock_requests):
        """Test initialization with testnet configuration / 测试使用测试网配置初始化"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient(testnet=True)

        # Verify testnet URL is used (correct testnet endpoint)
        assert client.base_url == "https://api.hyperliquid-testnet.xyz"
        assert client.testnet is True
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_api_key",
            "HYPERLIQUID_API_SECRET": "test_api_secret",
        },
        clear=False,
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_init_with_mainnet_config(self, mock_requests):
        """Test initialization with mainnet configuration / 测试使用主网配置初始化"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient(testnet=False)

        # Verify mainnet URL is used
        assert client.base_url == "https://api.hyperliquid.xyz"
        assert client.testnet is False

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_api_key",
            "HYPERLIQUID_API_SECRET": "test_api_secret",
            "HYPERLIQUID_TESTNET": "false",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_init_reads_env_vars(self, mock_requests):
        """Test that initialization reads environment variables / 测试初始化读取环境变量"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Verify environment variables are read
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
        assert client.testnet is False

    @patch.dict(os.environ, {}, clear=True)
    @patch("src.trading.hyperliquid_client.requests")
    def test_init_with_explicit_credentials(self, mock_requests):
        """Test initialization with explicit credentials / 测试使用显式凭证初始化"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient(
            api_key="explicit_key", api_secret="explicit_secret", testnet=True
        )

        assert client.api_key == "explicit_key"
        assert client.api_secret == "explicit_secret"
        assert client.testnet is True


class TestHyperliquidClientAuthentication:
    """Test AC-2: Authentication Success / 测试 AC-2: 认证成功"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "valid_key",
            "HYPERLIQUID_API_SECRET": "valid_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_success(self, mock_requests):
        """Test successful authentication with valid credentials / 测试使用有效凭证成功认证"""
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok", "user": "test_user"}
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Authentication should happen during __init__
        # Verify that authentication was attempted
        assert mock_requests.post.called
        # Check that connection is established
        assert client.is_connected is True

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "valid_key",
            "HYPERLIQUID_API_SECRET": "valid_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_returns_connection_status(self, mock_requests):
        """Test that authentication returns connection status / 测试认证返回连接状态"""
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        # Also mock get for health check
        mock_requests.get.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Should have connection status
        status = client.get_connection_status()
        assert status["connected"] is True
        assert "last_successful_call" in status


class TestHyperliquidClientAuthenticationFailure:
    """Test AC-3: Authentication Failure Handling / 测试 AC-3: 认证失败处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "invalid_key",
            "HYPERLIQUID_API_SECRET": "invalid_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_failure_invalid_credentials(self, mock_requests):
        """Test authentication failure with invalid credentials / 测试使用无效凭证认证失败"""
        # Mock authentication failure response
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid API key"}
        mock_response.text = '{"error": "Invalid API key"}'
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import (
            HyperliquidClient,
            AuthenticationError,
        )

        # Should raise AuthenticationError with bilingual message
        with pytest.raises(AuthenticationError) as exc_info:
            HyperliquidClient()

        error_message = str(exc_info.value)
        # Verify bilingual error message
        assert "认证失败" in error_message or "Authentication failed" in error_message
        assert "Invalid API key" in error_message or "无效的 API 密钥" in error_message

    @patch.dict(os.environ, {}, clear=True)
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_failure_missing_credentials(self, mock_requests):
        """Test authentication failure with missing credentials / 测试缺少凭证时认证失败"""
        from src.trading.hyperliquid_client import (
            HyperliquidClient,
            AuthenticationError,
        )
        import src.trading.hyperliquid_client as hyperliquid_module

        # Mock the config values to None
        with patch.object(hyperliquid_module, "HYPERLIQUID_API_KEY", None), patch.object(
            hyperliquid_module, "HYPERLIQUID_API_SECRET", None
        ):
            # Should raise AuthenticationError when credentials are missing
            with pytest.raises(AuthenticationError) as exc_info:
                HyperliquidClient()

            error_message = str(exc_info.value)
            # Verify bilingual error message
            assert (
                "API 凭证" in error_message
                or "API credentials" in error_message
                or "missing" in error_message.lower()
                or "缺失" in error_message
            )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_authentication_failure_network_error(self, mock_requests):
        """Test authentication failure due to network error / 测试网络错误导致的认证失败"""
        # Mock network error
        import requests

        mock_requests.post.side_effect = requests.exceptions.ConnectionError(
            "Connection timeout"
        )

        from src.trading.hyperliquid_client import HyperliquidClient, ConnectionError

        # Should raise ConnectionError with bilingual message
        with pytest.raises(ConnectionError) as exc_info:
            HyperliquidClient()

        error_message = str(exc_info.value)
        # Verify bilingual error message
        assert (
            "连接失败" in error_message
            or "Connection failed" in error_message
            or "网络" in error_message
            or "network" in error_message.lower()
        )


class TestHyperliquidClientTestnetMainnet:
    """Test AC-4: Testnet and Mainnet Support / 测试 AC-4: 测试网和主网支持"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "true",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_connects_to_testnet(self, mock_requests):
        """Test connection to testnet environment / 测试连接到测试网环境"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient(testnet=True)

        # Verify testnet URL (correct testnet endpoint)
        assert client.base_url == "https://api.hyperliquid-testnet.xyz"
        # Verify that API calls use testnet URL
        assert any(
            "api.hyperliquid-testnet.xyz" in str(call)
            for call in mock_requests.post.call_args_list
        )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
            "HYPERLIQUID_TESTNET": "false",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_connects_to_mainnet(self, mock_requests):
        """Test connection to mainnet environment / 测试连接到主网环境"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient(testnet=False)

        # Verify mainnet URL
        assert client.base_url == "https://api.hyperliquid.xyz"
        # Verify that API calls use mainnet URL
        assert any(
            "api.hyperliquid.xyz" in str(call)
            for call in mock_requests.post.call_args_list
        )

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
        clear=False,
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_defaults_to_mainnet_when_not_specified(self, mock_requests):
        """Test that mainnet is default when testnet not specified / 测试未指定时默认为主网"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Should default to mainnet
        assert client.base_url == "https://api.hyperliquid.xyz"
        assert client.testnet is False


class TestHyperliquidClientHealthMonitoring:
    """Test AC-5: Health Monitoring / 测试 AC-5: 健康监控"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_health_monitoring_returns_status(self, mock_requests):
        """Test health monitoring returns connection status / 测试健康监控返回连接状态"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Get health status
        health = client.get_connection_status()

        # Verify health status structure
        assert "connected" in health
        assert isinstance(health["connected"], bool)
        assert health["connected"] is True

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_health_monitoring_returns_last_successful_call_timestamp(
        self, mock_requests
    ):
        """Test health monitoring returns last successful API call timestamp / 测试健康监控返回最后一次成功的 API 调用时间戳"""
        import time

        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Get health status
        health = client.get_connection_status()

        # Verify timestamp is present
        assert "last_successful_call" in health
        assert isinstance(health["last_successful_call"], (int, float))
        # Timestamp should be recent (within last minute)
        assert time.time() - health["last_successful_call"] < 60

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_health_monitoring_shows_disconnected_when_connection_lost(
        self, mock_requests
    ):
        """Test health monitoring shows disconnected when connection is lost / 测试连接丢失时健康监控显示已断开"""
        # Mock successful initial connection
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Simulate connection loss on POST request (used by health check)
        # Note: Hyperliquid uses POST for /info endpoint
        mock_requests.post.side_effect = Exception("Connection lost")

        # Health check should show disconnected
        health = client.get_connection_status()
        assert health["connected"] is False


class TestHyperliquidClientConnectionErrorHandling:
    """Test AC-6: Connection Error Handling / 测试 AC-6: 连接错误处理"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_connection_error_with_retry_mechanism(self, mock_sleep, mock_requests):
        """Test connection error handling with retry mechanism / 测试带重试机制的连接错误处理"""
        import requests

        # Mock initial failure, then success
        # Note: _connect_and_authenticate makes 2 POST calls: /info and /exchange
        # So we need to mock both calls
        mock_requests.post.side_effect = [
            requests.exceptions.ConnectionError("Connection timeout"),  # First attempt /info fails
            requests.exceptions.ConnectionError("Connection timeout"),  # First attempt /exchange fails
            MagicMock(status_code=200, json=lambda: {"status": "ok"}),  # Second attempt /info succeeds
            MagicMock(status_code=200, json=lambda: {"status": "ok"}),  # Second attempt /exchange succeeds
        ]

        from src.trading.hyperliquid_client import HyperliquidClient

        # Should retry and eventually succeed
        client = HyperliquidClient()

        # Verify retry was attempted
        assert mock_requests.post.call_count >= 2
        # Verify exponential backoff was used
        assert mock_sleep.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_connection_error_exponential_backoff(self, mock_sleep, mock_requests):
        """Test exponential backoff in retry mechanism / 测试重试机制中的指数退避"""
        import requests

        # Mock multiple failures
        mock_requests.post.side_effect = requests.exceptions.ConnectionError(
            "Connection timeout"
        )

        from src.trading.hyperliquid_client import HyperliquidClient, ConnectionError

        # Should raise ConnectionError after retries exhausted
        with pytest.raises(ConnectionError):
            HyperliquidClient()

        # Verify exponential backoff was used (sleep times should increase)
        if mock_sleep.call_count > 1:
            sleep_times = [call[0][0] for call in mock_sleep.call_args_list]
            # Check that sleep times are increasing (exponential backoff)
            for i in range(1, len(sleep_times)):
                assert sleep_times[i] >= sleep_times[i - 1]

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_connection_error_graceful_handling(self, mock_requests):
        """Test graceful handling of connection errors / 测试优雅处理连接错误"""
        import requests

        # Mock connection error
        mock_requests.post.side_effect = requests.exceptions.ConnectionError(
            "Network unreachable"
        )

        from src.trading.hyperliquid_client import HyperliquidClient, ConnectionError

        # Should raise ConnectionError with user-friendly message
        with pytest.raises(ConnectionError) as exc_info:
            HyperliquidClient()

        error_message = str(exc_info.value)
        # Verify bilingual error message
        assert (
            "连接" in error_message
            or "Connection" in error_message
            or "网络" in error_message
            or "network" in error_message.lower()
        )


class TestHyperliquidClientInterfaceConsistency:
    """Test that HyperliquidClient implements same interface as BinanceClient / 测试 HyperliquidClient 实现与 BinanceClient 相同的接口"""

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_implements_exchange_client_interface(self, mock_requests):
        """Test that HyperliquidClient implements ExchangeClient interface / 测试 HyperliquidClient 实现 ExchangeClient 接口"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.get.return_value = mock_response
        mock_requests.post.return_value = mock_response

        from src.trading.hyperliquid_client import HyperliquidClient

        client = HyperliquidClient()

        # Verify required methods exist (from ExchangeClient interface)
        required_methods = [
            "set_symbol",
            "get_leverage",
            "set_leverage",
            "get_max_leverage",
            "get_symbol_limits",
            "fetch_market_data",
            "fetch_funding_rate",
            "fetch_account_data",
            "fetch_open_orders",
            "place_orders",
            "cancel_orders",
            "cancel_all_orders",
        ]

        for method_name in required_methods:
            assert hasattr(
                client, method_name
            ), f"HyperliquidClient missing required method: {method_name}"
            assert callable(
                getattr(client, method_name)
            ), f"HyperliquidClient.{method_name} is not callable"
