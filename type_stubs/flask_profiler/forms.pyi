from dataclasses import dataclass
from datetime import datetime
from typing import Callable

from _typeshed import Incomplete

class OptionalStringField:
    name: Incomplete
    value: str | None
    normalize: Incomplete
    def __init__(self, name: str, normalize: Callable[[str], str] = ...) -> None: ...
    def set_field_name(self, name: str) -> None: ...
    def parse_value(self, form: dict[str, str]) -> None: ...
    def get_value(self) -> str | None: ...

class OptionalDatetimeField:
    name: Incomplete
    value: datetime | None
    def __init__(self, name: str) -> None: ...
    def set_field_name(self, name: str) -> None: ...
    def parse_value(self, form: dict[str, str]) -> None: ...
    def get_value(self) -> datetime | None: ...

@dataclass
class FilterFormData:
    name: str | None
    method: str | None
    requested_after: datetime | None
    requested_before: datetime | None
    sorted_by: str | None
    @classmethod
    def parse_from_from(self, args: dict[str, str]) -> FilterFormData: ...
