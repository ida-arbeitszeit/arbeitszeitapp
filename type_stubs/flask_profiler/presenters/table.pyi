from typing import List, Optional

class Table:
    headers: List[Header]
    rows: List[List[Cell]]
    def __init__(self, headers, rows) -> None: ...

class Header:
    label: str
    link_target: Optional[str]
    def __init__(self, label, link_target) -> None: ...

class Cell:
    text: str
    link_target: Optional[str]
    def __init__(self, text, link_target) -> None: ...
