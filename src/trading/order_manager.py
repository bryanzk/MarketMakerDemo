"""
Order Manager Module / 订单管理模块

Manages order synchronization between current and target orders.
管理当前订单和目标订单之间的同步。

Owner: Agent TRADING
"""

import logging
import time
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Default minimum order age in seconds / 默认最小订单年龄（秒）
DEFAULT_MIN_ORDER_AGE_SECONDS = 60.0  # Increased from 30 to 60 seconds / 从 30 秒增加到 60 秒


class OrderManager:
    """Manages order synchronization."""

    def __init__(self):
        """Initialize OrderManager with default stability window settings."""
        self.base_min_order_age_seconds = DEFAULT_MIN_ORDER_AGE_SECONDS

    def _calculate_stability_window(
        self,
        volatility_1h: Optional[float] = None,
        volatility_24h: Optional[float] = None,
        base_min_age: Optional[float] = None,
    ) -> float:
        """
        Calculate stability window based on volatility.
        Low volatility -> extended window, high volatility -> shorter window.
        
        根据波动率计算稳定性窗口。
        低波动 -> 延长窗口，高波动 -> 更短窗口。
        
        Args:
            volatility_1h: 1-hour volatility (preferred)
            volatility_24h: 24-hour volatility (fallback)
            base_min_age: Base minimum age in seconds (defaults to self.base_min_order_age_seconds)
            
        Returns:
            Calculated stability window in seconds
        """
        if base_min_age is None:
            base_min_age = self.base_min_order_age_seconds
        
        # Use 1h volatility if available, otherwise 24h
        # 如果可用，使用 1h 波动率，否则使用 24h
        volatility = volatility_1h if volatility_1h is not None else volatility_24h
        
        # If no volatility data, use base window
        # 如果没有波动率数据，使用基础窗口
        if volatility is None:
            return base_min_age
        
        # Adjust window based on volatility
        # 根据波动率调整窗口
        if volatility < 0.02:  # Low volatility: < 2%
            # Extend window by 50% for low volatility
            # 低波动时延长窗口 50%
            return base_min_age * 1.5
        elif volatility < 0.05:  # Medium volatility: 2-5%
            # Use base window
            # 使用基础窗口
            return base_min_age
        elif volatility < 0.10:  # High volatility: 5-10%
            # Reduce window by 25% for high volatility
            # 高波动时减少窗口 25%
            return base_min_age * 0.75
        else:  # Very high volatility: > 10%
            # Reduce window by 50% for very high volatility
            # 极高波动时减少窗口 50%
            return base_min_age * 0.5

    def _should_cancel_order(
        self,
        current_order: Dict[str, Any],
        target_order: Optional[Dict[str, Any]],
        min_order_age_seconds: float,
        current_time: Optional[float] = None,
    ) -> bool:
        """
        Determine if an order should be cancelled based on stability window.
        
        根据稳定性窗口确定订单是否应该被取消。
        
        Args:
            current_order: Current order dict (should have 'timestamp' field)
            target_order: Target order dict (None if no target)
            min_order_age_seconds: Minimum order age in seconds before cancellation
            current_time: Current timestamp (defaults to time.time())
            
        Returns:
            True if order should be cancelled, False if it should be kept
        """
        if current_time is None:
            current_time = time.time()
        
        # If no target order, always cancel (regardless of age)
        # 如果没有目标订单，总是取消（无论年龄）
        if target_order is None:
            return True
        
        # Check if order has timestamp
        # 检查订单是否有时间戳
        order_timestamp = current_order.get("timestamp")
        if order_timestamp is None:
            # No timestamp: assume order is old enough to cancel
            # 没有时间戳：假设订单足够旧可以取消
            logger.debug(
                f"Order {current_order.get('id')} has no timestamp, allowing cancellation. "
                f"订单 {current_order.get('id')} 没有时间戳，允许取消。"
            )
            return True
        
        # Calculate order age
        # 计算订单年龄
        order_age = current_time - order_timestamp
        
        # If order is younger than minimum age, don't cancel
        # 如果订单小于最小年龄，不取消
        if order_age < min_order_age_seconds:
            logger.debug(
                f"Order {current_order.get('id')} is too young ({order_age:.1f}s < {min_order_age_seconds:.1f}s). "
                f"Keeping order for stability window. "
                f"订单 {current_order.get('id')} 太新（{order_age:.1f}秒 < {min_order_age_seconds:.1f}秒）。"
                f"保留订单以等待稳定性窗口。"
            )
            return False
        
        # Order is old enough to cancel
        # 订单足够旧可以取消
        return True

    def sync_orders(
        self,
        current_orders: List[Dict[str, Any]],
        target_orders: List[Dict[str, Any]],
        mid_price: Optional[float] = None,
        min_order_age_seconds: Optional[float] = None,
        volatility_1h: Optional[float] = None,
        volatility_24h: Optional[float] = None,
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Compares current and target orders to determine actions.

        Args:
            current_orders: List of current open orders
            target_orders: List of target orders to achieve

        Returns:
            Tuple of (order_ids_to_cancel, orders_to_place)
        """
        to_cancel = []
        to_place = []

        # Calculate stability window based on volatility
        # 根据波动率计算稳定性窗口
        if min_order_age_seconds is None:
            # Auto-calculate based on volatility
            # 根据波动率自动计算
            min_order_age_seconds = self._calculate_stability_window(
                volatility_1h=volatility_1h,
                volatility_24h=volatility_24h,
            )
        # If explicitly provided, use it directly (no adjustment)
        # 如果明确提供，直接使用（不调整）
        
        current_time = time.time()

        # Helper to group by side
        curr_buy = next((o for o in current_orders if o["side"] == "buy"), None)
        curr_sell = next((o for o in current_orders if o["side"] == "sell"), None)

        tgt_buy = next((o for o in target_orders if o["side"] == "buy"), None)
        tgt_sell = next((o for o in target_orders if o["side"] == "sell"), None)

        # Log target orders for debugging
        logger.debug(
            f"Order sync: target_buy={tgt_buy}, target_sell={tgt_sell}, "
            f"current_buy={curr_buy}, current_sell={curr_sell}"
        )

        # Compare Buy
        if tgt_buy:
            if curr_buy:
                # Check if price OR quantity changed significantly
                curr_price = curr_buy.get("price", 0)
                tgt_price = tgt_buy.get("price", 0)
                curr_qty = curr_buy.get("quantity", 0)
                tgt_qty = tgt_buy.get("quantity", 0)
                
                price_diff = abs(curr_price - tgt_price)
                qty_diff = abs(curr_qty - tgt_qty)
                
                if price_diff > 0.01 or qty_diff > 0.001:  # Also check quantity
                    # Check stability window before cancelling
                    # 在取消前检查稳定性窗口
                    should_cancel = self._should_cancel_order(
                        current_order=curr_buy,
                        target_order=tgt_buy,
                        min_order_age_seconds=min_order_age_seconds,
                        current_time=current_time,
                    )
                    
                    if should_cancel:
                        logger.info(
                            f"Buy order needs update: price_diff={price_diff:.4f}, qty_diff={qty_diff:.4f}. "
                            f"Current: price={curr_price}, qty={curr_qty}. "
                            f"Target: price={tgt_price}, qty={tgt_qty}. "
                            f"买入订单需要更新: 价格差={price_diff:.4f}, 数量差={qty_diff:.4f}。"
                        )
                        to_cancel.append(curr_buy["id"])
                        to_place.append(tgt_buy)
                    else:
                        logger.info(
                            f"Buy order price/quantity changed but order is too young. "
                            f"Keeping order for stability window (min_age={min_order_age_seconds:.1f}s). "
                            f"买入订单价格/数量已变化，但订单太新。"
                            f"保留订单以等待稳定性窗口（最小年龄={min_order_age_seconds:.1f}秒）。"
                        )
                else:
                    logger.debug(
                        f"Buy order unchanged: price={curr_price}, qty={curr_qty}. "
                        f"买入订单未变化: 价格={curr_price}, 数量={curr_qty}。"
                    )
            else:
                logger.info(
                    f"No current buy order, will place: price={tgt_buy.get('price')}, qty={tgt_buy.get('quantity')}. "
                    f"没有当前买入订单，将下单: 价格={tgt_buy.get('price')}, 数量={tgt_buy.get('quantity')}。"
                )
                to_place.append(tgt_buy)
        else:
            if curr_buy:
                # No target order: check stability window (but typically cancel anyway)
                # 没有目标订单：检查稳定性窗口（但通常无论如何都会取消）
                should_cancel = self._should_cancel_order(
                    current_order=curr_buy,
                    target_order=None,  # No target order
                    min_order_age_seconds=min_order_age_seconds,
                    current_time=current_time,
                )
                if should_cancel:
                    logger.info(
                        f"No target buy order, will cancel current: {curr_buy['id']}. "
                        f"没有目标买入订单，将取消当前订单: {curr_buy['id']}。"
                    )
                    to_cancel.append(curr_buy["id"])

        # Compare Sell
        if tgt_sell:
            if curr_sell:
                curr_price = curr_sell.get("price", 0)
                tgt_price = tgt_sell.get("price", 0)
                curr_qty = curr_sell.get("quantity", 0)
                tgt_qty = tgt_sell.get("quantity", 0)
                
                price_diff = abs(curr_price - tgt_price)
                qty_diff = abs(curr_qty - tgt_qty)
                
                if price_diff > 0.01 or qty_diff > 0.001:  # Also check quantity
                    # Check stability window before cancelling
                    # 在取消前检查稳定性窗口
                    should_cancel = self._should_cancel_order(
                        current_order=curr_sell,
                        target_order=tgt_sell,
                        min_order_age_seconds=min_order_age_seconds,
                        current_time=current_time,
                    )
                    
                    if should_cancel:
                        logger.info(
                            f"Sell order needs update: price_diff={price_diff:.4f}, qty_diff={qty_diff:.4f}. "
                            f"Current: price={curr_price}, qty={curr_qty}. "
                            f"Target: price={tgt_price}, qty={tgt_qty}. "
                            f"卖出订单需要更新: 价格差={price_diff:.4f}, 数量差={qty_diff:.4f}。"
                        )
                        to_cancel.append(curr_sell["id"])
                        to_place.append(tgt_sell)
                    else:
                        logger.info(
                            f"Sell order price/quantity changed but order is too young. "
                            f"Keeping order for stability window (min_age={min_order_age_seconds:.1f}s). "
                            f"卖出订单价格/数量已变化，但订单太新。"
                            f"保留订单以等待稳定性窗口（最小年龄={min_order_age_seconds:.1f}秒）。"
                        )
                else:
                    logger.debug(
                        f"Sell order unchanged: price={curr_price}, qty={curr_qty}. "
                        f"卖出订单未变化: 价格={curr_price}, 数量={curr_qty}。"
                    )
            else:
                logger.info(
                    f"No current sell order, will place: price={tgt_sell.get('price')}, qty={tgt_sell.get('quantity')}. "
                    f"没有当前卖出订单，将下单: 价格={tgt_sell.get('price')}, 数量={tgt_sell.get('quantity')}。"
                )
                to_place.append(tgt_sell)
        else:
            if curr_sell:
                # No target order: check stability window (but typically cancel anyway)
                # 没有目标订单：检查稳定性窗口（但通常无论如何都会取消）
                should_cancel = self._should_cancel_order(
                    current_order=curr_sell,
                    target_order=None,  # No target order
                    min_order_age_seconds=min_order_age_seconds,
                    current_time=current_time,
                )
                if should_cancel:
                    logger.info(
                        f"No target sell order, will cancel current: {curr_sell['id']}. "
                        f"没有目标卖出订单，将取消当前订单: {curr_sell['id']}。"
                    )
                    to_cancel.append(curr_sell["id"])

        # Log summary
        buy_count = sum(1 for o in to_place if o.get("side") == "buy")
        sell_count = sum(1 for o in to_place if o.get("side") == "sell")
        logger.info(
            f"Order sync result: to_cancel={len(to_cancel)}, to_place={len(to_place)} "
            f"(buy={buy_count}, sell={sell_count}). "
            f"订单同步结果: 取消={len(to_cancel)}, 下单={len(to_place)} "
            f"(买入={buy_count}, 卖出={sell_count})。"
        )

        return to_cancel, to_place
