from dataclasses import dataclass


@dataclass
class NavbarItem:
    text: str
    has_url: bool
    url: str | None
