###
# LLM向けの差分を吸収するための抽象クラス


from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    @abstractmethod
    def generate(self, *, user_message: str, system_prompt: str | None = None) -> str:
        """入力メッセージから応答テキストを生成する。"""
        raise NotImplementedError