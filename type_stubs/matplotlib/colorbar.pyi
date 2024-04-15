import matplotlib.spines as mspines
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import cm as cm
from matplotlib import collections as collections
from matplotlib import colors as colors
from matplotlib import contour as contour
from matplotlib import ticker as ticker

class _ColorbarSpine(mspines.Spine):
    def __init__(self, axes) -> None: ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    stale: bool
    def set_xy(self, xy) -> None: ...
    def draw(self, renderer): ...

class _ColorbarAxesLocator:
    def __init__(self, cbar) -> None: ...
    def __call__(self, ax, renderer): ...
    def get_subplotspec(self): ...

class Colorbar:
    n_rasterize: int
    mappable: Incomplete
    ax: Incomplete
    alpha: Incomplete
    cmap: Incomplete
    norm: Incomplete
    values: Incomplete
    boundaries: Incomplete
    extend: Incomplete
    spacing: Incomplete
    orientation: Incomplete
    drawedges: Incomplete
    extendfrac: Incomplete
    extendrect: Incomplete
    solids: Incomplete
    solids_patches: Incomplete
    lines: Incomplete
    outline: Incomplete
    dividers: Incomplete
    ticklocation: Incomplete
    def __init__(
        self,
        ax,
        mappable: Incomplete | None = None,
        *,
        cmap: Incomplete | None = None,
        norm: Incomplete | None = None,
        alpha: Incomplete | None = None,
        values: Incomplete | None = None,
        boundaries: Incomplete | None = None,
        orientation: Incomplete | None = None,
        ticklocation: str = "auto",
        extend: Incomplete | None = None,
        spacing: str = "uniform",
        ticks: Incomplete | None = None,
        format: Incomplete | None = None,
        drawedges: bool = False,
        extendfrac: Incomplete | None = None,
        extendrect: bool = False,
        label: str = "",
        location: Incomplete | None = None,
    ) -> None: ...
    @property
    def locator(self): ...
    @locator.setter
    def locator(self, loc) -> None: ...
    @property
    def minorlocator(self): ...
    @minorlocator.setter
    def minorlocator(self, loc) -> None: ...
    @property
    def formatter(self): ...
    @formatter.setter
    def formatter(self, fmt) -> None: ...
    @property
    def minorformatter(self): ...
    @minorformatter.setter
    def minorformatter(self, fmt) -> None: ...
    stale: bool
    def update_normal(self, mappable) -> None: ...
    def add_lines(self, *args, **kwargs): ...
    def update_ticks(self) -> None: ...
    def set_ticks(
        self, ticks, *, labels: Incomplete | None = None, minor: bool = False, **kwargs
    ) -> None: ...
    def get_ticks(self, minor: bool = False): ...
    def set_ticklabels(self, ticklabels, *, minor: bool = False, **kwargs) -> None: ...
    def minorticks_on(self) -> None: ...
    def minorticks_off(self) -> None: ...
    def set_label(self, label, *, loc: Incomplete | None = None, **kwargs) -> None: ...
    def set_alpha(self, alpha) -> None: ...
    def remove(self) -> None: ...
    def drag_pan(self, button, key, x, y) -> None: ...

ColorbarBase = Colorbar

def make_axes(
    parents,
    location: Incomplete | None = None,
    orientation: Incomplete | None = None,
    fraction: float = 0.15,
    shrink: float = 1.0,
    aspect: int = 20,
    **kwargs,
): ...
def make_axes_gridspec(
    parent,
    *,
    location: Incomplete | None = None,
    orientation: Incomplete | None = None,
    fraction: float = 0.15,
    shrink: float = 1.0,
    aspect: int = 20,
    **kwargs,
): ...
