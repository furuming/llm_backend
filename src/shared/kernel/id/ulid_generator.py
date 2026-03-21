from src.shared.kernel.id.generator import IDGenerator
from src.shared.kernel.id.ulid import new_ulid


class ULIDGenerator(IDGenerator):
    def generate(self) -> str:
        return new_ulid()
