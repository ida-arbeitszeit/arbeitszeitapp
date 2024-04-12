import dataclasses
import typing as t

def get_recorded_queries() -> list[_QueryInfo]: ...
@dataclasses.dataclass
class _QueryInfo:
    statement: str | None
    parameters: t.Any
    start_time: float
    end_time: float
    location: str
    @property
    def duration(self) -> float: ...
    def __init__(
        self, statement, parameters, start_time, end_time, location
    ) -> None: ...
