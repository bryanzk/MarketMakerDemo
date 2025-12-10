"""
Fixed Spread Strategy / 固定点差策略

Market making strategy with fixed spread around mid price.
围绕中间价固定点差的做市策略。

Owner: Agent TRADING
"""

from typing import Any, Dict, List, Optional

from src.shared.config import LEVERAGE, QUANTITY, RISK_LIMITS, SPREAD_PCT
from src.shared.logger import setup_logger
from src.shared.utils import round_step_size, round_tick_size

logger = setup_logger("FixedSpreadStrategy")


class FixedSpreadStrategy:
    """Fixed spread market making strategy."""

    def __init__(self):
        self.spread = SPREAD_PCT
        self.base_spread = SPREAD_PCT  # Base spread for adaptive adjustment
        self.quantity = QUANTITY
        self.leverage = LEVERAGE
        
        # Aggressive spread multipliers (more aggressive than before)
        # 激进价差乘数（比以前更激进）
        self.spread_multipliers = {
            "low": 0.3,  # Low volatility: 0.3x (was 0.5) - more aggressive
            "medium": 1.0,  # Medium volatility: 1.0x (unchanged)
            "high": 1.3,  # High volatility: 1.3x (unchanged)
            "very_high": 1.5,  # Very high volatility: 1.5x (unchanged)
        }
        
        # Volatility thresholds
        # 波动率阈值
        self.volatility_thresholds = {
            "low": 0.02,  # < 2%
            "medium": 0.05,  # 2-5%
            "high": 0.10,  # 5-10%
            # very_high: > 10%
        }
        
        # Market spread threshold for aggressive adjustment
        # 市场价差阈值，用于激进调整
        self.market_spread_threshold = 0.001  # 0.1%
        
        # Store initial safe defaults for risk fallback
        self._safe_defaults = {
            "spread": SPREAD_PCT,
            "quantity": QUANTITY,
            "leverage": LEVERAGE,
        }

    def reset_to_safe_defaults(self) -> Dict[str, Any]:
        """
        Reset strategy parameters to initial safe defaults.
        Called when risk validation fails.

        Returns:
            Dict with the reset values
        """
        self.spread = self._safe_defaults["spread"]
        self.quantity = self._safe_defaults["quantity"]
        self.leverage = self._safe_defaults["leverage"]
        return self._safe_defaults.copy()

    def get_safe_defaults(self) -> Dict[str, Any]:
        """Return a copy of the safe default parameters."""
        return self._safe_defaults.copy()

    def calculate_adaptive_spread(
        self,
        volatility_1h: Optional[float] = None,
        volatility_24h: Optional[float] = None,
        market_spread: Optional[float] = None,
    ) -> float:
        """
        Calculate adaptive spread based on volatility and market spread.
        Uses more aggressive multipliers for low volatility (0.2-0.3 instead of 0.5).
        Adjusts based on market spread when very small (<0.1%).
        
        根据波动率和市场价差计算自适应价差。
        低波动时使用更激进的乘数（0.2-0.3 而不是 0.5）。
        当市场价差很小时（<0.1%）根据市场价差调整。
        
        Args:
            volatility_1h: 1-hour volatility (preferred)
            volatility_24h: 24-hour volatility (fallback)
            market_spread: Current market spread (best_ask - best_bid) / best_bid
            
        Returns:
            Adjusted spread value
        """
        # Use 1h volatility if available, otherwise 24h
        # 如果可用，使用 1h 波动率，否则使用 24h
        volatility = volatility_1h if volatility_1h is not None else volatility_24h
        
        # If no volatility data, keep current spread unchanged
        # 如果没有波动率数据，保持当前价差不变
        if volatility is None:
            return self.spread
        
        # Determine volatility level
        # 确定波动率级别
        if volatility < self.volatility_thresholds["low"]:
            level = "low"
        elif volatility < self.volatility_thresholds["medium"]:
            level = "medium"
        elif volatility < self.volatility_thresholds["high"]:
            level = "high"
        else:
            level = "very_high"
        
        # Calculate base adjusted spread from volatility
        # 从波动率计算基础调整价差
        multiplier = self.spread_multipliers[level]
        adjusted_spread = self.base_spread * multiplier
        
        # Apply market spread-based adjustment if market spread is very small
        # 如果市场价差很小，应用基于市场价差的调整
        if market_spread is not None and market_spread > 0:
            if market_spread < self.market_spread_threshold:
                # Market spread is very small (<0.1%), adjust our spread to be competitive
                # 市场价差很小（<0.1%），调整我们的价差以保持竞争力
                # Use market spread as reference, but ensure minimum spread
                # 使用市场价差作为参考，但确保最小价差
                market_based_spread = market_spread * 2.0  # 2x market spread for competitiveness
                
                # Combine volatility-based and market-based adjustments
                # 结合基于波动率和基于市场的调整
                # Take the more aggressive (smaller) of the two, but respect minimum
                # 取两者中更激进的（更小的），但遵守最小值
                adjusted_spread = min(adjusted_spread, market_based_spread)
                
                logger.debug(
                    f"Market spread {market_spread:.4f} < threshold {self.market_spread_threshold:.4f}. "
                    f"Adjusting spread to {adjusted_spread:.4f} based on market spread. "
                    f"市场价差 {market_spread:.4f} < 阈值 {self.market_spread_threshold:.4f}。"
                    f"根据市场价差将价差调整为 {adjusted_spread:.4f}。"
                )
            elif market_spread < self.market_spread_threshold * 2:
                # Market spread is small but not very small, moderate adjustment
                # 市场价差小但不是很小，适度调整
                market_based_spread = market_spread * 2.5
                adjusted_spread = min(adjusted_spread, market_based_spread)
        
        # Clamp to risk limits to ensure compliance
        # 限制在风险范围内以确保合规
        min_spread_limit = RISK_LIMITS.get("MIN_SPREAD", 0.001)
        max_spread_limit = RISK_LIMITS.get("MAX_SPREAD", 0.05)
        
        original_adjusted = adjusted_spread
        if adjusted_spread < min_spread_limit:
            logger.warning(
                f"Adjusted spread {adjusted_spread:.4f} below MIN_SPREAD {min_spread_limit:.4f}. "
                f"Clamping to minimum. "
                f"调整后的价差 {adjusted_spread:.4f} 低于 MIN_SPREAD {min_spread_limit:.4f}。限制到最小值。"
            )
            adjusted_spread = min_spread_limit
        elif adjusted_spread > max_spread_limit:
            logger.warning(
                f"Adjusted spread {adjusted_spread:.4f} above MAX_SPREAD {max_spread_limit:.4f}. "
                f"Clamping to maximum. "
                f"调整后的价差 {adjusted_spread:.4f} 高于 MAX_SPREAD {max_spread_limit:.4f}。限制到最大值。"
            )
            adjusted_spread = max_spread_limit
        
        # Update current spread
        # 更新当前价差
        self.spread = adjusted_spread
        return adjusted_spread

    def calculate_target_orders(
        self, market_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Calculates target orders based on fixed spread.
        Uses best_bid/best_ask for pricing when available, falls back to mid_price.

        Args:
            market_data: Dict with 'mid_price', 'best_bid', 'best_ask', 'tick_size', 'step_size'

        Returns:
            List of order dicts with 'side', 'price', 'quantity'
        """
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

        best_bid = market_data.get("best_bid")
        best_ask = market_data.get("best_ask")
        mid_price = market_data.get("mid_price")

        # Priority: Use best_bid/best_ask for pricing when available
        # 优先级：当可用时使用 best_bid/best_ask 进行定价
        if best_bid and best_ask and best_bid > 0 and best_ask > 0:
            # Calculate offset based on spread percentage
            # 基于价差百分比计算偏移量
            # Use a small fraction of the spread to position orders competitively
            # 使用价差的一小部分来定位订单以保持竞争力
            spread_offset_pct = self.spread / 4  # Use 1/4 of spread for offset
            
            # Buy price: slightly above best_bid (competitive but not crossing)
            # 买入价：略高于 best_bid（有竞争力但不跨越）
            bid_price = best_bid * (1 + spread_offset_pct)
            # Ensure at least one tick above best_bid (strictly greater)
            # 确保至少比 best_bid 高一个 tick（严格大于）
            min_bid = best_bid + tick_size
            bid_price = max(bid_price, min_bid)
            # Round first, then ensure it's strictly above best_bid
            # 先舍入，然后确保严格大于 best_bid
            bid_price = round_tick_size(bid_price, tick_size)
            if bid_price <= best_bid:
                bid_price = round_tick_size(best_bid + tick_size, tick_size)
            
            # Sell price: slightly below best_ask (competitive but not crossing)
            # 卖出价：略低于 best_ask（有竞争力但不跨越）
            ask_price = best_ask * (1 - spread_offset_pct)
            # Ensure at least one tick below best_ask (strictly less)
            # 确保至少比 best_ask 低一个 tick（严格小于）
            max_ask = best_ask - tick_size
            ask_price = min(ask_price, max_ask)
            # Round first, then ensure it's strictly below best_ask
            # 先舍入，然后确保严格小于 best_ask
            ask_price = round_tick_size(ask_price, tick_size)
            if ask_price >= best_ask:
                ask_price = round_tick_size(best_ask - tick_size, tick_size)
            
            # Safety check: Ensure we don't cross the spread
            # 安全检查：确保不会跨越价差
            if bid_price >= best_ask:
                bid_price = round_tick_size(best_ask - tick_size, tick_size)
            if ask_price <= best_bid:
                ask_price = round_tick_size(best_bid + tick_size, tick_size)
            
            # Ensure buy price is below sell price
            # 确保买入价低于卖出价
            if bid_price >= ask_price:
                # If too close, use mid-point
                # 如果太接近，使用中点
                mid = (best_bid + best_ask) / 2
                bid_price = round_tick_size(mid - tick_size, tick_size)
                ask_price = round_tick_size(mid + tick_size, tick_size)
                # Final safety check
                # 最终安全检查
                if bid_price <= best_bid:
                    bid_price = round_tick_size(best_bid + tick_size, tick_size)
                if ask_price >= best_ask:
                    ask_price = round_tick_size(best_ask - tick_size, tick_size)
        elif mid_price and mid_price > 0:
            # Fallback to mid_price-based pricing when best_bid/best_ask unavailable
            # 当 best_bid/best_ask 不可用时，回退到基于 mid_price 的定价
            bid_price = mid_price * (1 - self.spread / 2)
            ask_price = mid_price * (1 + self.spread / 2)
            
            # Safety check: Ensure we don't cross the spread if available
            # 安全检查：如果可用，确保不会跨越价差
            if best_ask and bid_price >= best_ask:
                bid_price = best_ask * 0.9995
            if best_bid and ask_price <= best_bid:
                ask_price = best_bid * 1.0005
        else:
            # No valid pricing data available
            # 没有可用的有效定价数据
            return []

        # Use dynamic tick_size and step_size
        # 使用动态的 tick_size 和 step_size
        # Only round if not already rounded (for best_bid/best_ask path)
        # 仅在未舍入时舍入（对于 best_bid/best_ask 路径）
        if best_bid and best_ask and best_bid > 0 and best_ask > 0:
            # Already rounded in best_bid/best_ask path
            # 已在 best_bid/best_ask 路径中舍入
            final_bid = bid_price
            final_ask = ask_price
        else:
            # Round for mid_price fallback path
            # 为 mid_price 回退路径舍入
            final_bid = round_tick_size(bid_price, tick_size)
            final_ask = round_tick_size(ask_price, tick_size)
        qty = round_step_size(self.quantity, step_size)

        return [
            {"side": "buy", "price": final_bid, "quantity": qty},
            {"side": "sell", "price": final_ask, "quantity": qty},
        ]
