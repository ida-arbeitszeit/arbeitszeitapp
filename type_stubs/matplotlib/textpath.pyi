from _typeshed import Incomplete
from matplotlib import dviread as dviread
from matplotlib.font_manager import FontProperties as FontProperties
from matplotlib.font_manager import get_font as get_font
from matplotlib.ft2font import LOAD_NO_HINTING as LOAD_NO_HINTING
from matplotlib.ft2font import LOAD_TARGET_LIGHT as LOAD_TARGET_LIGHT
from matplotlib.mathtext import MathTextParser as MathTextParser
from matplotlib.path import Path as Path
from matplotlib.texmanager import TexManager as TexManager
from matplotlib.transforms import Affine2D as Affine2D

class TextToPath:
    FONT_SCALE: float
    DPI: int
    mathtext_parser: Incomplete
    def __init__(self) -> None: ...
    def get_text_width_height_descent(self, s, prop, ismath): ...
    def get_text_path(self, prop, s, ismath: bool = False): ...
    def get_glyphs_with_font(
        self,
        font,
        s,
        glyph_map: Incomplete | None = None,
        return_new_glyphs_only: bool = False,
    ): ...
    def get_glyphs_mathtext(
        self,
        prop,
        s,
        glyph_map: Incomplete | None = None,
        return_new_glyphs_only: bool = False,
    ): ...
    def get_glyphs_tex(
        self,
        prop,
        s,
        glyph_map: Incomplete | None = None,
        return_new_glyphs_only: bool = False,
    ): ...

text_to_path: Incomplete

class TextPath(Path):
    def __init__(
        self,
        xy,
        s,
        size: Incomplete | None = None,
        prop: Incomplete | None = None,
        _interpolation_steps: int = 1,
        usetex: bool = False,
    ) -> None: ...
    def set_size(self, size) -> None: ...
    def get_size(self): ...
    @property
    def vertices(self): ...
    @property
    def codes(self): ...
