###
# openAI向けのクライアント


from src.shared.llm.base import BaseLLMClient

class OpenAIClient(BaseLLMClient):

    def generate(self, prompt: str) -> str:
        # 仮
        return f"[OpenAI] {prompt}"
