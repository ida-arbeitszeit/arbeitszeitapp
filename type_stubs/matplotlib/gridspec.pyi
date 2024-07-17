from _typeshed import Incomplete
from matplotlib.transforms import Bbox as Bbox

class GridSpecBase:
    def __init__(
        self,
        nrows,
        ncols,
        height_ratios: Incomplete | None = None,
        width_ratios: Incomplete | None = None,
    ) -> None: ...
    nrows: Incomplete
    ncols: Incomplete
    def get_geometry(self): ...
    def get_subplot_params(self, figure: Incomplete | None = None) -> None: ...
    def new_subplotspec(self, loc, rowspan: int = 1, colspan: int = 1): ...
    def set_width_ratios(self, width_ratios) -> None: ...
    def get_width_ratios(self): ...
    def set_height_ratios(self, height_ratios) -> None: ...
    def get_height_ratios(self): ...
    def get_grid_positions(self, fig): ...
    def __getitem__(self, key): ...
    def subplots(
        self,
        *,
        sharex: bool = False,
        sharey: bool = False,
        squeeze: bool = True,
        subplot_kw: Incomplete | None = None,
    ): ...

class GridSpec(GridSpecBase):
    left: Incomplete
    bottom: Incomplete
    right: Incomplete
    top: Incomplete
    wspace: Incomplete
    hspace: Incomplete
    figure: Incomplete
    def __init__(
        self,
        nrows,
        ncols,
        figure: Incomplete | None = None,
        left: Incomplete | None = None,
        bottom: Incomplete | None = None,
        right: Incomplete | None = None,
        top: Incomplete | None = None,
        wspace: Incomplete | None = None,
        hspace: Incomplete | None = None,
        width_ratios: Incomplete | None = None,
        height_ratios: Incomplete | None = None,
    ) -> None: ...
    def update(self, **kwargs) -> None: ...
    def get_subplot_params(self, figure: Incomplete | None = None): ...
    def locally_modified_subplot_params(self): ...
    def tight_layout(
        self,
        figure,
        renderer: Incomplete | None = None,
        pad: float = 1.08,
        h_pad: Incomplete | None = None,
        w_pad: Incomplete | None = None,
        rect: Incomplete | None = None,
    ) -> None: ...

class GridSpecFromSubplotSpec(GridSpecBase):
    figure: Incomplete
    def __init__(
        self,
        nrows,
        ncols,
        subplot_spec,
        wspace: Incomplete | None = None,
        hspace: Incomplete | None = None,
        height_ratios: Incomplete | None = None,
        width_ratios: Incomplete | None = None,
    ) -> None: ...
    def get_subplot_params(self, figure: Incomplete | None = None): ...
    def get_topmost_subplotspec(self): ...

class SubplotSpec:
    num1: Incomplete
    def __init__(self, gridspec, num1, num2: Incomplete | None = None) -> None: ...
    @property
    def num2(self): ...
    @num2.setter
    def num2(self, value) -> None: ...
    def get_gridspec(self): ...
    def get_geometry(self): ...
    @property
    def rowspan(self): ...
    @property
    def colspan(self): ...
    def is_first_row(self): ...
    def is_last_row(self): ...
    def is_first_col(self): ...
    def is_last_col(self): ...
    def get_position(self, figure): ...
    def get_topmost_subplotspec(self): ...
    def __eq__(self, other): ...
    def __hash__(self): ...
    def subgridspec(self, nrows, ncols, **kwargs): ...

class SubplotParams:
    def __init__(
        self,
        left: Incomplete | None = None,
        bottom: Incomplete | None = None,
        right: Incomplete | None = None,
        top: Incomplete | None = None,
        wspace: Incomplete | None = None,
        hspace: Incomplete | None = None,
    ) -> None: ...
    left: Incomplete
    right: Incomplete
    bottom: Incomplete
    top: Incomplete
    wspace: Incomplete
    hspace: Incomplete
    def update(
        self,
        left: Incomplete | None = None,
        bottom: Incomplete | None = None,
        right: Incomplete | None = None,
        top: Incomplete | None = None,
        wspace: Incomplete | None = None,
        hspace: Incomplete | None = None,
    ) -> None: ...
