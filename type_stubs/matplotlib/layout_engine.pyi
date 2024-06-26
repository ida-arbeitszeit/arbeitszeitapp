from _typeshed import Incomplete
from matplotlib._constrained_layout import (
    do_constrained_layout as do_constrained_layout,
)
from matplotlib._tight_layout import get_subplotspec_list as get_subplotspec_list
from matplotlib._tight_layout import get_tight_layout_figure as get_tight_layout_figure

class LayoutEngine:
    def __init__(self, **kwargs) -> None: ...
    def set(self, **kwargs) -> None: ...
    @property
    def colorbar_gridspec(self): ...
    @property
    def adjust_compatible(self): ...
    def get(self): ...
    def execute(self, fig) -> None: ...

class PlaceHolderLayoutEngine(LayoutEngine):
    def __init__(self, adjust_compatible, colorbar_gridspec, **kwargs) -> None: ...
    def execute(self, fig) -> None: ...

class TightLayoutEngine(LayoutEngine):
    def __init__(
        self,
        *,
        pad: float = 1.08,
        h_pad: Incomplete | None = None,
        w_pad: Incomplete | None = None,
        rect=(0, 0, 1, 1),
        **kwargs,
    ) -> None: ...
    def execute(self, fig) -> None: ...
    def set(
        self,
        *,
        pad: Incomplete | None = None,
        w_pad: Incomplete | None = None,
        h_pad: Incomplete | None = None,
        rect: Incomplete | None = None,
    ) -> None: ...

class ConstrainedLayoutEngine(LayoutEngine):
    def __init__(
        self,
        *,
        h_pad: Incomplete | None = None,
        w_pad: Incomplete | None = None,
        hspace: Incomplete | None = None,
        wspace: Incomplete | None = None,
        rect=(0, 0, 1, 1),
        compress: bool = False,
        **kwargs,
    ) -> None: ...
    def execute(self, fig): ...
    def set(
        self,
        *,
        h_pad: Incomplete | None = None,
        w_pad: Incomplete | None = None,
        hspace: Incomplete | None = None,
        wspace: Incomplete | None = None,
        rect: Incomplete | None = None,
    ) -> None: ...
