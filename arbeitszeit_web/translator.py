from abc import ABC, abstractmethod


class Translator(ABC):
    @abstractmethod
    def gettext(self, text: str) -> str:
        ...

    @abstractmethod
    def pgettext(self, context: str, text: str) -> str:
        ...
