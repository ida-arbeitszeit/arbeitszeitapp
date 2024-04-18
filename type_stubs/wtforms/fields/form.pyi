from _typeshed import Incomplete

from .core import Field

__all__ = ["FormField"]

class FormField(Field):
    widget: Incomplete
    form_class: Incomplete
    separator: Incomplete
    def __init__(
        self,
        form_class,
        label: Incomplete | None = None,
        validators: Incomplete | None = None,
        separator: str = "-",
        **kwargs,
    ) -> None: ...
    object_data: Incomplete
    form: Incomplete
    def process(
        self, formdata, data=..., extra_filters: Incomplete | None = None
    ) -> None: ...
    def validate(self, form, extra_validators=()): ...
    def populate_obj(self, obj, name) -> None: ...
    def __iter__(self): ...
    def __getitem__(self, name): ...
    def __getattr__(self, name): ...
    @property
    def data(self): ...
    @property
    def errors(self): ...
