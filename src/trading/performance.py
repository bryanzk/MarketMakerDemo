"""
Performance Tracker Module / 绩效追踪模块

Tracks trading performance metrics including PnL and win rate.
追踪交易绩效指标，包括盈亏和胜率。

Owner: Agent TRADING
"""

from collections import deque
from datetime import datetime
from typing import Any, Dict, List


class PerformanceTracker:
    """Tracks trading performance metrics."""

    def __init__(self, max_history: int = 100):
        """
        Initialize performance tracker.

        Args:
            max_history: Maximum number of PnL history points to keep
        """
        self.realized_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.pnl_history = deque(maxlen=max_history)
        self.last_position = 0.0
        self.avg_entry_price = 0.0

    def update_position(self, new_position: float, current_price: float) -> None:
        """
        Update position and calculate realized PnL if position decreased.

        Args:
            new_position: New position size (can be negative for short)
            current_price: Current market price
        """
        position_change = new_position - self.last_position

        # If position decreased (partial or full close)
        if abs(new_position) < abs(self.last_position):
            closed_size = self.last_position - new_position

            # Calculate realized PnL for the closed portion
            if self.avg_entry_price > 0:
                pnl = (current_price - self.avg_entry_price) * closed_size
                self.realized_pnl += pnl

                # Record as a trade if we closed a position
                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1

                # Store PnL snapshot
                self._add_pnl_snapshot()

        # Update average entry price for new positions or additions
        if abs(new_position) > abs(self.last_position):
            # Adding to position
            if self.last_position == 0:
                self.avg_entry_price = current_price
            else:
                # Weighted average
                total_size = abs(new_position)
                old_value = abs(self.last_position) * self.avg_entry_price
                new_value = abs(position_change) * current_price
                self.avg_entry_price = (old_value + new_value) / total_size
        elif new_position == 0:
            # Position fully closed
            self.avg_entry_price = 0.0

        self.last_position = new_position

    def _add_pnl_snapshot(self) -> None:
        """Add current PnL to history with timestamp."""
        timestamp = int(datetime.now().timestamp() * 1000)
        self.pnl_history.append([timestamp, round(self.realized_pnl, 4)])

    def get_win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_trades == 0:
            return 0.0
        return round((self.winning_trades / self.total_trades) * 100, 2)

    def get_stats(self) -> Dict[str, Any]:
        """Get all performance statistics."""
        return {
            "realized_pnl": round(self.realized_pnl, 4),
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "win_rate": self.get_win_rate(),
            "pnl_history": list(self.pnl_history),
        }

    def reset(self) -> None:
        """Reset all statistics."""
        self.realized_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.pnl_history.clear()
        self.last_position = 0.0
        self.avg_entry_price = 0.0

