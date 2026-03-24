###
# openAI向けのクライアント


from src.shared.llm.base import BaseLLMClient

class OpenAIClient(BaseLLMClient):

    def generate(self, prompt: str) -> str:
        """OpenAI 向けの応答生成を行う簡易実装。"""
        # 仮
        return f"[OpenAI] {prompt}"
