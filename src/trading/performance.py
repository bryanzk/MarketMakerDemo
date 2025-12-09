"""
Performance Tracker Module / 绩效追踪模块

Tracks trading performance metrics including PnL and win rate.
追踪交易绩效指标，包括盈亏和胜率。

Owner: Agent TRADING
"""

from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional


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


def calculate_trade_performance(
    trades: List[Dict[str, Any]],
    start_time_ms: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Calculate aggregate performance statistics from a list of trade dicts.

    Designed to mirror the logic used by /api/performance so it can be reused
    for strategy-specific performance calculations.
    """
    start_time_sec: Optional[float] = None
    if start_time_ms is not None:
        start_time_sec = start_time_ms / 1000.0

    if start_time_sec is not None:
        filtered_trades = [
            t for t in trades if t.get("timestamp", 0) >= start_time_sec
        ]
    else:
        filtered_trades = list(trades)

    total_trades = len(filtered_trades)
    winning_trades = len([t for t in filtered_trades if t.get("pnl", 0) > 0])
    losing_trades = len([t for t in filtered_trades if t.get("pnl", 0) <= 0])
    realized_pnl = sum(float(t.get("pnl", 0.0)) for t in filtered_trades)

    win_rate = (
        (winning_trades / total_trades) * 100 if total_trades > 0 else 0.0
    )

    pnl_history: List[List[float]] = []
    cumulative_pnl = 0.0

    # Add initial point at session start if provided
    if start_time_ms is not None:
        pnl_history.append([int(start_time_ms), 0])

    for trade in filtered_trades:
        cumulative_pnl += float(trade.get("pnl", 0.0))
        ts_ms = int(float(trade.get("timestamp", 0)) * 1000)
        pnl_history.append([ts_ms, cumulative_pnl])

    return {
        "realized_pnl": realized_pnl,
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "win_rate": win_rate,
        "pnl_history": pnl_history,
    }


def calculate_strategy_performance(
    trades: List[Dict[str, Any]],
    start_time_ms: Optional[int] = None,
    strategy_type: Optional[str] = None,
    strategy_id: Optional[str] = None,
    symbol: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Calculate performance statistics for a specific strategy subset.

    Filters trades by strategy_type/strategy_id/symbol first, then delegates to
    calculate_trade_performance for aggregate stats.
    """
    filtered: List[Dict[str, Any]] = []
    for trade in trades:
        if strategy_type and trade.get("strategy_type") != strategy_type:
            continue
        if strategy_id and trade.get("strategy_id") != strategy_id:
            continue
        if symbol and trade.get("symbol") != symbol:
            continue
        filtered.append(trade)

    return calculate_trade_performance(filtered, start_time_ms=start_time_ms)
