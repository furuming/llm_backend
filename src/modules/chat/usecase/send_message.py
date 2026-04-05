from dataclasses import dataclass

from src.modules.chat.domain.entities import ChatMessage
from src.modules.chat.infrastructure.repository import ChatRepository
from src.modules.chat.services.context_provider import ContextProvider, RetrievedContext
from src.shared.kernel.id.generator import IDGenerator
from src.shared.llm.base import BaseLLMClient


@dataclass
class SendMessageResult:
    """チャット応答と利用した補助情報を表す。"""

    reply: str
    used_rag: bool
    retrieved_chunk_count: int
    room_id: str | None


class SendMessageUseCase:
    def __init__(
        self,
        repository: ChatRepository,
        id_generator: IDGenerator,
        llm_client: BaseLLMClient,
        context_provider: ContextProvider | None = None,
    ):
        """必要な依存を受け取って初期化する。"""
        self.repository = repository
        self.id_generator = id_generator
        self.llm_client = llm_client
        self.context_provider = context_provider

    def execute(
        self,
        user_id: str,
        message: str,
        model: str,
        *,
        room_id: str | None = None,
        use_rag: bool = False,
        rag_top_k: int = 5,
    ) -> SendMessageResult:
        """ユーザーメッセージを保存し、必要に応じて RAG を使って応答を生成する。"""
        retrieved_context = self._fetch_context(message, use_rag=use_rag, rag_top_k=rag_top_k)
        used_rag = bool(retrieved_context.context)
        retrieved_chunk_count = retrieved_context.chunk_count

        user_message = ChatMessage(
            id=self.id_generator.generate(),
            user_id=user_id,
            room_id=room_id,
            role="user",
            model=model,
            content=message,
            used_rag=used_rag,
            retrieved_chunk_count=retrieved_chunk_count,
        )
        self.repository.save(user_message)

        system_prompt = self._build_system_prompt(retrieved_context)
        reply = self.llm_client.generate(
            user_message=message,
            system_prompt=system_prompt,
        )

        assistant_message = ChatMessage(
            id=self.id_generator.generate(),
            user_id=user_id,
            room_id=room_id,
            role="assistant",
            model=model,
            content=reply,
            used_rag=used_rag,
            retrieved_chunk_count=retrieved_chunk_count,
        )
        self.repository.save(assistant_message)

        return SendMessageResult(
            reply=reply,
            used_rag=used_rag,
            retrieved_chunk_count=retrieved_chunk_count,
            room_id=room_id,
        )

    def _fetch_context(self, message: str, *, use_rag: bool, rag_top_k: int) -> RetrievedContext:
        if not use_rag or self.context_provider is None:
            return RetrievedContext(context='', chunk_count=0)

        try:
            return self.context_provider.get_context(query=message, top_k=rag_top_k)
        except Exception:
            return RetrievedContext(context='', chunk_count=0)

    @staticmethod
    def _build_system_prompt(retrieved_context: RetrievedContext) -> str:
        base_prompt = 'You are a helpful assistant. Answer in Japanese.'
        if not retrieved_context.context:
            return base_prompt

        return (
            f'{base_prompt}\n\n'
            'Use the following retrieved context if it is relevant to the user question. '
            'If the context is insufficient, say so briefly and answer conservatively.\n\n'
            f'[Retrieved Context]\n{retrieved_context.context}'
        )
