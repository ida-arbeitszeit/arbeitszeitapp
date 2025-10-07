from _typeshed import Incomplete
from wtforms.fields.core import Field

__all__ = [
    "IntegerField",
    "DecimalField",
    "FloatField",
    "IntegerRangeField",
    "DecimalRangeField",
]

class LocaleAwareNumberField(Field):
    use_locale: Incomplete
    number_format: Incomplete
    locale: Incomplete
    def __init__(
        self,
        label=None,
        validators=None,
        use_locale: bool = False,
        number_format=None,
        **kwargs,
    ) -> None: ...

class IntegerField(Field):
    widget: Incomplete
    def __init__(self, label=None, validators=None, **kwargs) -> None: ...
    data: Incomplete
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...

class DecimalField(LocaleAwareNumberField):
    widget: Incomplete
    places: Incomplete
    rounding: Incomplete
    def __init__(
        self, label=None, validators=None, places=..., rounding=None, **kwargs
    ) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class FloatField(Field):
    widget: Incomplete
    def __init__(self, label=None, validators=None, **kwargs) -> None: ...
    data: Incomplete
    def process_formdata(self, valuelist) -> None: ...

class IntegerRangeField(IntegerField):
    widget: Incomplete

class DecimalRangeField(DecimalField):
    widget: Incomplete
