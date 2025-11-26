"""
Unit Tests for LLM Providers (OpenAI, Claude, and Utility Functions)
LLM Provider 单元测试（OpenAI、Claude 和工具函数）

Tests for:
- OpenAIProvider initialization and generation
- ClaudeProvider initialization and generation
- create_all_providers() function
- create_provider() function
- LLMGateway.provider_name property
- GeminiProvider.name property
"""

from unittest.mock import Mock, patch

import pytest

from alphaloop.core.llm import (
    ClaudeProvider,
    LLMGateway,
    OpenAIProvider,
    create_all_providers,
    create_provider,
    GeminiProvider,
)


class TestOpenAIProvider:
    """Test cases for OpenAIProvider"""

    def test_init_success(self):
        """Test successful initialization with API key"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_openai.return_value = mock_client
                provider = OpenAIProvider()
                assert provider.api_key == "test_key"
                assert provider._model_name == "gpt-4o"
                mock_openai.assert_called_with(api_key="test_key")

    def test_init_failure_no_key(self):
        """Test initialization failure when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="OPENAI_API_KEY is not set"):
                OpenAIProvider()

    def test_init_with_custom_model(self):
        """Test initialization with custom model"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI"):
                provider = OpenAIProvider(model="gpt-3.5-turbo")
                assert provider._model_name == "gpt-3.5-turbo"

    def test_name_property(self):
        """Test name property returns correct format"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI"):
                provider = OpenAIProvider()
                assert provider.name == "OpenAI (gpt-4o)"

    def test_generate_success(self):
        """Test successful content generation"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock()]
                mock_response.choices[0].message = Mock()
                mock_response.choices[0].message.content = "Generated content"
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai.return_value = mock_client

                provider = OpenAIProvider()
                result = provider.generate("Test prompt")

                assert result == "Generated content"
                mock_client.chat.completions.create.assert_called_once()

    def test_generate_error(self):
        """Test error handling during generation"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI") as mock_openai:
                mock_client = Mock()
                mock_client.chat.completions.create.side_effect = Exception("API Error")
                mock_openai.return_value = mock_client

                provider = OpenAIProvider()
                with pytest.raises(RuntimeError, match="OpenAI API error"):
                    provider.generate("Test prompt")

    def test_init_import_error(self):
        """Test initialization failure when openai package is not installed"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'openai'")):
                with pytest.raises(ImportError, match="openai package is required"):
                    OpenAIProvider()


class TestClaudeProvider:
    """Test cases for ClaudeProvider"""

    def test_init_success(self):
        """Test successful initialization with API key"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_anthropic.Anthropic.return_value = mock_client
                provider = ClaudeProvider()
                assert provider.api_key == "test_key"
                assert provider._model_name == "claude-sonnet-4-20250514"
                mock_anthropic.Anthropic.assert_called_with(api_key="test_key")

    def test_init_failure_no_key(self):
        """Test initialization failure when API key is missing"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY is not set"):
                ClaudeProvider()

    def test_init_with_custom_model(self):
        """Test initialization with custom model"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic"):
                provider = ClaudeProvider(model="claude-3-opus-20240229")
                assert provider._model_name == "claude-3-opus-20240229"

    def test_name_property(self):
        """Test name property returns correct format"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic"):
                provider = ClaudeProvider()
                assert provider.name == "Claude (claude-sonnet-4-20250514)"

    def test_generate_success(self):
        """Test successful content generation"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.content = [Mock()]
                mock_response.content[0].text = "Generated content"
                mock_client.messages.create.return_value = mock_response
                mock_anthropic.Anthropic.return_value = mock_client

                provider = ClaudeProvider()
                result = provider.generate("Test prompt")

                assert result == "Generated content"
                mock_client.messages.create.assert_called_once()

    def test_generate_error(self):
        """Test error handling during generation"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic") as mock_anthropic:
                mock_client = Mock()
                mock_client.messages.create.side_effect = Exception("API Error")
                mock_anthropic.Anthropic.return_value = mock_client

                provider = ClaudeProvider()
                with pytest.raises(RuntimeError, match="Claude API error"):
                    provider.generate("Test prompt")

    def test_init_import_error(self):
        """Test initialization failure when anthropic package is not installed"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("builtins.__import__", side_effect=ImportError("No module named 'anthropic'")):
                with pytest.raises(ImportError, match="anthropic package is required"):
                    ClaudeProvider()


class TestGeminiProviderName:
    """Test cases for GeminiProvider.name property"""

    def test_name_property_default(self):
        """Test name property with default model"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    provider = GeminiProvider()
                    assert provider.name == "Gemini (gemini-1.5-pro)"

    def test_name_property_custom_model(self):
        """Test name property with custom model"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    provider = GeminiProvider(model="gemini-pro")
                    assert provider.name == "Gemini (gemini-pro)"


class TestLLMGatewayProperties:
    """Test cases for LLMGateway properties"""

    def test_provider_name_property(self):
        """Test provider_name property"""
        mock_provider = Mock()
        mock_provider.name = "Test Provider"

        gateway = LLMGateway(mock_provider)
        assert gateway.provider_name == "Test Provider"


class TestCreateAllProviders:
    """Test cases for create_all_providers() function"""

    def test_create_all_providers_all_available(self):
        """Test creating all providers when all API keys are available"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "gemini_key",
                "OPENAI_API_KEY": "openai_key",
                "ANTHROPIC_API_KEY": "anthropic_key",
            },
        ):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    with patch("alphaloop.core.llm.OpenAI"):
                        with patch("alphaloop.core.llm.anthropic"):
                            providers = create_all_providers()
                            assert len(providers) == 3
                            assert any(p.name.startswith("Gemini") for p in providers)
                            assert any(p.name.startswith("OpenAI") for p in providers)
                            assert any(p.name.startswith("Claude") for p in providers)

    def test_create_all_providers_partial_available(self):
        """Test creating providers when only some API keys are available"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "gemini_key",
                "OPENAI_API_KEY": "openai_key",
            },
        ):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    with patch("alphaloop.core.llm.OpenAI"):
                        providers = create_all_providers()
                        assert len(providers) == 2
                        assert any(p.name.startswith("Gemini") for p in providers)
                        assert any(p.name.startswith("OpenAI") for p in providers)

    def test_create_all_providers_none_available(self):
        """Test creating providers when no API keys are available"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="No LLM providers available"):
                create_all_providers()

    def test_create_all_providers_handles_import_errors(self):
        """Test that import errors are handled gracefully"""
        with patch.dict(
            "os.environ",
            {
                "GEMINI_API_KEY": "gemini_key",
                "OPENAI_API_KEY": "openai_key",
            },
        ):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    # Simulate OpenAI import error
                    with patch("alphaloop.core.llm.OpenAI", side_effect=ImportError):
                        providers = create_all_providers()
                        # Should still get Gemini
                        assert len(providers) >= 1
                        assert any(p.name.startswith("Gemini") for p in providers)


class TestCreateProvider:
    """Test cases for create_provider() function"""

    def test_create_provider_gemini(self):
        """Test creating Gemini provider"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    provider = create_provider("gemini")
                    assert isinstance(provider, GeminiProvider)

    def test_create_provider_openai(self):
        """Test creating OpenAI provider"""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.OpenAI"):
                provider = create_provider("openai")
                assert isinstance(provider, OpenAIProvider)

    def test_create_provider_claude(self):
        """Test creating Claude provider"""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test_key"}):
            with patch("alphaloop.core.llm.anthropic"):
                provider = create_provider("claude")
                assert isinstance(provider, ClaudeProvider)

    def test_create_provider_case_insensitive(self):
        """Test that provider name is case insensitive"""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test_key"}):
            with patch("google.generativeai.configure"):
                with patch("google.generativeai.GenerativeModel"):
                    provider1 = create_provider("GEMINI")
                    provider2 = create_provider("gemini")
                    assert isinstance(provider1, GeminiProvider)
                    assert isinstance(provider2, GeminiProvider)

    def test_create_provider_unknown(self):
        """Test creating unknown provider raises ValueError"""
        with pytest.raises(ValueError, match="Unknown provider"):
            create_provider("unknown_provider")

    def test_create_provider_missing_api_key(self):
        """Test creating provider without API key raises ValueError"""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError):
                create_provider("gemini")

