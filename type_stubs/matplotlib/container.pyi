from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.artist import Artist as Artist

class Container(tuple):
    def __new__(cls, *args, **kwargs): ...
    def __init__(self, kl, label: Incomplete | None = None) -> None: ...
    def remove(self): ...
    def get_children(self): ...
    get_label: Incomplete
    set_label: Incomplete
    add_callback: Incomplete
    remove_callback: Incomplete
    pchanged: Incomplete

class BarContainer(Container):
    patches: Incomplete
    errorbar: Incomplete
    datavalues: Incomplete
    orientation: Incomplete
    def __init__(
        self,
        patches,
        errorbar: Incomplete | None = None,
        *,
        datavalues: Incomplete | None = None,
        orientation: Incomplete | None = None,
        **kwargs,
    ) -> None: ...

class ErrorbarContainer(Container):
    lines: Incomplete
    has_xerr: Incomplete
    has_yerr: Incomplete
    def __init__(
        self, lines, has_xerr: bool = False, has_yerr: bool = False, **kwargs
    ) -> None: ...

class StemContainer(Container):
    markerline: Incomplete
    stemlines: Incomplete
    baseline: Incomplete
    def __init__(self, markerline_stemlines_baseline, **kwargs) -> None: ...
