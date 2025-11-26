"""
LLM Provider implementations
支持 Gemini, OpenAI, Claude 三家 LLM
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional

import google.generativeai as genai


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

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self._model_name = model

    @property
    def name(self) -> str:
        return f"Gemini ({self._model_name})"

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")


class OpenAIProvider(LLMProvider):
    """OpenAI GPT implementation of LLMProvider"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self._model_name = model
        # Lazy import to avoid dependency issues
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
            raise RuntimeError(f"OpenAI API error: {e}")


class ClaudeProvider(LLMProvider):
    """Anthropic Claude implementation of LLMProvider"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"
    ):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        self._model_name = model
        # Lazy import to avoid dependency issues
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

    Usage:
        providers = create_all_providers()
        for provider in providers:
            print(f"Available: {provider.name}")
    """
    providers = []
    errors = []

    # Try Gemini
    try:
        providers.append(GeminiProvider())
    except (ValueError, ImportError) as e:
        errors.append(f"Gemini: {e}")

    # Try OpenAI
    try:
        providers.append(OpenAIProvider())
    except (ValueError, ImportError) as e:
        errors.append(f"OpenAI: {e}")

    # Try Claude
    try:
        providers.append(ClaudeProvider())
    except (ValueError, ImportError) as e:
        errors.append(f"Claude: {e}")

    if not providers:
        raise ValueError(f"No LLM providers available. Errors: {'; '.join(errors)}")

    return providers


def create_provider(provider_name: str) -> LLMProvider:
    """
    Create a specific LLM provider by name.

    Args:
        provider_name: "gemini", "openai", or "claude"

    Returns:
        LLMProvider instance

    Raises:
        ValueError: If provider name is unknown or API key is not set
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
