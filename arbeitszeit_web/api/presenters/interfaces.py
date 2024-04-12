from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Protocol, Union

JsonValue = Union[
    "JsonObject",
    "JsonString",
    "JsonDecimal",
    "JsonBoolean",
    "JsonDatetime",
    "JsonInteger",
    "JsonList",
]


@dataclass
class JsonObject:
    members: Dict[str, JsonValue]
    name: str
    required: bool = True


@dataclass
class JsonString:
    required: bool = True


@dataclass
class JsonDecimal:
    """A floating point number with an arbitrary precision."""

    required: bool = True


@dataclass
class JsonBoolean:
    required: bool = True


@dataclass
class JsonInteger:
    required: bool = True


@dataclass
class JsonDatetime:
    required: bool = True


@dataclass
class JsonList:
    elements: JsonValue
    required: bool = True


class Namespace(Protocol):
    def __init__(self, name: str, description: str) -> None: ...

    @property
    def models(self) -> Dict[str, Any]: ...

    def model(self, name: str, model: Any) -> Any: ...


class ApiPresenter(Protocol):
    @classmethod
    def get_schema(cls) -> JsonValue: ...
