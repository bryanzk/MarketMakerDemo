"""
Unit Tests for Risk Indicators (P0)

Tests for:
- US-R1: Liquidation Buffer
- US-R2: Inventory Drift
- US-R3: Max Drawdown
- US-R4: Overall Risk Level
- US-R5: API Endpoints
"""

import pytest
from unittest.mock import MagicMock, patch

# Import the module to be tested (will be created next)
from alphaloop.portfolio.risk import RiskIndicators


class TestLiquidationBuffer:
    """US-R1: Liquidation Buffer Tests"""

    def test_liquidation_buffer_long_position(self):
        """
        US-R1.1: Calculate liquidation buffer for long position
        Given: current_price=100, liquidation_price=80, position_side='long'
        Then: buffer = (100-80)/100 = 20%
        """
        buffer = RiskIndicators.calculate_liquidation_buffer(
            current_price=100.0,
            liquidation_price=80.0,
            position_side="long"
        )
        assert buffer == pytest.approx(20.0, rel=0.01)

    def test_liquidation_buffer_short_position(self):
        """
        US-R1.1: Calculate liquidation buffer for short position
        Given: current_price=100, liquidation_price=120, position_side='short'
        Then: buffer = (120-100)/100 = 20%
        """
        buffer = RiskIndicators.calculate_liquidation_buffer(
            current_price=100.0,
            liquidation_price=120.0,
            position_side="short"
        )
        assert buffer == pytest.approx(20.0, rel=0.01)

    def test_liquidation_buffer_no_position(self):
        """
        US-R1.1: No position returns None
        """
        buffer = RiskIndicators.calculate_liquidation_buffer(
            current_price=100.0,
            liquidation_price=0.0,
            position_side=None
        )
        assert buffer is None

    def test_liquidation_buffer_status_safe(self):
        """
        US-R1.2: Buffer > 20% returns 'safe'
        """
        status = RiskIndicators.get_liquidation_buffer_status(25.0)
        assert status == "safe"

    def test_liquidation_buffer_status_warning(self):
        """
        US-R1.2: Buffer 10-20% returns 'warning'
        """
        status = RiskIndicators.get_liquidation_buffer_status(15.0)
        assert status == "warning"

    def test_liquidation_buffer_status_danger(self):
        """
        US-R1.2: Buffer 5-10% returns 'danger'
        """
        status = RiskIndicators.get_liquidation_buffer_status(8.0)
        assert status == "danger"

    def test_liquidation_buffer_status_critical(self):
        """
        US-R1.2: Buffer < 5% returns 'critical'
        """
        status = RiskIndicators.get_liquidation_buffer_status(3.0)
        assert status == "critical"


class TestInventoryDrift:
    """US-R2: Inventory Drift Tests"""

    def test_inventory_drift_long_position(self):
        """
        US-R2.1: Long position drift calculation
        Given: position=0.5, max_position=1.0
        Then: drift = +50%
        """
        drift = RiskIndicators.calculate_inventory_drift(
            position_amt=0.5,
            max_position=1.0
        )
        assert drift == pytest.approx(50.0, rel=0.01)

    def test_inventory_drift_short_position(self):
        """
        US-R2.1: Short position drift calculation
        Given: position=-0.3, max_position=1.0
        Then: drift = -30%
        """
        drift = RiskIndicators.calculate_inventory_drift(
            position_amt=-0.3,
            max_position=1.0
        )
        assert drift == pytest.approx(-30.0, rel=0.01)

    def test_inventory_drift_balanced(self):
        """
        US-R2.1: Near-zero position is balanced
        """
        drift = RiskIndicators.calculate_inventory_drift(
            position_amt=0.05,
            max_position=1.0
        )
        assert drift == pytest.approx(5.0, rel=0.01)

    def test_inventory_drift_status_balanced(self):
        """
        US-R2.1: |drift| < 20% returns 'balanced'
        """
        status = RiskIndicators.get_inventory_drift_status(15.0)
        assert status == "balanced"

    def test_inventory_drift_status_offset(self):
        """
        US-R2.1: |drift| 20-50% returns 'offset'
        """
        status = RiskIndicators.get_inventory_drift_status(35.0)
        assert status == "offset"

    def test_inventory_drift_status_severe(self):
        """
        US-R2.1: |drift| 50-80% returns 'severe'
        """
        status = RiskIndicators.get_inventory_drift_status(-65.0)
        assert status == "severe"

    def test_inventory_drift_status_extreme(self):
        """
        US-R2.1: |drift| > 80% returns 'extreme'
        """
        status = RiskIndicators.get_inventory_drift_status(90.0)
        assert status == "extreme"

    def test_inventory_drift_direction_long(self):
        """
        US-R2.2: Positive drift indicates long direction
        """
        direction = RiskIndicators.get_inventory_direction(45.0)
        assert direction == "long"

    def test_inventory_drift_direction_short(self):
        """
        US-R2.2: Negative drift indicates short direction
        """
        direction = RiskIndicators.get_inventory_direction(-30.0)
        assert direction == "short"


class TestMaxDrawdown:
    """US-R3: Max Drawdown Tests"""

    def test_max_drawdown_calculation(self):
        """
        US-R3.1: Calculate max drawdown from PnL history
        Given: PnL history [0, 100, 150, 120, 180]
        Peak = 150, Trough after peak = 120
        Then: Max DD = (150-120)/150 = 20%
        """
        pnl_history = [0, 100, 150, 120, 180]
        drawdown = RiskIndicators.calculate_max_drawdown(pnl_history)
        assert drawdown == pytest.approx(-20.0, rel=0.01)

    def test_max_drawdown_no_drawdown(self):
        """
        US-R3.1: Monotonically increasing PnL has 0% drawdown
        """
        pnl_history = [0, 50, 100, 150, 200]
        drawdown = RiskIndicators.calculate_max_drawdown(pnl_history)
        assert drawdown == pytest.approx(0.0, rel=0.01)

    def test_max_drawdown_empty_history(self):
        """
        US-R3.1: Empty history returns 0
        """
        drawdown = RiskIndicators.calculate_max_drawdown([])
        assert drawdown == 0.0

    def test_max_drawdown_single_point(self):
        """
        US-R3.1: Single point returns 0
        """
        drawdown = RiskIndicators.calculate_max_drawdown([100])
        assert drawdown == 0.0

    def test_max_drawdown_status_excellent(self):
        """
        US-R3.1: |dd| < 5% returns 'excellent'
        """
        status = RiskIndicators.get_max_drawdown_status(-3.0)
        assert status == "excellent"

    def test_max_drawdown_status_normal(self):
        """
        US-R3.1: |dd| 5-10% returns 'normal'
        """
        status = RiskIndicators.get_max_drawdown_status(-7.0)
        assert status == "normal"

    def test_max_drawdown_status_warning(self):
        """
        US-R3.1: |dd| 10-20% returns 'warning'
        """
        status = RiskIndicators.get_max_drawdown_status(-15.0)
        assert status == "warning"

    def test_max_drawdown_status_danger(self):
        """
        US-R3.1: |dd| > 20% returns 'danger'
        """
        status = RiskIndicators.get_max_drawdown_status(-25.0)
        assert status == "danger"


class TestOverallRiskLevel:
    """US-R4: Overall Risk Level Tests"""

    def test_overall_risk_critical(self):
        """
        US-R4.1: Any critical indicator -> overall critical
        """
        risk_level = RiskIndicators.calculate_overall_risk_level(
            liq_buffer_status="critical",
            inv_drift_status="balanced",
            max_dd_status="normal"
        )
        assert risk_level == "critical"

    def test_overall_risk_high(self):
        """
        US-R4.1: Any danger indicator -> overall high
        """
        risk_level = RiskIndicators.calculate_overall_risk_level(
            liq_buffer_status="safe",
            inv_drift_status="severe",
            max_dd_status="normal"
        )
        assert risk_level == "high"

    def test_overall_risk_medium(self):
        """
        US-R4.1: Any warning indicator -> overall medium
        """
        risk_level = RiskIndicators.calculate_overall_risk_level(
            liq_buffer_status="warning",
            inv_drift_status="balanced",
            max_dd_status="excellent"
        )
        assert risk_level == "medium"

    def test_overall_risk_low(self):
        """
        US-R4.1: All safe indicators -> overall low
        """
        risk_level = RiskIndicators.calculate_overall_risk_level(
            liq_buffer_status="safe",
            inv_drift_status="balanced",
            max_dd_status="excellent"
        )
        assert risk_level == "low"


class TestRiskIndicatorsAPI:
    """US-R5: API Tests"""

    @pytest.fixture
    def mock_exchange(self):
        """Create mock exchange with position data"""
        exchange = MagicMock()
        exchange.fetch_account_data.return_value = {
            "position_amt": 0.5,
            "entry_price": 2000.0,
            "balance": 5000.0,
            "liquidation_price": 1800.0,
        }
        return exchange

    def test_get_risk_indicators(self, mock_exchange):
        """
        US-R5.1: Get all risk indicators
        """
        # Use the RiskIndicators class to compute from exchange data
        indicators = RiskIndicators.from_exchange_data(
            current_price=2000.0,
            position_amt=0.5,
            liquidation_price=1800.0,
            max_position=1.0,
            pnl_history=[0, 50, 100, 80, 120]
        )

        assert "liquidation_buffer" in indicators
        assert "liquidation_buffer_status" in indicators
        assert "inventory_drift" in indicators
        assert "inventory_drift_status" in indicators
        assert "max_drawdown" in indicators
        assert "max_drawdown_status" in indicators
        assert "overall_risk_level" in indicators

    def test_risk_indicators_values(self):
        """
        US-R5.1: Verify indicator values
        Given: price=2000, liq_price=1700 (long), position=0.3/1.0, pnl with 20% dd
        """
        indicators = RiskIndicators.from_exchange_data(
            current_price=2000.0,
            position_amt=0.3,  # Changed to get 30% drift (offset range)
            liquidation_price=1700.0,  # 15% buffer (warning range)
            max_position=1.0,
            pnl_history=[0, 100, 150, 120, 180]
        )

        # Liquidation buffer: (2000-1700)/2000 = 15%
        assert indicators["liquidation_buffer"] == pytest.approx(15.0, rel=0.01)
        assert indicators["liquidation_buffer_status"] == "warning"

        # Inventory drift: 0.3/1.0 = 30%
        assert indicators["inventory_drift"] == pytest.approx(30.0, rel=0.01)
        assert indicators["inventory_drift_status"] == "offset"

        # Max drawdown: (150-120)/150 = 20%
        assert indicators["max_drawdown"] == pytest.approx(-20.0, rel=0.01)
        assert indicators["max_drawdown_status"] == "danger"  # >20% is danger


class TestRiskIndicatorsAPIEndpoint:
    """Integration tests for /api/risk-indicators endpoint"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from fastapi.testclient import TestClient
        # Import here to avoid circular imports during test collection
        import sys
        sys.path.insert(0, "/Users/kezheng/Codes/CursorDeveloper/MarketMakerDemo")
        from server import app
        return TestClient(app)

    def test_risk_indicators_endpoint_returns_200(self, client):
        """
        US-R5.1: API returns 200 status
        """
        response = client.get("/api/risk-indicators")
        assert response.status_code == 200

    def test_risk_indicators_endpoint_structure(self, client):
        """
        US-R5.1: API returns expected structure
        """
        response = client.get("/api/risk-indicators")
        data = response.json()

        # Check all expected fields exist
        expected_fields = [
            "liquidation_buffer",
            "liquidation_buffer_status",
            "inventory_drift",
            "inventory_drift_status",
            "max_drawdown",
            "max_drawdown_status",
            "overall_risk_level"
        ]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    def test_risk_indicators_endpoint_valid_statuses(self, client):
        """
        US-R5.1: API returns valid status values
        """
        response = client.get("/api/risk-indicators")
        data = response.json()

        valid_liq_statuses = ["safe", "warning", "danger", "critical", None]
        valid_drift_statuses = ["balanced", "offset", "severe", "extreme", None]
        valid_dd_statuses = ["excellent", "normal", "warning", "danger", None]
        valid_overall = ["low", "medium", "high", "critical"]

        assert data["liquidation_buffer_status"] in valid_liq_statuses
        assert data["inventory_drift_status"] in valid_drift_statuses
        assert data["max_drawdown_status"] in valid_dd_statuses
        assert data["overall_risk_level"] in valid_overall

