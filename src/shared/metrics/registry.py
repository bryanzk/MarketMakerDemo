"""
Metrics Registry / 指标注册表

Central registry for managing and calculating metrics.
用于管理和计算指标的中央注册表。

Owner: Agent ARCH
"""

from typing import Any, Dict

from src.shared.logger import setup_logger
from src.shared.metrics.base import Metric

logger = setup_logger("MetricsRegistry")


class MetricsRegistry:
    """Registry for managing metric instances."""

    def __init__(self):
        self.metrics: Dict[str, Metric] = {}

    def register(self, metric_instance: Metric) -> None:
        """
        Register a metric if it's enabled.

        Args:
            metric_instance: The metric instance to register
        """
        if metric_instance.enabled:
            self.metrics[metric_instance.name] = metric_instance
            logger.info(f"Registered metric: {metric_instance.name}")

    def calculate_all(self, data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all registered metrics.

        Args:
            data: Data dict to pass to each metric

        Returns:
            Dict of metric names to calculated values
        """
        results: Dict[str, float] = {}
        for name, metric in self.metrics.items():
            try:
                val = metric.calculate(data)
                if val is not None:
                    results[name] = val
            except Exception as e:
                logger.error(f"Error calculating {name}: {e}")
        return results

