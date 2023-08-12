from _typeshed import Incomplete
from matplotlib.patches import PathPatch as PathPatch
from matplotlib.path import Path as Path
from matplotlib.transforms import Affine2D as Affine2D

__credits__: Incomplete
RIGHT: int
UP: int
DOWN: int

class Sankey:
    diagrams: Incomplete
    ax: Incomplete
    unit: Incomplete
    format: Incomplete
    scale: Incomplete
    gap: Incomplete
    radius: Incomplete
    shoulder: Incomplete
    offset: Incomplete
    margin: Incomplete
    pitch: Incomplete
    tolerance: Incomplete
    extent: Incomplete
    def __init__(self, ax: Incomplete | None = ..., scale: float = ..., unit: str = ..., format: str = ..., gap: float = ..., radius: float = ..., shoulder: float = ..., offset: float = ..., head_angle: int = ..., margin: float = ..., tolerance: float = ..., **kwargs) -> None: ...
    def add(self, patchlabel: str = ..., flows: Incomplete | None = ..., orientations: Incomplete | None = ..., labels: str = ..., trunklength: float = ..., pathlengths: float = ..., prior: Incomplete | None = ..., connect=..., rotation: int = ..., **kwargs): ...
    def finish(self): ...
