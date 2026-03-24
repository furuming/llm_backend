from abc import ABC, abstractmethod


class IDGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        """一意な ID を生成して返す。"""
        pass
