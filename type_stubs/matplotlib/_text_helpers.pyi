import dataclasses
from collections.abc import Generator

from _typeshed import Incomplete

from .ft2font import KERNING_DEFAULT as KERNING_DEFAULT
from .ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING
from .ft2font import FT2Font as FT2Font

@dataclasses.dataclass(frozen=True)
class LayoutItem:
    ft_object: FT2Font
    char: str
    glyph_idx: int
    x: float
    prev_kern: float
    def __init__(self, ft_object, char, glyph_idx, x, prev_kern) -> None: ...

def warn_on_missing_glyph(codepoint, fontnames) -> None: ...
def layout(string, font, *, kern_mode=...) -> Generator[Incomplete, None, None]: ...
