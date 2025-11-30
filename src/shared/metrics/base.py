"""
Base Metric Class / 基础指标类

Abstract base class for all metrics.
所有指标的抽象基类。

Owner: Agent ARCH
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Metric(ABC):
    """Abstract base class for metrics."""

    def __init__(self, name: str, config: Dict[str, Any]):
        """
        Initialize a metric.

        Args:
            name: Metric name
            config: Configuration dict with 'enabled' flag and other settings
        """
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)

    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> Optional[float]:
        """
        Calculates the metric based on provided data.

        Args:
            data: dict containing necessary data (trades, prices, etc.)

        Returns:
            The calculated metric value, or None if calculation fails.
        """
        pass
