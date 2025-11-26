import pytest
from alphaloop.market.performance import PerformanceTracker


class TestPerformanceTracker:
    """Test cases for PerformanceTracker class"""

    def setup_method(self):
        """Setup for each test method"""
        self.tracker = PerformanceTracker()

    def test_initial_state(self):
        """Test initial state of tracker"""
        assert self.tracker.realized_pnl == 0.0
        assert self.tracker.total_trades == 0
        assert self.tracker.winning_trades == 0
        assert len(self.tracker.pnl_history) == 0
        assert self.tracker.get_win_rate() == 0.0

    def test_update_position_new_long(self):
        """Test opening a new long position"""
        self.tracker.update_position(0.1, 3000.0)

        assert self.tracker.last_position == 0.1
        assert self.tracker.avg_entry_price == 3000.0
        assert self.tracker.realized_pnl == 0.0  # No close yet
        assert self.tracker.total_trades == 0

    def test_update_position_new_short(self):
        """Test opening a new short position"""
        self.tracker.update_position(-0.1, 3000.0)

        assert self.tracker.last_position == -0.1
        assert self.tracker.avg_entry_price == 3000.0
        assert self.tracker.realized_pnl == 0.0

    def test_update_position_full_close_profitable(self):
        """Test closing a full long position with profit"""
        # Open long at 3000
        self.tracker.update_position(0.1, 3000.0)

        # Close at 3100 (100 profit per unit)
        self.tracker.update_position(0.0, 3100.0)

        assert self.tracker.realized_pnl == 10.0  # 0.1 * 100
        assert self.tracker.total_trades == 1
        assert self.tracker.winning_trades == 1
        assert self.tracker.get_win_rate() == 100.0
        assert len(self.tracker.pnl_history) == 1

    def test_update_position_full_close_loss(self):
        """Test closing a full long position with loss"""
        # Open long at 3000
        self.tracker.update_position(0.1, 3000.0)

        # Close at 2900 (100 loss per unit)
        self.tracker.update_position(0.0, 2900.0)

        assert self.tracker.realized_pnl == -10.0  # 0.1 * (-100)
        assert self.tracker.total_trades == 1
        assert self.tracker.winning_trades == 0
        assert self.tracker.get_win_rate() == 0.0

    def test_update_position_partial_close(self):
        """Test partial position close"""
        # Open long 0.2 at 3000
        self.tracker.update_position(0.2, 3000.0)

        # Partial close to 0.1 at 3100
        self.tracker.update_position(0.1, 3100.0)

        # Should realize profit on closed portion (0.1 * 100)
        assert self.tracker.realized_pnl == 10.0
        assert self.tracker.total_trades == 1
        assert self.tracker.last_position == 0.1

    def test_update_position_add_to_position(self):
        """Test adding to existing position"""
        # Open long 0.1 at 3000
        self.tracker.update_position(0.1, 3000.0)

        # Add 0.1 at 3100
        self.tracker.update_position(0.2, 3100.0)

        # Average entry should be 3050
        assert self.tracker.avg_entry_price == 3050.0
        assert self.tracker.realized_pnl == 0.0  # No close
        assert self.tracker.total_trades == 0

    def test_update_position_short_profitable(self):
        """Test closing a short position with profit"""
        # Open short at 3000
        self.tracker.update_position(-0.1, 3000.0)

        # Close at 2900 (profit on short)
        self.tracker.update_position(0.0, 2900.0)

        # Profit = (3000 - 2900) * 0.1 = 10
        assert self.tracker.realized_pnl == 10.0
        assert self.tracker.winning_trades == 1

    def test_win_rate_mixed_trades(self):
        """Test win rate with mixed winning and losing trades"""
        # Trade 1: Win
        self.tracker.update_position(0.1, 3000.0)
        self.tracker.update_position(0.0, 3100.0)

        # Trade 2: Loss
        self.tracker.update_position(0.1, 3100.0)
        self.tracker.update_position(0.0, 3050.0)

        # Trade 3: Win
        self.tracker.update_position(0.1, 3050.0)
        self.tracker.update_position(0.0, 3150.0)

        assert self.tracker.total_trades == 3
        assert self.tracker.winning_trades == 2
        assert self.tracker.get_win_rate() == 66.67

    def test_pnl_history_limit(self):
        """Test that PnL history is limited to max_history"""
        tracker = PerformanceTracker(max_history=3)

        # Make 5 trades
        for i in range(5):
            tracker.update_position(0.1, 3000.0)
            tracker.update_position(0.0, 3100.0)

        # Should only keep last 3
        assert len(tracker.pnl_history) == 3

    def test_get_stats(self):
        """Test get_stats returns complete statistics"""
        self.tracker.update_position(0.1, 3000.0)
        self.tracker.update_position(0.0, 3100.0)

        stats = self.tracker.get_stats()

        assert "realized_pnl" in stats
        assert "total_trades" in stats
        assert "winning_trades" in stats
        assert "win_rate" in stats
        assert "pnl_history" in stats

        assert stats["realized_pnl"] == 10.0
        assert stats["total_trades"] == 1
        assert stats["win_rate"] == 100.0

    def test_reset(self):
        """Test reset functionality"""
        # Make a trade
        self.tracker.update_position(0.1, 3000.0)
        self.tracker.update_position(0.0, 3100.0)

        # Reset
        self.tracker.reset()

        assert self.tracker.realized_pnl == 0.0
        assert self.tracker.total_trades == 0
        assert self.tracker.winning_trades == 0
        assert len(self.tracker.pnl_history) == 0
        assert self.tracker.last_position == 0.0
        assert self.tracker.avg_entry_price == 0.0
