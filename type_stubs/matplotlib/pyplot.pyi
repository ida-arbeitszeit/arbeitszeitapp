import datetime
import os
import pathlib
from collections.abc import Callable as Callable
from collections.abc import Hashable, Iterable, Sequence
from contextlib import AbstractContextManager, ExitStack
from typing import Any, BinaryIO, Literal, overload

import matplotlib.axes
import numpy as np
import PIL.Image
from _typeshed import Incomplete
from cycler import cycler as cycler
from matplotlib import cbook as cbook
from matplotlib import interactive as interactive
from matplotlib import mlab as mlab
from matplotlib import rcParamsDefault as rcParamsDefault
from matplotlib import rcParamsOrig as rcParamsOrig
from matplotlib import rcsetup as rcsetup
from matplotlib.artist import Artist as Artist
from matplotlib.axes import Axes as Axes
from matplotlib.axes import Subplot as Subplot
from matplotlib.axes._base import _AxesBase
from matplotlib.axis import Tick as Tick
from matplotlib.backend_bases import Event as Event
from matplotlib.backend_bases import FigureCanvasBase as FigureCanvasBase
from matplotlib.backend_bases import FigureManagerBase as FigureManagerBase
from matplotlib.backend_bases import MouseButton as MouseButton
from matplotlib.backend_bases import RendererBase as RendererBase
from matplotlib.backends import BackendFilter as BackendFilter
from matplotlib.backends import backend_registry as backend_registry
from matplotlib.cm import ScalarMappable as ScalarMappable
from matplotlib.collections import Collection as Collection
from matplotlib.collections import EventCollection as EventCollection
from matplotlib.collections import LineCollection as LineCollection
from matplotlib.collections import PathCollection as PathCollection
from matplotlib.collections import PolyCollection as PolyCollection
from matplotlib.collections import QuadMesh as QuadMesh
from matplotlib.colorbar import Colorbar as Colorbar
from matplotlib.colors import Colormap as Colormap
from matplotlib.colors import Normalize as Normalize
from matplotlib.container import BarContainer as BarContainer
from matplotlib.container import ErrorbarContainer as ErrorbarContainer
from matplotlib.container import StemContainer as StemContainer
from matplotlib.contour import ContourSet as ContourSet
from matplotlib.contour import QuadContourSet as QuadContourSet
from matplotlib.figure import Figure as Figure
from matplotlib.figure import FigureBase as FigureBase
from matplotlib.figure import SubFigure as SubFigure
from matplotlib.figure import figaspect as figaspect
from matplotlib.gridspec import GridSpec as GridSpec
from matplotlib.gridspec import SubplotSpec as SubplotSpec
from matplotlib.image import AxesImage as AxesImage
from matplotlib.image import FigureImage as FigureImage
from matplotlib.legend import Legend as Legend
from matplotlib.lines import AxLine as AxLine
from matplotlib.lines import Line2D as Line2D
from matplotlib.mlab import GaussianKDE as GaussianKDE
from matplotlib.patches import Arrow as Arrow
from matplotlib.patches import Circle as Circle
from matplotlib.patches import FancyArrow as FancyArrow
from matplotlib.patches import Polygon as Polygon
from matplotlib.patches import Rectangle as Rectangle
from matplotlib.patches import StepPatch as StepPatch
from matplotlib.patches import Wedge as Wedge
from matplotlib.projections import PolarAxes as PolarAxes
from matplotlib.quiver import Barbs as Barbs
from matplotlib.quiver import Quiver as Quiver
from matplotlib.quiver import QuiverKey as QuiverKey
from matplotlib.scale import ScaleBase as ScaleBase
from matplotlib.scale import get_scale_names as get_scale_names
from matplotlib.text import Annotation as Annotation
from matplotlib.text import Text as Text
from matplotlib.transforms import Bbox as Bbox
from matplotlib.transforms import Transform as Transform
from matplotlib.typing import ColorType as ColorType
from matplotlib.typing import HashableList as HashableList
from matplotlib.typing import LineStyleType as LineStyleType
from matplotlib.typing import MarkerType as MarkerType
from matplotlib.widgets import Button as Button
from matplotlib.widgets import Slider as Slider
from matplotlib.widgets import SubplotTool as SubplotTool
from matplotlib.widgets import Widget as Widget
from numpy.typing import ArrayLike as ArrayLike

from .ticker import AutoLocator as AutoLocator
from .ticker import FixedFormatter as FixedFormatter
from .ticker import FixedLocator as FixedLocator
from .ticker import FormatStrFormatter as FormatStrFormatter
from .ticker import Formatter as Formatter
from .ticker import FuncFormatter as FuncFormatter
from .ticker import IndexLocator as IndexLocator
from .ticker import LinearLocator as LinearLocator
from .ticker import Locator as Locator
from .ticker import LogFormatter as LogFormatter
from .ticker import LogFormatterExponent as LogFormatterExponent
from .ticker import LogFormatterMathtext as LogFormatterMathtext
from .ticker import LogLocator as LogLocator
from .ticker import MaxNLocator as MaxNLocator
from .ticker import MultipleLocator as MultipleLocator
from .ticker import NullFormatter as NullFormatter
from .ticker import NullLocator as NullLocator
from .ticker import ScalarFormatter as ScalarFormatter
from .ticker import TickHelper as TickHelper

colormaps: Incomplete
color_sequences: Incomplete

def install_repl_displayhook() -> None: ...
def uninstall_repl_displayhook() -> None: ...

draw_all: Incomplete

def set_loglevel(*args, **kwargs) -> None: ...
def findobj(
    o: Artist | None = None,
    match: Callable[[Artist], bool] | type[Artist] | None = None,
    include_self: bool = True,
) -> list[Artist]: ...
def switch_backend(newbackend: str) -> None: ...
def new_figure_manager(*args, **kwargs): ...
def draw_if_interactive(*args, **kwargs): ...
def show(*args, **kwargs) -> None: ...
def isinteractive() -> bool: ...
def ioff() -> AbstractContextManager: ...
def ion() -> AbstractContextManager: ...
def pause(interval: float) -> None: ...
def rc(group: str, **kwargs) -> None: ...
def rc_context(
    rc: dict[str, Any] | None = None,
    fname: str | pathlib.Path | os.PathLike | None = None,
) -> AbstractContextManager[None]: ...
def rcdefaults() -> None: ...
def getp(obj, *args, **kwargs): ...
def get(obj, *args, **kwargs): ...
def setp(obj, *args, **kwargs): ...
def xkcd(scale: float = 1, length: float = 100, randomness: float = 2) -> ExitStack: ...
def figure(
    num: int | str | Figure | SubFigure | None = None,
    figsize: tuple[float, float] | None = None,
    dpi: float | None = None,
    *,
    facecolor: ColorType | None = None,
    edgecolor: ColorType | None = None,
    frameon: bool = True,
    FigureClass: type[Figure] = ...,
    clear: bool = False,
    **kwargs,
) -> Figure: ...
def gcf() -> Figure: ...
def fignum_exists(num: int | str) -> bool: ...
def get_fignums() -> list[int]: ...
def get_figlabels() -> list[Any]: ...
def get_current_fig_manager() -> FigureManagerBase | None: ...
def connect(s: str, func: Callable[[Event], Any]) -> int: ...
def disconnect(cid: int) -> None: ...
def close(fig: None | int | str | Figure | Literal["all"] = None) -> None: ...
def clf() -> None: ...
def draw() -> None: ...
def savefig(*args, **kwargs) -> None: ...
def figlegend(*args, **kwargs) -> Legend: ...
def axes(
    arg: None | tuple[float, float, float, float] = None, **kwargs
) -> matplotlib.axes.Axes: ...
def delaxes(ax: matplotlib.axes.Axes | None = None) -> None: ...
def sca(ax: Axes) -> None: ...
def cla() -> None: ...
def subplot(*args, **kwargs) -> Axes: ...
@overload
def subplots(
    nrows: Literal[1] = ...,
    ncols: Literal[1] = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[True] = ...,
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw,
) -> tuple[Figure, Axes]: ...
@overload
def subplots(
    nrows: int = ...,
    ncols: int = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: Literal[False],
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw,
) -> tuple[Figure, np.ndarray]: ...
@overload
def subplots(
    nrows: int = ...,
    ncols: int = ...,
    *,
    sharex: bool | Literal["none", "all", "row", "col"] = ...,
    sharey: bool | Literal["none", "all", "row", "col"] = ...,
    squeeze: bool = ...,
    width_ratios: Sequence[float] | None = ...,
    height_ratios: Sequence[float] | None = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    **fig_kw,
) -> tuple[Figure, Any]: ...
@overload
def subplot_mosaic(
    mosaic: str,
    *,
    sharex: bool = ...,
    sharey: bool = ...,
    width_ratios: ArrayLike | None = ...,
    height_ratios: ArrayLike | None = ...,
    empty_sentinel: str = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    per_subplot_kw: dict[str | tuple[str, ...], dict[str, Any]] | None = ...,
    **fig_kw: Any,
) -> tuple[Figure, dict[str, matplotlib.axes.Axes]]: ...
@overload
def subplot_mosaic(
    mosaic: list[HashableList[_T]],
    *,
    sharex: bool = ...,
    sharey: bool = ...,
    width_ratios: ArrayLike | None = ...,
    height_ratios: ArrayLike | None = ...,
    empty_sentinel: _T = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    per_subplot_kw: dict[_T | tuple[_T, ...], dict[str, Any]] | None = ...,
    **fig_kw: Any,
) -> tuple[Figure, dict[_T, matplotlib.axes.Axes]]: ...
@overload
def subplot_mosaic(
    mosaic: list[HashableList[Hashable]],
    *,
    sharex: bool = ...,
    sharey: bool = ...,
    width_ratios: ArrayLike | None = ...,
    height_ratios: ArrayLike | None = ...,
    empty_sentinel: Any = ...,
    subplot_kw: dict[str, Any] | None = ...,
    gridspec_kw: dict[str, Any] | None = ...,
    per_subplot_kw: dict[Hashable | tuple[Hashable, ...], dict[str, Any]] | None = ...,
    **fig_kw: Any,
) -> tuple[Figure, dict[Hashable, matplotlib.axes.Axes]]: ...
def subplot2grid(
    shape: tuple[int, int],
    loc: tuple[int, int],
    rowspan: int = 1,
    colspan: int = 1,
    fig: Figure | None = None,
    **kwargs,
) -> matplotlib.axes.Axes: ...
def twinx(ax: matplotlib.axes.Axes | None = None) -> _AxesBase: ...
def twiny(ax: matplotlib.axes.Axes | None = None) -> _AxesBase: ...
def subplot_tool(targetfig: Figure | None = None) -> SubplotTool | None: ...
def box(on: bool | None = None) -> None: ...
def xlim(*args, **kwargs) -> tuple[float, float]: ...
def ylim(*args, **kwargs) -> tuple[float, float]: ...
def xticks(
    ticks: ArrayLike | None = None,
    labels: Sequence[str] | None = None,
    *,
    minor: bool = False,
    **kwargs,
) -> tuple[list[Tick] | np.ndarray, list[Text]]: ...
def yticks(
    ticks: ArrayLike | None = None,
    labels: Sequence[str] | None = None,
    *,
    minor: bool = False,
    **kwargs,
) -> tuple[list[Tick] | np.ndarray, list[Text]]: ...
def rgrids(
    radii: ArrayLike | None = None,
    labels: Sequence[str | Text] | None = None,
    angle: float | None = None,
    fmt: str | None = None,
    **kwargs,
) -> tuple[list[Line2D], list[Text]]: ...
def thetagrids(
    angles: ArrayLike | None = None,
    labels: Sequence[str | Text] | None = None,
    fmt: str | None = None,
    **kwargs,
) -> tuple[list[Line2D], list[Text]]: ...
def get_plot_commands() -> list[str]: ...
def colorbar(
    mappable: ScalarMappable | None = None,
    cax: matplotlib.axes.Axes | None = None,
    ax: matplotlib.axes.Axes | Iterable[matplotlib.axes.Axes] | None = None,
    **kwargs,
) -> Colorbar: ...
def clim(vmin: float | None = None, vmax: float | None = None) -> None: ...
def get_cmap(
    name: Colormap | str | None = None, lut: int | None = None
) -> Colormap: ...
def set_cmap(cmap: Colormap | str) -> None: ...
def imread(
    fname: str | pathlib.Path | BinaryIO, format: str | None = None
) -> np.ndarray: ...
def imsave(fname: str | os.PathLike | BinaryIO, arr: ArrayLike, **kwargs) -> None: ...
def matshow(A: ArrayLike, fignum: None | int = None, **kwargs) -> AxesImage: ...
def polar(*args, **kwargs) -> list[Line2D]: ...
def figimage(
    X: ArrayLike,
    xo: int = 0,
    yo: int = 0,
    alpha: float | None = None,
    norm: str | Normalize | None = None,
    cmap: str | Colormap | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    origin: Literal["upper", "lower"] | None = None,
    resize: bool = False,
    **kwargs,
) -> FigureImage: ...
def figtext(
    x: float, y: float, s: str, fontdict: dict[str, Any] | None = None, **kwargs
) -> Text: ...
def gca() -> Axes: ...
def gci() -> ScalarMappable | None: ...
def ginput(
    n: int = 1,
    timeout: float = 30,
    show_clicks: bool = True,
    mouse_add: MouseButton = ...,
    mouse_pop: MouseButton = ...,
    mouse_stop: MouseButton = ...,
) -> list[tuple[int, int]]: ...
def subplots_adjust(
    left: float | None = None,
    bottom: float | None = None,
    right: float | None = None,
    top: float | None = None,
    wspace: float | None = None,
    hspace: float | None = None,
) -> None: ...
def suptitle(t: str, **kwargs) -> Text: ...
def tight_layout(
    *,
    pad: float = 1.08,
    h_pad: float | None = None,
    w_pad: float | None = None,
    rect: tuple[float, float, float, float] | None = None,
) -> None: ...
def waitforbuttonpress(timeout: float = -1) -> None | bool: ...
def acorr(
    x: ArrayLike, *, data: Incomplete | None = None, **kwargs
) -> tuple[np.ndarray, np.ndarray, LineCollection | Line2D, Line2D | None]: ...
def angle_spectrum(
    x: ArrayLike,
    Fs: float | None = None,
    Fc: int | None = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, Line2D]: ...
def annotate(
    text: str,
    xy: tuple[float, float],
    xytext: tuple[float, float] | None = None,
    xycoords: (
        str
        | Artist
        | Transform
        | Callable[[RendererBase], Bbox | Transform]
        | tuple[float, float]
    ) = "data",
    textcoords: (
        str
        | Artist
        | Transform
        | Callable[[RendererBase], Bbox | Transform]
        | tuple[float, float]
        | None
    ) = None,
    arrowprops: dict[str, Any] | None = None,
    annotation_clip: bool | None = None,
    **kwargs,
) -> Annotation: ...
def arrow(x: float, y: float, dx: float, dy: float, **kwargs) -> FancyArrow: ...
def autoscale(
    enable: bool = True,
    axis: Literal["both", "x", "y"] = "both",
    tight: bool | None = None,
) -> None: ...
def axhline(y: float = 0, xmin: float = 0, xmax: float = 1, **kwargs) -> Line2D: ...
def axhspan(
    ymin: float, ymax: float, xmin: float = 0, xmax: float = 1, **kwargs
) -> Rectangle: ...
def axis(
    arg: tuple[float, float, float, float] | bool | str | None = None,
    /,
    *,
    emit: bool = True,
    **kwargs,
) -> tuple[float, float, float, float]: ...
def axline(
    xy1: tuple[float, float],
    xy2: tuple[float, float] | None = None,
    *,
    slope: float | None = None,
    **kwargs,
) -> AxLine: ...
def axvline(x: float = 0, ymin: float = 0, ymax: float = 1, **kwargs) -> Line2D: ...
def axvspan(
    xmin: float, xmax: float, ymin: float = 0, ymax: float = 1, **kwargs
) -> Rectangle: ...
def bar(
    x: float | ArrayLike,
    height: float | ArrayLike,
    width: float | ArrayLike = 0.8,
    bottom: float | ArrayLike | None = None,
    *,
    align: Literal["center", "edge"] = "center",
    data: Incomplete | None = None,
    **kwargs,
) -> BarContainer: ...
def barbs(*args, data: Incomplete | None = None, **kwargs) -> Barbs: ...
def barh(
    y: float | ArrayLike,
    width: float | ArrayLike,
    height: float | ArrayLike = 0.8,
    left: float | ArrayLike | None = None,
    *,
    align: Literal["center", "edge"] = "center",
    data: Incomplete | None = None,
    **kwargs,
) -> BarContainer: ...
def bar_label(
    container: BarContainer,
    labels: ArrayLike | None = None,
    *,
    fmt: str | Callable[[float], str] = "%g",
    label_type: Literal["center", "edge"] = "edge",
    padding: float = 0,
    **kwargs,
) -> list[Annotation]: ...
def boxplot(
    x: ArrayLike | Sequence[ArrayLike],
    notch: bool | None = None,
    sym: str | None = None,
    vert: bool | None = None,
    whis: float | tuple[float, float] | None = None,
    positions: ArrayLike | None = None,
    widths: float | ArrayLike | None = None,
    patch_artist: bool | None = None,
    bootstrap: int | None = None,
    usermedians: ArrayLike | None = None,
    conf_intervals: ArrayLike | None = None,
    meanline: bool | None = None,
    showmeans: bool | None = None,
    showcaps: bool | None = None,
    showbox: bool | None = None,
    showfliers: bool | None = None,
    boxprops: dict[str, Any] | None = None,
    tick_labels: Sequence[str] | None = None,
    flierprops: dict[str, Any] | None = None,
    medianprops: dict[str, Any] | None = None,
    meanprops: dict[str, Any] | None = None,
    capprops: dict[str, Any] | None = None,
    whiskerprops: dict[str, Any] | None = None,
    manage_ticks: bool = True,
    autorange: bool = False,
    zorder: float | None = None,
    capwidths: float | ArrayLike | None = None,
    label: Sequence[str] | None = None,
    *,
    data: Incomplete | None = None,
) -> dict[str, Any]: ...
def broken_barh(
    xranges: Sequence[tuple[float, float]],
    yrange: tuple[float, float],
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> PolyCollection: ...
def clabel(CS: ContourSet, levels: ArrayLike | None = None, **kwargs) -> list[Text]: ...
def cohere(
    x: ArrayLike,
    y: ArrayLike,
    NFFT: int = 256,
    Fs: float = 2,
    Fc: int = 0,
    detrend: Literal["none", "mean", "linear"] | Callable[[ArrayLike], ArrayLike] = ...,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike = ...,
    noverlap: int = 0,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] = "default",
    scale_by_freq: bool | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray]: ...
def contour(*args, data: Incomplete | None = None, **kwargs) -> QuadContourSet: ...
def contourf(*args, data: Incomplete | None = None, **kwargs) -> QuadContourSet: ...
def csd(
    x: ArrayLike,
    y: ArrayLike,
    NFFT: int | None = None,
    Fs: float | None = None,
    Fc: int | None = None,
    detrend: (
        Literal["none", "mean", "linear"] | Callable[[ArrayLike], ArrayLike] | None
    ) = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    noverlap: int | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    scale_by_freq: bool | None = None,
    return_line: bool | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, Line2D]: ...
def ecdf(
    x: ArrayLike,
    weights: ArrayLike | None = None,
    *,
    complementary: bool = False,
    orientation: Literal["vertical", "horizonatal"] = "vertical",
    compress: bool = False,
    data: Incomplete | None = None,
    **kwargs,
) -> Line2D: ...
def errorbar(
    x: float | ArrayLike,
    y: float | ArrayLike,
    yerr: float | ArrayLike | None = None,
    xerr: float | ArrayLike | None = None,
    fmt: str = "",
    ecolor: ColorType | None = None,
    elinewidth: float | None = None,
    capsize: float | None = None,
    barsabove: bool = False,
    lolims: bool | ArrayLike = False,
    uplims: bool | ArrayLike = False,
    xlolims: bool | ArrayLike = False,
    xuplims: bool | ArrayLike = False,
    errorevery: int | tuple[int, int] = 1,
    capthick: float | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> ErrorbarContainer: ...
def eventplot(
    positions: ArrayLike | Sequence[ArrayLike],
    orientation: Literal["horizontal", "vertical"] = "horizontal",
    lineoffsets: float | Sequence[float] = 1,
    linelengths: float | Sequence[float] = 1,
    linewidths: float | Sequence[float] | None = None,
    colors: ColorType | Sequence[ColorType] | None = None,
    alpha: float | Sequence[float] | None = None,
    linestyles: LineStyleType | Sequence[LineStyleType] = "solid",
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> EventCollection: ...
def fill(*args, data: Incomplete | None = None, **kwargs) -> list[Polygon]: ...
def fill_between(
    x: ArrayLike,
    y1: ArrayLike | float,
    y2: ArrayLike | float = 0,
    where: Sequence[bool] | None = None,
    interpolate: bool = False,
    step: Literal["pre", "post", "mid"] | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> PolyCollection: ...
def fill_betweenx(
    y: ArrayLike,
    x1: ArrayLike | float,
    x2: ArrayLike | float = 0,
    where: Sequence[bool] | None = None,
    step: Literal["pre", "post", "mid"] | None = None,
    interpolate: bool = False,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> PolyCollection: ...
def grid(
    visible: bool | None = None,
    which: Literal["major", "minor", "both"] = "major",
    axis: Literal["both", "x", "y"] = "both",
    **kwargs,
) -> None: ...
def hexbin(
    x: ArrayLike,
    y: ArrayLike,
    C: ArrayLike | None = None,
    gridsize: int | tuple[int, int] = 100,
    bins: Literal["log"] | int | Sequence[float] | None = None,
    xscale: Literal["linear", "log"] = "linear",
    yscale: Literal["linear", "log"] = "linear",
    extent: tuple[float, float, float, float] | None = None,
    cmap: str | Colormap | None = None,
    norm: str | Normalize | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    alpha: float | None = None,
    linewidths: float | None = None,
    edgecolors: Literal["face", "none"] | ColorType = "face",
    reduce_C_function: Callable[[np.ndarray | list[float]], float] = ...,
    mincnt: int | None = None,
    marginals: bool = False,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> PolyCollection: ...
def hist(
    x: ArrayLike | Sequence[ArrayLike],
    bins: int | Sequence[float] | str | None = None,
    range: tuple[float, float] | None = None,
    density: bool = False,
    weights: ArrayLike | None = None,
    cumulative: bool | float = False,
    bottom: ArrayLike | float | None = None,
    histtype: Literal["bar", "barstacked", "step", "stepfilled"] = "bar",
    align: Literal["left", "mid", "right"] = "mid",
    orientation: Literal["vertical", "horizontal"] = "vertical",
    rwidth: float | None = None,
    log: bool = False,
    color: ColorType | Sequence[ColorType] | None = None,
    label: str | Sequence[str] | None = None,
    stacked: bool = False,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[
    np.ndarray | list[np.ndarray],
    np.ndarray,
    BarContainer | Polygon | list[BarContainer | Polygon],
]: ...
def stairs(
    values: ArrayLike,
    edges: ArrayLike | None = None,
    *,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    baseline: float | ArrayLike | None = 0,
    fill: bool = False,
    data: Incomplete | None = None,
    **kwargs,
) -> StepPatch: ...
def hist2d(
    x: ArrayLike,
    y: ArrayLike,
    bins: None | int | tuple[int, int] | ArrayLike | tuple[ArrayLike, ArrayLike] = 10,
    range: ArrayLike | None = None,
    density: bool = False,
    weights: ArrayLike | None = None,
    cmin: float | None = None,
    cmax: float | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, QuadMesh]: ...
def hlines(
    y: float | ArrayLike,
    xmin: float | ArrayLike,
    xmax: float | ArrayLike,
    colors: ColorType | Sequence[ColorType] | None = None,
    linestyles: LineStyleType = "solid",
    label: str = "",
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> LineCollection: ...
def imshow(
    X: ArrayLike | PIL.Image.Image,
    cmap: str | Colormap | None = None,
    norm: str | Normalize | None = None,
    *,
    aspect: Literal["equal", "auto"] | float | None = None,
    interpolation: str | None = None,
    alpha: float | ArrayLike | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    origin: Literal["upper", "lower"] | None = None,
    extent: tuple[float, float, float, float] | None = None,
    interpolation_stage: Literal["data", "rgba"] | None = None,
    filternorm: bool = True,
    filterrad: float = 4.0,
    resample: bool | None = None,
    url: str | None = None,
    data: Incomplete | None = None,
    **kwargs,
) -> AxesImage: ...
def legend(*args, **kwargs) -> Legend: ...
def locator_params(
    axis: Literal["both", "x", "y"] = "both", tight: bool | None = None, **kwargs
) -> None: ...
def loglog(*args, **kwargs) -> list[Line2D]: ...
def magnitude_spectrum(
    x: ArrayLike,
    Fs: float | None = None,
    Fc: int | None = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    scale: Literal["default", "linear", "dB"] | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, Line2D]: ...
def margins(
    *margins: float,
    x: float | None = None,
    y: float | None = None,
    tight: bool | None = True,
) -> tuple[float, float] | None: ...
def minorticks_off() -> None: ...
def minorticks_on() -> None: ...
def pcolor(
    *args: ArrayLike,
    shading: Literal["flat", "nearest", "auto"] | None = None,
    alpha: float | None = None,
    norm: str | Normalize | None = None,
    cmap: str | Colormap | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    data: Incomplete | None = None,
    **kwargs,
) -> Collection: ...
def pcolormesh(
    *args: ArrayLike,
    alpha: float | None = None,
    norm: str | Normalize | None = None,
    cmap: str | Colormap | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    shading: Literal["flat", "nearest", "gouraud", "auto"] | None = None,
    antialiased: bool = False,
    data: Incomplete | None = None,
    **kwargs,
) -> QuadMesh: ...
def phase_spectrum(
    x: ArrayLike,
    Fs: float | None = None,
    Fc: int | None = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, Line2D]: ...
def pie(
    x: ArrayLike,
    explode: ArrayLike | None = None,
    labels: Sequence[str] | None = None,
    colors: ColorType | Sequence[ColorType] | None = None,
    autopct: str | Callable[[float], str] | None = None,
    pctdistance: float = 0.6,
    shadow: bool = False,
    labeldistance: float | None = 1.1,
    startangle: float = 0,
    radius: float = 1,
    counterclock: bool = True,
    wedgeprops: dict[str, Any] | None = None,
    textprops: dict[str, Any] | None = None,
    center: tuple[float, float] = (0, 0),
    frame: bool = False,
    rotatelabels: bool = False,
    *,
    normalize: bool = True,
    hatch: str | Sequence[str] | None = None,
    data: Incomplete | None = None,
) -> tuple[list[Wedge], list[Text]] | tuple[list[Wedge], list[Text], list[Text]]: ...
def plot(
    *args: float | ArrayLike | str,
    scalex: bool = True,
    scaley: bool = True,
    data: Incomplete | None = None,
    **kwargs,
) -> list[Line2D]: ...
def plot_date(
    x: ArrayLike,
    y: ArrayLike,
    fmt: str = "o",
    tz: str | datetime.tzinfo | None = None,
    xdate: bool = True,
    ydate: bool = False,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> list[Line2D]: ...
def psd(
    x: ArrayLike,
    NFFT: int | None = None,
    Fs: float | None = None,
    Fc: int | None = None,
    detrend: (
        Literal["none", "mean", "linear"] | Callable[[ArrayLike], ArrayLike] | None
    ) = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    noverlap: int | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    scale_by_freq: bool | None = None,
    return_line: bool | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray] | tuple[np.ndarray, np.ndarray, Line2D]: ...
def quiver(*args, data: Incomplete | None = None, **kwargs) -> Quiver: ...
def quiverkey(
    Q: Quiver, X: float, Y: float, U: float, label: str, **kwargs
) -> QuiverKey: ...
def scatter(
    x: float | ArrayLike,
    y: float | ArrayLike,
    s: float | ArrayLike | None = None,
    c: ArrayLike | Sequence[ColorType] | ColorType | None = None,
    marker: MarkerType | None = None,
    cmap: str | Colormap | None = None,
    norm: str | Normalize | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    alpha: float | None = None,
    linewidths: float | Sequence[float] | None = None,
    *,
    edgecolors: Literal["face", "none"] | ColorType | Sequence[ColorType] | None = None,
    plotnonfinite: bool = False,
    data: Incomplete | None = None,
    **kwargs,
) -> PathCollection: ...
def semilogx(*args, **kwargs) -> list[Line2D]: ...
def semilogy(*args, **kwargs) -> list[Line2D]: ...
def specgram(
    x: ArrayLike,
    NFFT: int | None = None,
    Fs: float | None = None,
    Fc: int | None = None,
    detrend: (
        Literal["none", "mean", "linear"] | Callable[[ArrayLike], ArrayLike] | None
    ) = None,
    window: Callable[[ArrayLike], ArrayLike] | ArrayLike | None = None,
    noverlap: int | None = None,
    cmap: str | Colormap | None = None,
    xextent: tuple[float, float] | None = None,
    pad_to: int | None = None,
    sides: Literal["default", "onesided", "twosided"] | None = None,
    scale_by_freq: bool | None = None,
    mode: Literal["default", "psd", "magnitude", "angle", "phase"] | None = None,
    scale: Literal["default", "linear", "dB"] | None = None,
    vmin: float | None = None,
    vmax: float | None = None,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, AxesImage]: ...
def spy(
    Z: ArrayLike,
    precision: float | Literal["present"] = 0,
    marker: str | None = None,
    markersize: float | None = None,
    aspect: Literal["equal", "auto"] | float | None = "equal",
    origin: Literal["upper", "lower"] = "upper",
    **kwargs,
) -> AxesImage: ...
def stackplot(
    x,
    *args,
    labels=(),
    colors: Incomplete | None = None,
    hatch: Incomplete | None = None,
    baseline: str = "zero",
    data: Incomplete | None = None,
    **kwargs,
): ...
def stem(
    *args: ArrayLike | str,
    linefmt: str | None = None,
    markerfmt: str | None = None,
    basefmt: str | None = None,
    bottom: float = 0,
    label: str | None = None,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    data: Incomplete | None = None,
) -> StemContainer: ...
def step(
    x: ArrayLike,
    y: ArrayLike,
    *args,
    where: Literal["pre", "post", "mid"] = "pre",
    data: Incomplete | None = None,
    **kwargs,
) -> list[Line2D]: ...
def streamplot(
    x,
    y,
    u,
    v,
    density: int = 1,
    linewidth: Incomplete | None = None,
    color: Incomplete | None = None,
    cmap: Incomplete | None = None,
    norm: Incomplete | None = None,
    arrowsize: int = 1,
    arrowstyle: str = "-|>",
    minlength: float = 0.1,
    transform: Incomplete | None = None,
    zorder: Incomplete | None = None,
    start_points: Incomplete | None = None,
    maxlength: float = 4.0,
    integration_direction: str = "both",
    broken_streamlines: bool = True,
    *,
    data: Incomplete | None = None,
): ...
def table(
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
def text(
    x: float, y: float, s: str, fontdict: dict[str, Any] | None = None, **kwargs
) -> Text: ...
def tick_params(axis: Literal["both", "x", "y"] = "both", **kwargs) -> None: ...
def ticklabel_format(
    *,
    axis: Literal["both", "x", "y"] = "both",
    style: Literal["", "sci", "scientific", "plain"] | None = None,
    scilimits: tuple[int, int] | None = None,
    useOffset: bool | float | None = None,
    useLocale: bool | None = None,
    useMathText: bool | None = None,
) -> None: ...
def tricontour(*args, **kwargs): ...
def tricontourf(*args, **kwargs): ...
def tripcolor(
    *args,
    alpha: float = 1.0,
    norm: Incomplete | None = None,
    cmap: Incomplete | None = None,
    vmin: Incomplete | None = None,
    vmax: Incomplete | None = None,
    shading: str = "flat",
    facecolors: Incomplete | None = None,
    **kwargs,
): ...
def triplot(*args, **kwargs): ...
def violinplot(
    dataset: ArrayLike | Sequence[ArrayLike],
    positions: ArrayLike | None = None,
    vert: bool = True,
    widths: float | ArrayLike = 0.5,
    showmeans: bool = False,
    showextrema: bool = True,
    showmedians: bool = False,
    quantiles: Sequence[float | Sequence[float]] | None = None,
    points: int = 100,
    bw_method: (
        Literal["scott", "silverman"] | float | Callable[[GaussianKDE], float] | None
    ) = None,
    side: Literal["both", "low", "high"] = "both",
    *,
    data: Incomplete | None = None,
) -> dict[str, Collection]: ...
def vlines(
    x: float | ArrayLike,
    ymin: float | ArrayLike,
    ymax: float | ArrayLike,
    colors: ColorType | Sequence[ColorType] | None = None,
    linestyles: LineStyleType = "solid",
    label: str = "",
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> LineCollection: ...
def xcorr(
    x: ArrayLike,
    y: ArrayLike,
    normed: bool = True,
    detrend: Callable[[ArrayLike], ArrayLike] = ...,
    usevlines: bool = True,
    maxlags: int = 10,
    *,
    data: Incomplete | None = None,
    **kwargs,
) -> tuple[np.ndarray, np.ndarray, LineCollection | Line2D, Line2D | None]: ...
def sci(im: ScalarMappable) -> None: ...
def title(
    label: str,
    fontdict: dict[str, Any] | None = None,
    loc: Literal["left", "center", "right"] | None = None,
    pad: float | None = None,
    *,
    y: float | None = None,
    **kwargs,
) -> Text: ...
def xlabel(
    xlabel: str,
    fontdict: dict[str, Any] | None = None,
    labelpad: float | None = None,
    *,
    loc: Literal["left", "center", "right"] | None = None,
    **kwargs,
) -> Text: ...
def ylabel(
    ylabel: str,
    fontdict: dict[str, Any] | None = None,
    labelpad: float | None = None,
    *,
    loc: Literal["bottom", "center", "top"] | None = None,
    **kwargs,
) -> Text: ...
def xscale(value: str | ScaleBase, **kwargs) -> None: ...
def yscale(value: str | ScaleBase, **kwargs) -> None: ...
def autumn() -> None: ...
def bone() -> None: ...
def cool() -> None: ...
def copper() -> None: ...
def flag() -> None: ...
def gray() -> None: ...
def hot() -> None: ...
def hsv() -> None: ...
def jet() -> None: ...
def pink() -> None: ...
def prism() -> None: ...
def spring() -> None: ...
def summer() -> None: ...
def winter() -> None: ...
def magma() -> None: ...
def inferno() -> None: ...
def plasma() -> None: ...
def viridis() -> None: ...
def nipy_spectral() -> None: ...
