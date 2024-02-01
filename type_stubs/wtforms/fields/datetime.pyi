from _typeshed import Incomplete
from wtforms.fields.core import Field

class DateTimeField(Field):
    widget: Incomplete
    format: Incomplete
    strptime_format: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., format: str = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class DateField(DateTimeField):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., format: str = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class TimeField(DateTimeField):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., format: str = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class MonthField(DateField):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., format: str = ..., **kwargs) -> None: ...

class WeekField(DateField):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., format: str = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class DateTimeLocalField(DateTimeField):
    widget: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
