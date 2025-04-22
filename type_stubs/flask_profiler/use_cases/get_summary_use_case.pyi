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

@dataclass
class Response:
    measurements: list[Measurement]
    total_results: int
    request: Request

@dataclass
class GetSummaryUseCase:
    archivist: measurement_archive.MeasurementArchivist
    def get_summary(self, request: Request) -> Response: ...
