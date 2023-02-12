from dataclasses import dataclass
from typing import Type, Union


@dataclass
class ExpectedInput:
    name: str
    type: Type
    description: str
    default: Union[None, str, int, bool]
