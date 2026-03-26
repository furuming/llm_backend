from src.modules.rag.services.embedder import Embedder


class HashEmbedder(Embedder):
    """外部依存なしで埋め込みを生成する簡易実装。"""

    def __init__(self, dimensions: int = 32) -> None:
        """ベクトル次元数を受け取って初期化する。"""
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        """埋め込みベクトルの次元数を返す。"""
        return self._dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """文字単位のハッシュで決定的な埋め込みベクトルを生成する。"""
        return [self._embed_text(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        """検索クエリを埋め込みベクトルへ変換する。"""
        return self._embed_text(text)

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self._dimensions
        normalized = text.strip().lower()
        if not normalized:
            return vector

        for index, char in enumerate(normalized):
            bucket = (ord(char) + index) % self._dimensions
            vector[bucket] += 1.0

        length = sum(value * value for value in vector) ** 0.5
        if length > 0:
            vector = [value / length for value in vector]
        return vector
