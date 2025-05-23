from dataclasses import dataclass
from datetime import date
from typing import Iterator

class Calendar:
    def day_interval(self, *, since: date, until: date) -> DateSpan: ...

@dataclass
class DateSpan:
    since: date
    until: date
    def __contains__(self, element: date) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(self) -> Iterator[date]: ...
