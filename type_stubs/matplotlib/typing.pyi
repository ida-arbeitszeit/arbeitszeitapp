import pathlib
from . import path as path
from ._enums import CapStyle as CapStyle, JoinStyle as JoinStyle
from .markers import MarkerStyle as MarkerStyle
from _typeshed import Incomplete
from collections.abc import Sequence
from typing import Any, Union

RGBColorType = Union[tuple[float, float, float], str]
RGBAColorType = Union[str, tuple[float, float, float, float], tuple[RGBColorType, float], tuple[tuple[float, float, float, float], float]]
ColorType = Union[RGBColorType, RGBAColorType]
RGBColourType = RGBColorType
RGBAColourType = RGBAColorType
ColourType = ColorType
LineStyleType = Union[str, tuple[float, Sequence[float]]]
DrawStyleType: Incomplete
MarkEveryType = Union[None, int, tuple[int, int], slice, list[int], float, tuple[float, float], list[bool]]
MarkerType = Union[str, path.Path, MarkerStyle]
FillStyleType: Incomplete
JoinStyleType: Incomplete
CapStyleType: Incomplete
RcStyleType = Union[str, dict[str, Any], pathlib.Path, Sequence[Union[str, pathlib.Path, dict[str, Any]]]]
HashableList: Incomplete
