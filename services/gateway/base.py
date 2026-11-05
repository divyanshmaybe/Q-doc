"""
Abstract Base Adapters for Q-Doc Model Gateway.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseSTTAdapter(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, language_code: str = "hi-IN") -> Dict[str, Any]:
        pass

class BaseTTSAdapter(ABC):
    @abstractmethod
    def synthesize(self, text: str, language_code: str = "hi-IN") -> Dict[str, Any]:
        pass

class BaseLLMAdapter(ABC):
    @abstractmethod
    def generate_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        pass

