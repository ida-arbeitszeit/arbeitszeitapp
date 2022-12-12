from dataclasses import dataclass
from typing import Protocol

from arbeitszeit_web.api_presenters.namespace import Model


class NestedListField(Protocol):
    def __init__(self, model: Model, as_list: bool):
        ...


class StringField(Protocol):
    ...


class DateTimeField(Protocol):
    ...


class DecimalField(Protocol):
    ...


class BooleanField(Protocol):
    ...


@dataclass
class Fields:
    nested_list_field: NestedListField
    string_field: StringField
    datetime_field: DateTimeField
    decimal_field: DecimalField
    boolean_field: BooleanField
