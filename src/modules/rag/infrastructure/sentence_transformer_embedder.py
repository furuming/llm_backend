from sentence_transformers import SentenceTransformer

from src.modules.rag.services.embedder import Embedder


class SentenceTransformerEmbedder(Embedder):
    """Sentence Transformers を使った埋め込み実装。"""

    def __init__(
        self,
        model_name: str,
        *,
        device: str | None = None,
        normalize_embeddings: bool = True,
        query_instruction: str | None = None,
        document_instruction: str | None = None,
    ) -> None:
        """利用するモデルとエンコード設定を保持する。"""
        model_kwargs: dict[str, str] = {}
        if device:
            model_kwargs['device'] = device

        self._model = SentenceTransformer(model_name, **model_kwargs)
        self._normalize_embeddings = normalize_embeddings
        self._query_instruction = query_instruction or ''
        self._document_instruction = document_instruction or ''

    @property
    def dimensions(self) -> int:
        """埋め込みベクトルの次元数を返す。"""
        dimensions = self._model.get_sentence_embedding_dimension()
        if dimensions is None:
            raise ValueError('Embedding dimension could not be resolved from the model.')
        return dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """文書群を埋め込みベクトルへ変換する。"""
        prepared = [self._apply_instruction(text, self._document_instruction) for text in texts]
        vectors = self._model.encode(
            prepared,
            normalize_embeddings=self._normalize_embeddings,
        )
        return [vector.tolist() for vector in vectors]

    def embed_query(self, text: str) -> list[float]:
        """検索クエリを埋め込みベクトルへ変換する。"""
        vector = self._model.encode(
            self._apply_instruction(text, self._query_instruction),
            normalize_embeddings=self._normalize_embeddings,
        )
        return vector.tolist()

    @staticmethod
    def _apply_instruction(text: str, instruction: str) -> str:
        normalized = text.strip()
        if not instruction:
            return normalized
        return f'{instruction}{normalized}'
