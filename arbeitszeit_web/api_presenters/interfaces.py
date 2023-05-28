from dataclasses import dataclass
from typing import Any, Dict, Protocol, Union

JsonValue = Union[
    "JsonObject",
    "JsonString",
    "JsonDecimal",
    "JsonBoolean",
    "JsonDatetime",
    "JsonInteger",
]


@dataclass
class JsonObject:
    members: Dict[str, JsonValue]
    name: str
    as_list: bool = False


@dataclass
class JsonString:
    required: bool = True
    as_list: bool = False


@dataclass
class JsonDecimal:
    """A floating point number with an arbitrary precision."""

    required: bool = True
    as_list: bool = False


@dataclass
class JsonBoolean:
    required: bool = True
    as_list: bool = False


@dataclass
class JsonInteger:
    required: bool = True
    as_list: bool = False


@dataclass
class JsonDatetime:
    required: bool = True
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
