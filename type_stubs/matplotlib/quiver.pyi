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
    def __init__(self, Q, X, Y, U, label, *, angle: int = ..., coordinates: str = ..., color: Incomplete | None = ..., labelsep: float = ..., labelpos: str = ..., labelcolor: Incomplete | None = ..., fontproperties: Incomplete | None = ..., **kwargs) -> None: ...
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
    def __init__(self, ax, *args, scale: Incomplete | None = ..., headwidth: int = ..., headlength: int = ..., headaxislength: float = ..., minshaft: int = ..., minlength: int = ..., units: str = ..., scale_units: Incomplete | None = ..., angles: str = ..., width: Incomplete | None = ..., color: str = ..., pivot: str = ..., **kwargs) -> None: ...
    def get_datalim(self, transData): ...
    stale: bool
    def draw(self, renderer) -> None: ...
    U: Incomplete
    V: Incomplete
    Umask: Incomplete
    def set_UVC(self, U, V, C: Incomplete | None = ...) -> None: ...
    quiver_doc: Incomplete

class Barbs(mcollections.PolyCollection):
    sizes: Incomplete
    fill_empty: Incomplete
    barb_increments: Incomplete
    rounding: Incomplete
    flip: Incomplete
    x: Incomplete
    y: Incomplete
    def __init__(self, ax, *args, pivot: str = ..., length: int = ..., barbcolor: Incomplete | None = ..., flagcolor: Incomplete | None = ..., sizes: Incomplete | None = ..., fill_empty: bool = ..., barb_increments: Incomplete | None = ..., rounding: bool = ..., flip_barb: bool = ..., **kwargs) -> None: ...
    u: Incomplete
    v: Incomplete
    stale: bool
    def set_UVC(self, U, V, C: Incomplete | None = ...) -> None: ...
    def set_offsets(self, xy) -> None: ...
    barbs_doc: Incomplete
