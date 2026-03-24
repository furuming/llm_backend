from src.modules.rag.services.embedder import Embedder


class EmbeddingGateway(Embedder):
    """外部依存なしで埋め込みを生成する簡易実装。"""

    def __init__(self, dimensions: int = 32) -> None:
        """ベクトル次元数を受け取って初期化する。"""
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        """文字単位のハッシュで決定的な埋め込みベクトルを生成する。"""
        vectors: list[list[float]] = []
        for text in texts:
            vector = [0.0] * self.dimensions
            normalized = text.strip().lower()
            if not normalized:
                vectors.append(vector)
                continue

            for index, char in enumerate(normalized):
                bucket = (ord(char) + index) % self.dimensions
                vector[bucket] += 1.0

            length = sum(value * value for value in vector) ** 0.5
            if length > 0:
                vector = [value / length for value in vector]
            vectors.append(vector)
        return vectors
