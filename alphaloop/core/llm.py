import os
from abc import ABC, abstractmethod
from typing import Optional
import google.generativeai as genai

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class GeminiProvider(LLMProvider):
    """Google Gemini implementation of LLMProvider"""
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)

    def generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

class LLMGateway:
    """Gateway service for interacting with LLMs"""
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        """Generate content using the configured provider"""
        return self.provider.generate(prompt)
