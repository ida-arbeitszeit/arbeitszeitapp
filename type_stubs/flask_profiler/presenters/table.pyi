from dataclasses import dataclass

@dataclass
class Table:
    headers: list[Header]
    rows: list[list[Cell]]

@dataclass
class Header:
    label: str
    link_target: str | None = ...

@dataclass
class Cell:
    text: str
    link_target: str | None = ...
