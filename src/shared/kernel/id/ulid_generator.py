from src.shared.kernel.id.generator import IDGenerator
from src.shared.kernel.id.ulid import new_ulid


class ULIDGenerator(IDGenerator):
    def generate(self) -> str:
        """ULID を使って一意な ID を生成する。"""
        return new_ulid()
