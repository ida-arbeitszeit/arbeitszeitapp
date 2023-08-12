from _typeshed import Incomplete
from enum import Enum

class _AutoStringNameEnum(Enum):
    def __hash__(self): ...

class JoinStyle(str, _AutoStringNameEnum):
    miter: Incomplete
    round: Incomplete
    bevel: Incomplete
    @staticmethod
    def demo() -> None: ...

class CapStyle(str, _AutoStringNameEnum):
    butt: Incomplete
    projecting: Incomplete
    round: Incomplete
    @staticmethod
    def demo() -> None: ...
