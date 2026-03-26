###
# openAI向けのクライアント

from src.shared.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    def generate(self, *, user_message: str, system_prompt: str | None = None) -> str:
        """OpenAI 向けの応答生成を行う簡易実装。"""
        prompt = user_message if system_prompt is None else f'{system_prompt}\n\nUser: {user_message}'
        return f"[OpenAI] {prompt}"
