from dataclasses import dataclass
from typing import List

@dataclass
class Table:
    headers: List[Header]
    rows: List[List[Cell]]
    def __init__(self, headers, rows) -> None: ...

@dataclass
class Header:
    label: str
    link_target: str | None = ...
    def __init__(self, label, link_target) -> None: ...

@dataclass
class Cell:
    text: str
    link_target: str | None = ...
    def __init__(self, text, link_target) -> None: ...
