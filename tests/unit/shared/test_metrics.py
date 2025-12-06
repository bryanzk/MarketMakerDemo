"""
Unit tests for metrics module / 指标模块单元测试

Tests for exchange metrics tracking, latency buckets, and error rates.
测试交易所指标跟踪、延迟桶和错误率。

Owner: Agent QA
"""

import time
from unittest.mock import patch

import pytest

from src.shared.exchange_metrics import (
    ExchangeMetrics,
    ExchangeName,
    LatencyBucket,
    MetricsCollector,
    OperationType,
    metrics_collector,
    track_exchange_operation,
)


class TestLatencyBucket:
    """Test LatencyBucket class / 测试 LatencyBucket 类"""

    def test_latency_bucket_add(self):
        """Test adding latency measurements / 测试添加延迟测量"""
        bucket = LatencyBucket()
        bucket.add(0.1)
        bucket.add(0.2)
        bucket.add(0.3)

        assert bucket.count == 3
        assert bucket.total_latency == pytest.approx(0.6, abs=0.01)
        assert bucket.min_latency == 0.1
        assert bucket.max_latency == 0.3
        assert bucket.avg_latency == pytest.approx(0.2, abs=0.01)

    def test_latency_bucket_empty(self):
        """Test empty latency bucket / 测试空延迟桶"""
        bucket = LatencyBucket()
        assert bucket.count == 0
        assert bucket.avg_latency == 0.0


class TestExchangeMetrics:
    """Test ExchangeMetrics class / 测试 ExchangeMetrics 类"""

    def test_record_success(self):
        """Test recording successful operation / 测试记录成功操作"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        metrics.record_success(OperationType.MARKET_DATA, 0.1)

        assert metrics.total_requests == 1
        assert metrics.total_errors == 0
        assert metrics.latency_buckets[OperationType.MARKET_DATA].count == 1
        assert metrics.last_success_time is not None

    def test_record_error(self):
        """Test recording error / 测试记录错误"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        metrics.record_error(
            OperationType.PLACE_ORDER, "Insufficient balance", "InsufficientFunds"
        )

        assert metrics.total_requests == 1
        assert metrics.total_errors == 1
        assert metrics.error_counts[OperationType.PLACE_ORDER] == 1
        assert metrics.last_error_time is not None
        assert metrics.last_error_message == "Insufficient balance"
        assert len(metrics.recent_errors) == 1

    def test_error_rate(self):
        """Test error rate calculation / 测试错误率计算"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        metrics.record_success(OperationType.MARKET_DATA, 0.1)
        metrics.record_success(OperationType.MARKET_DATA, 0.1)
        metrics.record_error(OperationType.PLACE_ORDER, "Error", "ErrorType")

        assert metrics.error_rate == pytest.approx(33.33, abs=0.1)

    def test_error_rate_zero_requests(self):
        """Test error rate with zero requests / 测试零请求时的错误率"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        assert metrics.error_rate == 0.0

    def test_is_healthy(self):
        """Test health check / 测试健康检查"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        metrics.record_success(OperationType.MARKET_DATA, 0.1)

        assert metrics.is_healthy is True

    def test_is_unhealthy_high_error_rate(self):
        """Test unhealthy with high error rate / 测试高错误率时不健康"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        # Record 11 errors out of 100 requests (11% error rate)
        for _ in range(11):
            metrics.record_error(OperationType.MARKET_DATA, "Error", "ErrorType")
        for _ in range(89):
            metrics.record_success(OperationType.MARKET_DATA, 0.1)

        assert metrics.is_healthy is False

    def test_get_summary(self):
        """Test getting metrics summary / 测试获取指标摘要"""
        metrics = ExchangeMetrics(exchange=ExchangeName.BINANCE)
        metrics.record_success(OperationType.MARKET_DATA, 0.1)
        metrics.record_error(OperationType.PLACE_ORDER, "Error", "ErrorType")

        summary = metrics.get_summary()

        assert summary["exchange"] == "binance"
        assert summary["total_requests"] == 2
        assert summary["total_errors"] == 1
        assert "operations" in summary
        assert OperationType.MARKET_DATA.value in summary["operations"]
        assert OperationType.PLACE_ORDER.value in summary["operations"]


class TestMetricsCollector:
    """Test MetricsCollector class / 测试 MetricsCollector 类"""

    def test_get_metrics(self):
        """Test getting metrics for exchange / 测试获取交易所指标"""
        collector = MetricsCollector()
        metrics = collector.get_metrics(ExchangeName.HYPERLIQUID)

        assert metrics.exchange == ExchangeName.HYPERLIQUID
        assert metrics.total_requests == 0

    def test_record_success(self):
        """Test recording success / 测试记录成功"""
        collector = MetricsCollector()
        collector.record_success(ExchangeName.BINANCE, OperationType.MARKET_DATA, 0.1)

        metrics = collector.get_metrics(ExchangeName.BINANCE)
        assert metrics.total_requests == 1
        assert metrics.latency_buckets[OperationType.MARKET_DATA].count == 1

    def test_record_error(self):
        """Test recording error / 测试记录错误"""
        collector = MetricsCollector()
        collector.record_error(
            ExchangeName.HYPERLIQUID,
            OperationType.PLACE_ORDER,
            "Insufficient balance",
            "InsufficientFunds",
        )

        metrics = collector.get_metrics(ExchangeName.HYPERLIQUID)
        assert metrics.total_errors == 1
        assert metrics.error_counts[OperationType.PLACE_ORDER] == 1

    def test_get_all_metrics(self):
        """Test getting all metrics / 测试获取所有指标"""
        collector = MetricsCollector()
        collector.record_success(ExchangeName.BINANCE, OperationType.MARKET_DATA, 0.1)
        collector.record_success(
            ExchangeName.HYPERLIQUID, OperationType.MARKET_DATA, 0.2
        )

        all_metrics = collector.get_all_metrics()

        assert "binance" in all_metrics
        assert "hyperliquid" in all_metrics
        assert all_metrics["binance"]["total_requests"] == 1
        assert all_metrics["hyperliquid"]["total_requests"] == 1

    def test_get_health_summary(self):
        """Test getting health summary / 测试获取健康摘要"""
        collector = MetricsCollector()
        collector.record_success(ExchangeName.BINANCE, OperationType.MARKET_DATA, 0.1)

        health = collector.get_health_summary()

        assert "binance" in health
        assert health["binance"]["is_healthy"] is True
        assert health["binance"]["error_rate"] == 0.0


class TestTrackExchangeOperation:
    """Test track_exchange_operation decorator / 测试 track_exchange_operation 装饰器"""

    @patch("src.shared.tracing.get_trace_id")
    def test_decorator_success(self, mock_get_trace_id):
        """Test decorator with successful operation / 测试成功操作的装饰器"""
        mock_get_trace_id.return_value = "test_trace_id"

        @track_exchange_operation(ExchangeName.BINANCE, OperationType.MARKET_DATA)
        def fetch_market_data():
            time.sleep(0.01)  # Simulate latency
            return {"price": 100.0}

        result = fetch_market_data()

        assert result == {"price": 100.0}
        metrics = metrics_collector.get_metrics(ExchangeName.BINANCE)
        assert metrics.total_requests == 1
        assert metrics.total_errors == 0
        assert metrics.latency_buckets[OperationType.MARKET_DATA].count == 1

    @patch("src.shared.tracing.get_trace_id")
    def test_decorator_error(self, mock_get_trace_id):
        """Test decorator with error / 测试带错误的装饰器"""
        mock_get_trace_id.return_value = "test_trace_id"

        @track_exchange_operation(ExchangeName.HYPERLIQUID, OperationType.PLACE_ORDER)
        def place_order():
            raise ValueError("Invalid order")

        with pytest.raises(ValueError):
            place_order()

        metrics = metrics_collector.get_metrics(ExchangeName.HYPERLIQUID)
        assert metrics.total_requests == 1
        assert metrics.total_errors == 1
        assert metrics.error_counts[OperationType.PLACE_ORDER] == 1


class TestGlobalMetricsCollector:
    """Test global metrics_collector instance / 测试全局 metrics_collector 实例"""

    def test_global_instance(self):
        """Test global metrics collector instance / 测试全局指标收集器实例"""
        assert metrics_collector is not None
        assert isinstance(metrics_collector, MetricsCollector)

    def test_global_instance_records_metrics(self):
        """Test global instance records metrics / 测试全局实例记录指标"""
        # Reset by getting fresh metrics
        metrics = metrics_collector.get_metrics(ExchangeName.BINANCE)
        initial_requests = metrics.total_requests

        metrics_collector.record_success(ExchangeName.BINANCE, OperationType.MARKET_DATA, 0.1)

        metrics = metrics_collector.get_metrics(ExchangeName.BINANCE)
        assert metrics.total_requests == initial_requests + 1

