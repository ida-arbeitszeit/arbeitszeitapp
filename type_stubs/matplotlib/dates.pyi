from _typeshed import Incomplete
from dateutil.relativedelta import relativedelta as relativedelta
from dateutil.rrule import DAILY as DAILY
from dateutil.rrule import FR as FR
from dateutil.rrule import HOURLY as HOURLY
from dateutil.rrule import MINUTELY as MINUTELY
from dateutil.rrule import MO as MO
from dateutil.rrule import MONTHLY as MONTHLY
from dateutil.rrule import SA as SA
from dateutil.rrule import SECONDLY as SECONDLY
from dateutil.rrule import SU as SU
from dateutil.rrule import TH as TH
from dateutil.rrule import TU as TU
from dateutil.rrule import WE as WE
from dateutil.rrule import WEEKLY as WEEKLY
from dateutil.rrule import YEARLY as YEARLY
from dateutil.rrule import rrule as rrule
from matplotlib import ticker, units

__all__ = [
    "datestr2num",
    "date2num",
    "num2date",
    "num2timedelta",
    "drange",
    "set_epoch",
    "get_epoch",
    "DateFormatter",
    "ConciseDateFormatter",
    "AutoDateFormatter",
    "DateLocator",
    "RRuleLocator",
    "AutoDateLocator",
    "YearLocator",
    "MonthLocator",
    "WeekdayLocator",
    "DayLocator",
    "HourLocator",
    "MinuteLocator",
    "SecondLocator",
    "MicrosecondLocator",
    "rrule",
    "MO",
    "TU",
    "WE",
    "TH",
    "FR",
    "SA",
    "SU",
    "YEARLY",
    "MONTHLY",
    "WEEKLY",
    "DAILY",
    "HOURLY",
    "MINUTELY",
    "SECONDLY",
    "MICROSECONDLY",
    "relativedelta",
    "DateConverter",
    "ConciseDateConverter",
    "rrulewrapper",
]

MICROSECONDLY: Incomplete

def set_epoch(epoch) -> None: ...
def get_epoch(): ...
def datestr2num(d, default: Incomplete | None = None): ...
def date2num(d): ...
def num2date(x, tz: Incomplete | None = None): ...
def num2timedelta(x): ...
def drange(dstart, dend, delta): ...

class DateFormatter(ticker.Formatter):
    tz: Incomplete
    fmt: Incomplete
    def __init__(
        self, fmt, tz: Incomplete | None = None, *, usetex: Incomplete | None = None
    ) -> None: ...
    def __call__(self, x, pos: int = 0): ...
    def set_tzinfo(self, tz) -> None: ...

class ConciseDateFormatter(ticker.Formatter):
    defaultfmt: str
    formats: Incomplete
    zero_formats: Incomplete
    offset_formats: Incomplete
    offset_string: str
    show_offset: Incomplete
    def __init__(
        self,
        locator,
        tz: Incomplete | None = None,
        formats: Incomplete | None = None,
        offset_formats: Incomplete | None = None,
        zero_formats: Incomplete | None = None,
        show_offset: bool = True,
        *,
        usetex: Incomplete | None = None,
    ) -> None: ...
    def __call__(self, x, pos: Incomplete | None = None): ...
    def format_ticks(self, values): ...
    def get_offset(self): ...
    def format_data_short(self, value): ...

class AutoDateFormatter(ticker.Formatter):
    defaultfmt: Incomplete
    scaled: Incomplete
    def __init__(
        self,
        locator,
        tz: Incomplete | None = None,
        defaultfmt: str = "%Y-%m-%d",
        *,
        usetex: Incomplete | None = None,
    ) -> None: ...
    def __call__(self, x, pos: Incomplete | None = None): ...

class rrulewrapper:
    def __init__(self, freq, tzinfo: Incomplete | None = None, **kwargs) -> None: ...
    def set(self, **kwargs) -> None: ...
    def __getattr__(self, name): ...

class DateLocator(ticker.Locator):
    hms0d: Incomplete
    tz: Incomplete
    def __init__(self, tz: Incomplete | None = None) -> None: ...
    def set_tzinfo(self, tz) -> None: ...
    def datalim_to_dt(self): ...
    def viewlim_to_dt(self): ...
    def nonsingular(self, vmin, vmax): ...

class RRuleLocator(DateLocator):
    rule: Incomplete
    def __init__(self, o, tz: Incomplete | None = None) -> None: ...
    def __call__(self): ...
    def tick_values(self, vmin, vmax): ...
    @staticmethod
    def get_unit_generic(freq): ...

class AutoDateLocator(DateLocator):
    minticks: Incomplete
    maxticks: Incomplete
    interval_multiples: Incomplete
    intervald: Incomplete
    def __init__(
        self,
        tz: Incomplete | None = None,
        minticks: int = 5,
        maxticks: Incomplete | None = None,
        interval_multiples: bool = True,
    ) -> None: ...
    def __call__(self): ...
    def tick_values(self, vmin, vmax): ...
    def nonsingular(self, vmin, vmax): ...
    def get_locator(self, dmin, dmax): ...

class YearLocator(RRuleLocator):
    base: Incomplete
    def __init__(
        self, base: int = 1, month: int = 1, day: int = 1, tz: Incomplete | None = None
    ) -> None: ...

class MonthLocator(RRuleLocator):
    def __init__(
        self,
        bymonth: Incomplete | None = None,
        bymonthday: int = 1,
        interval: int = 1,
        tz: Incomplete | None = None,
    ) -> None: ...

class WeekdayLocator(RRuleLocator):
    def __init__(
        self, byweekday: int = 1, interval: int = 1, tz: Incomplete | None = None
    ) -> None: ...

class DayLocator(RRuleLocator):
    def __init__(
        self,
        bymonthday: Incomplete | None = None,
        interval: int = 1,
        tz: Incomplete | None = None,
    ) -> None: ...

class HourLocator(RRuleLocator):
    def __init__(
        self,
        byhour: Incomplete | None = None,
        interval: int = 1,
        tz: Incomplete | None = None,
    ) -> None: ...

class MinuteLocator(RRuleLocator):
    def __init__(
        self,
        byminute: Incomplete | None = None,
        interval: int = 1,
        tz: Incomplete | None = None,
    ) -> None: ...

class SecondLocator(RRuleLocator):
    def __init__(
        self,
        bysecond: Incomplete | None = None,
        interval: int = 1,
        tz: Incomplete | None = None,
    ) -> None: ...

class MicrosecondLocator(DateLocator):
    def __init__(self, interval: int = 1, tz: Incomplete | None = None) -> None: ...
    def set_axis(self, axis): ...
    def __call__(self): ...
    def tick_values(self, vmin, vmax): ...

class DateConverter(units.ConversionInterface):
    def __init__(self, *, interval_multiples: bool = True) -> None: ...
    def axisinfo(self, unit, axis): ...
    @staticmethod
    def convert(value, unit, axis): ...
    @staticmethod
    def default_units(x, axis): ...

class ConciseDateConverter(DateConverter):
    def __init__(
        self,
        formats: Incomplete | None = None,
        zero_formats: Incomplete | None = None,
        offset_formats: Incomplete | None = None,
        show_offset: bool = True,
        *,
        interval_multiples: bool = True,
    ) -> None: ...
    def axisinfo(self, unit, axis): ...

class _SwitchableDateConverter:
    def axisinfo(self, *args, **kwargs): ...
    def default_units(self, *args, **kwargs): ...
    def convert(self, *args, **kwargs): ...
