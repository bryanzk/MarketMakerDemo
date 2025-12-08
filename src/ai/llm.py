"""
LLM Provider Implementations / LLM 提供者实现

支持 Gemini, OpenAI, Claude 三家 LLM

Owner: Agent AI
"""

import os
from abc import ABC, abstractmethod
from typing import List, Optional

try:
    from google import genai as genai_new
    _USE_NEW_SDK = True
except ImportError:
    # Fallback to old SDK if new one is not available
    # 如果新 SDK 不可用，回退到旧 SDK
    genai_new = None
    _USE_NEW_SDK = False

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
            model: Model name. Default: "gemini-3-pro-preview" (latest Gemini 3 model available)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")

        env_preferred = os.getenv("GEMINI_MODEL")
        # Use gemini-3-pro-preview as default (latest Gemini 3 model available)
        # 使用 gemini-3-pro-preview 作为默认值（可用的最新 Gemini 3 模型）
        self._model_name = model or env_preferred or "gemini-3-pro-preview"

        # Use new SDK if available, otherwise fallback to old SDK
        # 如果新 SDK 可用则使用，否则回退到旧 SDK
        if _USE_NEW_SDK:
            try:
                # New SDK: genai.Client() with api_key parameter
                # 新 SDK：使用 genai.Client() 并传入 api_key 参数
                self.client = genai_new.Client(api_key=self.api_key)
                self.model = None  # Model is specified per request in new SDK
                logger.info(f"Using new Google GenAI SDK for model '{self._model_name}'")
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini client: {e}")
        else:
            # Fallback to old SDK
            # 回退到旧 SDK
            try:
                import google.generativeai as genai_old
                genai_old.configure(api_key=self.api_key)
                self.client = None
                try:
                    self.model = genai_old.GenerativeModel(self._model_name)
                    logger.info(f"Using old Google GenerativeAI SDK for model '{self._model_name}'")
                except Exception as e:
                    self._init_error = e
                    self.model = None
                    logger.warning(f"Failed to initialize Gemini model '{self._model_name}': {e}")
            except ImportError:
                raise ImportError(
                    "Neither 'google-genai' nor 'google-generativeai' package is installed. "
                    "Install with: pip install google-genai"
                )

    @property
    def name(self) -> str:
        return f"Gemini ({self._model_name})"

    def generate(self, prompt: str) -> str:
        """
        Generate response from Gemini model

        Uses new SDK (genai.Client) if available, otherwise falls back to old SDK
        如果可用则使用新 SDK (genai.Client)，否则回退到旧 SDK
        """
        if _USE_NEW_SDK:
            # New SDK: client.models.generate_content()
            # 新 SDK：使用 client.models.generate_content()
            try:
                response = self.client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                )
                # Handle response.text which might be None
                # 处理可能为 None 的 response.text
                if response.text is None:
                    # Try to get text from candidates if available
                    # 如果可用，尝试从 candidates 获取文本
                    if response.candidates and len(response.candidates) > 0:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'content') and candidate.content:
                            # Extract text from content parts
                            # 从 content parts 提取文本
                            text_parts = []
                            for part in candidate.content:
                                if hasattr(part, 'text') and part.text:
                                    text_parts.append(part.text)
                            if text_parts:
                                return "\n".join(text_parts)
                    raise RuntimeError(
                        f"Gemini API returned empty response for model '{self._model_name}'. "
                        f"Please check the API response. / "
                        f"Gemini API 为模型 '{self._model_name}' 返回了空响应。"
                        f"请检查 API 响应。"
                    )
                return response.text
            except Exception as e:
                # Directly raise error from API provider without fallback
                # 直接抛出 API 提供方的错误，不使用回退
                error_msg = str(e)
                raise RuntimeError(
                    f"Gemini API error ({self._model_name}): {error_msg}. / "
                    f"Gemini API 错误 ({self._model_name}): {error_msg}。"
                )
        else:
            # Old SDK: model.generate_content()
            # 旧 SDK：使用 model.generate_content()
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
                    import google.generativeai as genai_old
                    self.model = genai_old.GenerativeModel(self._model_name)
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
                # Directly raise error from API provider without fallback
                # 直接抛出 API 提供方的错误，不使用回退
                error_msg = str(e)
                raise RuntimeError(
                    f"Gemini API error ({self._model_name}): {error_msg}. / "
                    f"Gemini API 错误 ({self._model_name}): {error_msg}。"
                )


class OpenAIProvider(LLMProvider):
    """OpenAI GPT implementation of LLMProvider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
    ):
        """
        Initialize OpenAI Provider

        Args:
            api_key: OpenAI API key (optional, will use OPENAI_API_KEY env var if not provided)
            model: Model name. Default: "gpt-5.1" (or OPENAI_MODEL env var)
            base_url: Base URL for API requests (optional, for custom endpoints)
            timeout: Request timeout in seconds (optional)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set")

        # Support OPENAI_MODEL environment variable
        # 支持 OPENAI_MODEL 环境变量
        env_model = os.getenv("OPENAI_MODEL")
        self._model_name = model or env_model or "gpt-5.1"

        try:
            from openai import OpenAI

            # Initialize client with optional parameters
            # 使用可选参数初始化客户端
            client_kwargs = {"api_key": self.api_key}
            if base_url:
                client_kwargs["base_url"] = base_url
            if timeout:
                client_kwargs["timeout"] = timeout

            self.client = OpenAI(**client_kwargs)
        except ImportError:
            raise ImportError(
                "openai package is required. Install with: pip install openai"
            )

    @property
    def name(self) -> str:
        return f"OpenAI ({self._model_name})"

    def generate(self, prompt: str) -> str:
        """
        Generate response from OpenAI model

        Args:
            prompt: User prompt

        Returns:
            Generated text response

        Raises:
            RuntimeError: If API call fails
        """
        messages = [
            {
                "role": "system",
                "content": "You are an expert quantitative trading analyst.",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self._model_name,
                messages=messages,
                temperature=0.7,
            )
            if not response.choices or not response.choices[0].message.content:
                raise RuntimeError("OpenAI API returned empty response")
            return response.choices[0].message.content
        except Exception as e:
            # Directly raise error from API provider without fallback
            # 直接抛出 API 提供方的错误，不使用回退
            error_msg = str(e)
            raise RuntimeError(
                f"OpenAI API error ({self._model_name}): {error_msg}. / "
                f"OpenAI API 错误 ({self._model_name}): {error_msg}。"
            )


class ClaudeProvider(LLMProvider):
    """Anthropic Claude implementation of LLMProvider"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize Claude Provider

        Args:
            api_key: Anthropic API key (optional, will use ANTHROPIC_API_KEY env var if not provided)
            model: Model name. Default: "claude-sonnet-4-5" (or ANTHROPIC_MODEL env var)
            max_tokens: Maximum tokens for response. Default: 1024
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")

        # Support ANTHROPIC_MODEL environment variable
        # 支持 ANTHROPIC_MODEL 环境变量
        env_model = os.getenv("ANTHROPIC_MODEL")
        # Use claude-sonnet-4-5 as default (latest Claude model available)
        # 使用 claude-sonnet-4-5 作为默认值（可用的最新 Claude 模型）
        self._model_name = model or env_model or "claude-sonnet-4-5"
        self.max_tokens = max_tokens or 1024

        try:
            import anthropic

            # Initialize client with API key
            # 使用 API key 初始化客户端
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError(
                "anthropic package is required. Install with: pip install anthropic"
            )

    @property
    def name(self) -> str:
        return f"Claude ({self._model_name})"

    def generate(self, prompt: str) -> str:
        """
        Generate response from Claude model

        Args:
            prompt: User prompt

        Returns:
            Generated text response

        Raises:
            RuntimeError: If API call fails
        """
        try:
            message = self.client.messages.create(
                model=self._model_name,
                max_tokens=self.max_tokens,
                messages=[{"role": "user", "content": prompt}],
                system="You are an expert quantitative trading analyst.",
            )
            if not message.content or not message.content[0].text:
                raise RuntimeError("Claude API returned empty response")
            return message.content[0].text
        except Exception as e:
            # Directly raise error from API provider without fallback
            # 直接抛出 API 提供方的错误，不使用回退
            error_msg = str(e)
            raise RuntimeError(
                f"Claude API error ({self._model_name}): {error_msg}. / "
                f"Claude API 错误 ({self._model_name}): {error_msg}。"
            )


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


def get_provider_availability() -> dict:
    """
    Check availability of all LLM providers and return detailed status.
    Returns a dict with available and unavailable providers with reasons.
    
    检查所有 LLM 提供商的可用性并返回详细状态。
    返回包含可用和不可用提供商及其原因的字典。
    
    Returns:
        {
            "available": [
                {"name": "Gemini", "provider": GeminiProvider instance}
            ],
            "unavailable": [
                {"name": "OpenAI", "reason": "OPENAI_API_KEY is not set", "api_key_name": "OPENAI_API_KEY"}
            ]
        }
    """
    result = {
        "available": [],
        "unavailable": []
    }
    
    # Check Gemini
    try:
        provider = GeminiProvider()
        result["available"].append({
            "name": "Gemini",
            "provider": provider
        })
    except (ValueError, ImportError) as e:
        error_msg = str(e)
        api_key_name = "GEMINI_API_KEY"
        if "API_KEY" in error_msg or "not set" in error_msg.lower():
            reason = f"{api_key_name} is not set / {api_key_name} 未设置"
        else:
            reason = error_msg
        result["unavailable"].append({
            "name": "Gemini",
            "reason": reason,
            "api_key_name": api_key_name
        })
    
    # Check OpenAI
    try:
        provider = OpenAIProvider()
        result["available"].append({
            "name": "OpenAI",
            "provider": provider
        })
    except (ValueError, ImportError) as e:
        error_msg = str(e)
        api_key_name = "OPENAI_API_KEY"
        if "API_KEY" in error_msg or "not set" in error_msg.lower():
            reason = f"{api_key_name} is not set / {api_key_name} 未设置"
        else:
            reason = error_msg
        result["unavailable"].append({
            "name": "OpenAI",
            "reason": reason,
            "api_key_name": api_key_name
        })
    
    # Check Claude
    try:
        provider = ClaudeProvider()
        result["available"].append({
            "name": "Claude",
            "provider": provider
        })
    except (ValueError, ImportError) as e:
        error_msg = str(e)
        api_key_name = "ANTHROPIC_API_KEY"
        if "API_KEY" in error_msg or "not set" in error_msg.lower():
            reason = f"{api_key_name} is not set / {api_key_name} 未设置"
        else:
            reason = error_msg
        result["unavailable"].append({
            "name": "Claude",
            "reason": reason,
            "api_key_name": api_key_name
        })
    
    return result


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
