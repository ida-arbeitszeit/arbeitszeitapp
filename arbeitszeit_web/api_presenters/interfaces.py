from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Union

JsonValue = Union[
    "JsonDict",
    "JsonString",
    "JsonDecimal",
    "JsonBoolean",
    "JsonDatetime",
    "JsonInteger",
]


@dataclass
class JsonDict:
    """
    if `schema_name` is given, this JsonDict will be registered as a model with the given name.
    if `as_list` is True, it will be returned in an array.
    """

    members: Dict[str, JsonValue]
    schema_name: Optional[str] = None
    as_list: bool = False


@dataclass
class JsonString:
    as_list: bool = False


@dataclass
class JsonDecimal:
    """A floating point number with an arbitrary precision."""

    as_list: bool = False


@dataclass
class JsonBoolean:
    as_list: bool = False


@dataclass
class JsonInteger:
    as_list: bool = False


@dataclass
class JsonDatetime:
    as_list: bool = False


class Namespace(Protocol):
    def __init__(self, name: str, description: str) -> None:
        ...

    @property
    def models(self) -> Dict[str, Any]:
        ...

    def model(self, name: str, model: Any) -> Any:
        ...


class ApiPresenter(Protocol):
    @classmethod
    def get_schema(cls) -> JsonValue:
        ...
