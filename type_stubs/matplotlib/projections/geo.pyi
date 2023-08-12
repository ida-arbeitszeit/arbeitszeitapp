from _typeshed import Incomplete
from matplotlib.axes import Axes as Axes
from matplotlib.patches import Circle as Circle
from matplotlib.path import Path as Path
from matplotlib.ticker import FixedLocator as FixedLocator, Formatter as Formatter, NullFormatter as NullFormatter, NullLocator as NullLocator
from matplotlib.transforms import Affine2D as Affine2D, BboxTransformTo as BboxTransformTo, Transform as Transform

class GeoAxes(Axes):
    class ThetaFormatter(Formatter):
        def __init__(self, round_to: float = ...) -> None: ...
        def __call__(self, x, pos: Incomplete | None = ...): ...
    RESOLUTION: int
    def clear(self) -> None: ...
    def get_xaxis_transform(self, which: str = ...): ...
    def get_xaxis_text1_transform(self, pad): ...
    def get_xaxis_text2_transform(self, pad): ...
    def get_yaxis_transform(self, which: str = ...): ...
    def get_yaxis_text1_transform(self, pad): ...
    def get_yaxis_text2_transform(self, pad): ...
    def set_yscale(self, *args, **kwargs) -> None: ...
    set_xscale = set_yscale
    def set_xlim(self, *args, **kwargs) -> None: ...
    set_ylim = set_xlim
    def format_coord(self, lon, lat): ...
    def set_longitude_grid(self, degrees) -> None: ...
    def set_latitude_grid(self, degrees) -> None: ...
    def set_longitude_grid_ends(self, degrees) -> None: ...
    def get_data_ratio(self): ...
    def can_zoom(self): ...
    def can_pan(self): ...
    def start_pan(self, x, y, button) -> None: ...
    def end_pan(self) -> None: ...
    def drag_pan(self, button, key, x, y) -> None: ...

class _GeoTransform(Transform):
    input_dims: int
    output_dims: int
    def __init__(self, resolution) -> None: ...
    def transform_path_non_affine(self, path): ...

class AitoffAxes(GeoAxes):
    name: str
    class AitoffTransform(_GeoTransform):
        def transform_non_affine(self, ll): ...
        def inverted(self): ...
    class InvertedAitoffTransform(_GeoTransform):
        def transform_non_affine(self, xy): ...
        def inverted(self): ...
    def __init__(self, *args, **kwargs) -> None: ...

class HammerAxes(GeoAxes):
    name: str
    class HammerTransform(_GeoTransform):
        def transform_non_affine(self, ll): ...
        def inverted(self): ...
    class InvertedHammerTransform(_GeoTransform):
        def transform_non_affine(self, xy): ...
        def inverted(self): ...
    def __init__(self, *args, **kwargs) -> None: ...

class MollweideAxes(GeoAxes):
    name: str
    class MollweideTransform(_GeoTransform):
        def transform_non_affine(self, ll): ...
        def inverted(self): ...
    class InvertedMollweideTransform(_GeoTransform):
        def transform_non_affine(self, xy): ...
        def inverted(self): ...
    def __init__(self, *args, **kwargs) -> None: ...

class LambertAxes(GeoAxes):
    name: str
    class LambertTransform(_GeoTransform):
        def __init__(self, center_longitude, center_latitude, resolution) -> None: ...
        def transform_non_affine(self, ll): ...
        def inverted(self): ...
    class InvertedLambertTransform(_GeoTransform):
        def __init__(self, center_longitude, center_latitude, resolution) -> None: ...
        def transform_non_affine(self, xy): ...
        def inverted(self): ...
    def __init__(self, *args, center_longitude: int = ..., center_latitude: int = ..., **kwargs) -> None: ...
    def clear(self) -> None: ...
