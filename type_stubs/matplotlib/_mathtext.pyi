import abc
import enum
import typing as T
from typing import NamedTuple

from _typeshed import Incomplete
from pyparsing import ParserElement, ParseResults

from . import cbook as cbook
from ._mathtext_data import latex_to_bakoma as latex_to_bakoma
from ._mathtext_data import stix_glyph_fixes as stix_glyph_fixes
from ._mathtext_data import stix_virtual_fonts as stix_virtual_fonts
from ._mathtext_data import tex2uni as tex2uni
from .font_manager import FontProperties as FontProperties
from .font_manager import findfont as findfont
from .font_manager import get_font as get_font
from .ft2font import KERNING_DEFAULT as KERNING_DEFAULT
from .ft2font import FT2Font as FT2Font
from .ft2font import FT2Image as FT2Image
from .ft2font import Glyph as Glyph

def get_unicode_index(symbol: str) -> int: ...

class VectorParse(NamedTuple):
    width: float
    height: float
    depth: float
    glyphs: list[tuple[FT2Font, float, int, float, float]]
    rects: list[tuple[float, float, float, float]]

class RasterParse(NamedTuple):
    ox: float
    oy: float
    width: float
    height: float
    depth: float
    image: FT2Image

class Output:
    box: Incomplete
    glyphs: Incomplete
    rects: Incomplete
    def __init__(self, box: Box) -> None: ...
    def to_vector(self) -> VectorParse: ...
    def to_raster(self, *, antialiased: bool) -> RasterParse: ...

class FontMetrics(NamedTuple):
    advance: float
    height: float
    width: float
    xmin: float
    xmax: float
    ymin: float
    ymax: float
    iceberg: float
    slanted: bool

class FontInfo(NamedTuple):
    font: FT2Font
    fontsize: float
    postscript_name: str
    metrics: FontMetrics
    num: int
    glyph: Glyph
    offset: float

class Fonts(abc.ABC):
    default_font_prop: Incomplete
    load_glyph_flags: Incomplete
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...
    def get_kern(
        self,
        font1: str,
        fontclass1: str,
        sym1: str,
        fontsize1: float,
        font2: str,
        fontclass2: str,
        sym2: str,
        fontsize2: float,
        dpi: float,
    ) -> float: ...
    def get_metrics(
        self, font: str, font_class: str, sym: str, fontsize: float, dpi: float
    ) -> FontMetrics: ...
    def render_glyph(
        self,
        output: Output,
        ox: float,
        oy: float,
        font: str,
        font_class: str,
        sym: str,
        fontsize: float,
        dpi: float,
    ) -> None: ...
    def render_rect_filled(
        self, output: Output, x1: float, y1: float, x2: float, y2: float
    ) -> None: ...
    def get_xheight(self, font: str, fontsize: float, dpi: float) -> float: ...
    def get_underline_thickness(
        self, font: str, fontsize: float, dpi: float
    ) -> float: ...
    def get_sized_alternatives_for_symbol(
        self, fontname: str, sym: str
    ) -> list[tuple[str, str]]: ...

class TruetypeFonts(Fonts, metaclass=abc.ABCMeta):
    fontmap: Incomplete
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...
    def get_xheight(self, fontname: str, fontsize: float, dpi: float) -> float: ...
    def get_underline_thickness(
        self, font: str, fontsize: float, dpi: float
    ) -> float: ...
    def get_kern(
        self,
        font1: str,
        fontclass1: str,
        sym1: str,
        fontsize1: float,
        font2: str,
        fontclass2: str,
        sym2: str,
        fontsize2: float,
        dpi: float,
    ) -> float: ...

class BakomaFonts(TruetypeFonts):
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...
    def get_sized_alternatives_for_symbol(
        self, fontname: str, sym: str
    ) -> list[tuple[str, str]]: ...

class UnicodeFonts(TruetypeFonts):
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...
    def get_sized_alternatives_for_symbol(
        self, fontname: str, sym: str
    ) -> list[tuple[str, str]]: ...

class DejaVuFonts(UnicodeFonts, metaclass=abc.ABCMeta):
    bakoma: Incomplete
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...

class DejaVuSerifFonts(DejaVuFonts): ...
class DejaVuSansFonts(DejaVuFonts): ...

class StixFonts(UnicodeFonts):
    def __init__(
        self, default_font_prop: FontProperties, load_glyph_flags: int
    ) -> None: ...
    def get_sized_alternatives_for_symbol(
        self, fontname: str, sym: str
    ) -> list[tuple[str, str]] | list[tuple[int, str]]: ...

class StixSansFonts(StixFonts): ...

SHRINK_FACTOR: float
NUM_SIZE_LEVELS: int

class FontConstantsBase:
    script_space: T.ClassVar[float]
    subdrop: T.ClassVar[float]
    sup1: T.ClassVar[float]
    sub1: T.ClassVar[float]
    sub2: T.ClassVar[float]
    delta: T.ClassVar[float]
    delta_slanted: T.ClassVar[float]
    delta_integral: T.ClassVar[float]

class ComputerModernFontConstants(FontConstantsBase):
    script_space: float
    subdrop: float
    sup1: float
    sub1: float
    sub2: float
    delta: float
    delta_slanted: float
    delta_integral: float

class STIXFontConstants(FontConstantsBase):
    script_space: float
    sup1: float
    sub2: float
    delta: float
    delta_slanted: float
    delta_integral: float

class STIXSansFontConstants(FontConstantsBase):
    script_space: float
    sup1: float
    delta_slanted: float
    delta_integral: float

class DejaVuSerifFontConstants(FontConstantsBase): ...
class DejaVuSansFontConstants(FontConstantsBase): ...

class Node:
    size: int
    def __init__(self) -> None: ...
    def get_kerning(self, next: Node | None) -> float: ...
    def shrink(self) -> None: ...
    def render(self, output: Output, x: float, y: float) -> None: ...

class Box(Node):
    width: Incomplete
    height: Incomplete
    depth: Incomplete
    def __init__(self, width: float, height: float, depth: float) -> None: ...
    def shrink(self) -> None: ...
    def render(
        self, output: Output, x1: float, y1: float, x2: float, y2: float
    ) -> None: ...

class Vbox(Box):
    def __init__(self, height: float, depth: float) -> None: ...

class Hbox(Box):
    def __init__(self, width: float) -> None: ...

class Char(Node):
    c: Incomplete
    fontset: Incomplete
    font: Incomplete
    font_class: Incomplete
    fontsize: Incomplete
    dpi: Incomplete
    def __init__(self, c: str, state: ParserState) -> None: ...
    def is_slanted(self) -> bool: ...
    def get_kerning(self, next: Node | None) -> float: ...
    def render(self, output: Output, x: float, y: float) -> None: ...
    def shrink(self) -> None: ...

class Accent(Char):
    def shrink(self) -> None: ...
    def render(self, output: Output, x: float, y: float) -> None: ...

class List(Box):
    shift_amount: float
    children: Incomplete
    glue_set: float
    glue_sign: int
    glue_order: int
    def __init__(self, elements: T.Sequence[Node]) -> None: ...
    def shrink(self) -> None: ...

class Hlist(List):
    def __init__(
        self,
        elements: T.Sequence[Node],
        w: float = 0.0,
        m: T.Literal["additional", "exactly"] = "additional",
        do_kern: bool = True,
    ) -> None: ...
    children: Incomplete
    def kern(self) -> None: ...
    height: Incomplete
    depth: Incomplete
    width: Incomplete
    glue_sign: int
    glue_order: int
    glue_ratio: float
    def hpack(
        self, w: float = 0.0, m: T.Literal["additional", "exactly"] = "additional"
    ) -> None: ...

class Vlist(List):
    def __init__(
        self,
        elements: T.Sequence[Node],
        h: float = 0.0,
        m: T.Literal["additional", "exactly"] = "additional",
    ) -> None: ...
    width: Incomplete
    depth: Incomplete
    height: Incomplete
    glue_sign: int
    glue_order: int
    glue_ratio: float
    def vpack(
        self,
        h: float = 0.0,
        m: T.Literal["additional", "exactly"] = "additional",
        l: float = ...,
    ) -> None: ...

class Rule(Box):
    fontset: Incomplete
    def __init__(
        self, width: float, height: float, depth: float, state: ParserState
    ) -> None: ...
    def render(
        self, output: Output, x: float, y: float, w: float, h: float
    ) -> None: ...

class Hrule(Rule):
    def __init__(self, state: ParserState, thickness: float | None = None) -> None: ...

class Vrule(Rule):
    def __init__(self, state: ParserState) -> None: ...

class _GlueSpec(NamedTuple):
    width: float
    stretch: float
    stretch_order: int
    shrink: float
    shrink_order: int

class Glue(Node):
    glue_spec: Incomplete
    def __init__(
        self,
        glue_type: (
            _GlueSpec
            | T.Literal[
                "fil",
                "fill",
                "filll",
                "neg_fil",
                "neg_fill",
                "neg_filll",
                "empty",
                "ss",
            ]
        ),
    ) -> None: ...
    def shrink(self) -> None: ...

class HCentered(Hlist):
    def __init__(self, elements: list[Node]) -> None: ...

class VCentered(Vlist):
    def __init__(self, elements: list[Node]) -> None: ...

class Kern(Node):
    height: int
    depth: int
    width: Incomplete
    def __init__(self, width: float) -> None: ...
    def shrink(self) -> None: ...

class AutoHeightChar(Hlist):
    shift_amount: Incomplete
    def __init__(
        self,
        c: str,
        height: float,
        depth: float,
        state: ParserState,
        always: bool = False,
        factor: float | None = None,
    ) -> None: ...

class AutoWidthChar(Hlist):
    width: Incomplete
    def __init__(
        self,
        c: str,
        width: float,
        state: ParserState,
        always: bool = False,
        char_class: type[Char] = ...,
    ) -> None: ...

def ship(box: Box, xy: tuple[float, float] = (0, 0)) -> Output: ...
def Error(msg: str) -> ParserElement: ...

class ParserState:
    fontset: Incomplete
    font_class: Incomplete
    fontsize: Incomplete
    dpi: Incomplete
    def __init__(
        self, fontset: Fonts, font: str, font_class: str, fontsize: float, dpi: float
    ) -> None: ...
    def copy(self) -> ParserState: ...
    @property
    def font(self) -> str: ...
    @font.setter
    def font(self, name: str) -> None: ...
    def get_current_underline_thickness(self) -> float: ...

def cmd(expr: str, args: ParserElement) -> ParserElement: ...

class Parser:
    class _MathStyle(enum.Enum):
        DISPLAYSTYLE = 0
        TEXTSTYLE = 1
        SCRIPTSTYLE = 2
        SCRIPTSCRIPTSTYLE = 3

    def __init__(self) -> None: ...
    def parse(
        self, s: str, fonts_object: Fonts, fontsize: float, dpi: float
    ) -> Hlist: ...
    def get_state(self) -> ParserState: ...
    def pop_state(self) -> None: ...
    def push_state(self) -> None: ...
    def main(self, toks: ParseResults) -> list[Hlist]: ...
    def math_string(self, toks: ParseResults) -> ParseResults: ...
    def math(self, toks: ParseResults) -> T.Any: ...
    def non_math(self, toks: ParseResults) -> T.Any: ...
    float_literal: Incomplete
    def text(self, toks: ParseResults) -> T.Any: ...
    def space(self, toks: ParseResults) -> T.Any: ...
    def customspace(self, toks: ParseResults) -> T.Any: ...
    def symbol(
        self, s: str, loc: int, toks: ParseResults | dict[str, str]
    ) -> T.Any: ...
    def unknown_symbol(self, s: str, loc: int, toks: ParseResults) -> T.Any: ...
    def accent(self, toks: ParseResults) -> T.Any: ...
    def function(self, s: str, loc: int, toks: ParseResults) -> T.Any: ...
    def operatorname(self, s: str, loc: int, toks: ParseResults) -> T.Any: ...
    def start_group(self, toks: ParseResults) -> T.Any: ...
    def group(self, toks: ParseResults) -> T.Any: ...
    def required_group(self, toks: ParseResults) -> T.Any: ...
    optional_group = required_group
    def end_group(self) -> T.Any: ...
    def unclosed_group(self, s: str, loc: int, toks: ParseResults) -> T.Any: ...
    def font(self, toks: ParseResults) -> T.Any: ...
    def is_overunder(self, nucleus: Node) -> bool: ...
    def is_dropsub(self, nucleus: Node) -> bool: ...
    def is_slanted(self, nucleus: Node) -> bool: ...
    def subsuper(self, s: str, loc: int, toks: ParseResults) -> T.Any: ...
    def style_literal(self, toks: ParseResults) -> T.Any: ...
    def genfrac(self, toks: ParseResults) -> T.Any: ...
    def frac(self, toks: ParseResults) -> T.Any: ...
    def dfrac(self, toks: ParseResults) -> T.Any: ...
    def binom(self, toks: ParseResults) -> T.Any: ...
    overset: Incomplete
    underset: Incomplete
    def sqrt(self, toks: ParseResults) -> T.Any: ...
    def overline(self, toks: ParseResults) -> T.Any: ...
    def auto_delim(self, toks: ParseResults) -> T.Any: ...
    def boldsymbol(self, toks: ParseResults) -> T.Any: ...
    def substack(self, toks: ParseResults) -> T.Any: ...
