from alphaloop.core.logger import setup_logger

logger = setup_logger("MetricsRegistry")


class MetricsRegistry:
    def __init__(self):
        self.metrics = {}

    def register(self, metric_instance):
        if metric_instance.enabled:
            self.metrics[metric_instance.name] = metric_instance
            logger.info(f"Registered metric: {metric_instance.name}")

    def calculate_all(self, data):
        results = {}
        for name, metric in self.metrics.items():
            try:
                val = metric.calculate(data)
                if val is not None:
                    results[name] = val
            except Exception as e:
                logger.error(f"Error calculating {name}: {e}")
        return results
