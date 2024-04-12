from dataclasses import dataclass
from datetime import datetime
from sqlite3 import Cursor
from typing import Any, Callable, Generic, Iterator, List, TypeVar

from _typeshed import Incomplete
from flask_profiler import query as q
from flask_profiler.entities import measurement_archive as interface
from typing_extensions import Self

T = TypeVar("T")
SelectQueryT = TypeVar("SelectQueryT", bound="SelectQuery")
LOGGER: Incomplete

@dataclass
class SelectQuery(Generic[T]):
    mapping: Callable[[Any], T]
    db: Cursor
    query: q.Select
    def __iter__(self) -> Iterator[T]: ...
    def __len__(self) -> int: ...
    def limit(self, n: int) -> SelectQueryT: ...
    def offset(self, n: int) -> SelectQueryT: ...
    def first(self) -> T | None: ...
    def __init__(self, mapping, db, query) -> None: ...

class RecordResult(SelectQuery[interface.Record]):
    def summarize(self) -> SummarizedMeasurementsImpl: ...
    def summarize_by_interval(
        self, timestamps: List[datetime]
    ) -> SummarizedMeasurementsImpl: ...
    @classmethod
    def summary_mapping(cls, row: Any) -> interface.Summary: ...
    def with_method(self, method: str) -> RecordResult: ...
    def with_name(self, name: str) -> RecordResult: ...
    def with_name_containing(self, substring: str) -> RecordResult: ...
    def requested_after(self, t: datetime) -> RecordResult: ...
    def requested_before(self, t: datetime) -> RecordResult: ...
    def with_id(self, id_: int) -> RecordResult: ...
    def ordered_by_start_time(self, ascending: bool = True) -> RecordResult: ...

class SummarizedMeasurementsImpl(SelectQuery[interface.Summary]):
    def sorted_by_avg_elapsed(self, ascending: bool = True) -> Self: ...
    def sorted_by_route_name(self, ascending: bool = True) -> Self: ...
