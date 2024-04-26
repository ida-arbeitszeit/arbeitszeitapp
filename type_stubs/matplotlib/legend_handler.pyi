from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.lines import Line2D as Line2D
from matplotlib.patches import Rectangle as Rectangle

def update_from_first_child(tgt, src) -> None: ...

class HandlerBase:
    def __init__(
        self,
        xpad: float = 0.0,
        ypad: float = 0.0,
        update_func: Incomplete | None = None,
    ) -> None: ...
    def update_prop(self, legend_handle, orig_handle, legend) -> None: ...
    def adjust_drawing_area(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize
    ): ...
    def legend_artist(self, legend, orig_handle, fontsize, handlebox): ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ) -> None: ...

class HandlerNpoints(HandlerBase):
    def __init__(
        self, marker_pad: float = 0.3, numpoints: Incomplete | None = None, **kwargs
    ) -> None: ...
    def get_numpoints(self, legend): ...
    def get_xdata(self, legend, xdescent, ydescent, width, height, fontsize): ...

class HandlerNpointsYoffsets(HandlerNpoints):
    def __init__(
        self,
        numpoints: Incomplete | None = None,
        yoffsets: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_ydata(self, legend, xdescent, ydescent, width, height, fontsize): ...

class HandlerLine2DCompound(HandlerNpoints):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerLine2D(HandlerNpoints):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerPatch(HandlerBase):
    def __init__(self, patch_func: Incomplete | None = None, **kwargs) -> None: ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerStepPatch(HandlerBase):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerLineCollection(HandlerLine2D):
    def get_numpoints(self, legend): ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerRegularPolyCollection(HandlerNpointsYoffsets):
    def __init__(
        self,
        yoffsets: Incomplete | None = None,
        sizes: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_numpoints(self, legend): ...
    def get_sizes(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize
    ): ...
    def update_prop(self, legend_handle, orig_handle, legend) -> None: ...
    def create_collection(self, orig_handle, sizes, offsets, offset_transform): ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerPathCollection(HandlerRegularPolyCollection):
    def create_collection(self, orig_handle, sizes, offsets, offset_transform): ...

class HandlerCircleCollection(HandlerRegularPolyCollection):
    def create_collection(self, orig_handle, sizes, offsets, offset_transform): ...

class HandlerErrorbar(HandlerLine2D):
    def __init__(
        self,
        xerr_size: float = 0.5,
        yerr_size: Incomplete | None = None,
        marker_pad: float = 0.3,
        numpoints: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_err_size(self, legend, xdescent, ydescent, width, height, fontsize): ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerStem(HandlerNpointsYoffsets):
    def __init__(
        self,
        marker_pad: float = 0.3,
        numpoints: Incomplete | None = None,
        bottom: Incomplete | None = None,
        yoffsets: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_ydata(self, legend, xdescent, ydescent, width, height, fontsize): ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerTuple(HandlerBase):
    def __init__(
        self, ndivide: int = 1, pad: Incomplete | None = None, **kwargs
    ) -> None: ...
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...

class HandlerPolyCollection(HandlerBase):
    def create_artists(
        self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans
    ): ...
