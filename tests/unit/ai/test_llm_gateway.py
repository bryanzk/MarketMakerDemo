import os
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.ai.llm import GeminiProvider, LLMGateway, LLMProvider


class TestGeminiProvider:
    """Test cases for GeminiProvider"""

    def test_init_success_new_sdk(self):
        """Test successful initialization with new SDK (google-genai)"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            # Mock new SDK
            with patch("src.ai.llm._USE_NEW_SDK", True):
                with patch("src.ai.llm.genai_new") as mock_genai:
                    mock_client = MagicMock()
                    mock_genai.Client.return_value = mock_client
                    provider = GeminiProvider()
                    mock_genai.Client.assert_called_with(api_key="test_key")
                    assert provider.client == mock_client

    def test_init_success_old_sdk(self):
        """Test successful initialization with old SDK (google-generativeai)"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            # Mock old SDK fallback
            with patch("src.ai.llm._USE_NEW_SDK", False):
                with patch("google.generativeai.configure") as mock_config:
                    with patch("google.generativeai.GenerativeModel") as mock_model:
                        provider = GeminiProvider()
                        mock_config.assert_called_with(api_key="test_key")
                        mock_model.assert_called_with("gemini-3-pro-preview")

    def test_init_respects_env_model_preference_new_sdk(self):
        """Should pick model specified via GEMINI_MODEL env (new SDK)"""
        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "gemini-1.5-flash"},
            clear=True,
        ):
            with patch("src.ai.llm._USE_NEW_SDK", True):
                with patch("src.ai.llm.genai_new") as mock_genai:
                    mock_genai.Client.return_value = MagicMock()
                    provider = GeminiProvider()
                    assert provider._model_name == "gemini-1.5-flash"

    def test_init_respects_env_model_preference_old_sdk(self):
        """Should pick model specified via GEMINI_MODEL env (old SDK)"""
        with patch.dict(
            "os.environ",
            {"GEMINI_API_KEY": "test_key", "GEMINI_MODEL": "gemini-1.5-flash"},
            clear=True,
        ):
            with patch("src.ai.llm._USE_NEW_SDK", False):
                with patch("google.generativeai.configure"):
                    with patch("google.generativeai.GenerativeModel") as mock_model:
                        GeminiProvider()
                        mock_model.assert_called_with("gemini-1.5-flash")

    def test_init_failure_no_key(self):
        """Test initialization failure when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="GEMINI_API_KEY is not set"):
                GeminiProvider()

    def test_generate_success_new_sdk(self):
        """Test successful content generation with new SDK"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("src.ai.llm._USE_NEW_SDK", True):
                with patch("src.ai.llm.genai_new") as mock_genai:
                    mock_client = MagicMock()
                    mock_response = MagicMock()
                    mock_response.text = "Generated content"
                    mock_client.models.generate_content.return_value = mock_response
                    mock_genai.Client.return_value = mock_client

                    provider = GeminiProvider()
                    result = provider.generate("Test prompt")

                    assert result == "Generated content"
                    mock_client.models.generate_content.assert_called_with(
                        model="gemini-3-pro-preview", contents="Test prompt"
                    )

    def test_generate_success_old_sdk(self):
        """Test successful content generation with old SDK"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("src.ai.llm._USE_NEW_SDK", False):
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

    def test_generate_error_new_sdk(self):
        """Test error handling during generation with new SDK"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("src.ai.llm._USE_NEW_SDK", True):
                with patch("src.ai.llm.genai_new") as mock_genai:
                    mock_client = MagicMock()
                    mock_client.models.generate_content.side_effect = Exception("API Error")
                    mock_genai.Client.return_value = mock_client

                    provider = GeminiProvider()
                    with pytest.raises(RuntimeError, match="Gemini API error"):
                        provider.generate("Test prompt")

    def test_generate_error_old_sdk(self):
        """Test error handling during generation with old SDK"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("src.ai.llm._USE_NEW_SDK", False):
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
