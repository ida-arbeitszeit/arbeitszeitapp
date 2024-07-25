from dataclasses import dataclass

@dataclass
class Table:
    headers: list[Header]
    rows: list[list[Cell]]
    def __init__(self, headers, rows) -> None: ...

@dataclass
class Header:
    label: str
    link_target: str | None = ...
    def __init__(self, label, link_target=...) -> None: ...

@dataclass
class Cell:
    text: str
    link_target: str | None = ...
    def __init__(self, text, link_target=...) -> None: ...
