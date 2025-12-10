"""
Fixed Spread Strategy / 固定点差策略

Market making strategy with fixed spread around mid price.
围绕中间价固定点差的做市策略。

Owner: Agent TRADING
"""

from typing import Any, Dict, List

from src.shared.config import LEVERAGE, QUANTITY, RISK_LIMITS, SPREAD_PCT
from src.shared.logger import setup_logger
from src.shared.utils import round_step_size, round_tick_size

logger = setup_logger("FixedSpreadStrategy")


class FixedSpreadStrategy:
    """Fixed spread market making strategy with dynamic spread adjustment."""

    def __init__(self):
        self.base_spread = SPREAD_PCT  # Base spread from config / 配置中的基础价差
        self.spread = SPREAD_PCT  # Current effective spread / 当前有效价差
        self.quantity = QUANTITY
        self.leverage = LEVERAGE
        # Store initial safe defaults for risk fallback
        self._safe_defaults = {
            "spread": SPREAD_PCT,
            "quantity": QUANTITY,
            "leverage": LEVERAGE,
        }
        # Volatility thresholds for spread adjustment / 价差调整的波动率阈值
        self.volatility_thresholds = {
            "low": 0.02,      # 2% - below this, reduce spread
            "medium": 0.05,   # 5% - above this, increase spread
            "high": 0.10,    # 10% - above this, significantly increase spread
        }
        # Spread multipliers based on volatility / 基于波动率的价差倍数
        # More aggressive reduction in low volatility to improve fill rate
        # 在低波动时更激进的降低价差以提高成交率
        self.spread_multipliers = {
            "low": 0.5,      # Reduce spread by 50% in low volatility (was 0.8, now more aggressive)
            "medium": 1.0,   # No adjustment in medium volatility
            "high": 1.3,     # Increase spread by 30% in high volatility
            "very_high": 1.5, # Increase spread by 50% in very high volatility
        }

    def calculate_adaptive_spread(
        self, 
        volatility_1h: float = None,
        volatility_24h: float = None,
        market_spread: float = None
    ) -> float:
        """
        Calculate adaptive spread based on market volatility.
        根据市场波动率计算自适应价差。
        
        Args:
            volatility_1h: 1-hour volatility (preferred for short-term adjustment)
            volatility_24h: 24-hour volatility (for longer-term context)
            market_spread: Current market spread (for reference)
            
        Returns:
            Adjusted spread as decimal (e.g., 0.015 for 1.5%)
        """
        # Use 1h volatility if available, otherwise use 24h / 如果可用，使用 1h 波动率，否则使用 24h
        volatility = volatility_1h if volatility_1h is not None else volatility_24h
        
        # If no volatility data, use base spread / 如果没有波动率数据，使用基础价差
        if volatility is None:
            self.spread = self.base_spread
            return self.base_spread
        
        # Determine volatility category / 确定波动率类别
        if volatility < self.volatility_thresholds["low"]:
            # Low volatility: reduce spread to improve fill rate / 低波动：减小价差以提高成交率
            multiplier = self.spread_multipliers["low"]
            category = "low"
        elif volatility < self.volatility_thresholds["medium"]:
            # Medium volatility: use base spread / 中等波动：使用基础价差
            multiplier = self.spread_multipliers["medium"]
            category = "medium"
        elif volatility < self.volatility_thresholds["high"]:
            # High volatility: increase spread for risk protection / 高波动：增大价差以保护风险
            multiplier = self.spread_multipliers["high"]
            category = "high"
        else:
            # Very high volatility: significantly increase spread / 极高波动：显著增大价差
            multiplier = self.spread_multipliers["very_high"]
            category = "very_high"
        
        # Calculate adjusted spread / 计算调整后的价差
        adjusted_spread = self.base_spread * multiplier
        
        # Optional: Adjust based on market spread if provided / 可选：如果提供了市场价差，基于市场价差调整
        if market_spread is not None and market_spread > 0:
            # Ensure our spread is at least 1.3x market spread in high volatility
            # 在高波动时，确保我们的价差至少是市场价差的 1.3 倍
            if volatility >= self.volatility_thresholds["medium"]:
                min_spread = market_spread * 1.3
                adjusted_spread = max(adjusted_spread, min_spread)
        
        # Clamp to risk limits to ensure compliance / 限制在风险范围内以确保合规
        min_spread_limit = RISK_LIMITS["MIN_SPREAD"]
        max_spread_limit = RISK_LIMITS["MAX_SPREAD"]
        
        original_adjusted = adjusted_spread
        if adjusted_spread < min_spread_limit:
            logger.warning(
                f"Adjusted spread {adjusted_spread*100:.2f}% below MIN_SPREAD {min_spread_limit*100:.2f}%. "
                f"Clamping to {min_spread_limit*100:.2f}%. "
                f"调整后的价差 {adjusted_spread*100:.2f}% 低于最小价差 {min_spread_limit*100:.2f}%。限制为 {min_spread_limit*100:.2f}%。"
            )
            adjusted_spread = min_spread_limit
        elif adjusted_spread > max_spread_limit:
            logger.warning(
                f"Adjusted spread {adjusted_spread*100:.2f}% above MAX_SPREAD {max_spread_limit*100:.2f}%. "
                f"Clamping to {max_spread_limit*100:.2f}%. "
                f"调整后的价差 {adjusted_spread*100:.2f}% 高于最大价差 {max_spread_limit*100:.2f}%。限制为 {max_spread_limit*100:.2f}%。"
            )
            adjusted_spread = max_spread_limit
        
        # Update current spread / 更新当前价差
        self.spread = adjusted_spread
        
        return adjusted_spread

    def reset_to_safe_defaults(self) -> Dict[str, Any]:
        """
        Reset strategy parameters to initial safe defaults.
        Called when risk validation fails.

        Returns:
            Dict with the reset values
        """
        self.spread = self._safe_defaults["spread"]
        self.base_spread = self._safe_defaults["spread"]
        self.quantity = self._safe_defaults["quantity"]
        self.leverage = self._safe_defaults["leverage"]
        return self._safe_defaults.copy()

    def get_safe_defaults(self) -> Dict[str, Any]:
        """Return a copy of the safe default parameters."""
        return self._safe_defaults.copy()

    def calculate_target_orders(
        self, market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculates target orders based on fixed spread with dynamic adjustment.
        基于固定价差计算目标订单，支持动态调整。

        Args:
            market_data: Dict with 'mid_price', 'best_bid', 'best_ask', 'tick_size', 'step_size',
                        'volatility_1h' (optional), 'volatility_24h' (optional), 'market_spread' (optional)

        Returns:
            List of order dicts with 'side', 'price', 'quantity'
        """
        mid_price = market_data.get("mid_price")
        if not mid_price:
            return []

        # Get volatility data from market_data if available / 如果可用，从 market_data 获取波动率数据
        volatility_1h = market_data.get("volatility_1h")
        volatility_24h = market_data.get("volatility_24h")
        market_spread = market_data.get("market_spread")  # Current market bid-ask spread
        
        # Calculate adaptive spread based on volatility / 根据波动率计算自适应价差
        self.calculate_adaptive_spread(
            volatility_1h=volatility_1h,
            volatility_24h=volatility_24h,
            market_spread=market_spread
        )

        # Get tick_size and step_size from market_data if available
        # 如果可用，从 market_data 获取 tick_size 和 step_size
        tick_size = market_data.get("tick_size")
        step_size = market_data.get("step_size")
        
        # Fallback to defaults if not available
        # 如果不可用，使用默认值
        if tick_size is None:
            tick_size = 0.1  # Default for ETH (changed from 0.01)
        if step_size is None:
            step_size = 0.001  # Default for ETH

        # Calculate raw prices using adjusted spread / 使用调整后的价差计算原始价格
        bid_price = mid_price * (1 - self.spread / 2)
        ask_price = mid_price * (1 + self.spread / 2)

        # Safety check: Ensure we don't cross the spread
        best_ask = market_data.get("best_ask")
        best_bid = market_data.get("best_bid")

        if best_ask and bid_price >= best_ask:
            bid_price = best_ask * 0.9995
        if best_bid and ask_price <= best_bid:
            ask_price = best_bid * 1.0005

        # Use dynamic tick_size and step_size
        # 使用动态的 tick_size 和 step_size
        final_bid = round_tick_size(bid_price, tick_size)
        final_ask = round_tick_size(ask_price, tick_size)
        
        # Ensure ask price is always above mid_price after rounding
        # If rounding down causes ask to be <= mid_price, round up one tick
        # 确保卖出价格在舍入后始终大于 mid_price
        # 如果向下舍入导致卖出价格 <= mid_price，则向上舍入一个 tick
        if final_ask <= mid_price:
            from decimal import Decimal
            ask_decimal = Decimal(str(ask_price))
            tick_size_decimal = Decimal(str(tick_size))
            # Round up one tick / 向上舍入一个 tick
            ticks_rounded = (ask_decimal // tick_size_decimal) + Decimal("1")
            final_ask = float(ticks_rounded * tick_size_decimal)
        
        qty = round_step_size(self.quantity, step_size)

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]
