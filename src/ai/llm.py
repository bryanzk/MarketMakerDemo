"""
LLM Provider Implementations / LLM 提供者实现

支持 Gemini, OpenAI, Claude 三家 LLM

Owner: Agent AI
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional

import google.generativeai as genai

from src.shared.logger import setup_logger

logger = setup_logger("LLMProvider")


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name for identification"""
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from the LLM"""
        pass


class GeminiProvider(LLMProvider):
    """Google Gemini implementation of LLMProvider"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Gemini Provider

        Args:
            api_key: Gemini API key (optional, will use GEMINI_API_KEY env var if not provided)
            model: Model name. Default: "gemini-3-pro"
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=self.api_key)

        env_preferred = os.getenv("GEMINI_MODEL")
        self._model_name = model or env_preferred or "gemini-3-pro"
        self.model = genai.GenerativeModel(self._model_name)

    @property
    def name(self) -> str:
        return f"Gemini ({self._model_name})"

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(
                f"Gemini API error ({self._model_name}): {e}. "
                "Please ensure the requested model is available."
            )


class OpenAIProvider(LLMProvider):
    """OpenAI GPT implementation of LLMProvider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-5"):
        """
        Initialize OpenAI Provider

        Args:
            api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var if not provided)
            model: Model name. Default: "gpt-5" (latest)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._model_name = model
        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    @property
    def name(self) -> str:
        return f"OpenAI ({self._model_name})"

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert quantitative trading analyst.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            if self._model_name == "gpt-5" and (
                "not found" in str(e).lower() or "invalid" in str(e).lower()
            ):
                logger.warning(f"GPT-5 not available, falling back to gpt-4o: {e}")
                self._model_name = "gpt-4o"
                response = self.client.chat.completions.create(
                    model=self._model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert quantitative trading analyst.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.7,
                )
                return response.choices[0].message.content
            raise RuntimeError(f"OpenAI API error: {e}")


class ClaudeProvider(LLMProvider):
    """Anthropic Claude implementation of LLMProvider"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        self._model_name = model
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    @property
    def name(self) -> str:
        return f"Claude ({self._model_name})"

    def generate(self, prompt: str) -> str:
        try:
            message = self.client.messages.create(
                model=self._model_name,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                system="You are an expert quantitative trading analyst.",
            )
            return message.content[0].text
        except Exception as e:
            raise RuntimeError(f"Claude API error: {e}")


class LLMGateway:
    """Gateway service for interacting with LLMs"""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    @property
    def provider_name(self) -> str:
        """Return the name of the current provider"""
        return self.provider.name

    def generate(self, prompt: str) -> str:
        """Generate content using the configured provider"""
        return self.provider.generate(prompt)


def create_all_providers() -> List[LLMProvider]:
    """
    Create all available LLM providers based on configured API keys.
    Returns a list of successfully initialized providers.
    """
    providers = []
    errors = []

    try:
        providers.append(GeminiProvider())
        logger.info("✅ Gemini provider initialized successfully")
    except (ValueError, ImportError) as e:
        error_msg = f"Gemini: {e}"
        errors.append(error_msg)
        logger.warning(f"⚠️ Failed to initialize Gemini provider: {e}")

    try:
        providers.append(OpenAIProvider())
        logger.info("✅ OpenAI provider initialized successfully")
    except (ValueError, ImportError) as e:
        error_msg = f"OpenAI: {e}"
        errors.append(error_msg)
        logger.warning(f"⚠️ Failed to initialize OpenAI provider: {e}")

    try:
        providers.append(ClaudeProvider())
        logger.info("✅ Claude provider initialized successfully")
    except (ValueError, ImportError) as e:
        error_msg = f"Claude: {e}"
        errors.append(error_msg)
        logger.warning(f"⚠️ Failed to initialize Claude provider: {e}")

    if not providers:
        error_summary = '; '.join(errors)
        raise ValueError(f"No LLM providers available. Errors: {error_summary}")
    
    if errors:
        logger.warning(f"⚠️ Some LLM providers failed to initialize: {'; '.join(errors)}")
        logger.info(f"✅ Successfully initialized {len(providers)} provider(s): {[p.name for p in providers]}")

    return providers


def create_provider(provider_name: str) -> LLMProvider:
    """
    Create a specific LLM provider by name.

    Args:
        provider_name: "gemini", "openai", or "claude"

    Returns:
        LLMProvider instance
    """
    provider_name = provider_name.lower()

    if provider_name == "gemini":
        return GeminiProvider()
    elif provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "claude":
        return ClaudeProvider()
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. Use 'gemini', 'openai', or 'claude'"
        )
