from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import dviread as dviread

class TexManager:
    texcache: Incomplete
    def __new__(cls): ...
    @classmethod
    def get_basefile(cls, tex, fontsize, dpi: Incomplete | None = None): ...
    @classmethod
    def get_font_preamble(cls): ...
    @classmethod
    def get_custom_preamble(cls): ...
    @classmethod
    def make_tex(cls, tex, fontsize): ...
    @classmethod
    def make_dvi(cls, tex, fontsize): ...
    @classmethod
    def make_png(cls, tex, fontsize, dpi): ...
    @classmethod
    def get_grey(
        cls, tex, fontsize: Incomplete | None = None, dpi: Incomplete | None = None
    ): ...
    @classmethod
    def get_rgba(
        cls,
        tex,
        fontsize: Incomplete | None = None,
        dpi: Incomplete | None = None,
        rgb=(0, 0, 0),
    ): ...
    @classmethod
    def get_text_width_height_descent(
        cls, tex, fontsize, renderer: Incomplete | None = None
    ): ...
