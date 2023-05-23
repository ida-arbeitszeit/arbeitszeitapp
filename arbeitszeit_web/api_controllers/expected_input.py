from dataclasses import dataclass
from typing import Optional, Type, Union


@dataclass
class ExpectedInput:
    name: str
    type: Type
    description: str
    default: Union[None, str, int, bool]
    location: Optional[str] = None
