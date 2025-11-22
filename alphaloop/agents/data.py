import numpy as np
from alphaloop.core.logger import setup_logger
from alphaloop.core.config import METRICS_CONFIG
from alphaloop.metrics.registry import MetricsRegistry
from alphaloop.metrics.definitions import SharpeRatio, Slippage, FillRate, TickToTradeLatency

logger = setup_logger("DataAgent")

class DataAgent:
    def __init__(self):
        self.trade_history = []
        self.price_history = []
        self.registry = MetricsRegistry()
        self._register_metrics()
        
    def _register_metrics(self):
        # Layer 1
        l1_conf = METRICS_CONFIG.get('layer_1_infrastructure', {})
        self.registry.register(TickToTradeLatency("tick_to_trade_latency", l1_conf.get('tick_to_trade_latency', {})))
        
        # Layer 2
        l2_conf = METRICS_CONFIG.get('layer_2_execution', {})
        self.registry.register(Slippage("slippage_bps", l2_conf.get('slippage_bps', {})))
        self.registry.register(FillRate("fill_rate", l2_conf.get('fill_rate', {})))
        
        # Layer 4
        l4_conf = METRICS_CONFIG.get('layer_4_strategy', {})
        self.registry.register(SharpeRatio("sharpe_ratio", l4_conf.get('sharpe_ratio', {})))
        
    def ingest_data(self, market_data, trades):
        """
        Ingests market data and trades for analysis.
        """
        self.price_history.append(market_data['price'])
        self.trade_history.extend(trades)
        
    def calculate_metrics(self):
        """
        Calculates metrics using the registry.
        """
        data_context = {
            'trades': self.trade_history,
            'prices': self.price_history
        }
        
        metrics = self.registry.calculate_all(data_context)
        logger.info("Calculated Metrics", extra={'extra_data': metrics})
        return metrics
