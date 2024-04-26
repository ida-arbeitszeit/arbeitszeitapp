from collections.abc import Generator

from _typeshed import Incomplete

from .ft2font import KERNING_DEFAULT as KERNING_DEFAULT
from .ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING

LayoutItem: Incomplete

def warn_on_missing_glyph(codepoint) -> None: ...
def layout(string, font, *, kern_mode=...) -> Generator[Incomplete, None, None]: ...
