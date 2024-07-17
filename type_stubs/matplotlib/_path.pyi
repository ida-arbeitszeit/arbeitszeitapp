import numpy

def affine_transform(
    points: numpy.ndarray[numpy.float64], trans: trans_affine
) -> object: ...
def cleanup_path(
    path: PathIterator,
    trans: trans_affine,
    remove_nans: bool,
    clip_rect: rect_d,
    snap_mode: e_snap_mode,
    stroke_width: float,
    simplify: bool | None,
    return_curves: bool,
    sketch: SketchParams,
) -> tuple: ...
def clip_path_to_rect(path: PathIterator, rect: rect_d, inside: bool) -> list: ...
def convert_path_to_polygons(
    path: PathIterator,
    trans: trans_affine,
    width: float = ...,
    height: float = ...,
    closed_only: bool = ...,
) -> list: ...
def convert_to_string(
    path: PathIterator,
    trans: trans_affine,
    clip_rect: rect_d,
    simplify: bool | None,
    sketch: SketchParams,
    precision: int,
    codes,
    postfix: bool,
) -> object: ...
def count_bboxes_overlapping_bbox(bbox: rect_d, bboxes: object) -> int: ...
def get_path_collection_extents(
    master_transform: trans_affine,
    paths: object,
    transforms: object,
    offsets: object,
    offset_transform: trans_affine,
) -> tuple: ...
def is_sorted_and_has_non_nan(array: object) -> bool: ...
def path_in_path(
    path_a: PathIterator,
    trans_a: trans_affine,
    path_b: PathIterator,
    trans_b: trans_affine,
) -> bool: ...
def path_intersects_path(
    path1: PathIterator, path2: PathIterator, filled: bool = ...
) -> bool: ...
def path_intersects_rectangle(
    path: PathIterator,
    rect_x1: float,
    rect_y1: float,
    rect_x2: float,
    rect_y2: float,
    filled: bool = ...,
) -> bool: ...
def point_in_path(
    x: float, y: float, radius: float, path: PathIterator, trans: trans_affine
) -> bool: ...
def point_in_path_collection(
    x: float,
    y: float,
    radius: float,
    master_transform: trans_affine,
    paths: object,
    transforms: object,
    offsets: object,
    offset_trans: trans_affine,
    filled: bool,
) -> object: ...
def points_in_path(
    points: numpy.ndarray[numpy.float64],
    radius: float,
    path: PathIterator,
    trans: trans_affine,
) -> numpy.ndarray[numpy.float64]: ...
def update_path_extents(
    path: PathIterator,
    trans: trans_affine,
    rect: rect_d,
    minpos: numpy.ndarray[numpy.float64],
    ignore: bool,
) -> tuple: ...
