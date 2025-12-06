"""
LLM Provider Implementations / LLM 提供者实现

支持 Gemini, OpenAI, Claude 三家 LLM

Owner: Agent AI
"""

import os
from abc import ABC, abstractmethod
from collections import deque
from typing import Deque, List, Optional

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

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        """
        Initialize Gemini Provider

        Args:
            api_key: Gemini API key (optional, will use GEMINI_API_KEY env var if not provided)
            model: Model name. Default: "gemini-3-pro" (latest)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=self.api_key)

        preferred = model or "gemini-1.5-flash"
        default_candidates = [
            preferred,
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.0-pro",
        ]
        deduped = []
        for candidate in default_candidates:
            if candidate and candidate not in deduped:
                deduped.append(candidate)
        self._model_candidates: Deque[str] = deque(deduped)
        self._initialize_model()

    @property
    def name(self) -> str:
        return f"Gemini ({self._model_name})"

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            if self._should_try_fallback(e) and self._switch_to_next_model():
                logger.warning(
                    f"Gemini model {self.name} failed, attempting fallback: {e}"
                )
                return self.generate(prompt)
            raise RuntimeError(f"Gemini API error: {e}")

    def _initialize_model(self) -> None:
        if not self._model_candidates:
            raise ValueError("No Gemini models available to initialize")
        self._model_name = self._model_candidates[0]
        self.model = genai.GenerativeModel(self._model_name)

    def _switch_to_next_model(self) -> bool:
        if len(self._model_candidates) <= 1:
            return False
        self._model_candidates.popleft()
        self._initialize_model()
        return True

    @staticmethod
    def _should_try_fallback(error: Exception) -> bool:
        message = str(error).lower()
        fallback_keywords = [
            "not found",
            "unsupported",
            "does not exist",
            "unavailable",
        ]
        return any(keyword in message for keyword in fallback_keywords)


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
