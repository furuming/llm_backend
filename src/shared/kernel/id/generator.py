from abc import ABC, abstractmethod


class IDGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        pass
