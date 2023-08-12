import matplotlib.cm as cm
from _typeshed import Incomplete
from matplotlib.backend_bases import MouseButton as MouseButton
from matplotlib.text import Text as Text

class ClabelText(Text):
    def get_rotation(self): ...

class ContourLabeler:
    labelFmt: Incomplete
    labelManual: Incomplete
    rightside_up: Incomplete
    labelLevelList: Incomplete
    labelIndiceList: Incomplete
    labelMappable: Incomplete
    labelCValueList: Incomplete
    labelXYs: Incomplete
    def clabel(self, levels: Incomplete | None = ..., *, fontsize: Incomplete | None = ..., inline: bool = ..., inline_spacing: int = ..., fmt: Incomplete | None = ..., colors: Incomplete | None = ..., use_clabeltext: bool = ..., manual: bool = ..., rightside_up: bool = ..., zorder: Incomplete | None = ...): ...
    @property
    def labelFontProps(self): ...
    @property
    def labelFontSizeList(self): ...
    @property
    def labelTextsList(self): ...
    def print_label(self, linecontour, labelwidth): ...
    def too_close(self, x, y, lw): ...
    def set_label_props(self, label, text, color) -> None: ...
    def get_text(self, lev, fmt): ...
    def locate_label(self, linecontour, labelwidth): ...
    def calc_label_rot_and_inline(self, slc, ind, lw, lc: Incomplete | None = ..., spacing: int = ...): ...
    def add_label(self, x, y, rotation, lev, cvalue) -> None: ...
    def add_label_clabeltext(self, x, y, rotation, lev, cvalue) -> None: ...
    def add_label_near(self, x, y, inline: bool = ..., inline_spacing: int = ..., transform: Incomplete | None = ...) -> None: ...
    def pop_label(self, index: int = ...) -> None: ...
    def labels(self, inline, inline_spacing) -> None: ...
    def remove(self) -> None: ...

class ContourSet(cm.ScalarMappable, ContourLabeler):
    axes: Incomplete
    levels: Incomplete
    filled: Incomplete
    linewidths: Incomplete
    linestyles: Incomplete
    hatches: Incomplete
    alpha: Incomplete
    origin: Incomplete
    extent: Incomplete
    colors: Incomplete
    extend: Incomplete
    antialiased: Incomplete
    nchunk: Incomplete
    locator: Incomplete
    logscale: bool
    negative_linestyles: Incomplete
    collections: Incomplete
    labelTexts: Incomplete
    labelCValues: Incomplete
    allkinds: Incomplete
    tlinewidths: Incomplete
    def __init__(self, ax, *args, levels: Incomplete | None = ..., filled: bool = ..., linewidths: Incomplete | None = ..., linestyles: Incomplete | None = ..., hatches=..., alpha: Incomplete | None = ..., origin: Incomplete | None = ..., extent: Incomplete | None = ..., cmap: Incomplete | None = ..., colors: Incomplete | None = ..., norm: Incomplete | None = ..., vmin: Incomplete | None = ..., vmax: Incomplete | None = ..., extend: str = ..., antialiased: Incomplete | None = ..., nchunk: int = ..., locator: Incomplete | None = ..., transform: Incomplete | None = ..., negative_linestyles: Incomplete | None = ..., **kwargs) -> None: ...
    def get_transform(self): ...
    def legend_elements(self, variable_name: str = ..., str_format=...): ...
    tcolors: Incomplete
    def changed(self) -> None: ...
    def get_alpha(self): ...
    def set_alpha(self, alpha) -> None: ...
    def find_nearest_contour(self, x, y, indices: Incomplete | None = ..., pixel: bool = ...): ...
    def remove(self) -> None: ...

class QuadContourSet(ContourSet): ...