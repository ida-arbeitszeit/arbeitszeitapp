from _typeshed import Incomplete
from matplotlib._path import affine_transform as affine_transform
from matplotlib._path import (
    count_bboxes_overlapping_bbox as count_bboxes_overlapping_bbox,
)
from matplotlib._path import update_path_extents as update_path_extents

from .path import Path as Path

DEBUG: bool

class TransformNode:
    INVALID_NON_AFFINE: Incomplete
    INVALID_AFFINE: Incomplete
    INVALID: Incomplete
    is_affine: bool
    is_bbox: Incomplete
    pass_through: bool
    def __init__(self, shorthand_name: Incomplete | None = None) -> None: ...
    def __copy__(self): ...
    def invalidate(self): ...
    def set_children(self, *children): ...
    def frozen(self): ...

class BboxBase(TransformNode):
    is_bbox: Incomplete
    is_affine: bool
    def frozen(self): ...
    def __array__(self, *args, **kwargs): ...
    @property
    def x0(self): ...
    @property
    def y0(self): ...
    @property
    def x1(self): ...
    @property
    def y1(self): ...
    @property
    def p0(self): ...
    @property
    def p1(self): ...
    @property
    def xmin(self): ...
    @property
    def ymin(self): ...
    @property
    def xmax(self): ...
    @property
    def ymax(self): ...
    @property
    def min(self): ...
    @property
    def max(self): ...
    @property
    def intervalx(self): ...
    @property
    def intervaly(self): ...
    @property
    def width(self): ...
    @property
    def height(self): ...
    @property
    def size(self): ...
    @property
    def bounds(self): ...
    @property
    def extents(self): ...
    def get_points(self) -> None: ...
    def containsx(self, x): ...
    def containsy(self, y): ...
    def contains(self, x, y): ...
    def overlaps(self, other): ...
    def fully_containsx(self, x): ...
    def fully_containsy(self, y): ...
    def fully_contains(self, x, y): ...
    def fully_overlaps(self, other): ...
    def transformed(self, transform): ...
    coefs: Incomplete
    def anchored(self, c, container: Incomplete | None = None): ...
    def shrunk(self, mx, my): ...
    def shrunk_to_aspect(
        self, box_aspect, container: Incomplete | None = None, fig_aspect: float = 1.0
    ): ...
    def splitx(self, *args): ...
    def splity(self, *args): ...
    def count_contains(self, vertices): ...
    def count_overlaps(self, bboxes): ...
    def expanded(self, sw, sh): ...
    def padded(self, w_pad, h_pad: Incomplete | None = None): ...
    def translated(self, tx, ty): ...
    def corners(self): ...
    def rotated(self, radians): ...
    @staticmethod
    def union(bboxes): ...
    @staticmethod
    def intersection(bbox1, bbox2): ...

class Bbox(BboxBase):
    def __init__(self, points, **kwargs) -> None: ...
    ___init__ = __init__
    def __init__(self, points, **kwargs) -> None: ...
    def invalidate(self) -> None: ...
    def frozen(self): ...
    @staticmethod
    def unit(): ...
    @staticmethod
    def null(): ...
    @staticmethod
    def from_bounds(x0, y0, width, height): ...
    @staticmethod
    def from_extents(*args, minpos: Incomplete | None = None): ...
    def __format__(self, fmt) -> str: ...
    def ignore(self, value) -> None: ...
    def update_from_path(
        self,
        path,
        ignore: Incomplete | None = None,
        updatex: bool = True,
        updatey: bool = True,
    ) -> None: ...
    def update_from_data_x(self, x, ignore: Incomplete | None = None) -> None: ...
    def update_from_data_y(self, y, ignore: Incomplete | None = None) -> None: ...
    def update_from_data_xy(
        self,
        xy,
        ignore: Incomplete | None = None,
        updatex: bool = True,
        updatey: bool = True,
    ) -> None: ...
    @BboxBase.x0.setter
    def x0(self, val) -> None: ...
    @BboxBase.y0.setter
    def y0(self, val) -> None: ...
    @BboxBase.x1.setter
    def x1(self, val) -> None: ...
    @BboxBase.y1.setter
    def y1(self, val) -> None: ...
    @BboxBase.p0.setter
    def p0(self, val) -> None: ...
    @BboxBase.p1.setter
    def p1(self, val) -> None: ...
    @BboxBase.intervalx.setter
    def intervalx(self, interval) -> None: ...
    @BboxBase.intervaly.setter
    def intervaly(self, interval) -> None: ...
    @BboxBase.bounds.setter
    def bounds(self, bounds) -> None: ...
    @property
    def minpos(self): ...
    @minpos.setter
    def minpos(self, val) -> None: ...
    @property
    def minposx(self): ...
    @minposx.setter
    def minposx(self, val) -> None: ...
    @property
    def minposy(self): ...
    @minposy.setter
    def minposy(self, val) -> None: ...
    def get_points(self): ...
    def set_points(self, points) -> None: ...
    def set(self, other) -> None: ...
    def mutated(self): ...
    def mutatedx(self): ...
    def mutatedy(self): ...

class TransformedBbox(BboxBase):
    def __init__(self, bbox, transform, **kwargs) -> None: ...
    def get_points(self): ...
    def get_points(self): ...
    def contains(self, x, y): ...
    def fully_contains(self, x, y): ...

class LockableBbox(BboxBase):
    def __init__(
        self,
        bbox,
        x0: Incomplete | None = None,
        y0: Incomplete | None = None,
        x1: Incomplete | None = None,
        y1: Incomplete | None = None,
        **kwargs,
    ) -> None: ...
    def get_points(self): ...
    def get_points(self): ...
    @property
    def locked_x0(self): ...
    @locked_x0.setter
    def locked_x0(self, x0) -> None: ...
    @property
    def locked_y0(self): ...
    @locked_y0.setter
    def locked_y0(self, y0) -> None: ...
    @property
    def locked_x1(self): ...
    @locked_x1.setter
    def locked_x1(self, x1) -> None: ...
    @property
    def locked_y1(self): ...
    @locked_y1.setter
    def locked_y1(self, y1) -> None: ...

class Transform(TransformNode):
    input_dims: Incomplete
    output_dims: Incomplete
    is_separable: bool
    has_inverse: bool
    def __init_subclass__(cls) -> None: ...
    def __add__(self, other): ...
    @property
    def depth(self): ...
    def contains_branch(self, other): ...
    def contains_branch_seperately(self, other_transform): ...
    def __sub__(self, other): ...
    def __array__(self, *args, **kwargs): ...
    def transform(self, values): ...
    def transform_affine(self, values): ...
    def transform_non_affine(self, values): ...
    def transform_bbox(self, bbox): ...
    def get_affine(self): ...
    def get_matrix(self): ...
    def transform_point(self, point): ...
    def transform_path(self, path): ...
    def transform_path_affine(self, path): ...
    def transform_path_non_affine(self, path): ...
    def transform_angles(
        self, angles, pts, radians: bool = False, pushoff: float = 1e-05
    ): ...
    def inverted(self) -> None: ...

class TransformWrapper(Transform):
    pass_through: bool
    def __init__(self, child) -> None: ...
    def __eq__(self, other): ...
    def frozen(self): ...
    transform: Incomplete
    transform_affine: Incomplete
    transform_non_affine: Incomplete
    transform_path: Incomplete
    transform_path_affine: Incomplete
    transform_path_non_affine: Incomplete
    get_affine: Incomplete
    inverted: Incomplete
    get_matrix: Incomplete
    def set(self, child) -> None: ...
    input_dims: Incomplete
    output_dims: Incomplete
    is_affine: Incomplete
    is_separable: Incomplete
    has_inverse: Incomplete

class AffineBase(Transform):
    is_affine: bool
    def __init__(self, *args, **kwargs) -> None: ...
    def __array__(self, *args, **kwargs): ...
    def __eq__(self, other): ...
    def transform(self, values): ...
    def transform_affine(self, values) -> None: ...
    def transform_non_affine(self, values): ...
    def transform_path(self, path): ...
    def transform_path_affine(self, path): ...
    def transform_path_non_affine(self, path): ...
    def get_affine(self): ...

class Affine2DBase(AffineBase):
    input_dims: int
    output_dims: int
    def frozen(self): ...
    @property
    def is_separable(self): ...
    def to_values(self): ...
    def transform_affine(self, values): ...
    def transform_affine(self, values): ...
    def inverted(self): ...

class Affine2D(Affine2DBase):
    def __init__(self, matrix: Incomplete | None = None, **kwargs) -> None: ...
    @staticmethod
    def from_values(a, b, c, d, e, f): ...
    def get_matrix(self): ...
    def set_matrix(self, mtx) -> None: ...
    def set(self, other) -> None: ...
    def clear(self): ...
    def rotate(self, theta): ...
    def rotate_deg(self, degrees): ...
    def rotate_around(self, x, y, theta): ...
    def rotate_deg_around(self, x, y, degrees): ...
    def translate(self, tx, ty): ...
    def scale(self, sx, sy: Incomplete | None = None): ...
    def skew(self, xShear, yShear): ...
    def skew_deg(self, xShear, yShear): ...

class IdentityTransform(Affine2DBase):
    def frozen(self): ...
    def get_matrix(self): ...
    def transform(self, values): ...
    def transform_affine(self, values): ...
    def transform_non_affine(self, values): ...
    def transform_path(self, path): ...
    def transform_path_affine(self, path): ...
    def transform_path_non_affine(self, path): ...
    def get_affine(self): ...
    def inverted(self): ...

class _BlendedMixin:
    def __eq__(self, other): ...
    def contains_branch_seperately(self, transform): ...

class BlendedGenericTransform(_BlendedMixin, Transform):
    input_dims: int
    output_dims: int
    is_separable: bool
    pass_through: bool
    def __init__(self, x_transform, y_transform, **kwargs) -> None: ...
    @property
    def depth(self): ...
    def contains_branch(self, other): ...
    is_affine: Incomplete
    has_inverse: Incomplete
    def frozen(self): ...
    def transform_non_affine(self, values): ...
    def inverted(self): ...
    def get_affine(self): ...

class BlendedAffine2D(_BlendedMixin, Affine2DBase):
    is_separable: bool
    def __init__(self, x_transform, y_transform, **kwargs) -> None: ...
    def get_matrix(self): ...

def blended_transform_factory(x_transform, y_transform): ...

class CompositeGenericTransform(Transform):
    pass_through: bool
    input_dims: Incomplete
    output_dims: Incomplete
    def __init__(self, a, b, **kwargs) -> None: ...
    def frozen(self): ...
    def __eq__(self, other): ...
    def contains_branch_seperately(self, other_transform): ...
    depth: Incomplete
    is_affine: Incomplete
    is_separable: Incomplete
    has_inverse: Incomplete
    def transform_affine(self, values): ...
    def transform_non_affine(self, values): ...
    def transform_path_non_affine(self, path): ...
    def get_affine(self): ...
    def inverted(self): ...

class CompositeAffine2D(Affine2DBase):
    input_dims: Incomplete
    output_dims: Incomplete
    def __init__(self, a, b, **kwargs) -> None: ...
    @property
    def depth(self): ...
    def get_matrix(self): ...

def composite_transform_factory(a, b): ...

class BboxTransform(Affine2DBase):
    is_separable: bool
    def __init__(self, boxin, boxout, **kwargs) -> None: ...
    def get_matrix(self): ...

class BboxTransformTo(Affine2DBase):
    is_separable: bool
    def __init__(self, boxout, **kwargs) -> None: ...
    def get_matrix(self): ...

class BboxTransformToMaxOnly(BboxTransformTo):
    def get_matrix(self): ...

class BboxTransformFrom(Affine2DBase):
    is_separable: bool
    def __init__(self, boxin, **kwargs) -> None: ...
    def get_matrix(self): ...

class ScaledTranslation(Affine2DBase):
    def __init__(self, xt, yt, scale_trans, **kwargs) -> None: ...
    def get_matrix(self): ...

class AffineDeltaTransform(Affine2DBase):
    def __init__(self, transform, **kwargs) -> None: ...
    def get_matrix(self): ...

class TransformedPath(TransformNode):
    def __init__(self, path, transform) -> None: ...
    def get_transformed_points_and_affine(self): ...
    def get_transformed_path_and_affine(self): ...
    def get_fully_transformed_path(self): ...
    def get_affine(self): ...

class TransformedPatchPath(TransformedPath):
    def __init__(self, patch) -> None: ...

def nonsingular(
    vmin, vmax, expander: float = 0.001, tiny: float = 1e-15, increasing: bool = True
): ...
def interval_contains(interval, val): ...
def interval_contains_open(interval, val): ...
def offset_copy(
    trans,
    fig: Incomplete | None = None,
    x: float = 0.0,
    y: float = 0.0,
    units: str = "inches",
): ...
