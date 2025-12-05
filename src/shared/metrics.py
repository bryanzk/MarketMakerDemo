"""
Metrics Module / 指标模块

Tracks latency buckets, error rates, and exchange health metrics.
跟踪延迟桶、错误率和交易所健康指标。

Owner: Agent ARCH
"""

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from src.shared.tracing import get_trace_id


class ExchangeName(str, Enum):
    """Exchange names / 交易所名称"""

    BINANCE = "binance"
    HYPERLIQUID = "hyperliquid"


class OperationType(str, Enum):
    """Operation types for metrics tracking / 用于指标跟踪的操作类型"""

    MARKET_DATA = "market_data"
    ACCOUNT_DATA = "account_data"
    PLACE_ORDER = "place_order"
    CANCEL_ORDER = "cancel_order"
    FETCH_ORDERS = "fetch_orders"
    FETCH_POSITIONS = "fetch_positions"
    CONNECT = "connect"
    DISCONNECT = "disconnect"


@dataclass
class LatencyBucket:
    """Latency bucket for tracking response times / 用于跟踪响应时间的延迟桶"""

    count: int = 0
    total_latency: float = 0.0
    min_latency: Optional[float] = None
    max_latency: Optional[float] = None

    def add(self, latency: float):
        """Add latency measurement / 添加延迟测量"""
        self.count += 1
        self.total_latency += latency
        if self.min_latency is None or latency < self.min_latency:
            self.min_latency = latency
        if self.max_latency is None or latency > self.max_latency:
            self.max_latency = latency

    @property
    def avg_latency(self) -> float:
        """Average latency / 平均延迟"""
        return self.total_latency / self.count if self.count > 0 else 0.0


@dataclass
class ExchangeMetrics:
    """Metrics for a specific exchange / 特定交易所的指标"""

    exchange: ExchangeName
    total_requests: int = 0
    total_errors: int = 0
    latency_buckets: Dict[OperationType, LatencyBucket] = field(
        default_factory=lambda: defaultdict(LatencyBucket)
    )
    error_counts: Dict[OperationType, int] = field(
        default_factory=lambda: defaultdict(int)
    )
    recent_errors: deque = field(default_factory=lambda: deque(maxlen=100))
    last_success_time: Optional[float] = None
    last_error_time: Optional[float] = None
    last_error_message: Optional[str] = None

    def record_success(self, operation: OperationType, latency: float):
        """Record successful operation / 记录成功操作"""
        self.total_requests += 1
        self.latency_buckets[operation].add(latency)
        self.last_success_time = time.time()

    def record_error(
        self,
        operation: OperationType,
        error_message: str,
        error_type: Optional[str] = None,
    ):
        """Record error / 记录错误"""
        self.total_requests += 1
        self.total_errors += 1
        self.error_counts[operation] += 1
        self.last_error_time = time.time()
        self.last_error_message = error_message

        error_record = {
            "timestamp": time.time(),
            "operation": operation.value,
            "error_message": error_message,
            "error_type": error_type,
            "trace_id": get_trace_id(),
        }
        self.recent_errors.append(error_record)

    @property
    def error_rate(self) -> float:
        """Error rate as percentage / 错误率（百分比）"""
        if self.total_requests == 0:
            return 0.0
        return (self.total_errors / self.total_requests) * 100.0

    @property
    def is_healthy(self) -> bool:
        """Check if exchange is healthy / 检查交易所是否健康"""
        # Consider unhealthy if error rate > 10% or no successful requests in last 5 minutes
        # 如果错误率 > 10% 或过去 5 分钟内没有成功请求，则认为不健康
        if self.error_rate > 10.0:
            return False
        if self.last_success_time is None:
            return False
        if time.time() - self.last_success_time > 300:  # 5 minutes
            return False
        return True

    def get_summary(self) -> Dict:
        """Get metrics summary / 获取指标摘要"""
        return {
            "exchange": self.exchange.value,
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate": round(self.error_rate, 2),
            "is_healthy": self.is_healthy,
            "last_success_time": self.last_success_time,
            "last_error_time": self.last_error_time,
            "last_error_message": self.last_error_message,
            "operations": {
                op.value: {
                    "count": self.latency_buckets[op].count,
                    "avg_latency_ms": round(
                        self.latency_buckets[op].avg_latency * 1000, 2
                    ),
                    "min_latency_ms": (
                        round(self.latency_buckets[op].min_latency * 1000, 2)
                        if self.latency_buckets[op].min_latency is not None
                        else None
                    ),
                    "max_latency_ms": (
                        round(self.latency_buckets[op].max_latency * 1000, 2)
                        if self.latency_buckets[op].max_latency is not None
                        else None
                    ),
                    "error_count": self.error_counts[op],
                }
                for op in OperationType
                if self.latency_buckets[op].count > 0 or self.error_counts[op] > 0
            },
            "recent_errors": list(self.recent_errors)[-10:],  # Last 10 errors
        }


class MetricsCollector:
    """
    Global metrics collector / 全局指标收集器

    Tracks metrics for all exchanges and operations.
    跟踪所有交易所和操作的指标。
    """

    def __init__(self):
        self._metrics: Dict[ExchangeName, ExchangeMetrics] = {}

    def get_metrics(self, exchange: ExchangeName) -> ExchangeMetrics:
        """Get or create metrics for exchange / 获取或创建交易所指标"""
        if exchange not in self._metrics:
            self._metrics[exchange] = ExchangeMetrics(exchange=exchange)
        return self._metrics[exchange]

    def record_success(
        self, exchange: ExchangeName, operation: OperationType, latency: float
    ):
        """Record successful operation / 记录成功操作"""
        metrics = self.get_metrics(exchange)
        metrics.record_success(operation, latency)

    def record_error(
        self,
        exchange: ExchangeName,
        operation: OperationType,
        error_message: str,
        error_type: Optional[str] = None,
    ):
        """Record error / 记录错误"""
        metrics = self.get_metrics(exchange)
        metrics.record_error(operation, error_message, error_type)

    def get_all_metrics(self) -> Dict[str, Dict]:
        """Get all metrics summaries / 获取所有指标摘要"""
        return {
            exchange.value: metrics.get_summary()
            for exchange, metrics in self._metrics.items()
        }

    def get_health_summary(self) -> Dict:
        """Get health summary for all exchanges / 获取所有交易所的健康摘要"""
        return {
            exchange.value: {
                "is_healthy": metrics.is_healthy,
                "error_rate": round(metrics.error_rate, 2),
                "total_requests": metrics.total_requests,
                "total_errors": metrics.total_errors,
                "last_success_time": metrics.last_success_time,
                "last_error_time": metrics.last_error_time,
            }
            for exchange, metrics in self._metrics.items()
        }


# Global metrics collector instance / 全局指标收集器实例
metrics_collector = MetricsCollector()


def track_exchange_operation(exchange: ExchangeName, operation: OperationType):
    """
    Decorator to track exchange operations with metrics and structured logging.
    用于跟踪交易所操作（带指标和结构化日志）的装饰器。

    Usage / 用法:
        @track_exchange_operation(ExchangeName.HYPERLIQUID, OperationType.MARKET_DATA)
        def fetch_market_data(self):
            ...
    """

    def decorator(func):
        import functools
        import logging

        logger = logging.getLogger(func.__module__)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = get_trace_id()

            # Log operation start / 记录操作开始
            logger.info(
                f"Exchange operation started: {operation.value}",
                extra={
                    "exchange": exchange.value,
                    "operation": operation.value,
                    "function": func.__name__,
                    "trace_id": trace_id,
                },
            )

            try:
                result = func(*args, **kwargs)
                latency = time.time() - start_time

                # Record success / 记录成功
                metrics_collector.record_success(exchange, operation, latency)

                # Log operation success / 记录操作成功
                logger.info(
                    f"Exchange operation succeeded: {operation.value}",
                    extra={
                        "exchange": exchange.value,
                        "operation": operation.value,
                        "function": func.__name__,
                        "latency_ms": round(latency * 1000, 2),
                        "trace_id": trace_id,
                    },
                )

                return result

            except Exception as e:
                latency = time.time() - start_time
                error_message = str(e)
                error_type = type(e).__name__

                # Record error / 记录错误
                metrics_collector.record_error(
                    exchange, operation, error_message, error_type
                )

                # Log operation error / 记录操作错误
                logger.error(
                    f"Exchange operation failed: {operation.value}",
                    exc_info=True,
                    extra={
                        "exchange": exchange.value,
                        "operation": operation.value,
                        "function": func.__name__,
                        "error_type": error_type,
                        "error_message": error_message,
                        "latency_ms": round(latency * 1000, 2),
                        "trace_id": trace_id,
                    },
                )

                raise

        return wrapper

    return decorator
