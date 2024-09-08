from _typeshed import Incomplete

from .artist import Artist as Artist
from .artist import allow_rasterization as allow_rasterization
from .patches import Rectangle as Rectangle
from .path import Path as Path
from .text import Text as Text
from .transforms import Bbox as Bbox

class Cell(Rectangle):
    PAD: float
    def __init__(
        self,
        xy,
        width,
        height,
        *,
        edgecolor: str = "k",
        facecolor: str = "w",
        fill: bool = True,
        text: str = "",
        loc: str = "right",
        fontproperties: Incomplete | None = None,
        visible_edges: str = "closed",
    ) -> None: ...
    stale: bool
    def set_transform(self, t) -> None: ...
    def set_figure(self, fig) -> None: ...
    def get_text(self): ...
    def set_fontsize(self, size) -> None: ...
    def get_fontsize(self): ...
    def auto_set_font_size(self, renderer): ...
    def draw(self, renderer) -> None: ...
    def get_text_bounds(self, renderer): ...
    def get_required_width(self, renderer): ...
    def set_text_props(self, **kwargs) -> None: ...
    @property
    def visible_edges(self): ...
    @visible_edges.setter
    def visible_edges(self, value) -> None: ...
    def get_path(self): ...

CustomCell = Cell

class Table(Artist):
    codes: Incomplete
    FONTSIZE: int
    AXESPAD: float
    def __init__(
        self,
        ax,
        loc: Incomplete | None = None,
        bbox: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def add_cell(self, row, col, *args, **kwargs): ...
    stale: bool
    def __setitem__(self, position, cell) -> None: ...
    def __getitem__(self, position): ...
    @property
    def edges(self): ...
    @edges.setter
    def edges(self, value) -> None: ...
    def draw(self, renderer) -> None: ...
    def contains(self, mouseevent): ...
    def get_children(self): ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    def auto_set_column_width(self, col) -> None: ...
    def auto_set_font_size(self, value: bool = True) -> None: ...
    def scale(self, xscale, yscale) -> None: ...
    def set_fontsize(self, size) -> None: ...
    def get_celld(self): ...

def table(
    ax,
    cellText: Incomplete | None = None,
    cellColours: Incomplete | None = None,
    cellLoc: str = "right",
    colWidths: Incomplete | None = None,
    rowLabels: Incomplete | None = None,
    rowColours: Incomplete | None = None,
    rowLoc: str = "left",
    colLabels: Incomplete | None = None,
    colColours: Incomplete | None = None,
    colLoc: str = "center",
    loc: str = "bottom",
    bbox: Incomplete | None = None,
    edges: str = "closed",
    **kwargs,
): ...
