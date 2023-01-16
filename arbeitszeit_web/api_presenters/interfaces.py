from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol, Union

JsonValue = Union["JsonDict", "JsonString"]


@dataclass
class JsonDict:
    """
    if `schema_name` is given, this JsonDict will be registered as a model with the given name.
    if `as_list` is True, it's members will be returned in an array.
    """

    members: Dict[str, JsonValue]
    schema_name: Optional[str] = None
    as_list: bool = False


@dataclass
class JsonString:
    pass


class Namespace(Protocol):
    def __init__(self, name: str, description: str) -> None:
        ...

    def model(self, name: str, model: Any) -> Any:
        ...


class ApiPresenter(Protocol):
    @classmethod
    def get_schema(cls) -> JsonValue:
        ...
