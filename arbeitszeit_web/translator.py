from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Union

Number = Union[int, float, Decimal]


class Translator(ABC):
    @abstractmethod
    def gettext(self, text: str) -> str: ...

    @abstractmethod
    def pgettext(self, context: str, text: str) -> str: ...

    @abstractmethod
    def ngettext(self, singular: str, plural: str, n: Number) -> str:
        """Implementations have to supply the ``n`` argument as ``num`` for
        formatting the ``singular`` and ``plural`` argument.

        Example:
        translator.ngettext("%(num)d beer", "%(num)d beers", 1)
        should yield "1 beer" if 'translated' to english.
        """
        ...
