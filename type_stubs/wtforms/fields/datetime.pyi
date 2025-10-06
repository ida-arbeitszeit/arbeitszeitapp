from _typeshed import Incomplete
from wtforms.fields.core import Field

__all__ = [
    "DateTimeField",
    "DateField",
    "TimeField",
    "MonthField",
    "DateTimeLocalField",
    "WeekField",
]

class DateTimeField(Field):
    widget: Incomplete
    format: Incomplete
    strptime_format: Incomplete
    def __init__(
        self, label=None, validators=None, format: str = "%Y-%m-%d %H:%M:%S", **kwargs
    ) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class DateField(DateTimeField):
    widget: Incomplete
    def __init__(
        self, label=None, validators=None, format: str = "%Y-%m-%d", **kwargs
    ) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class TimeField(DateTimeField):
    widget: Incomplete
    def __init__(
        self, label=None, validators=None, format: str = "%H:%M", **kwargs
    ) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class MonthField(DateField):
    widget: Incomplete
    def __init__(
        self, label=None, validators=None, format: str = "%Y-%m", **kwargs
    ) -> None: ...

class WeekField(DateField):
    widget: Incomplete
    def __init__(
        self, label=None, validators=None, format: str = "%Y-W%W", **kwargs
    ) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class DateTimeLocalField(DateTimeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
