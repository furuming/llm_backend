import httpx

from src.core.config import get_settings
from src.shared.llm.base import BaseLLMClient


class LocalLLMClient(BaseLLMClient):
    def __init__(
        self,
        base_url: str | None = None,
        timeout_sec: float | None = None,
        model_name: str | None = None,
    ) -> None:
        """ローカル LLM 接続に必要な設定値を初期化する。"""
        settings = get_settings()
        self.base_url = (base_url or settings.local_llm_base_url).rstrip("/")
        self.timeout_sec = timeout_sec or settings.local_llm_timeout_sec
        self.model_name = model_name or settings.local_llm_model_name

    def generate(self, *, user_message: str, system_prompt: str | None = None) -> str:
        """ローカル LLM にプロンプトを送信し、生成テキストを返す。"""
        messages: list[dict[str, str]] = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_message})

        payload = {
            # "model": self.model_name,
            # "messages": messages,
            # "generation_config": {
            #     # Gemma系で無難な初期値
            #     "max_new_tokens": 2048,
            #     "temperature": 0.7,
            #     "top_p": 0.95,
            #     "do_sample": True,
            #     "repetition_penalty": 1.05,
            # },
            "prompt": user_message,
            "max_new_tokens": 2048,
            "temperature": 0.7
        }

        with httpx.Client(timeout=self.timeout_sec) as client:
            response = client.post(f"{self.base_url}/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        # 返却形式はサーバ側に合わせて調整
        # 例: {"text": "..."} を想定
        text = data.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Invalid local LLM response: {data}")

        return text
