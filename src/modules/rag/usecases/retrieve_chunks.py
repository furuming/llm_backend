from dataclasses import dataclass

from src.modules.rag.models.retrieved_chunk import RetrievedChunk
from src.modules.rag.services.prompt_context_builder import PromptContextBuilder
from src.modules.rag.services.retriver import Retriever


@dataclass
class RetrieveChunksResult:
    """検索結果とプロンプト用文脈をまとめて返す。"""

    chunks: list[RetrievedChunk]
    context: str


class RetrieveChunksUseCase:
    """問い合わせに関連するチャンクを取得する。"""

    def __init__(self, retriever: Retriever, prompt_context_builder: PromptContextBuilder) -> None:
        """検索実行に必要な依存を受け取る。"""
        self.retriever = retriever
        self.prompt_context_builder = prompt_context_builder

    def execute(self, query: str, top_k: int = 5) -> RetrieveChunksResult:
        """クエリに関連するチャンク群と文脈を返す。"""
        chunks = self.retriever.retrieve(query, top_k=top_k)
        context = self.prompt_context_builder.build(chunks)
        return RetrieveChunksResult(chunks=chunks, context=context)
