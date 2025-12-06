import os
from unittest.mock import Mock, patch

import pytest

from src.ai.llm import GeminiProvider, LLMGateway, LLMProvider


class TestGeminiProvider:
    """Test cases for GeminiProvider"""

    def test_init_success(self):
        """Test successful initialization with API key"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure") as mock_config:
                with patch("google.generativeai.GenerativeModel") as mock_model:
                    provider = GeminiProvider()
                    mock_config.assert_called_with(api_key="test_key")
                    mock_model.assert_called_with("gemini-1.5-flash")

    def test_init_respects_env_model_preference(self):
        """Should pick model specified via GEMINI_MODEL env"""
        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "gemini-3-pro"},
            clear=True,
        ):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel") as mock_model:
                    GeminiProvider()
                    mock_model.assert_called_with("gemini-3-pro")

    def test_init_failure_no_key(self):
        """Test initialization failure when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
                GeminiProvider()

    def test_generate_success(self):
        """Test successful content generation"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel") as mock_model_cls:
                    mock_model = Mock()
                    mock_response = Mock()
                    mock_response.text = "Generated content"
                    mock_model.generate_content.return_value = mock_response
                    mock_model_cls.return_value = mock_model

                    provider = GeminiProvider()
                    result = provider.generate("Test prompt")

                    assert result == "Generated content"
                    mock_model.generate_content.assert_called_with("Test prompt")

    def test_generate_error(self):
        """Test error handling during generation"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel") as mock_model_cls:
                    mock_model = Mock()
                    mock_model.generate_content.side_effect = Exception("API Error")
                    mock_model_cls.return_value = mock_model

                    provider = GeminiProvider()
                    with pytest.raises(RuntimeError, match="Gemini API error"):
                        provider.generate("Test prompt")


class TestLLMGateway:
    """Test cases for LLMGateway"""

    def test_generate_delegation(self):
        """Test that gateway delegates generation to provider"""
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "Provider response"

        gateway = LLMGateway(mock_provider)
        result = gateway.generate("Test prompt")

        assert result == "Provider response"
        mock_provider.generate.assert_called_with("Test prompt")
