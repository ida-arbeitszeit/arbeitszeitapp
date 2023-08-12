from _typeshed import Incomplete
from wtforms.fields.core import Field

class LocaleAwareNumberField(Field):
    use_locale: Incomplete
    number_format: Incomplete
    locale: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., use_locale: bool = ..., number_format: Incomplete | None = ..., **kwargs) -> None: ...

class IntegerField(Field):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...

class DecimalField(LocaleAwareNumberField):
    widget: Incomplete
    places: Incomplete
    rounding: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., places=..., rounding: Incomplete | None = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class FloatField(Field):
    widget: Incomplete
    def __init__(self, label: Incomplete | None = ..., validators: Incomplete | None = ..., **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class IntegerRangeField(IntegerField):
    widget: Incomplete

class DecimalRangeField(DecimalField):
    widget: Incomplete
