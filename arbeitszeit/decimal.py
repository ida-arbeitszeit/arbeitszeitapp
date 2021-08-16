import functools
from decimal import Decimal
from typing import Iterable


def decimal_sum(iterable: Iterable[Decimal]) -> Decimal:
    return functools.reduce(lambda x, y: x + y, iterable, Decimal(0))
