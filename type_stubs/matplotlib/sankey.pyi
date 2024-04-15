from _typeshed import Incomplete
from matplotlib.patches import PathPatch as PathPatch
from matplotlib.path import Path as Path
from matplotlib.transforms import Affine2D as Affine2D

__credits__: Incomplete
__version__: str
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
    def __init__(
        self,
        ax: Incomplete | None = None,
        scale: float = 1.0,
        unit: str = "",
        format: str = "%G",
        gap: float = 0.25,
        radius: float = 0.1,
        shoulder: float = 0.03,
        offset: float = 0.15,
        head_angle: int = 100,
        margin: float = 0.4,
        tolerance: float = 1e-06,
        **kwargs,
    ) -> None: ...
    def add(
        self,
        patchlabel: str = "",
        flows: Incomplete | None = None,
        orientations: Incomplete | None = None,
        labels: str = "",
        trunklength: float = 1.0,
        pathlengths: float = 0.25,
        prior: Incomplete | None = None,
        connect=(0, 0),
        rotation: int = 0,
        **kwargs,
    ): ...
    def finish(self): ...
