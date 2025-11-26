from unittest.mock import Mock, patch

import pytest

from alphaloop.agents.quant import QuantAgent


class TestQuantAgent:
    """Test cases for QuantAgent"""

    def test_init_fallback(self):
        """Test initialization falls back when no API key"""
        with patch("alphaloop.agents.quant.GeminiProvider") as mock_provider:
            mock_provider.side_effect = ValueError("No API Key")
            agent = QuantAgent()
            assert agent.gateway is None

    def test_analyze_with_llm_success(self):
        """Test successful LLM analysis"""
        mock_gateway = Mock()
        mock_gateway.generate.return_value = '{"spread": 0.02, "reasoning": "Test"}'

        agent = QuantAgent(gateway=mock_gateway)

        config = {"spread": 0.01}
        stats = {"sharpe_ratio": 0.5}

        proposal = agent.analyze_and_propose(config, stats)

        assert proposal["spread"] == 0.02
        mock_gateway.generate.assert_called_once()

    def test_analyze_with_llm_json_error(self):
        """Test LLM returns invalid JSON, falls back to rules"""
        mock_gateway = Mock()
        mock_gateway.generate.return_value = "Invalid JSON"

        agent = QuantAgent(gateway=mock_gateway)

        config = {"spread": 0.01}
        stats = {
            "sharpe_ratio": 0.5,
            "win_rate": 40,
        }  # Low stats to trigger rule change

        # Should fall back to rule-based logic
        # Rule: if sharpe < 1.0, widen spread (0.01 * 1.1 = 0.011)
        proposal = agent.analyze_and_propose(config, stats)

        assert proposal["spread"] == pytest.approx(0.011)

    def test_rule_based_logic(self):
        """Test the fallback rule-based logic directly"""
        agent = QuantAgent(gateway=None)  # Force no gateway

        # Case 1: Low performance
        config = {"spread": 0.01}
        stats = {"sharpe_ratio": 0.5, "win_rate": 40}
        proposal = agent.analyze_and_propose(config, stats)
        assert proposal["spread"] > 0.01

        # Case 2: High performance
        stats = {"sharpe_ratio": 2.5, "win_rate": 60}
        proposal = agent.analyze_and_propose(config, stats)
        assert proposal["spread"] < 0.01
