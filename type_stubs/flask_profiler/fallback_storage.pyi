from datetime import datetime
from typing import Iterator

from flask_profiler.entities import measurement_archive as archive
from typing_extensions import Self

class MeasurementArchivistPlaceholder:
    def record_measurement(self, measurement: archive.Measurement) -> int: ...
    def get_records(self) -> RecordedMeasurementsPlaceholder: ...
    def close_connection(self) -> None: ...
    def create_database(self) -> None: ...

class RecordedMeasurementsPlaceholder:
    def __iter__(self) -> Iterator[archive.Record]: ...
    def limit(self, n: int) -> RecordedMeasurementsPlaceholder: ...
    def offset(self, n: int) -> RecordedMeasurementsPlaceholder: ...
    def __len__(self) -> int: ...
    def summarize(self) -> SummarizedMeasurementsPlaceholder: ...
    def summarize_by_interval(
        self, timestamps: list[datetime]
    ) -> SummarizedMeasurementsPlaceholder: ...
    def with_method(self, method: str) -> RecordedMeasurementsPlaceholder: ...
    def with_name(self, name: str) -> RecordedMeasurementsPlaceholder: ...
    def with_name_containing(
        self, substring: str
    ) -> RecordedMeasurementsPlaceholder: ...
    def requested_after(self, t: datetime) -> RecordedMeasurementsPlaceholder: ...
    def requested_before(self, t: datetime) -> RecordedMeasurementsPlaceholder: ...
    def with_id(self, id_: int) -> RecordedMeasurementsPlaceholder: ...
    def first(self) -> archive.Record | None: ...
    def ordered_by_start_time(
        self, ascending: bool = True
    ) -> RecordedMeasurementsPlaceholder: ...

class SummarizedMeasurementsPlaceholder:
    def __iter__(self) -> Iterator[archive.Summary]: ...
    def limit(self, n: int) -> SummarizedMeasurementsPlaceholder: ...
    def offset(self, n: int) -> SummarizedMeasurementsPlaceholder: ...
    def __len__(self) -> int: ...
    def first(self) -> archive.Summary | None: ...
    def sorted_by_avg_elapsed(self, ascending: bool = True) -> Self: ...
    def sorted_by_route_name(self, ascending: bool = True) -> Self: ...
