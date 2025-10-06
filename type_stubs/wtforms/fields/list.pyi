from _typeshed import Incomplete

from .core import Field

__all__ = ["FieldList"]

class FieldList(Field):
    widget: Incomplete
    unbound_field: Incomplete
    min_entries: Incomplete
    max_entries: Incomplete
    last_index: int
    def __init__(
        self,
        unbound_field,
        label=None,
        validators=None,
        min_entries: int = 0,
        max_entries=None,
        separator: str = "-",
        default=(),
        **kwargs,
    ) -> None: ...
    entries: Incomplete
    object_data: Incomplete
    def process(self, formdata, data=..., extra_filters=None) -> None: ...
    errors: Incomplete
    def validate(self, form, extra_validators=()): ...
    def populate_obj(self, obj, name) -> None: ...
    def append_entry(self, data=...): ...
    def pop_entry(self): ...
    def __iter__(self): ...
    def __len__(self) -> int: ...
    def __getitem__(self, index): ...
    @property
    def data(self): ...
