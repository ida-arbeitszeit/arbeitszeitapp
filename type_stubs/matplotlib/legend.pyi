from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib import colors as colors
from matplotlib import offsetbox as offsetbox
from matplotlib.artist import Artist as Artist
from matplotlib.artist import allow_rasterization as allow_rasterization
from matplotlib.cbook import silent_list as silent_list
from matplotlib.collections import CircleCollection as CircleCollection
from matplotlib.collections import Collection as Collection
from matplotlib.collections import LineCollection as LineCollection
from matplotlib.collections import PathCollection as PathCollection
from matplotlib.collections import PolyCollection as PolyCollection
from matplotlib.collections import RegularPolyCollection as RegularPolyCollection
from matplotlib.container import BarContainer as BarContainer
from matplotlib.container import ErrorbarContainer as ErrorbarContainer
from matplotlib.container import StemContainer as StemContainer
from matplotlib.font_manager import FontProperties as FontProperties
from matplotlib.lines import Line2D as Line2D
from matplotlib.offsetbox import AnchoredOffsetbox as AnchoredOffsetbox
from matplotlib.offsetbox import DraggableOffsetBox as DraggableOffsetBox
from matplotlib.offsetbox import DrawingArea as DrawingArea
from matplotlib.offsetbox import HPacker as HPacker
from matplotlib.offsetbox import TextArea as TextArea
from matplotlib.offsetbox import VPacker as VPacker
from matplotlib.patches import FancyBboxPatch as FancyBboxPatch
from matplotlib.patches import Patch as Patch
from matplotlib.patches import Rectangle as Rectangle
from matplotlib.patches import Shadow as Shadow
from matplotlib.patches import StepPatch as StepPatch
from matplotlib.text import Text as Text
from matplotlib.transforms import Bbox as Bbox
from matplotlib.transforms import BboxBase as BboxBase
from matplotlib.transforms import BboxTransformFrom as BboxTransformFrom
from matplotlib.transforms import BboxTransformTo as BboxTransformTo
from matplotlib.transforms import TransformedBbox as TransformedBbox

from . import legend_handler as legend_handler

class DraggableLegend(DraggableOffsetBox):
    legend: Incomplete
    def __init__(self, legend, use_blit: bool = False, update: str = "loc") -> None: ...
    def finalize_offset(self) -> None: ...

class Legend(Artist):
    codes: Incomplete
    zorder: int
    prop: Incomplete
    texts: Incomplete
    legend_handles: Incomplete
    numpoints: Incomplete
    markerscale: Incomplete
    scatterpoints: Incomplete
    borderpad: Incomplete
    labelspacing: Incomplete
    handlelength: Incomplete
    handleheight: Incomplete
    handletextpad: Incomplete
    borderaxespad: Incomplete
    columnspacing: Incomplete
    shadow: Incomplete
    isaxes: bool
    axes: Incomplete
    parent: Incomplete
    legendPatch: Incomplete
    def __init__(
        self,
        parent,
        handles,
        labels,
        *,
        loc: Incomplete | None = None,
        numpoints: Incomplete | None = None,
        markerscale: Incomplete | None = None,
        markerfirst: bool = True,
        reverse: bool = False,
        scatterpoints: Incomplete | None = None,
        scatteryoffsets: Incomplete | None = None,
        prop: Incomplete | None = None,
        fontsize: Incomplete | None = None,
        labelcolor: Incomplete | None = None,
        borderpad: Incomplete | None = None,
        labelspacing: Incomplete | None = None,
        handlelength: Incomplete | None = None,
        handleheight: Incomplete | None = None,
        handletextpad: Incomplete | None = None,
        borderaxespad: Incomplete | None = None,
        columnspacing: Incomplete | None = None,
        ncols: int = 1,
        mode: Incomplete | None = None,
        fancybox: Incomplete | None = None,
        shadow: Incomplete | None = None,
        title: Incomplete | None = None,
        title_fontsize: Incomplete | None = None,
        framealpha: Incomplete | None = None,
        edgecolor: Incomplete | None = None,
        facecolor: Incomplete | None = None,
        bbox_to_anchor: Incomplete | None = None,
        bbox_transform: Incomplete | None = None,
        frameon: Incomplete | None = None,
        handler_map: Incomplete | None = None,
        title_fontproperties: Incomplete | None = None,
        alignment: str = "center",
        ncol: int = 1,
        draggable: bool = False,
    ) -> None: ...
    def set_loc(self, loc: Incomplete | None = None) -> None: ...
    def set_ncols(self, ncols) -> None: ...
    stale: bool
    def draw(self, renderer) -> None: ...
    @classmethod
    def get_default_handler_map(cls): ...
    @classmethod
    def set_default_handler_map(cls, handler_map) -> None: ...
    @classmethod
    def update_default_handler_map(cls, handler_map) -> None: ...
    def get_legend_handler_map(self): ...
    @staticmethod
    def get_legend_handler(legend_handler_map, orig_handle): ...
    def get_children(self): ...
    def get_frame(self): ...
    def get_lines(self): ...
    def get_patches(self): ...
    def get_texts(self): ...
    def set_alignment(self, alignment) -> None: ...
    def get_alignment(self): ...
    def set_title(self, title, prop: Incomplete | None = None) -> None: ...
    def get_title(self): ...
    def get_window_extent(self, renderer: Incomplete | None = None): ...
    def get_tightbbox(self, renderer: Incomplete | None = None): ...
    def get_frame_on(self): ...
    def set_frame_on(self, b) -> None: ...
    draw_frame = set_frame_on
    def get_bbox_to_anchor(self): ...
    def set_bbox_to_anchor(self, bbox, transform: Incomplete | None = None) -> None: ...
    def contains(self, mouseevent): ...
    def set_draggable(self, state, use_blit: bool = False, update: str = "loc"): ...
    def get_draggable(self): ...
