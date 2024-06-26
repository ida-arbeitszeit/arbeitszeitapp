from _typeshed import Incomplete
from matplotlib import ticker as ticker
from matplotlib import units as units

class StrCategoryConverter(units.ConversionInterface):
    @staticmethod
    def convert(value, unit, axis): ...
    @staticmethod
    def axisinfo(unit, axis): ...
    @staticmethod
    def default_units(data, axis): ...

class StrCategoryLocator(ticker.Locator):
    def __init__(self, units_mapping) -> None: ...
    def __call__(self): ...
    def tick_values(self, vmin, vmax): ...

class StrCategoryFormatter(ticker.Formatter):
    def __init__(self, units_mapping) -> None: ...
    def __call__(self, x, pos: Incomplete | None = None): ...
    def format_ticks(self, values): ...

class UnitData:
    def __init__(self, data: Incomplete | None = None) -> None: ...
    def update(self, data) -> None: ...
