import enum
from dataclasses import dataclass
from datetime import datetime

from flask_profiler.entities import measurement_archive as measurement_archive

class SortingField(enum.Enum):
    average_time = ...
    route_name = ...
    none = ...

class SortingOrder(enum.Enum):
    ascending = ...
    descending = ...

@dataclass
class Measurement:
    name: str
    method: str
    request_count: int
    average_response_time_secs: float
    min_response_time_secs: float
    max_response_time_secs: float
    def __init__(
        self,
        name,
        method,
        request_count,
        average_response_time_secs,
        min_response_time_secs,
        max_response_time_secs,
    ) -> None: ...

@dataclass
class Request:
    limit: int
    offset: int
    sorting_order: SortingOrder
    sorting_field: SortingField
    method: str | None = ...
    name_filter: str | None = ...
    requested_after: datetime | None = ...
    requested_before: datetime | None = ...
    def __init__(
        self,
        limit,
        offset,
        sorting_order,
        sorting_field,
        method=...,
        name_filter=...,
        requested_after=...,
        requested_before=...,
    ) -> None: ...

@dataclass
class Response:
    measurements: list[Measurement]
    total_results: int
    request: Request
    def __init__(self, measurements, total_results, request) -> None: ...

@dataclass
class GetSummaryUseCase:
    archivist: measurement_archive.MeasurementArchivist
    def get_summary(self, request: Request) -> Response: ...
    def __init__(self, archivist) -> None: ...
