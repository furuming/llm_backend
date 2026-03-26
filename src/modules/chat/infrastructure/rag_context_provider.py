from sqlalchemy.orm import Session

from src.modules.chat.services.context_provider import ContextProvider, RetrievedContext
from src.modules.rag.infrastructure.rag_query_service import build_rag_usecases


class RagContextProvider(ContextProvider):
    """RAG モジュールを使ってチャット向け文脈を取得する。"""

    def __init__(self, session: Session) -> None:
        """RAG ユースケース構築に使う DB セッションを保持する。"""
        self._session = session

    def get_context(self, query: str, top_k: int) -> RetrievedContext:
        """関連チャンクを検索し、チャット用文脈へ変換して返す。"""
        result = build_rag_usecases(self._session).retrieve_chunks.execute(query=query, top_k=top_k)
        return RetrievedContext(context=result.context, chunk_count=len(result.chunks))
