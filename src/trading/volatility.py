"""
Volatility Calculation Module / 波动率计算模块

Calculates volatility from historical price data fetched from exchanges.
从交易所获取的历史价格数据计算波动率。

Owner: Agent TRADING
"""

import logging
import math
import time
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def calculate_returns(prices: List[float]) -> List[float]:
    """
    Calculate returns from price series / 从价格序列计算收益率
    
    Args:
        prices: List of prices in chronological order
        
    Returns:
        List of returns (percentage changes)
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] > 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            logger.warning(f"Zero or negative price at index {i-1}: {prices[i-1]}")
    
    return returns


def calculate_volatility(
    returns: List[float], 
    annualized: bool = False, 
    periods_per_year: int = 365
) -> float:
    """
    Calculate volatility (standard deviation) from returns / 从收益率计算波动率（标准差）
    
    Args:
        returns: List of returns (percentage changes)
        annualized: Whether to annualize the volatility
        periods_per_year: Number of periods per year for annualization (e.g., 365 for daily, 24 for hourly)
        
    Returns:
        Volatility as a decimal (e.g., 0.02 for 2%)
    """
    if len(returns) < 2:
        return 0.0
    
    # Calculate mean return / 计算平均收益率
    mean_return = sum(returns) / len(returns)
    
    # Calculate variance / 计算方差
    variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
    
    # Standard deviation (volatility) / 标准差（波动率）
    volatility = math.sqrt(variance)
    
    # Annualize if requested / 如果需要，进行年化
    if annualized:
        volatility = volatility * math.sqrt(periods_per_year)
    
    return volatility


class VolatilityCalculator:
    """
    Volatility calculator with caching / 带缓存的波动率计算器
    """
    
    def __init__(self, cache_ttl: int = 60):
        """
        Initialize volatility calculator / 初始化波动率计算器
        
        Args:
            cache_ttl: Cache time-to-live in seconds (default: 60)
        """
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, Dict] = {}
    
    def calculate_from_prices(
        self, 
        prices: List[float], 
        annualized: bool = False,
        periods_per_year: int = 365
    ) -> float:
        """
        Calculate volatility from price list / 从价格列表计算波动率
        
        Args:
            prices: List of prices in chronological order
            annualized: Whether to annualize the volatility
            periods_per_year: Number of periods per year for annualization
            
        Returns:
            Volatility as a decimal
        """
        returns = calculate_returns(prices)
        return calculate_volatility(returns, annualized=annualized, periods_per_year=periods_per_year)
    
    def get_cached_volatility(self, key: str) -> Optional[float]:
        """
        Get cached volatility value / 获取缓存的波动率值
        
        Args:
            key: Cache key (e.g., "ETH/USDC:USDC_1h")
            
        Returns:
            Cached volatility or None if expired/not found
        """
        if key in self._cache:
            cached = self._cache[key]
            if time.time() - cached["timestamp"] < self.cache_ttl:
                return cached["volatility"]
            else:
                # Remove expired cache / 删除过期缓存
                del self._cache[key]
        return None
    
    def cache_volatility(self, key: str, volatility: float) -> None:
        """
        Cache volatility value / 缓存波动率值
        
        Args:
            key: Cache key
            volatility: Volatility value to cache
        """
        self._cache[key] = {
            "volatility": volatility,
            "timestamp": time.time()
        }


def fetch_historical_prices(
    exchange, 
    symbol: str, 
    hours: int,
    interval_minutes: int = 1
) -> List[float]:
    """
    Fetch historical prices from exchange / 从交易所获取历史价格
    
    Args:
        exchange: Exchange client instance (HyperliquidClient or BinanceClient)
        symbol: Trading symbol (e.g., "ETH/USDC:USDC")
        hours: Number of hours of history to fetch
        interval_minutes: Interval between price points in minutes (default: 1)
        
    Returns:
        List of prices in chronological order
    """
    try:
        # Check if exchange has fetch_historical_prices method
        # 检查交易所是否有 fetch_historical_prices 方法
        if hasattr(exchange, "fetch_historical_prices"):
            return exchange.fetch_historical_prices(symbol, hours, interval_minutes)
        
        # Fallback: Try to use exchange-specific methods
        # 回退：尝试使用交易所特定方法
        if hasattr(exchange, "fetch_ohlcv"):
            # Use OHLCV data / 使用 OHLCV 数据
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=f"{interval_minutes}m", limit=hours * 60 // interval_minutes)
            # Extract close prices / 提取收盘价
            prices = [candle[4] for candle in ohlcv]  # Index 4 is close price
            return prices
        
        # If no method available, return empty list
        # 如果没有可用方法，返回空列表
        logger.warning(
            f"Exchange {type(exchange).__name__} does not support historical price fetching. "
            f"交易所 {type(exchange).__name__} 不支持历史价格获取。"
        )
        return []
        
    except Exception as e:
        logger.error(
            f"Error fetching historical prices for {symbol}: {e}. "
            f"获取 {symbol} 的历史价格时出错: {e}。",
            exc_info=True
        )
        return []


def fetch_and_calculate_volatility(
    exchange,
    symbol: str,
    hours: int,
    default: float = 0.02,
    calculator: Optional[VolatilityCalculator] = None
) -> float:
    """
    Fetch historical prices and calculate volatility / 获取历史价格并计算波动率
    
    Args:
        exchange: Exchange client instance
        symbol: Trading symbol
        hours: Number of hours of history to use
        default: Default volatility if calculation fails (default: 2%)
        calculator: Optional VolatilityCalculator instance for caching
        
    Returns:
        Volatility as a decimal (e.g., 0.02 for 2%)
    """
    # Check cache if calculator provided / 如果提供了计算器，检查缓存
    if calculator:
        cache_key = f"{symbol}_{hours}h"
        cached = calculator.get_cached_volatility(cache_key)
        if cached is not None:
            logger.debug(f"Using cached volatility for {cache_key}: {cached}")
            return cached
    
    try:
        # Fetch historical prices / 获取历史价格
        prices = fetch_historical_prices(exchange, symbol, hours)
        
        if len(prices) < 2:
            logger.warning(
                f"Insufficient price data for volatility calculation: {len(prices)} prices. "
                f"Using default {default:.2%}. "
                f"波动率计算的数据不足: {len(prices)} 个价格。使用默认值 {default:.2%}。"
            )
            return default
        
        # Calculate volatility / 计算波动率
        # For hourly data, use 24 periods per year for annualization
        # 对于小时数据，使用每年 24 个周期进行年化
        periods_per_year = 24 * 365  # Hourly periods per year
        volatility = calculate_volatility(
            calculate_returns(prices),
            annualized=False,  # Return hourly volatility, not annualized
            periods_per_year=periods_per_year
        )
        
        # Cache if calculator provided / 如果提供了计算器，缓存结果
        if calculator:
            cache_key = f"{symbol}_{hours}h"
            calculator.cache_volatility(cache_key, volatility)
        
        logger.info(
            f"Calculated {hours}h volatility for {symbol}: {volatility:.4%}. "
            f"计算 {symbol} 的 {hours} 小时波动率: {volatility:.4%}。"
        )
        
        return volatility
        
    except Exception as e:
        logger.error(
            f"Error calculating volatility for {symbol}: {e}. Using default {default:.2%}. "
            f"计算 {symbol} 的波动率时出错: {e}。使用默认值 {default:.2%}。",
            exc_info=True
        )
        return default


def calculate_volatility_1h_24h(
    exchange,
    symbol: str,
    calculator: Optional[VolatilityCalculator] = None
) -> Tuple[float, float]:
    """
    Calculate both 1-hour and 24-hour volatility / 计算 1 小时和 24 小时波动率
    
    Args:
        exchange: Exchange client instance
        symbol: Trading symbol
        calculator: Optional VolatilityCalculator instance for caching
        
    Returns:
        Tuple of (volatility_1h, volatility_24h) as decimals
    """
    volatility_1h = fetch_and_calculate_volatility(
        exchange, symbol, hours=1, default=0.01, calculator=calculator
    )
    volatility_24h = fetch_and_calculate_volatility(
        exchange, symbol, hours=24, default=0.03, calculator=calculator
    )
    
    return volatility_1h, volatility_24h

