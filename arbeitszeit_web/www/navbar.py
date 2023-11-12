from dataclasses import dataclass
from typing import Optional


@dataclass
class NavbarItem:
    text: str
    has_url: bool
    url: Optional[str]
