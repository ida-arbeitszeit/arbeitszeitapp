import json
from typing import NamedTuple

from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import ft2font as ft2font
from matplotlib._fontconfig_pattern import (
    generate_fontconfig_pattern as generate_fontconfig_pattern,
)
from matplotlib._fontconfig_pattern import (
    parse_fontconfig_pattern as parse_fontconfig_pattern,
)

font_scalings: Incomplete
stretch_dict: Incomplete
weight_dict: Incomplete
font_family_aliases: Incomplete

class _ExceptionProxy(NamedTuple):
    klass: Incomplete
    message: Incomplete

MSFolders: str
MSFontDirectories: Incomplete
MSUserFontDirectories: Incomplete
X11FontDirectories: Incomplete
OSXFontDirectories: Incomplete

def get_fontext_synonyms(fontext): ...
def list_fonts(directory, extensions): ...
def win32FontDirectory(): ...
def findSystemFonts(fontpaths: Incomplete | None = None, fontext: str = "ttf"): ...

FontEntry: Incomplete

def ttfFontProperty(font): ...
def afmFontProperty(fontpath, font): ...

class FontProperties:
    def __init__(
        self,
        family: Incomplete | None = None,
        style: Incomplete | None = None,
        variant: Incomplete | None = None,
        weight: Incomplete | None = None,
        stretch: Incomplete | None = None,
        size: Incomplete | None = None,
        fname: Incomplete | None = None,
        math_fontfamily: Incomplete | None = None,
    ) -> None: ...
    def __hash__(self): ...
    def __eq__(self, other): ...
    def get_family(self): ...
    def get_name(self): ...
    def get_style(self): ...
    def get_variant(self): ...
    def get_weight(self): ...
    def get_stretch(self): ...
    def get_size(self): ...
    def get_file(self): ...
    def get_fontconfig_pattern(self): ...
    def set_family(self, family) -> None: ...
    def set_style(self, style) -> None: ...
    def set_variant(self, variant) -> None: ...
    def set_weight(self, weight) -> None: ...
    def set_stretch(self, stretch) -> None: ...
    def set_size(self, size) -> None: ...
    def set_file(self, file) -> None: ...
    def set_fontconfig_pattern(self, pattern) -> None: ...
    def get_math_fontfamily(self): ...
    def set_math_fontfamily(self, fontfamily) -> None: ...
    def copy(self): ...
    set_name = set_family
    get_slant = get_style
    set_slant = set_style
    get_size_in_points = get_size

class _JSONEncoder(json.JSONEncoder):
    def default(self, o): ...

def json_dump(data, filename) -> None: ...
def json_load(filename): ...

class FontManager:
    __version__: int
    default_size: Incomplete
    defaultFamily: Incomplete
    afmlist: Incomplete
    ttflist: Incomplete
    def __init__(
        self, size: Incomplete | None = None, weight: str = "normal"
    ) -> None: ...
    def addfont(self, path) -> None: ...
    @property
    def defaultFont(self): ...
    def get_default_weight(self): ...
    @staticmethod
    def get_default_size(): ...
    def set_default_weight(self, weight) -> None: ...
    def score_family(self, families, family2): ...
    def score_style(self, style1, style2): ...
    def score_variant(self, variant1, variant2): ...
    def score_stretch(self, stretch1, stretch2): ...
    def score_weight(self, weight1, weight2): ...
    def score_size(self, size1, size2): ...
    def findfont(
        self,
        prop,
        fontext: str = "ttf",
        directory: Incomplete | None = None,
        fallback_to_default: bool = True,
        rebuild_if_missing: bool = True,
    ): ...
    def get_font_names(self): ...

def is_opentype_cff_font(filename): ...
def get_font(font_filepaths, hinting_factor: Incomplete | None = None): ...

fontManager: Incomplete
findfont: Incomplete
get_font_names: Incomplete
