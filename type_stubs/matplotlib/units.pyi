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
    def __init__(
        self,
        majloc: Incomplete | None = None,
        minloc: Incomplete | None = None,
        majfmt: Incomplete | None = None,
        minfmt: Incomplete | None = None,
        label: Incomplete | None = None,
        default_limits: Incomplete | None = None,
    ) -> None: ...

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
