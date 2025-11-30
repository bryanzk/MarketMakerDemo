"""
Risk Manager Module / 风险管理模块

Manages position risk limits and allowed trading sides.
管理仓位风险限制和允许的交易方向。

Owner: Agent TRADING
"""

from typing import List

from src.shared.config import MAX_POSITION


class RiskManager:
    """Manages position risk limits."""

    def check_position_limits(self, position_amt: float) -> List[str]:
        """
        Checks if position is within limits.

        Args:
            position_amt: Current position amount

        Returns:
            List of allowed sides ['buy', 'sell']
        """
        allowed_sides = ["buy", "sell"]

        if position_amt >= MAX_POSITION:
            if "buy" in allowed_sides:
                allowed_sides.remove("buy")
        elif position_amt <= -MAX_POSITION:
            if "sell" in allowed_sides:
                allowed_sides.remove("sell")

        return allowed_sides

