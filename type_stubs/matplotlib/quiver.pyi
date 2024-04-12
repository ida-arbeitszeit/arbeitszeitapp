import matplotlib.artist as martist
import matplotlib.collections as mcollections
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.patches import CirclePolygon as CirclePolygon

class QuiverKey(martist.Artist):
    halign: Incomplete
    valign: Incomplete
    pivot: Incomplete
    Q: Incomplete
    X: Incomplete
    Y: Incomplete
    U: Incomplete
    angle: Incomplete
    coord: Incomplete
    color: Incomplete
    label: Incomplete
    labelpos: Incomplete
    labelcolor: Incomplete
    fontproperties: Incomplete
    kw: Incomplete
    text: Incomplete
    zorder: Incomplete
    def __init__(
        self,
        Q,
        X,
        Y,
        U,
        label,
        *,
        angle: int = 0,
        coordinates: str = "axes",
        color: Incomplete | None = None,
        labelsep: float = 0.1,
        labelpos: str = "N",
        labelcolor: Incomplete | None = None,
        fontproperties: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    @property
    def labelsep(self): ...
    stale: bool
    def draw(self, renderer) -> None: ...
    def set_figure(self, fig) -> None: ...
    def contains(self, mouseevent): ...

class Quiver(mcollections.PolyCollection):
    X: Incomplete
    Y: Incomplete
    XY: Incomplete
    N: Incomplete
    scale: Incomplete
    headwidth: Incomplete
    headlength: Incomplete
    headaxislength: Incomplete
    minshaft: Incomplete
    minlength: Incomplete
    units: Incomplete
    scale_units: Incomplete
    angles: Incomplete
    width: Incomplete
    pivot: Incomplete
    transform: Incomplete
    polykw: Incomplete
    def __init__(
        self,
        ax,
        *args,
        scale: Incomplete | None = None,
        headwidth: int = 3,
        headlength: int = 5,
        headaxislength: float = 4.5,
        minshaft: int = 1,
        minlength: int = 1,
        units: str = "width",
        scale_units: Incomplete | None = None,
        angles: str = "uv",
        width: Incomplete | None = None,
        color: str = "k",
        pivot: str = "tail",
        **kwargs,
    ) -> None: ...
    def get_datalim(self, transData): ...
    stale: bool
    def draw(self, renderer) -> None: ...
    U: Incomplete
    V: Incomplete
    Umask: Incomplete
    def set_UVC(self, U, V, C: Incomplete | None = None) -> None: ...
    quiver_doc: Incomplete

class Barbs(mcollections.PolyCollection):
    sizes: Incomplete
    fill_empty: Incomplete
    barb_increments: Incomplete
    rounding: Incomplete
    flip: Incomplete
    x: Incomplete
    y: Incomplete
    def __init__(
        self,
        ax,
        *args,
        pivot: str = "tip",
        length: int = 7,
        barbcolor: Incomplete | None = None,
        flagcolor: Incomplete | None = None,
        sizes: Incomplete | None = None,
        fill_empty: bool = False,
        barb_increments: Incomplete | None = None,
        rounding: bool = True,
        flip_barb: bool = False,
        **kwargs,
    ) -> None: ...
    u: Incomplete
    v: Incomplete
    stale: bool
    def set_UVC(self, U, V, C: Incomplete | None = None) -> None: ...
    def set_offsets(self, xy) -> None: ...
    barbs_doc: Incomplete
