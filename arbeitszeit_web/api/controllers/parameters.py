from dataclasses import dataclass
from typing import Type, Union


@dataclass
class BodyParameter:
    name: str
    type: Type
    description: str
    default: Union[None, str, int, bool]
    required: bool = False


@dataclass
class QueryParameter:
    name: str
    type: Type
    description: str
    default: Union[None, str, int, bool]
    required: bool = False


@dataclass
class PathParameter:
    name: str
    description: str
