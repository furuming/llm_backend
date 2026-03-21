from src.shared.llm.base import BaseLLMClient
from src.shared.llm.local_client import LocalLLMClient
from src.shared.llm.openai_client import OpenAIClient


def get_llm_client(model: str) -> BaseLLMClient:
    if model == "openai":
        return OpenAIClient()
    if model == "local":
        return LocalLLMClient()
    raise ValueError(f"Unsupported model: {model}")
