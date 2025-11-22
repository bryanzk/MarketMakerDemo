from abc import ABC, abstractmethod

class Metric(ABC):
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.enabled = config.get('enabled', False)
        
    @abstractmethod
    def calculate(self, data):
        """
        Calculates the metric based on provided data.
        Args:
            data: dict containing necessary data (trades, prices, etc.)
        Returns:
            float or None: The calculated metric value.
        """
        pass
