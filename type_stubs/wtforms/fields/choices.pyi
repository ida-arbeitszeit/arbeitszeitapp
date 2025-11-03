from collections.abc import Generator

from _typeshed import Incomplete
from wtforms.fields.core import Field

__all__ = ["SelectField", "SelectMultipleField", "RadioField"]

class SelectFieldBase(Field):
    option_widget: Incomplete
    def __init__(
        self, label=None, validators=None, option_widget=None, **kwargs
    ) -> None: ...
    def iter_choices(self) -> None: ...
    def has_groups(self): ...
    def iter_groups(self) -> None: ...
    def __iter__(self): ...

    class _Option(Field):
        checked: bool

class SelectField(SelectFieldBase):
    widget: Incomplete
    coerce: Incomplete
    choices: Incomplete
    validate_choice: Incomplete
    def __init__(
        self,
        label=None,
        validators=None,
        coerce=...,
        choices=None,
        validate_choice: bool = True,
        **kwargs,
    ) -> None: ...
    def iter_choices(self): ...
    def has_groups(self): ...
    def iter_groups(self) -> Generator[Incomplete]: ...
    data: Incomplete
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...
    def pre_validate(self, form) -> None: ...

class SelectMultipleField(SelectField):
    widget: Incomplete
    data: Incomplete
    def process_data(self, value) -> None: ...
    def process_formdata(self, valuelist) -> None: ...
    def pre_validate(self, form) -> None: ...

class RadioField(SelectField):
    widget: Incomplete
    option_widget: Incomplete
