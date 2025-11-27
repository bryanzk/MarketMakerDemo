"""
Risk Indicators Module

Implements P0 risk monitoring indicators:
- Liquidation Buffer (防爆仓)
- Inventory Drift (库存偏移)
- Max Drawdown (最大回撤)

Based on User Stories: US-R1, US-R2, US-R3, US-R4
"""

from typing import Dict, List, Optional


class RiskIndicators:
    """
    Risk indicator calculations for market making strategies.

    All percentages are returned as float values (e.g., 20.0 for 20%)
    """

    # =========================================================================
    # US-R1: Liquidation Buffer
    # =========================================================================

    @staticmethod
    def calculate_liquidation_buffer(
        current_price: float, liquidation_price: float, position_side: Optional[str]
    ) -> Optional[float]:
        """
        Calculate the liquidation buffer percentage.

        For LONG positions: buffer = (current - liq) / current * 100
        For SHORT positions: buffer = (liq - current) / current * 100

        Args:
            current_price: Current market price
            liquidation_price: Forced liquidation price
            position_side: 'long', 'short', or None

        Returns:
            Buffer percentage, or None if no position
        """
        if position_side is None or liquidation_price <= 0 or current_price <= 0:
            return None

        if position_side == "long":
            buffer = (current_price - liquidation_price) / current_price * 100
        else:  # short
            buffer = (liquidation_price - current_price) / current_price * 100

        return max(0.0, buffer)  # Buffer cannot be negative (already liquidated)

    @staticmethod
    def get_liquidation_buffer_status(buffer: Optional[float]) -> Optional[str]:
        """
        Get risk status based on liquidation buffer.

        Thresholds:
        - > 20%: safe
        - 10-20%: warning
        - 5-10%: danger
        - < 5%: critical

        Args:
            buffer: Liquidation buffer percentage

        Returns:
            Status string: 'safe', 'warning', 'danger', 'critical', or None
        """
        if buffer is None:
            return None

        if buffer > 20:
            return "safe"
        elif buffer > 10:
            return "warning"
        elif buffer > 5:
            return "danger"
        else:
            return "critical"

    # =========================================================================
    # US-R2: Inventory Drift
    # =========================================================================

    @staticmethod
    def calculate_inventory_drift(position_amt: float, max_position: float) -> float:
        """
        Calculate inventory drift percentage.

        Drift = position / max_position * 100

        Positive drift = net long position
        Negative drift = net short position

        Args:
            position_amt: Current position amount (positive=long, negative=short)
            max_position: Maximum allowed position size

        Returns:
            Drift percentage (-100 to +100)
        """
        if max_position <= 0:
            return 0.0

        drift = (position_amt / max_position) * 100
        return max(-100.0, min(100.0, drift))  # Clamp to [-100, 100]

    @staticmethod
    def get_inventory_drift_status(drift: float) -> str:
        """
        Get risk status based on inventory drift.

        Thresholds (absolute value):
        - < 20%: balanced
        - 20-50%: offset
        - 50-80%: severe
        - > 80%: extreme

        Args:
            drift: Inventory drift percentage

        Returns:
            Status string: 'balanced', 'offset', 'severe', 'extreme'
        """
        abs_drift = abs(drift)

        if abs_drift < 20:
            return "balanced"
        elif abs_drift < 50:
            return "offset"
        elif abs_drift < 80:
            return "severe"
        else:
            return "extreme"

    @staticmethod
    def get_inventory_direction(drift: float) -> str:
        """
        Get inventory direction based on drift sign.

        Args:
            drift: Inventory drift percentage

        Returns:
            'long' if positive, 'short' if negative, 'neutral' if near zero
        """
        if drift > 5:
            return "long"
        elif drift < -5:
            return "short"
        else:
            return "neutral"

    # =========================================================================
    # US-R3: Max Drawdown
    # =========================================================================

    @staticmethod
    def calculate_max_drawdown(pnl_history: List[float]) -> float:
        """
        Calculate maximum drawdown from PnL history.

        Max Drawdown = (peak - trough) / peak * 100

        Returned as negative percentage (e.g., -20.0 for 20% drawdown)

        Args:
            pnl_history: List of cumulative PnL values

        Returns:
            Max drawdown as negative percentage (0.0 if no drawdown)
        """
        if not pnl_history or len(pnl_history) < 2:
            return 0.0

        peak = pnl_history[0]
        max_drawdown = 0.0

        for pnl in pnl_history:
            if pnl > peak:
                peak = pnl
            elif peak > 0:  # Only calculate drawdown if peak is positive
                drawdown = (peak - pnl) / peak * 100
                max_drawdown = max(max_drawdown, drawdown)

        return -max_drawdown  # Return as negative value

    @staticmethod
    def get_max_drawdown_status(drawdown: float) -> str:
        """
        Get risk status based on max drawdown.

        Thresholds (absolute value):
        - < 5%: excellent
        - 5-10%: normal
        - 10-20%: warning
        - > 20%: danger

        Args:
            drawdown: Max drawdown percentage (negative value)

        Returns:
            Status string: 'excellent', 'normal', 'warning', 'danger'
        """
        abs_dd = abs(drawdown)

        if abs_dd < 5:
            return "excellent"
        elif abs_dd < 10:
            return "normal"
        elif abs_dd < 20:
            return "warning"
        else:
            return "danger"

    # =========================================================================
    # US-R4: Overall Risk Level
    # =========================================================================

    @staticmethod
    def calculate_overall_risk_level(
        liq_buffer_status: Optional[str], inv_drift_status: str, max_dd_status: str
    ) -> str:
        """
        Calculate overall risk level from individual indicators.

        Priority (highest to lowest):
        - critical: Any indicator is critical
        - high: Any indicator is danger/severe/extreme
        - medium: Any indicator is warning/offset
        - low: All indicators are safe/balanced/excellent

        Args:
            liq_buffer_status: 'safe', 'warning', 'danger', 'critical', or None
            inv_drift_status: 'balanced', 'offset', 'severe', 'extreme'
            max_dd_status: 'excellent', 'normal', 'warning', 'danger'

        Returns:
            Overall risk level: 'low', 'medium', 'high', 'critical'
        """
        critical_statuses = {"critical"}
        danger_statuses = {"danger", "severe", "extreme"}
        warning_statuses = {"warning", "offset"}

        statuses = [liq_buffer_status, inv_drift_status, max_dd_status]

        # Check for critical
        if any(s in critical_statuses for s in statuses if s):
            return "critical"

        # Check for danger/high
        if any(s in danger_statuses for s in statuses if s):
            return "high"

        # Check for warning/medium
        if any(s in warning_statuses for s in statuses if s):
            return "medium"

        return "low"

    # =========================================================================
    # US-R5: Aggregate from Exchange Data
    # =========================================================================

    @classmethod
    def from_exchange_data(
        cls,
        current_price: float,
        position_amt: float,
        liquidation_price: float,
        max_position: float,
        pnl_history: List[float],
        position_side: Optional[str] = None,
    ) -> Dict:
        """
        Calculate all risk indicators from exchange data.

        Args:
            current_price: Current market price
            position_amt: Current position amount
            liquidation_price: Forced liquidation price
            max_position: Maximum allowed position
            pnl_history: List of cumulative PnL values
            position_side: 'long' or 'short' (auto-detected if None)

        Returns:
            Dict with all risk indicators and statuses
        """
        # Auto-detect position side if not provided
        if position_side is None:
            if position_amt > 0:
                position_side = "long"
            elif position_amt < 0:
                position_side = "short"
            else:
                position_side = None

        # Calculate individual indicators
        liq_buffer = cls.calculate_liquidation_buffer(
            current_price, liquidation_price, position_side
        )
        liq_buffer_status = cls.get_liquidation_buffer_status(liq_buffer)

        inv_drift = cls.calculate_inventory_drift(position_amt, max_position)
        inv_drift_status = cls.get_inventory_drift_status(inv_drift)
        inv_direction = cls.get_inventory_direction(inv_drift)

        max_dd = cls.calculate_max_drawdown(pnl_history)
        max_dd_status = cls.get_max_drawdown_status(max_dd)

        # Calculate overall risk
        overall_risk = cls.calculate_overall_risk_level(
            liq_buffer_status, inv_drift_status, max_dd_status
        )

        return {
            "liquidation_buffer": (
                round(liq_buffer, 2) if liq_buffer is not None else None
            ),
            "liquidation_buffer_status": liq_buffer_status,
            "inventory_drift": round(inv_drift, 2),
            "inventory_drift_status": inv_drift_status,
            "inventory_direction": inv_direction,
            "max_drawdown": round(max_dd, 2),
            "max_drawdown_status": max_dd_status,
            "overall_risk_level": overall_risk,
        }
