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
        
        try:
            genai.configure(api_key=self.api_key)
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {e}")

        env_preferred = os.getenv("GEMINI_MODEL")
        self._model_name = model or env_preferred or "gemini-3-pro"
        
        # Try to create model - delay actual model creation to first use if needed
        # 尝试创建模型 - 如果需要，延迟实际模型创建到首次使用时
        try:
            self.model = genai.GenerativeModel(self._model_name)
        except Exception as e:
            # Store error for better error message in generate() method
            # 存储错误以便在 generate() 方法中提供更好的错误消息
            self._init_error = e
            self.model = None
            logger.warning(f"Failed to initialize Gemini model '{self._model_name}': {e}")

    @property
    def name(self) -> str:
        return f"Gemini ({self._model_name})"

    def generate(self, prompt: str) -> str:
        # If model initialization failed, try to create it now or provide helpful error
        # 如果模型初始化失败，现在尝试创建它或提供有用的错误
        if self.model is None:
            if hasattr(self, '_init_error'):
                error_msg = str(self._init_error)
                if "v1beta" in error_msg or "not found" in error_msg.lower():
                    raise RuntimeError(
                        f"Gemini model '{self._model_name}' is not available with the current API configuration. "
                        f"Error: {error_msg}. "
                        f"This may be due to API version mismatch. Please check: "
                        f"1. The model name is correct (e.g., 'gemini-3-pro' or 'gemini-1.5-pro'), "
                        f"2. Your API key has access to this model, "
                        f"3. Try setting GEMINI_MODEL environment variable to a different model. / "
                        f"Gemini 模型 '{self._model_name}' 在当前 API 配置下不可用。"
                        f"错误: {error_msg}。"
                        f"这可能是由于 API 版本不匹配。请检查："
                        f"1. 模型名称是否正确（例如 'gemini-3-pro' 或 'gemini-1.5-pro'），"
                        f"2. 您的 API 密钥是否有权访问此模型，"
                        f"3. 尝试将 GEMINI_MODEL 环境变量设置为不同的模型。"
                    )
                raise RuntimeError(
                    f"Failed to initialize Gemini model '{self._model_name}': {error_msg}"
                )
            # Try to create model now
            # 现在尝试创建模型
            try:
                self.model = genai.GenerativeModel(self._model_name)
            except Exception as e:
                raise RuntimeError(
                    f"Gemini model '{self._model_name}' initialization failed: {e}. "
                    f"Please check the model name and API configuration. / "
                    f"Gemini 模型 '{self._model_name}' 初始化失败: {e}。"
                    f"请检查模型名称和 API 配置。"
                )
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            error_msg = str(e)
            # Provide more helpful error messages for common issues
            # 为常见问题提供更有用的错误消息
            if "v1beta" in error_msg or "not found" in error_msg.lower():
                raise RuntimeError(
                    f"Gemini API error ({self._model_name}): {error_msg}. "
                    f"The model may not be available with the current API version. "
                    f"Please check the model name or try a different model. / "
                    f"Gemini API 错误 ({self._model_name}): {error_msg}。"
                    f"该模型可能在当前 API 版本下不可用。"
                    f"请检查模型名称或尝试其他模型。"
                )
            raise RuntimeError(
                f"Gemini API error ({self._model_name}): {error_msg}. "
                "Please ensure the requested model is available and your API key is valid. / "
                "请确保请求的模型可用且您的 API 密钥有效。"
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
        error_summary = "; ".join(errors)
        raise ValueError(f"No LLM providers available. Errors: {error_summary}")

    if errors:
        logger.warning(
            f"⚠️ Some LLM providers failed to initialize: {'; '.join(errors)}"
        )
        logger.info(
            f"✅ Successfully initialized {len(providers)} provider(s): {[p.name for p in providers]}"
        )

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
