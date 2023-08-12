from .ft2font import KERNING_DEFAULT as KERNING_DEFAULT, LOAD_NO_HINTING as LOAD_NO_HINTING
from _typeshed import Incomplete
from collections.abc import Generator

LayoutItem: Incomplete

def warn_on_missing_glyph(codepoint) -> None: ...
def layout(string, font, *, kern_mode=...) -> Generator[Incomplete, None, None]: ...
