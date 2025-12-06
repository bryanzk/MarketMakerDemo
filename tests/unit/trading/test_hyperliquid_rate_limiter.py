"""
Unit tests for HyperliquidClient rate limiter
HyperliquidClient 速率限制器单元测试

Tests for rate limiting functionality to comply with Hyperliquid API restrictions
测试速率限制功能以符合 Hyperliquid API 限制

Owner: Agent TRADING
"""

import time
from unittest.mock import patch

import pytest

from src.trading.hyperliquid_client import RateLimiter


class TestRateLimiterInitialization:
    """Test RateLimiter initialization / 测试 RateLimiter 初始化"""

    def test_init_with_default_limit(self):
        """Test initialization with default limit / 测试使用默认限制初始化"""
        limiter = RateLimiter()
        assert limiter.max_weight_per_minute == 1200
        assert len(limiter.weight_history) == 0

    def test_init_with_custom_limit(self):
        """Test initialization with custom limit / 测试使用自定义限制初始化"""
        limiter = RateLimiter(max_weight_per_minute=600)
        assert limiter.max_weight_per_minute == 600

    def test_endpoint_weights_initialized(self):
        """Test endpoint weights are initialized / 测试端点权重已初始化"""
        limiter = RateLimiter()
        assert "/info" in limiter.endpoint_weights
        assert "/exchange" in limiter.endpoint_weights
        assert limiter.endpoint_weights["/info"] == 1
        assert limiter.endpoint_weights["/exchange"] == 5


class TestRateLimiterEndpointWeight:
    """Test endpoint weight calculation / 测试端点权重计算"""

    def test_get_exact_match_weight(self):
        """Test getting weight for exact endpoint match / 测试获取精确匹配端点的权重"""
        limiter = RateLimiter()
        assert limiter.get_endpoint_weight("/info") == 1
        assert limiter.get_endpoint_weight("/exchange") == 5

    def test_get_pattern_match_weight(self):
        """Test getting weight for pattern match / 测试获取模式匹配的权重"""
        limiter = RateLimiter()
        # Test endpoints that start with known patterns / 测试以已知模式开头的端点
        assert limiter.get_endpoint_weight("/info/status") == 1
        assert limiter.get_endpoint_weight("/exchange/orders") == 5

    def test_get_default_weight_for_unknown(self):
        """Test getting default weight for unknown endpoint / 测试获取未知端点的默认权重"""
        limiter = RateLimiter()
        # Unknown endpoint should return default weight (5) / 未知端点应返回默认权重 (5)
        assert limiter.get_endpoint_weight("/unknown/endpoint") == 5


class TestRateLimiterWeightTracking:
    """Test weight tracking functionality / 测试权重跟踪功能"""

    def test_record_request(self):
        """Test recording a request / 测试记录请求"""
        limiter = RateLimiter()
        limiter.record_request("/info")
        assert len(limiter.weight_history) == 1
        assert limiter.weight_history[0][1] == 1  # Weight for /info

    def test_record_multiple_requests(self):
        """Test recording multiple requests / 测试记录多个请求"""
        limiter = RateLimiter()
        limiter.record_request("/info")
        limiter.record_request("/exchange")
        assert len(limiter.weight_history) == 2
        assert limiter.weight_history[0][1] == 1  # First: /info
        assert limiter.weight_history[1][1] == 5  # Second: /exchange

    def test_get_current_weight(self):
        """Test getting current weight / 测试获取当前权重"""
        limiter = RateLimiter()
        limiter.record_request("/info")  # Weight: 1
        limiter.record_request("/exchange")  # Weight: 5
        assert limiter.get_current_weight() == 6

    def test_cleanup_old_weights(self):
        """Test cleanup of old weights / 测试清理旧权重"""
        limiter = RateLimiter()
        # Record a request with old timestamp / 记录一个带旧时间戳的请求
        old_time = time.time() - 70  # 70 seconds ago / 70 秒前
        limiter.weight_history.append((old_time, 5))
        
        # Record a recent request / 记录一个最近的请求
        limiter.record_request("/info")
        
        # Old weight should be cleaned up / 旧权重应该被清理
        assert len(limiter.weight_history) == 1
        assert limiter.weight_history[0][1] == 1  # Only recent request / 只有最近的请求


class TestRateLimiterCanMakeRequest:
    """Test can_make_request functionality / 测试 can_make_request 功能"""

    def test_can_make_request_when_under_limit(self):
        """Test can make request when under limit / 测试在限制下可以发出请求"""
        limiter = RateLimiter(max_weight_per_minute=1200)
        can_request, wait_time = limiter.can_make_request("/info")
        assert can_request is True
        assert wait_time == 0.0

    def test_can_make_request_when_at_limit(self):
        """Test can make request when at limit / 测试在限制处可以发出请求"""
        limiter = RateLimiter(max_weight_per_minute=5)
        limiter.record_request("/exchange")  # Weight: 5, at limit
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        # Should not allow another request / 不应允许另一个请求
        assert can_request is False
        assert wait_time > 0

    def test_can_make_request_when_over_limit(self):
        """Test can make request when over limit / 测试超过限制时不能发出请求"""
        limiter = RateLimiter(max_weight_per_minute=5)
        limiter.record_request("/exchange")  # Weight: 5
        limiter.record_request("/exchange")  # Weight: 5, total: 10 (over limit)
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        assert can_request is False
        assert wait_time > 0

    def test_wait_time_calculation(self):
        """Test wait time calculation / 测试等待时间计算"""
        limiter = RateLimiter(max_weight_per_minute=5)
        # Record request 30 seconds ago / 记录 30 秒前的请求
        old_time = time.time() - 30
        limiter.weight_history.append((old_time, 5))
        
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        assert can_request is False
        # Should wait approximately 30 seconds (60 - 30) / 应该等待大约 30 秒 (60 - 30)
        assert 25 <= wait_time <= 35  # Allow some tolerance / 允许一些容差

    @patch("time.time")
    def test_wait_time_with_mocked_time(self, mock_time):
        """Test wait time with mocked time / 使用模拟时间测试等待时间"""
        current_time = 1000.0
        mock_time.return_value = current_time
        
        limiter = RateLimiter(max_weight_per_minute=5)
        # Record request 45 seconds ago / 记录 45 秒前的请求
        limiter.weight_history.append((current_time - 45, 5))
        
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        assert can_request is False
        # Should wait 15 seconds (60 - 45) / 应该等待 15 秒 (60 - 45)
        assert 14 <= wait_time <= 16


class TestRateLimiterThreadSafety:
    """Test thread safety / 测试线程安全"""

    def test_concurrent_record_requests(self):
        """Test concurrent request recording / 测试并发请求记录"""
        import threading
        
        limiter = RateLimiter()
        results = []
        
        def record_request(endpoint):
            limiter.record_request(endpoint)
            results.append(limiter.get_current_weight())
        
        # Create multiple threads / 创建多个线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=record_request, args=("/info",))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads / 等待所有线程
        for thread in threads:
            thread.join()
        
        # All requests should be recorded / 所有请求都应该被记录
        assert len(limiter.weight_history) == 10
        assert limiter.get_current_weight() == 10  # 10 requests * 1 weight each / 10 个请求 * 每个 1 权重


class TestRateLimiterIntegration:
    """Test rate limiter integration scenarios / 测试速率限制器集成场景"""

    def test_sustained_request_rate(self):
        """Test sustained request rate / 测试持续请求速率"""
        limiter = RateLimiter(max_weight_per_minute=1200)
        
        # Simulate 100 requests with weight 5 each / 模拟 100 个请求，每个权重 5
        for i in range(100):
            limiter.record_request("/exchange")
        
        # Total weight: 100 * 5 = 500, should be under limit / 总权重: 100 * 5 = 500，应该在限制下
        assert limiter.get_current_weight() == 500
        can_request, wait_time = limiter.can_make_request("/exchange")
        assert can_request is True

    def test_rate_limit_enforcement(self):
        """Test rate limit enforcement / 测试速率限制执行"""
        limiter = RateLimiter(max_weight_per_minute=10)
        
        # Record requests until at limit / 记录请求直到达到限制
        limiter.record_request("/exchange")  # Weight: 5
        limiter.record_request("/exchange")  # Weight: 5, total: 10
        
        # Next request should be blocked / 下一个请求应该被阻止
        # Use larger max_wait_time to allow wait time calculation
        # 使用更大的 max_wait_time 以允许等待时间计算
        can_request, wait_time = limiter.can_make_request("/info", max_wait_time=60.0)
        assert can_request is False
        assert wait_time > 0

    def test_weight_reset_after_time_window(self):
        """Test weight reset after time window / 测试时间窗口后权重重置"""
        limiter = RateLimiter(max_weight_per_minute=10)
        
        # Record old request / 记录旧请求
        old_time = time.time() - 65  # 65 seconds ago / 65 秒前
        limiter.weight_history.append((old_time, 5))
        
        # Record recent request / 记录最近的请求
        limiter.record_request("/exchange")  # Weight: 5
        
        # Old weight should be cleaned up / 旧权重应该被清理
        current_weight = limiter.get_current_weight()
        assert current_weight == 5  # Only recent request / 只有最近的请求
        
        # Should be able to make another request / 应该能够发出另一个请求
        can_request, wait_time = limiter.can_make_request("/exchange")
        assert can_request is True

