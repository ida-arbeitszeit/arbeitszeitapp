import matplotlib.collections as mcoll
from _typeshed import Incomplete
from matplotlib.backend_bases import MouseButton as MouseButton
from matplotlib.lines import Line2D as Line2D
from matplotlib.path import Path as Path
from matplotlib.text import Text as Text

class ContourLabeler:
    labelFmt: Incomplete
    labelManual: Incomplete
    rightside_up: Incomplete
    labelLevelList: Incomplete
    labelIndiceList: Incomplete
    labelMappable: Incomplete
    labelCValueList: Incomplete
    labelXYs: Incomplete
    def clabel(
        self,
        levels: Incomplete | None = None,
        *,
        fontsize: Incomplete | None = None,
        inline: bool = True,
        inline_spacing: int = 5,
        fmt: Incomplete | None = None,
        colors: Incomplete | None = None,
        use_clabeltext: bool = False,
        manual: bool = False,
        rightside_up: bool = True,
        zorder: Incomplete | None = None,
    ): ...
    def print_label(self, linecontour, labelwidth): ...
    def too_close(self, x, y, lw): ...
    def get_text(self, lev, fmt): ...
    def locate_label(self, linecontour, labelwidth): ...
    def calc_label_rot_and_inline(
        self, slc, ind, lw, lc: Incomplete | None = None, spacing: int = 5
    ): ...
    def add_label(self, x, y, rotation, lev, cvalue) -> None: ...
    def add_label_clabeltext(self, x, y, rotation, lev, cvalue) -> None: ...
    def add_label_near(
        self,
        x,
        y,
        inline: bool = True,
        inline_spacing: int = 5,
        transform: Incomplete | None = None,
    ) -> None: ...
    def pop_label(self, index: int = -1) -> None: ...
    def labels(self, inline, inline_spacing) -> None: ...
    def remove(self) -> None: ...

class ContourSet(ContourLabeler, mcoll.Collection):
    axes: Incomplete
    levels: Incomplete
    filled: Incomplete
    hatches: Incomplete
    origin: Incomplete
    extent: Incomplete
    colors: Incomplete
    extend: Incomplete
    nchunk: Incomplete
    locator: Incomplete
    logscale: bool
    negative_linestyles: Incomplete
    labelTexts: Incomplete
    labelCValues: Incomplete
    def __init__(
        self,
        ax,
        *args,
        levels: Incomplete | None = None,
        filled: bool = False,
        linewidths: Incomplete | None = None,
        linestyles: Incomplete | None = None,
        hatches=(None,),
        alpha: Incomplete | None = None,
        origin: Incomplete | None = None,
        extent: Incomplete | None = None,
        cmap: Incomplete | None = None,
        colors: Incomplete | None = None,
        norm: Incomplete | None = None,
        vmin: Incomplete | None = None,
        vmax: Incomplete | None = None,
        extend: str = "neither",
        antialiased: Incomplete | None = None,
        nchunk: int = 0,
        locator: Incomplete | None = None,
        transform: Incomplete | None = None,
        negative_linestyles: Incomplete | None = None,
        clip_path: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    allsegs: Incomplete
    allkinds: Incomplete
    tcolors: Incomplete
    tlinewidths: Incomplete
    alpha: Incomplete
    linestyles: Incomplete
    @property
    def antialiased(self): ...
    @antialiased.setter
    def antialiased(self, aa) -> None: ...
    @property
    def collections(self): ...
    def get_transform(self): ...
    def legend_elements(self, variable_name: str = "x", str_format=...): ...
    def changed(self) -> None: ...
    def find_nearest_contour(
        self, x, y, indices: Incomplete | None = None, pixel: bool = True
    ): ...
    def draw(self, renderer) -> None: ...

class QuadContourSet(ContourSet): ...
