import matplotlib.axis as maxis
import matplotlib.ticker as mticker
import matplotlib.transforms as mtransforms
from _typeshed import Incomplete
from matplotlib import cbook as cbook
from matplotlib.axes import Axes as Axes
from matplotlib.path import Path as Path
from matplotlib.spines import Spine as Spine

class PolarTransform(mtransforms.Transform):
    input_dims: int
    output_dims: int
    def __init__(
        self,
        axis: Incomplete | None = None,
        use_rmin: bool = True,
        *,
        apply_theta_transforms: bool = True,
        scale_transform: Incomplete | None = None,
    ) -> None: ...
    def transform_non_affine(self, values): ...
    def transform_path_non_affine(self, path): ...
    def inverted(self): ...

class PolarAffine(mtransforms.Affine2DBase):
    def __init__(self, scale_transform, limits) -> None: ...
    def get_matrix(self): ...

class InvertedPolarTransform(mtransforms.Transform):
    input_dims: int
    output_dims: int
    def __init__(
        self,
        axis: Incomplete | None = None,
        use_rmin: bool = True,
        *,
        apply_theta_transforms: bool = True,
    ) -> None: ...
    def transform_non_affine(self, values): ...
    def inverted(self): ...

class ThetaFormatter(mticker.Formatter):
    def __call__(self, x, pos: Incomplete | None = None): ...

class _AxisWrapper:
    def __init__(self, axis) -> None: ...
    def get_view_interval(self): ...
    def set_view_interval(self, vmin, vmax) -> None: ...
    def get_minpos(self): ...
    def get_data_interval(self): ...
    def set_data_interval(self, vmin, vmax) -> None: ...
    def get_tick_space(self): ...

class ThetaLocator(mticker.Locator):
    base: Incomplete
    axis: Incomplete
    def __init__(self, base) -> None: ...
    def set_axis(self, axis) -> None: ...
    def __call__(self): ...
    def view_limits(self, vmin, vmax): ...

class ThetaTick(maxis.XTick):
    def __init__(self, axes, *args, **kwargs) -> None: ...
    def update_position(self, loc) -> None: ...

class ThetaAxis(maxis.XAxis):
    axis_name: str
    def clear(self) -> None: ...

class RadialLocator(mticker.Locator):
    base: Incomplete
    def __init__(self, base, axes: Incomplete | None = None) -> None: ...
    def set_axis(self, axis) -> None: ...
    def __call__(self): ...
    def nonsingular(self, vmin, vmax): ...
    def view_limits(self, vmin, vmax): ...

class _ThetaShift(mtransforms.ScaledTranslation):
    axes: Incomplete
    mode: Incomplete
    pad: Incomplete
    def __init__(self, axes, pad, mode) -> None: ...
    def get_matrix(self): ...

class RadialTick(maxis.YTick):
    def __init__(self, *args, **kwargs) -> None: ...
    def update_position(self, loc) -> None: ...

class RadialAxis(maxis.YAxis):
    axis_name: str
    def __init__(self, *args, **kwargs) -> None: ...
    def clear(self) -> None: ...

class _WedgeBbox(mtransforms.Bbox):
    def __init__(self, center, viewLim, originLim, **kwargs) -> None: ...
    def get_points(self): ...

class PolarAxes(Axes):
    name: str
    use_sticky_edges: bool
    def __init__(
        self,
        *args,
        theta_offset: int = 0,
        theta_direction: int = 1,
        rlabel_position: float = 22.5,
        **kwargs,
    ) -> None: ...
    def clear(self) -> None: ...
    def get_xaxis_transform(self, which: str = "grid"): ...
    def get_xaxis_text1_transform(self, pad): ...
    def get_xaxis_text2_transform(self, pad): ...
    def get_yaxis_transform(self, which: str = "grid"): ...
    def get_yaxis_text1_transform(self, pad): ...
    def get_yaxis_text2_transform(self, pad): ...
    def draw(self, renderer) -> None: ...
    def set_thetamax(self, thetamax) -> None: ...
    def get_thetamax(self): ...
    def set_thetamin(self, thetamin) -> None: ...
    def get_thetamin(self): ...
    def set_thetalim(self, *args, **kwargs): ...
    def set_theta_offset(self, offset) -> None: ...
    def get_theta_offset(self): ...
    def set_theta_zero_location(self, loc, offset: float = 0.0): ...
    def set_theta_direction(self, direction) -> None: ...
    def get_theta_direction(self): ...
    def set_rmax(self, rmax) -> None: ...
    def get_rmax(self): ...
    def set_rmin(self, rmin) -> None: ...
    def get_rmin(self): ...
    def set_rorigin(self, rorigin) -> None: ...
    def get_rorigin(self): ...
    def get_rsign(self): ...
    def set_rlim(
        self,
        bottom: Incomplete | None = None,
        top: Incomplete | None = None,
        *,
        emit: bool = True,
        auto: bool = False,
        **kwargs,
    ): ...
    def get_rlabel_position(self): ...
    def set_rlabel_position(self, value) -> None: ...
    def set_yscale(self, *args, **kwargs) -> None: ...
    def set_rscale(self, *args, **kwargs): ...
    def set_rticks(self, *args, **kwargs): ...
    def set_thetagrids(
        self,
        angles,
        labels: Incomplete | None = None,
        fmt: Incomplete | None = None,
        **kwargs,
    ): ...
    def set_rgrids(
        self,
        radii,
        labels: Incomplete | None = None,
        angle: Incomplete | None = None,
        fmt: Incomplete | None = None,
        **kwargs,
    ): ...
    def format_coord(self, theta, r): ...
    def get_data_ratio(self): ...
    def can_zoom(self): ...
    def can_pan(self): ...
    def start_pan(self, x, y, button) -> None: ...
    def end_pan(self) -> None: ...
    def drag_pan(self, button, key, x, y) -> None: ...
