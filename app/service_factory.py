from enum import Enum
from typing import Union
from app.openai_service import OpenAIService
from app.grok_service import GrokService
from app.schemas import AIProvider

class ServiceFactory:
    @staticmethod
    def get_service(provider: AIProvider) -> Union[OpenAIService, GrokService]:
        if provider == AIProvider.OPENAI:
            return OpenAIService()
        elif provider == AIProvider.GROK:
            return GrokService()
        else:
            raise ValueError(f"Unknown AI provider: {provider}")
