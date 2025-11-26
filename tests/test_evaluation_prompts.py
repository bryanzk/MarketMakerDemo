"""
Unit Tests for Evaluation Prompt Templates
评估 Prompt 模板单元测试

Tests for:
- StrategyAdvisorPrompt
- RiskAdvisorPrompt
- MarketDiagnosisPrompt
"""

import pytest
from alphaloop.evaluation.prompts import (
    MarketDiagnosisPrompt,
    RiskAdvisorPrompt,
    StrategyAdvisorPrompt,
)
from alphaloop.evaluation.schemas import MarketContext


class TestStrategyAdvisorPrompt:
    """Test cases for StrategyAdvisorPrompt"""

    def test_generate_includes_market_context(self):
        """Test that generated prompt includes market context"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = StrategyAdvisorPrompt.generate(context)

        assert "ETHUSDT" in prompt
        assert "2,500.00" in prompt or "2500" in prompt  # Formatted price
        assert "3.50%" in prompt or "0.035" in prompt  # volatility_24h (formatted as percentage)
        assert "0.0100%" in prompt or "0.0001" in prompt  # funding_rate (formatted as percentage)

    def test_generate_includes_template_structure(self):
        """Test that generated prompt includes template structure"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = StrategyAdvisorPrompt.generate(context)

        assert "recommended_strategy" in prompt
        assert "spread" in prompt
        assert "confidence" in prompt
        assert "JSON" in prompt or "json" in prompt

    def test_generate_parameter_guidelines(self):
        """Test that prompt includes parameter guidelines"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = StrategyAdvisorPrompt.generate(context)

        assert "0.005 to 0.03" in prompt or "0.5% to 3%" in prompt
        assert "50 to 200" in prompt  # skew_factor range


class TestRiskAdvisorPrompt:
    """Test cases for RiskAdvisorPrompt"""

    def test_generate_includes_market_context(self):
        """Test that generated prompt includes market context"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
            current_position=0.5,
            position_side="long",
        )

        prompt = RiskAdvisorPrompt.generate(context)

        assert "ETHUSDT" in prompt
        assert "0.5" in prompt  # current_position
        assert "long" in prompt

    def test_generate_includes_risk_assessment_structure(self):
        """Test that generated prompt includes risk assessment structure"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = RiskAdvisorPrompt.generate(context)

        assert "risk_score" in prompt
        assert "risk_level" in prompt
        assert "liquidation_risk" in prompt
        assert "recommended_action" in prompt

    def test_generate_includes_warnings_field(self):
        """Test that prompt includes warnings field"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = RiskAdvisorPrompt.generate(context)

        assert "warnings" in prompt


class TestMarketDiagnosisPrompt:
    """Test cases for MarketDiagnosisPrompt"""

    def test_generate_includes_market_context(self):
        """Test that generated prompt includes market context"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = MarketDiagnosisPrompt.generate(context)

        assert "ETHUSDT" in prompt
        assert "2,500.00" in prompt or "2500" in prompt  # Formatted price

    def test_generate_includes_diagnosis_structure(self):
        """Test that generated prompt includes diagnosis structure"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = MarketDiagnosisPrompt.generate(context)

        assert "market_regime" in prompt
        assert "short_term_bias" in prompt
        assert "key_factors" in prompt
        assert "recommended_strategy_type" in prompt

    def test_generate_includes_regime_options(self):
        """Test that prompt includes market regime options"""
        context = MarketContext(
            symbol="ETHUSDT",
            mid_price=2500.0,
            best_bid=2499.5,
            best_ask=2500.5,
            spread_bps=4.0,
            volatility_24h=0.035,
            volatility_1h=0.012,
            funding_rate=0.0001,
            funding_rate_trend="rising",
        )

        prompt = MarketDiagnosisPrompt.generate(context)

        assert "trending" in prompt or "ranging" in prompt or "volatile" in prompt

