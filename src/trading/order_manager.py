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

        # Compare Buy
        if tgt_buy:
            if curr_buy:
                # Check if price changed significantly (> 0.01 tolerance)
                if abs(curr_buy["price"] - tgt_buy["price"]) > 0.01:
                    to_cancel.append(curr_buy["id"])
                    to_place.append(tgt_buy)
            else:
                to_place.append(tgt_buy)
        else:
            if curr_buy:
                to_cancel.append(curr_buy["id"])

        # Compare Sell
        if tgt_sell:
            if curr_sell:
                if abs(curr_sell["price"] - tgt_sell["price"]) > 0.01:
                    to_cancel.append(curr_sell["id"])
                    to_place.append(tgt_sell)
            else:
                to_place.append(tgt_sell)
        else:
            if curr_sell:
                to_cancel.append(curr_sell["id"])

        return to_cancel, to_place

