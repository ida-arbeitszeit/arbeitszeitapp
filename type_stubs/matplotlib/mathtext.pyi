from ._mathtext import RasterParse as RasterParse, VectorParse as VectorParse, get_unicode_index as get_unicode_index
from _typeshed import Incomplete
from matplotlib.font_manager import FontProperties as FontProperties
from matplotlib.ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING

class MathTextParser:
    def __init__(self, output) -> None: ...
    def parse(self, s, dpi: int = ..., prop: Incomplete | None = ..., *, antialiased: Incomplete | None = ...): ...

def math_to_image(s, filename_or_obj, prop: Incomplete | None = ..., dpi: Incomplete | None = ..., format: Incomplete | None = ..., *, color: Incomplete | None = ...): ...
