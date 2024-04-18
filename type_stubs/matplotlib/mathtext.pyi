from _typeshed import Incomplete
from matplotlib.font_manager import FontProperties as FontProperties
from matplotlib.ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING

from ._mathtext import RasterParse as RasterParse
from ._mathtext import VectorParse as VectorParse
from ._mathtext import get_unicode_index as get_unicode_index

class MathTextParser:
    def __init__(self, output) -> None: ...
    def parse(
        self,
        s,
        dpi: int = 72,
        prop: Incomplete | None = None,
        *,
        antialiased: Incomplete | None = None,
    ): ...

def math_to_image(
    s,
    filename_or_obj,
    prop: Incomplete | None = None,
    dpi: Incomplete | None = None,
    format: Incomplete | None = None,
    *,
    color: Incomplete | None = None,
): ...
