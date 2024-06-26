from _typeshed import Incomplete

class Triangulation:
    x: Incomplete
    y: Incomplete
    mask: Incomplete
    is_delaunay: bool
    triangles: Incomplete
    def __init__(
        self, x, y, triangles: Incomplete | None = None, mask: Incomplete | None = None
    ) -> None: ...
    def calculate_plane_coefficients(self, z): ...
    @property
    def edges(self): ...
    def get_cpp_triangulation(self): ...
    def get_masked_triangles(self): ...
    @staticmethod
    def get_from_args_and_kwargs(*args, **kwargs): ...
    def get_trifinder(self): ...
    @property
    def neighbors(self): ...
    def set_mask(self, mask) -> None: ...
