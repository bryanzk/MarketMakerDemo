import pytest
from alphaloop.agents.risk import RiskAgent
from alphaloop.core.config import RISK_LIMITS


class TestRiskAgent:
    def setup_method(self):
        self.agent = RiskAgent()

    def test_validate_proposal_approved(self):
        # Spread within limits
        proposal = {"spread": 0.002}  # 0.2%
        approved, reason = self.agent.validate_proposal(proposal)
        assert approved == True
        assert reason == "Approved"

    def test_validate_proposal_too_tight(self):
        # Spread too tight
        proposal = {"spread": 0.0001}  # 0.01%
        approved, reason = self.agent.validate_proposal(proposal)
        assert approved == False
        assert "too tight" in reason

    def test_validate_proposal_too_wide(self):
        # Spread too wide
        proposal = {"spread": 0.1}  # 10%
        approved, reason = self.agent.validate_proposal(proposal)
        assert approved == False
        assert "too wide" in reason
