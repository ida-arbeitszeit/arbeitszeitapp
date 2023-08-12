from _typeshed import Incomplete
from matplotlib import cbook as cbook

class ConversionError(TypeError): ...

class AxisInfo:
    majloc: Incomplete
    minloc: Incomplete
    majfmt: Incomplete
    minfmt: Incomplete
    label: Incomplete
    default_limits: Incomplete
    def __init__(self, majloc: Incomplete | None = ..., minloc: Incomplete | None = ..., majfmt: Incomplete | None = ..., minfmt: Incomplete | None = ..., label: Incomplete | None = ..., default_limits: Incomplete | None = ...) -> None: ...

class ConversionInterface:
    @staticmethod
    def axisinfo(unit, axis) -> None: ...
    @staticmethod
    def default_units(x, axis) -> None: ...
    @staticmethod
    def convert(obj, unit, axis): ...

class DecimalConverter(ConversionInterface):
    @staticmethod
    def convert(value, unit, axis): ...

class Registry(dict):
    def get_converter(self, x): ...

registry: Incomplete
