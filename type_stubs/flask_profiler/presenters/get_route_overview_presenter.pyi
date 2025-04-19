from dataclasses import dataclass
from typing import Iterable

from flask_profiler.use_cases import get_route_overview as use_case

@dataclass
class Plot:
    data_points: list[Point]
    x_axis: Line
    y_axis: Line
    x_markings: list[Line]
    y_markings: list[Line]
    @property
    def point_connections(self) -> Iterable[Line]: ...
    def transform(self, transformation: Conversion) -> Plot: ...

@dataclass
class Point:
    @property
    def x(self) -> str: ...
    @property
    def y(self) -> str: ...

@dataclass
class Line:
    p1: Point
    p2: Point
    label: str | None = ...
    @property
    def x1(self) -> str: ...
    @property
    def y1(self) -> str: ...
    @property
    def x2(self) -> str: ...
    @property
    def y2(self) -> str: ...

@dataclass
class Graph:
    title: str
    width: str
    height: str
    plot: Plot

@dataclass
class ViewModel:
    headline: str
    graphs: list[Graph]

class GetRouteOverviewPresenter:
    def present_response(self, response: use_case.Response) -> ViewModel: ...

@dataclass
class Conversion:
    rows: list[list[float]]
    @classmethod
    def stretch(cls, *, x: float = 1, y: float = 1) -> Conversion: ...
    @classmethod
    def translation(cls, *, x: float = 0, y: float = 0) -> Conversion: ...
    @classmethod
    def mirror_y(cls) -> Conversion: ...
    def transform_point(self, p: Point) -> Point: ...
    def transform_line(self, line: Line) -> Line: ...
    def concat(self, other: Conversion) -> Conversion: ...
    def __getitem__(self, x: int) -> list[float]: ...
