from _typeshed import Incomplete

__all__ = ["streamplot"]

def streamplot(
    axes,
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
): ...

class StreamplotSet:
    lines: Incomplete
    arrows: Incomplete
    def __init__(self, lines, arrows) -> None: ...

class DomainMap:
    grid: Incomplete
    mask: Incomplete
    x_grid2mask: Incomplete
    y_grid2mask: Incomplete
    x_mask2grid: Incomplete
    y_mask2grid: Incomplete
    x_data2grid: Incomplete
    y_data2grid: Incomplete
    def __init__(self, grid, mask) -> None: ...
    def grid2mask(self, xi, yi): ...
    def mask2grid(self, xm, ym): ...
    def data2grid(self, xd, yd): ...
    def grid2data(self, xg, yg): ...
    def start_trajectory(self, xg, yg, broken_streamlines: bool = True) -> None: ...
    def reset_start_point(self, xg, yg) -> None: ...
    def update_trajectory(self, xg, yg, broken_streamlines: bool = True) -> None: ...
    def undo_trajectory(self) -> None: ...

class Grid:
    nx: Incomplete
    ny: Incomplete
    dx: Incomplete
    dy: Incomplete
    x_origin: Incomplete
    y_origin: Incomplete
    width: Incomplete
    height: Incomplete
    def __init__(self, x, y) -> None: ...
    @property
    def shape(self): ...
    def within_grid(self, xi, yi): ...

class StreamMask:
    shape: Incomplete
    def __init__(self, density) -> None: ...
    def __getitem__(self, args): ...

class InvalidIndexError(Exception): ...
class TerminateTrajectory(Exception): ...
class OutOfBounds(IndexError): ...
