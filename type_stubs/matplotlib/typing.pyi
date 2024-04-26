import pathlib
from collections.abc import Sequence
from typing import Any

from _typeshed import Incomplete

from . import path as path
from ._enums import CapStyle as CapStyle
from ._enums import JoinStyle as JoinStyle
from .markers import MarkerStyle as MarkerStyle

RGBColorType = tuple[float, float, float] | str
RGBAColorType = (
    str
    | tuple[float, float, float, float]
    | tuple[RGBColorType, float]
    | tuple[tuple[float, float, float, float], float]
)
ColorType = RGBColorType | RGBAColorType
RGBColourType = RGBColorType
RGBAColourType = RGBAColorType
ColourType = ColorType
LineStyleType = str | tuple[float, Sequence[float]]
DrawStyleType: Incomplete
MarkEveryType = (
    None
    | int
    | tuple[int, int]
    | slice
    | list[int]
    | float
    | tuple[float, float]
    | list[bool]
)
MarkerType = str | path.Path | MarkerStyle
FillStyleType: Incomplete
JoinStyleType: Incomplete
CapStyleType: Incomplete
RcStyleType = (
    str | dict[str, Any] | pathlib.Path | Sequence[str | pathlib.Path | dict[str, Any]]
)
HashableList: Incomplete
