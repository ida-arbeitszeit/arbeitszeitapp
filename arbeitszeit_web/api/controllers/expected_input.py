from dataclasses import dataclass
from enum import Enum, auto
from typing import Type, Union


class InputLocation(Enum):
    query = auto()
    path = auto()
    form = auto()


@dataclass
class ExpectedInput:
    name: str
    type: Type
    description: str
    location: InputLocation
    default: Union[None, str, int, bool]
    required: bool = False
