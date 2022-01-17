from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def trans_(self, text: str) -> str:
        ...
