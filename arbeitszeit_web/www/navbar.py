from dataclasses import dataclass
from typing import Optional


@dataclass
class NavbarItem:
    text: str
    url: Optional[str]
