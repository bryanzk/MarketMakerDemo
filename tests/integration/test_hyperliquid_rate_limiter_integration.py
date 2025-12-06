"""
Integration tests for HyperliquidClient rate limiter
HyperliquidClient 速率限制器集成测试

Tests for rate limiting functionality in real API call scenarios
测试真实 API 调用场景中的速率限制功能

Owner: Agent QA
"""

import os
import time
from unittest.mock import MagicMock, patch

import pytest
import requests
from requests.exceptions import HTTPError

from src.trading.hyperliquid_client import HyperliquidClient, RateLimiter


class TestRateLimiterAPIIntegration:
    """
    Integration tests for rate limiter with API calls.
    速率限制器与 API 调用的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_rate_limiter_prevents_exceeding_limit(self, mock_sleep, mock_requests):
        """
        Integration Test: Rate limiter prevents exceeding API limit
        集成测试：速率限制器防止超过 API 限制
        
        Verifies that rate limiter automatically waits when approaching limit.
        验证速率限制器在接近限制时自动等待。
        """
        # Mock successful API responses / 模拟成功的 API 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()

        # Set a low limit for testing / 设置低限制用于测试
        client.rate_limiter.max_weight_per_minute = 10

        # Record requests to approach limit / 记录请求以接近限制
        client.rate_limiter.record_request("/exchange")  # Weight: 5
        client.rate_limiter.record_request("/exchange")  # Weight: 5, total: 10

        # Next request should trigger wait / 下一个请求应该触发等待
        result = client._make_request("GET", "/info", public=True)

        # Verify sleep was called (rate limiter waited) / 验证 sleep 被调用（速率限制器等待）
        assert mock_sleep.called
        # Verify request still succeeded / 验证请求仍然成功
        assert result is not None

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_rate_limiter_tracks_weights_correctly(self, mock_requests):
        """
        Integration Test: Rate limiter tracks request weights correctly
        集成测试：速率限制器正确跟踪请求权重
        
        Verifies that different endpoints have correct weights.
        验证不同端点具有正确的权重。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()

        # Make requests to different endpoints / 向不同端点发出请求
        client._make_request("GET", "/info", public=True)  # Weight: 1
        client._make_request("POST", "/exchange", public=True)  # Weight: 5

        # Verify weights are tracked / 验证权重被跟踪
        assert client.rate_limiter.get_current_weight() == 6

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_rate_limiter_handles_429_errors(self, mock_requests):
        """
        Integration Test: Rate limiter works with 429 error handling
        集成测试：速率限制器与 429 错误处理配合工作
        
        Verifies that rate limiter and 429 retry logic work together.
        验证速率限制器和 429 重试逻辑协同工作。
        """
        # Mock 429 response first, then success / 首先模拟 429 响应，然后成功
        mock_429 = MagicMock()
        mock_429.status_code = 429
        mock_429.headers = {"Retry-After": "10"}
        mock_429.raise_for_status.side_effect = HTTPError(
            "Rate limit exceeded", response=mock_429
        )

        mock_success = MagicMock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"status": "ok"}

        # HyperliquidClient.__init__ makes multiple POST calls (info + exchange)
        # Ensure side_effect covers init + test request sequence:
        # 1) Connection attempt (/info)
        # 2) Authentication attempt (/exchange)
        # 3) Test request returning 429
        # 4) Retry request returning success
        mock_requests.post.side_effect = [
            mock_success,  # _connect_and_authenticate /info
            mock_success,  # _connect_and_authenticate /exchange
            mock_429,      # First test request -> 429
            mock_success,  # Retry succeeds
        ]
        mock_requests.get.return_value = mock_success
        mock_requests.exceptions = requests.exceptions

        client = HyperliquidClient()

        # Make request that triggers 429 / 发出触发 429 的请求
        with patch("src.trading.hyperliquid_client.time.sleep") as mock_sleep:
            result = client._make_request("POST", "/exchange", public=True, max_retries=1)

            # Should retry after 429 / 应该在 429 后重试
            assert mock_sleep.called
            # Should eventually succeed / 应该最终成功
            assert result is not None


class TestRateLimiterSustainedLoad:
    """
    Integration tests for rate limiter under sustained load.
    持续负载下速率限制器的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_sustained_request_rate(self, mock_sleep, mock_requests):
        """
        Integration Test: Rate limiter handles sustained request rate
        集成测试：速率限制器处理持续请求速率
        
        Verifies that rate limiter maintains compliance over time.
        验证速率限制器随时间保持合规。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()

        # Set realistic limit / 设置实际限制
        client.rate_limiter.max_weight_per_minute = 1200

        # Simulate sustained requests / 模拟持续请求
        request_count = 0
        sleep_count = 0

        for i in range(50):
            result = client._make_request("GET", "/info", public=True)
            request_count += 1
            if mock_sleep.called:
                sleep_count += 1
                mock_sleep.reset_mock()

        # All requests should succeed / 所有请求应该成功
        assert request_count == 50
        # Rate limiter should prevent exceeding limit / 速率限制器应该防止超过限制
        assert client.rate_limiter.get_current_weight() <= 1200

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_weight_cleanup_over_time(self, mock_requests):
        """
        Integration Test: Rate limiter cleans up old weights
        集成测试：速率限制器清理旧权重
        
        Verifies that old weights are removed after time window.
        验证旧权重在时间窗口后被移除。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()

        # Record old request manually / 手动记录旧请求
        old_time = time.time() - 65  # 65 seconds ago / 65 秒前
        client.rate_limiter.weight_history.append((old_time, 5))

        # Make a new request / 发出新请求
        client._make_request("GET", "/info", public=True)

        # Old weight should be cleaned up / 旧权重应该被清理
        # Current weight should only include recent request / 当前权重应该只包括最近的请求
        current_weight = client.rate_limiter.get_current_weight()
        assert current_weight == 1  # Only /info request / 只有 /info 请求


class TestRateLimiterConcurrentRequests:
    """
    Integration tests for rate limiter with concurrent requests.
    并发请求下速率限制器的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_concurrent_requests_respect_limit(self, mock_requests):
        """
        Integration Test: Concurrent requests respect rate limit
        集成测试：并发请求遵守速率限制
        
        Verifies that rate limiter works correctly with concurrent requests.
        验证速率限制器在并发请求时正确工作。
        """
        import threading

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()
        client.rate_limiter.max_weight_per_minute = 50

        results = []
        errors = []

        def make_request():
            try:
                result = client._make_request("GET", "/info", public=True)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Create multiple threads / 创建多个线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads / 等待所有线程
        for thread in threads:
            thread.join()

        # All requests should succeed / 所有请求应该成功
        assert len(results) == 10
        assert len(errors) == 0
        # Total weight should be tracked correctly / 总权重应该被正确跟踪
        assert client.rate_limiter.get_current_weight() == 10


class TestRateLimiterRealWorldScenarios:
    """
    Integration tests for real-world rate limiting scenarios.
    真实世界速率限制场景的集成测试。
    """

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    @patch("src.trading.hyperliquid_client.time.sleep")
    def test_rapid_succession_requests(self, mock_sleep, mock_requests):
        """
        Integration Test: Rapid succession requests are rate limited
        集成测试：快速连续请求被速率限制
        
        Verifies that rapid requests don't exceed limit.
        验证快速请求不会超过限制。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()
        client.rate_limiter.max_weight_per_minute = 10

        # Make rapid requests / 发出快速请求
        for i in range(5):
            client._make_request("POST", "/exchange", public=True)  # Weight: 5 each

        # Should have triggered rate limiting / 应该触发速率限制
        # Total weight: 5 * 5 = 25, but limit is 10 / 总权重: 5 * 5 = 25，但限制是 10
        # Rate limiter should have waited / 速率限制器应该等待
        assert mock_sleep.called

    @patch.dict(
        os.environ,
        {
            "HYPERLIQUID_API_KEY": "test_key",
            "HYPERLIQUID_API_SECRET": "test_secret",
        },
    )
    @patch("src.trading.hyperliquid_client.requests")
    def test_mixed_endpoint_weights(self, mock_requests):
        """
        Integration Test: Mixed endpoint weights are tracked correctly
        集成测试：混合端点权重被正确跟踪
        
        Verifies that different endpoint types have correct weights.
        验证不同端点类型具有正确的权重。
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_requests.post.return_value = mock_response
        mock_requests.get.return_value = mock_response

        client = HyperliquidClient()

        # Make requests to different endpoints / 向不同端点发出请求
        client._make_request("GET", "/info", public=True)  # Weight: 1
        client._make_request("GET", "/l2_snapshot", public=True)  # Weight: 2
        client._make_request("POST", "/exchange", public=True)  # Weight: 5
        client._make_request("GET", "/unknown", public=True)  # Weight: 5 (default)

        # Verify total weight / 验证总权重
        total_weight = client.rate_limiter.get_current_weight()
        assert total_weight == 13  # 1 + 2 + 5 + 5

