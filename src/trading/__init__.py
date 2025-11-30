# Trading Module - Exchange connectivity and order management
# Owner: Agent TRADING

"""
Trading module components:
- engine: AlphaLoop trading engine
- exchange: Exchange client (Binance)
- order_manager: Order synchronization
- risk_manager: Position risk management
- performance: Performance tracking
- simulation: Market simulation
- strategy_instance: Strategy instance management
- strategies/: Trading strategies
"""

from src.trading.exchange import BinanceClient
from src.trading.order_manager import OrderManager
from src.trading.risk_manager import RiskManager
from src.trading.performance import PerformanceTracker
from src.trading.simulation import MarketSimulator
from src.trading.strategy_instance import StrategyInstance
from src.trading.engine import AlphaLoop

__all__ = [
    "AlphaLoop",
    "BinanceClient",
    "OrderManager",
    "RiskManager",
    "PerformanceTracker",
    "MarketSimulator",
    "StrategyInstance",
]

