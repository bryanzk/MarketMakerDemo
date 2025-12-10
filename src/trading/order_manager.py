"""
Order Manager Module / 订单管理模块

Manages order synchronization between current and target orders.
管理当前订单和目标订单之间的同步。

Owner: Agent TRADING
"""

import logging
import time
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Order stability configuration / 订单稳定性配置
MIN_ORDER_AGE_SECONDS = 30  # Minimum time before allowing cancellation (seconds)
PRICE_THRESHOLD_PCT = 0.001  # 0.1% of mid price (adaptive threshold)
QTY_THRESHOLD_PCT = 0.01  # 1% quantity change threshold


class OrderManager:
    """Manages order synchronization."""

    def _should_cancel_order(
        self, 
        current_order: Dict[str, Any], 
        target_order: Dict[str, Any],
        mid_price: float
    ) -> bool:
        """
        Determine if an order should be cancelled based on stability window and adaptive thresholds.
        根据稳定性窗口和自适应阈值判断是否应该取消订单。
        
        Args:
            current_order: Current open order
            target_order: Target order to achieve
            mid_price: Current mid price for adaptive threshold calculation
            
        Returns:
            True if order should be cancelled, False otherwise
        """
        # Check order age (stability window) / 检查订单年龄（稳定性窗口）
        order_timestamp = current_order.get("timestamp", 0)
        if isinstance(order_timestamp, (int, float)) and order_timestamp > 0:
            # Convert milliseconds to seconds if needed
            if order_timestamp > 1e10:
                order_timestamp = order_timestamp / 1000
            order_age = time.time() - order_timestamp
            
            if order_age < MIN_ORDER_AGE_SECONDS:
                logger.debug(
                    f"Order {current_order.get('id')} is too new ({order_age:.1f}s < {MIN_ORDER_AGE_SECONDS}s). "
                    f"Keeping order active for stability. "
                    f"订单 {current_order.get('id')} 太新（{order_age:.1f}秒 < {MIN_ORDER_AGE_SECONDS}秒）。"
                    f"保持订单活跃以确保稳定性。"
                )
                return False
        
        # Calculate adaptive thresholds / 计算自适应阈值
        price_threshold = mid_price * PRICE_THRESHOLD_PCT if mid_price > 0 else 0.01
        curr_price = current_order.get("price", 0)
        tgt_price = target_order.get("price", 0)
        price_diff = abs(curr_price - tgt_price)
        
        # Quantity threshold (percentage-based) / 数量阈值（基于百分比）
        # Support both "quantity" and "amount" fields (different exchanges use different field names)
        # 支持 "quantity" 和 "amount" 字段（不同交易所使用不同的字段名）
        curr_qty = current_order.get("quantity") or current_order.get("amount", 0)
        tgt_qty = target_order.get("quantity") or target_order.get("amount", 0)
        qty_threshold = max(curr_qty, tgt_qty) * QTY_THRESHOLD_PCT if max(curr_qty, tgt_qty) > 0 else 0.001
        qty_diff = abs(curr_qty - tgt_qty)
        
        # Only cancel if difference exceeds adaptive threshold / 仅在差异超过自适应阈值时取消
        should_cancel = price_diff > price_threshold or qty_diff > qty_threshold
        
        if should_cancel:
            logger.info(
                f"Order {current_order.get('id')} exceeds threshold. "
                f"Price diff: {price_diff:.4f} > {price_threshold:.4f} ({PRICE_THRESHOLD_PCT*100:.2f}% of mid), "
                f"Qty diff: {qty_diff:.4f} > {qty_threshold:.4f}. "
                f"Will cancel and replace. "
                f"订单 {current_order.get('id')} 超过阈值。"
                f"价格差: {price_diff:.4f} > {price_threshold:.4f}（中间价的 {PRICE_THRESHOLD_PCT*100:.2f}%），"
                f"数量差: {qty_diff:.4f} > {qty_threshold:.4f}。将取消并替换。"
            )
        else:
            logger.debug(
                f"Order {current_order.get('id')} within threshold. "
                f"Price diff: {price_diff:.4f} <= {price_threshold:.4f}, "
                f"Qty diff: {qty_diff:.4f} <= {qty_threshold:.4f}. "
                f"Keeping order. "
                f"订单 {current_order.get('id')} 在阈值内。"
                f"价格差: {price_diff:.4f} <= {price_threshold:.4f}，"
                f"数量差: {qty_diff:.4f} <= {qty_threshold:.4f}。保持订单。"
            )
        
        return should_cancel

    def sync_orders(
        self, 
        current_orders: List[Dict[str, Any]], 
        target_orders: List[Dict[str, Any]],
        mid_price: float = None
    ) -> Tuple[List[str], List[Dict[str, Any]]]:
        """
        Compares current and target orders to determine actions.
        Uses adaptive thresholds and order stability window.

        Args:
            current_orders: List of current open orders
            target_orders: List of target orders to achieve
            mid_price: Current mid price for adaptive threshold (optional, will estimate if not provided)

        Returns:
            Tuple of (order_ids_to_cancel, orders_to_place)
        """
        to_cancel = []
        to_place = []

        # Helper to group by side
        curr_buy = next((o for o in current_orders if o["side"] == "buy"), None)
        curr_sell = next((o for o in current_orders if o["side"] == "sell"), None)

        tgt_buy = next((o for o in target_orders if o["side"] == "buy"), None)
        tgt_sell = next((o for o in target_orders if o["side"] == "sell"), None)

        # Estimate mid_price if not provided / 如果未提供，估算中间价
        if mid_price is None:
            if tgt_buy and tgt_sell:
                # Estimate from target orders / 从目标订单估算
                mid_price = (tgt_buy.get("price", 0) + tgt_sell.get("price", 0)) / 2
            elif curr_buy and curr_sell:
                # Estimate from current orders / 从当前订单估算
                mid_price = (curr_buy.get("price", 0) + curr_sell.get("price", 0)) / 2
            else:
                # Fallback to fixed threshold / 回退到固定阈值
                mid_price = 1000.0  # Default estimate
                logger.warning(
                    f"Mid price not provided, using default {mid_price} for threshold calculation. "
                    f"未提供中间价，使用默认值 {mid_price} 进行阈值计算。"
                )

        # Log target orders for debugging
        logger.debug(
            f"Order sync: target_buy={tgt_buy}, target_sell={tgt_sell}, "
            f"current_buy={curr_buy}, current_sell={curr_sell}, "
            f"mid_price={mid_price:.2f}"
        )

        # Compare Buy
        if tgt_buy:
            if curr_buy:
                # Use improved cancellation logic / 使用改进的取消逻辑
                if self._should_cancel_order(curr_buy, tgt_buy, mid_price):
                    to_cancel.append(curr_buy["id"])
                    to_place.append(tgt_buy)
                else:
                    logger.debug(
                        f"Buy order unchanged: price={curr_buy.get('price')}, qty={curr_buy.get('quantity')}. "
                        f"买入订单未变化: 价格={curr_buy.get('price')}, 数量={curr_buy.get('quantity')}。"
                    )
            else:
                logger.info(
                    f"No current buy order, will place: price={tgt_buy.get('price')}, qty={tgt_buy.get('quantity')}. "
                    f"没有当前买入订单，将下单: 价格={tgt_buy.get('price')}, 数量={tgt_buy.get('quantity')}。"
                )
                to_place.append(tgt_buy)
        else:
            if curr_buy:
                logger.info(
                    f"No target buy order, will cancel current: {curr_buy['id']}. "
                    f"没有目标买入订单，将取消当前订单: {curr_buy['id']}。"
                )
                to_cancel.append(curr_buy["id"])

        # Compare Sell
        if tgt_sell:
            if curr_sell:
                # Use improved cancellation logic / 使用改进的取消逻辑
                if self._should_cancel_order(curr_sell, tgt_sell, mid_price):
                    to_cancel.append(curr_sell["id"])
                    to_place.append(tgt_sell)
                else:
                    logger.debug(
                        f"Sell order unchanged: price={curr_sell.get('price')}, qty={curr_sell.get('quantity')}. "
                        f"卖出订单未变化: 价格={curr_sell.get('price')}, 数量={curr_sell.get('quantity')}。"
                    )
            else:
                logger.info(
                    f"No current sell order, will place: price={tgt_sell.get('price')}, qty={tgt_sell.get('quantity')}. "
                    f"没有当前卖出订单，将下单: 价格={tgt_sell.get('price')}, 数量={tgt_sell.get('quantity')}。"
                )
                to_place.append(tgt_sell)
        else:
            if curr_sell:
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
