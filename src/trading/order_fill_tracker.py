"""
Order Fill Tracker Module / 订单填充跟踪模块

Tracks order fill status and calculates fill rate statistics.
跟踪订单填充状态并计算成交率统计。

Owner: Agent TRADING
"""

import time
from collections import deque
from typing import Any, Dict, List, Optional

from src.shared.logger import setup_logger

logger = setup_logger("OrderFillTracker")


class OrderFillTracker:
    """
    Tracks order fill status and calculates fill rate metrics.
    跟踪订单填充状态并计算成交率指标。
    """

    def __init__(self, max_history: int = 500):
        """
        Initialize order fill tracker.
        
        Args:
            max_history: Maximum number of order records to keep
        """
        # Order tracking: order_id -> order_info
        # 订单跟踪：order_id -> order_info
        self.active_orders: Dict[str, Dict[str, Any]] = {}
        
        # Order history: list of order records with status changes
        # 订单历史：包含状态变化的订单记录列表
        self.order_history: deque = deque(maxlen=max_history)
        
        # Statistics
        # 统计信息
        self.total_orders_placed = 0
        self.total_orders_filled = 0
        self.total_orders_cancelled = 0
        self.total_orders_partial_filled = 0
        
        # Time-based statistics (for recent performance)
        # 基于时间的统计（用于近期表现）
        self.recent_window_seconds = 300  # 5 minutes / 5 分钟
        self.recent_orders_placed = 0
        self.recent_orders_filled = 0
        self.recent_orders_cancelled = 0

    def track_order_placed(
        self,
        order_id: str,
        side: str,
        price: float,
        quantity: float,
        symbol: str,
        strategy_id: str,
        strategy_type: str,
        timestamp: Optional[float] = None,
    ) -> None:
        """
        Track a newly placed order.
        跟踪一个新下单的订单。
        
        Args:
            order_id: Order ID
            side: "buy" or "sell"
            price: Order price
            quantity: Order quantity
            symbol: Trading symbol
            strategy_id: Strategy instance ID
            strategy_type: Strategy type
            timestamp: Order timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()
        
        order_info = {
            "id": order_id,
            "side": side,
            "price": price,
            "quantity": quantity,
            "symbol": symbol,
            "strategy_id": strategy_id,
            "strategy_type": strategy_type,
            "status": "placed",
            "placed_timestamp": timestamp,
            "filled_timestamp": None,
            "cancelled_timestamp": None,
            "filled_quantity": 0.0,
            "fill_price": None,
            "order_age_seconds": 0.0,
        }
        
        self.active_orders[order_id] = order_info
        self.total_orders_placed += 1
        self.recent_orders_placed += 1
        
        # Add to history
        # 添加到历史记录
        history_record = order_info.copy()
        history_record["event"] = "placed"
        history_record["event_timestamp"] = timestamp
        self.order_history.append(history_record)
        
        logger.debug(
            f"Tracking order {order_id} ({side}) at {price} qty {quantity}. "
            f"跟踪订单 {order_id} ({side})，价格 {price}，数量 {quantity}。"
        )

    def track_order_filled(
        self,
        order_id: str,
        filled_quantity: float,
        fill_price: Optional[float] = None,
        timestamp: Optional[float] = None,
    ) -> bool:
        """
        Track an order fill (full or partial).
        跟踪订单填充（完全或部分）。
        
        Args:
            order_id: Order ID
            filled_quantity: Filled quantity
            fill_price: Average fill price (optional)
            timestamp: Fill timestamp (defaults to current time)
            
        Returns:
            True if order was tracked, False if order not found
        """
        if timestamp is None:
            timestamp = time.time()
        
        if order_id not in self.active_orders:
            logger.warning(
                f"Order {order_id} not found in active orders when tracking fill. "
                f"可能订单已过期或未跟踪。"
            )
            return False
        
        order_info = self.active_orders[order_id]
        original_quantity = order_info["quantity"]
        
        # Update order info
        # 更新订单信息
        order_info["filled_quantity"] = filled_quantity
        if fill_price is not None:
            order_info["fill_price"] = fill_price
        order_info["filled_timestamp"] = timestamp
        order_info["order_age_seconds"] = timestamp - order_info["placed_timestamp"]
        
        # Determine if fully filled or partially filled
        # 判断是完全填充还是部分填充
        is_fully_filled = filled_quantity >= original_quantity * 0.99  # 99% threshold for rounding
        if is_fully_filled:
            order_info["status"] = "filled"
            self.total_orders_filled += 1
            self.recent_orders_filled += 1
            
            # Remove from active orders
            # 从活跃订单中移除
            del self.active_orders[order_id]
            
            logger.info(
                f"Order {order_id} fully filled: {filled_quantity}/{original_quantity} at {fill_price or 'N/A'}. "
                f"Age: {order_info['order_age_seconds']:.1f}s. "
                f"订单 {order_id} 完全成交: {filled_quantity}/{original_quantity}，价格 {fill_price or 'N/A'}。"
                f"存活时间: {order_info['order_age_seconds']:.1f}秒。"
            )
        else:
            order_info["status"] = "partially_filled"
            self.total_orders_partial_filled += 1
            
            logger.info(
                f"Order {order_id} partially filled: {filled_quantity}/{original_quantity} at {fill_price or 'N/A'}. "
                f"订单 {order_id} 部分成交: {filled_quantity}/{original_quantity}，价格 {fill_price or 'N/A'}。"
            )
        
        # Add to history
        # 添加到历史记录
        history_record = order_info.copy()
        history_record["event"] = "filled" if is_fully_filled else "partially_filled"
        history_record["event_timestamp"] = timestamp
        self.order_history.append(history_record)
        
        return True

    def track_order_cancelled(
        self,
        order_id: str,
        reason: Optional[str] = None,
        timestamp: Optional[float] = None,
    ) -> bool:
        """
        Track an order cancellation.
        跟踪订单取消。
        
        Args:
            order_id: Order ID
            reason: Cancellation reason (optional)
            timestamp: Cancellation timestamp (defaults to current time)
            
        Returns:
            True if order was tracked, False if order not found
        """
        if timestamp is None:
            timestamp = time.time()
        
        if order_id not in self.active_orders:
            # Order might have been filled before cancellation
            # 订单可能在取消前已成交
            logger.debug(
                f"Order {order_id} not found in active orders when tracking cancellation. "
                f"可能订单已成交。"
            )
            return False
        
        order_info = self.active_orders[order_id]
        order_info["status"] = "cancelled"
        order_info["cancelled_timestamp"] = timestamp
        order_info["cancellation_reason"] = reason or "unknown"
        order_info["order_age_seconds"] = timestamp - order_info["placed_timestamp"]
        
        self.total_orders_cancelled += 1
        self.recent_orders_cancelled += 1
        
        # Remove from active orders
        # 从活跃订单中移除
        del self.active_orders[order_id]
        
        logger.info(
            f"Order {order_id} cancelled. Age: {order_info['order_age_seconds']:.1f}s, "
            f"Reason: {reason or 'unknown'}. "
            f"订单 {order_id} 已取消。存活时间: {order_info['order_age_seconds']:.1f}秒，"
            f"原因: {reason or 'unknown'}。"
        )
        
        # Add to history
        # 添加到历史记录
        history_record = order_info.copy()
        history_record["event"] = "cancelled"
        history_record["event_timestamp"] = timestamp
        self.order_history.append(history_record)
        
        return True

    def update_order_status_from_exchange(
        self, exchange_orders: List[Dict[str, Any]]
    ) -> None:
        """
        Update order status by comparing with exchange orders.
        通过比较交易所订单更新订单状态。
        
        Args:
            exchange_orders: List of orders from exchange.fetch_open_orders()
        """
        exchange_order_ids = {o.get("id") for o in exchange_orders if o.get("id")}
        
        # Check for filled orders (in active_orders but not in exchange_orders)
        # 检查已成交订单（在 active_orders 中但不在 exchange_orders 中）
        active_order_ids = set(self.active_orders.keys())
        filled_order_ids = active_order_ids - exchange_order_ids
        
        for order_id in filled_order_ids:
            order_info = self.active_orders[order_id]
            # If order is not in exchange orders, assume it's fully filled
            # 如果订单不在交易所订单列表中，假设它已完全成交
            filled_qty = order_info["quantity"]  # Assume full fill
            fill_price = order_info.get("fill_price", order_info["price"])
            
            self.track_order_filled(
                order_id,
                filled_quantity=filled_qty,
                fill_price=fill_price,
            )
        
        # Update partially filled orders
        # 更新部分成交订单
        for exchange_order in exchange_orders:
            order_id = exchange_order.get("id")
            if order_id in self.active_orders:
                filled_qty = exchange_order.get("filled_quantity") or exchange_order.get("filled_qty") or 0.0
                if filled_qty > 0:
                    fill_price = exchange_order.get("fill_price") or exchange_order.get("price")
                    original_qty = self.active_orders[order_id]["quantity"]
                    
                    # Only update if fill quantity changed
                    # 仅在填充数量变化时更新
                    if filled_qty != self.active_orders[order_id].get("filled_quantity", 0):
                        self.track_order_filled(
                            order_id,
                            filled_quantity=filled_qty,
                            fill_price=fill_price,
                        )

    def get_fill_rate(self, recent_only: bool = False) -> float:
        """
        Calculate fill rate (filled orders / total orders).
        计算成交率（成交订单 / 总订单）。
        
        Args:
            recent_only: If True, only calculate for recent window
            
        Returns:
            Fill rate as percentage (0.0 to 1.0)
        """
        if recent_only:
            total = self.recent_orders_placed
            filled = self.recent_orders_filled
        else:
            total = self.total_orders_placed
            filled = self.total_orders_filled
        
        if total == 0:
            return 0.0
        
        return filled / total

    def get_cancellation_rate(self, recent_only: bool = False) -> float:
        """
        Calculate cancellation rate (cancelled orders / total orders).
        计算取消率（取消订单 / 总订单）。
        
        Args:
            recent_only: If True, only calculate for recent window
            
        Returns:
            Cancellation rate as percentage (0.0 to 1.0)
        """
        if recent_only:
            total = self.recent_orders_placed
            cancelled = self.recent_orders_cancelled
        else:
            total = self.total_orders_placed
            cancelled = self.total_orders_cancelled
        
        if total == 0:
            return 0.0
        
        return cancelled / total

    def get_average_order_age(self, status: Optional[str] = None) -> float:
        """
        Calculate average order age before fill/cancellation.
        计算订单在成交/取消前的平均存活时间。
        
        Args:
            status: Filter by status ("filled", "cancelled", None for all)
            
        Returns:
            Average age in seconds
        """
        ages = []
        for order_info in self.order_history:
            if order_info.get("order_age_seconds", 0) > 0:
                if status is None or order_info.get("status") == status:
                    ages.append(order_info["order_age_seconds"])
        
        if not ages:
            return 0.0
        
        return sum(ages) / len(ages)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive fill rate statistics.
        获取综合成交率统计。
        
        Returns:
            Dictionary with fill rate metrics
        """
        # Clean up old recent statistics
        # 清理旧的近期统计
        current_time = time.time()
        if self.recent_orders_placed > 0:
            # Simple cleanup: reset if too old (would need timestamp tracking for precise cleanup)
            # 简单清理：如果太旧则重置（精确清理需要时间戳跟踪）
            pass
        
        fill_rate = self.get_fill_rate(recent_only=False)
        recent_fill_rate = self.get_fill_rate(recent_only=True)
        cancellation_rate = self.get_cancellation_rate(recent_only=False)
        recent_cancellation_rate = self.get_cancellation_rate(recent_only=True)
        
        avg_fill_age = self.get_average_order_age(status="filled")
        avg_cancel_age = self.get_average_order_age(status="cancelled")
        
        return {
            "total_orders_placed": self.total_orders_placed,
            "total_orders_filled": self.total_orders_filled,
            "total_orders_cancelled": self.total_orders_cancelled,
            "total_orders_partial_filled": self.total_orders_partial_filled,
            "active_orders_count": len(self.active_orders),
            "fill_rate": fill_rate,
            "fill_rate_pct": fill_rate * 100,
            "recent_fill_rate": recent_fill_rate,
            "recent_fill_rate_pct": recent_fill_rate * 100,
            "cancellation_rate": cancellation_rate,
            "cancellation_rate_pct": cancellation_rate * 100,
            "recent_cancellation_rate": recent_cancellation_rate,
            "recent_cancellation_rate_pct": recent_cancellation_rate * 100,
            "average_fill_age_seconds": avg_fill_age,
            "average_cancel_age_seconds": avg_cancel_age,
            "recent_window_seconds": self.recent_window_seconds,
            "recent_orders_placed": self.recent_orders_placed,
            "recent_orders_filled": self.recent_orders_filled,
            "recent_orders_cancelled": self.recent_orders_cancelled,
        }

    def reset_statistics(self) -> None:
        """Reset all statistics (keep history)."""
        self.total_orders_placed = 0
        self.total_orders_filled = 0
        self.total_orders_cancelled = 0
        self.total_orders_partial_filled = 0
        self.recent_orders_placed = 0
        self.recent_orders_filled = 0
        self.recent_orders_cancelled = 0
        # Note: active_orders and order_history are kept for continuity
        # 注意：保留 active_orders 和 order_history 以保持连续性

