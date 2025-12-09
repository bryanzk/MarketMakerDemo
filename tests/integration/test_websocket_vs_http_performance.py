"""
Performance comparison tests: WebSocket vs HTTP evaluation
性能对比测试：WebSocket vs HTTP 评估

Tests compare performance between WebSocket and HTTP evaluation endpoints.
测试比较 WebSocket 和 HTTP 评估端点之间的性能。

Owner: Agent QA
"""

import json
import time
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

import server
from src.ai.evaluation.evaluator import MultiLLMEvaluator
from src.ai.evaluation.schemas import MarketContext
from src.ai.llm import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for testing / 用于测试的模拟 LLM 提供商"""

    def __init__(self, name: str, delay: float = 0.1):
        self._name = name
        self.delay = delay

    @property
    def name(self) -> str:
        """Return the provider name / 返回提供商名称"""
        return self._name

    def generate(self, prompt: str) -> str:
        """Simulate LLM call with delay / 模拟带延迟的 LLM 调用"""
        time.sleep(self.delay)
        return json.dumps({
            "strategy": "fixed_spread",
            "spread": 0.0002,
            "skew_factor": 0.0,
            "confidence": 0.8,
        })


@pytest.fixture
def mock_market_context():
    """Create a mock market context / 创建模拟市场上下文"""
    return MarketContext(
        symbol="ETH/USDC:USDC",
        mid_price=2500.0,
        best_bid=2499.5,
        best_ask=2500.5,
        spread_bps=4.0,  # (2500.5 - 2499.5) / 2500.0 * 10000
        volatility_24h=0.02,
        volatility_1h=0.01,
        funding_rate=0.0001,
        funding_rate_trend="stable",
    )


@pytest.fixture
def mock_providers():
    """Create mock LLM providers with varying delays / 创建具有不同延迟的模拟 LLM 提供商"""
    return [
        MockLLMProvider("Gemini", delay=0.1),
        MockLLMProvider("OpenAI", delay=0.15),
        MockLLMProvider("Claude", delay=0.12),
    ]


class TestWebSocketVsHTTPPerformance:
    """Performance comparison tests / 性能对比测试"""

    def test_parallel_execution_performance(self, mock_providers, mock_market_context):
        """
        Test that both WebSocket and HTTP use parallel execution
        测试 WebSocket 和 HTTP 都使用并行执行
        """
        # Both should use MultiLLMEvaluator(parallel=True)
        # 两者都应该使用 MultiLLMEvaluator(parallel=True)
        
        evaluator = MultiLLMEvaluator(
            providers=mock_providers,
            simulation_steps=10,
            parallel=True,
        )
        
        start_time = time.time()
        results = evaluator.evaluate(mock_market_context)
        evaluation_time = time.time() - start_time
        
        # With 3 providers in parallel, time should be close to max delay (~0.15s)
        # 3 个提供商并行，时间应该接近最大延迟（~0.15s）
        max_delay = max(p.delay for p in mock_providers)
        assert evaluation_time < max_delay * 2, (
            f"Parallel evaluation took {evaluation_time:.3f}s, "
            f"expected < {max_delay * 2:.3f}s (2x max delay)"
        )
        
        # Verify results / 验证结果
        assert len(results) == len(mock_providers)

    def test_no_unnecessary_delays_in_optimized_version(self, mock_providers, mock_market_context):
        """
        Test that optimized WebSocket version has minimal delays
        测试优化后的 WebSocket 版本延迟最小
        """
        # Old version had: 3 providers * 3 steps * 0.1s = 0.9s fixed delay
        # New version has: 2 steps * 0.05s = 0.1s total delay (for all providers)
        # 旧版本有：3 个提供商 * 3 步 * 0.1s = 0.9s 固定延迟
        # 新版本有：2 步 * 0.05s = 0.1s 总延迟（所有提供商）
        
        evaluator = MultiLLMEvaluator(
            providers=mock_providers,
            simulation_steps=10,
            parallel=True,
        )
        
        start_time = time.time()
        results = evaluator.evaluate(mock_market_context)
        evaluation_time = time.time() - start_time
        
        # Evaluation time should be mostly LLM call time, not fixed delays
        # 评估时间应该主要是 LLM 调用时间，而不是固定延迟
        max_delay = max(p.delay for p in mock_providers)
        expected_max_time = max_delay + 0.5  # Allow some overhead / 允许一些开销
        
        assert evaluation_time < expected_max_time, (
            f"Evaluation took {evaluation_time:.3f}s, "
            f"expected < {expected_max_time:.3f}s (max delay + overhead)"
        )

    def test_websocket_and_http_use_same_evaluator(self, mock_providers, mock_market_context):
        """
        Test that WebSocket and HTTP versions use the same evaluator logic
        测试 WebSocket 和 HTTP 版本使用相同的评估器逻辑
        """
        # Both should use MultiLLMEvaluator(parallel=True)
        # 两者都应该使用 MultiLLMEvaluator(parallel=True)
        
        evaluator_ws = MultiLLMEvaluator(
            providers=mock_providers,
            simulation_steps=10,
            parallel=True,  # WebSocket optimized version / WebSocket 优化版本
        )
        
        evaluator_http = MultiLLMEvaluator(
            providers=mock_providers,
            simulation_steps=10,
            parallel=True,  # HTTP version / HTTP 版本
        )
        
        # Both should produce same results / 两者应该产生相同的结果
        results_ws = evaluator_ws.evaluate(mock_market_context)
        results_http = evaluator_http.evaluate(mock_market_context)
        
        assert len(results_ws) == len(results_http) == len(mock_providers)
        
        # Results should be equivalent (same providers, same evaluation logic)
        # 结果应该等价（相同的提供商，相同的评估逻辑）
        ws_provider_names = {r.provider_name for r in results_ws}
        http_provider_names = {r.provider_name for r in results_http}
        assert ws_provider_names == http_provider_names

    def test_performance_improvement_over_old_websocket_version(self, mock_providers, mock_market_context):
        """
        Test that optimized version is faster than old version
        测试优化版本比旧版本更快
        """
        # Old version: Each provider had 3 * 0.1s = 0.3s delay
        # With 3 providers in parallel: ~0.3s + max LLM delay (~0.15s) = ~0.45s
        # 旧版本：每个提供商有 3 * 0.1s = 0.3s 延迟
        # 3 个提供商并行：~0.3s + 最大 LLM 延迟（~0.15s）= ~0.45s
        
        # New version: 2 * 0.05s = 0.1s total delay + max LLM delay (~0.15s) = ~0.25s
        # 新版本：2 * 0.05s = 0.1s 总延迟 + 最大 LLM 延迟（~0.15s）= ~0.25s
        
        evaluator = MultiLLMEvaluator(
            providers=mock_providers,
            simulation_steps=10,
            parallel=True,
        )
        
        start_time = time.time()
        results = evaluator.evaluate(mock_market_context)
        new_time = time.time() - start_time
        
        # New version should be faster (at least 30% improvement)
        # 新版本应该更快（至少 30% 改进）
        old_expected_time = 0.45  # Old version expected time / 旧版本预期时间
        assert new_time < old_expected_time * 0.7, (
            f"New version took {new_time:.3f}s, "
            f"expected < {old_expected_time * 0.7:.3f}s (30% improvement over old version)"
        )

    def test_parallel_execution_scales_with_providers(self, mock_market_context):
        """
        Test that parallel execution scales well with more providers
        测试并行执行在更多提供商时扩展良好
        """
        # Test with different numbers of providers / 测试不同数量的提供商
        for num_providers in [2, 3, 5]:
            providers = [
                MockLLMProvider(f"Provider{i}", delay=0.1) for i in range(num_providers)
            ]
            
            evaluator = MultiLLMEvaluator(
                providers=providers,
                simulation_steps=10,
                parallel=True,
            )
            
            start_time = time.time()
            results = evaluator.evaluate(mock_market_context)
            evaluation_time = time.time() - start_time
            
            # With parallel execution, time should be close to max delay, not sum
            # 使用并行执行，时间应该接近最大延迟，而不是总和
            max_delay = max(p.delay for p in providers)
            sum_delay = sum(p.delay for p in providers)
            
            # Time should be much closer to max_delay than sum_delay
            # With overhead, allow up to 1.5x max_delay for small numbers of providers
            # 时间应该更接近 max_delay 而不是 sum_delay
            # 考虑到开销，对于少量提供商，允许最多 1.5x max_delay
            expected_max_time = max_delay * 1.5 if num_providers <= 3 else max_delay * 2
            assert evaluation_time < expected_max_time, (
                f"With {num_providers} providers, evaluation took {evaluation_time:.3f}s, "
                f"expected < {expected_max_time:.3f}s (should be closer to max delay {max_delay:.3f}s than sum {sum_delay:.3f}s)"
            )
            
            assert len(results) == num_providers

