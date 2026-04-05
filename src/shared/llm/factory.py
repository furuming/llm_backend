from src.shared.llm.base import BaseLLMClient
from src.shared.llm.local_client import LocalLLMClient
from src.shared.llm.openai_client import OpenAIClient

OPENAI_MODEL_PREFIXES = (
    'gpt',
    'o1',
    'o3',
    'o4',
)


def get_llm_client(model_family: str) -> BaseLLMClient:
    """モデルファミリー名に応じた LLM クライアント実装を返す。"""
    normalized = model_family.strip().lower()
    if not normalized:
        raise ValueError('Model family is required')

    if normalized == 'openai' or normalized.startswith(OPENAI_MODEL_PREFIXES):
        return OpenAIClient(model_name=model_family)

    return LocalLLMClient(model_name=model_family)
