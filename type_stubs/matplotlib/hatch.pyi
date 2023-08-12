from _typeshed import Incomplete
from matplotlib.path import Path as Path

class HatchPatternBase: ...

class HorizontalHatch(HatchPatternBase):
    num_lines: Incomplete
    num_vertices: Incomplete
    def __init__(self, hatch, density) -> None: ...
    def set_vertices_and_codes(self, vertices, codes) -> None: ...

class VerticalHatch(HatchPatternBase):
    num_lines: Incomplete
    num_vertices: Incomplete
    def __init__(self, hatch, density) -> None: ...
    def set_vertices_and_codes(self, vertices, codes) -> None: ...

class NorthEastHatch(HatchPatternBase):
    num_lines: Incomplete
    num_vertices: Incomplete
    def __init__(self, hatch, density) -> None: ...
    def set_vertices_and_codes(self, vertices, codes) -> None: ...

class SouthEastHatch(HatchPatternBase):
    num_lines: Incomplete
    num_vertices: Incomplete
    def __init__(self, hatch, density) -> None: ...
    def set_vertices_and_codes(self, vertices, codes) -> None: ...

class Shapes(HatchPatternBase):
    filled: bool
    num_shapes: int
    num_vertices: int
    def __init__(self, hatch, density) -> None: ...
    def set_vertices_and_codes(self, vertices, codes) -> None: ...

class Circles(Shapes):
    shape_vertices: Incomplete
    shape_codes: Incomplete
    def __init__(self, hatch, density) -> None: ...

class SmallCircles(Circles):
    size: float
    num_rows: Incomplete
    def __init__(self, hatch, density) -> None: ...

class LargeCircles(Circles):
    size: float
    num_rows: Incomplete
    def __init__(self, hatch, density) -> None: ...

class SmallFilledCircles(Circles):
    size: float
    filled: bool
    num_rows: Incomplete
    def __init__(self, hatch, density) -> None: ...

class Stars(Shapes):
    size: Incomplete
    filled: bool
    num_rows: Incomplete
    shape_vertices: Incomplete
    shape_codes: Incomplete
    def __init__(self, hatch, density) -> None: ...

def get_path(hatchpattern, density: int = ...): ...
