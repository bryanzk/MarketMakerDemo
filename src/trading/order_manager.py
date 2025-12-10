"""
Order Manager Module / 订单管理模块

Manages order synchronization between current and target orders.
管理当前订单和目标订单之间的同步。

Owner: Agent TRADING
"""

import logging
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


class OrderManager:
    """Manages order synchronization."""

    def sync_orders(
        self, current_orders: List[Dict[str, Any]], target_orders: List[Dict[str, Any]]
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
                    logger.info(
                        f"Buy order needs update: price_diff={price_diff:.4f}, qty_diff={qty_diff:.4f}. "
                        f"Current: price={curr_price}, qty={curr_qty}. "
                        f"Target: price={tgt_price}, qty={tgt_qty}. "
                        f"买入订单需要更新: 价格差={price_diff:.4f}, 数量差={qty_diff:.4f}。"
                    )
                    to_cancel.append(curr_buy["id"])
                    to_place.append(tgt_buy)
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
                    logger.info(
                        f"Sell order needs update: price_diff={price_diff:.4f}, qty_diff={qty_diff:.4f}. "
                        f"Current: price={curr_price}, qty={curr_qty}. "
                        f"Target: price={tgt_price}, qty={tgt_qty}. "
                        f"卖出订单需要更新: 价格差={price_diff:.4f}, 数量差={qty_diff:.4f}。"
                    )
                    to_cancel.append(curr_sell["id"])
                    to_place.append(tgt_sell)
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
