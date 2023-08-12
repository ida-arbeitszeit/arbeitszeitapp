import enum
from _typeshed import Incomplete
from datetime import datetime
from flask_profiler.entities import measurement_archive as measurement_archive
from typing import List, Optional

class SortingField(enum.Enum):
    average_time: Incomplete
    route_name: Incomplete
    none: Incomplete

class SortingOrder(enum.Enum):
    ascending: Incomplete
    descending: Incomplete

class Measurement:
    name: str
    method: str
    request_count: int
    average_response_time_secs: float
    min_response_time_secs: float
    max_response_time_secs: float
    def __init__(self, name, method, request_count, average_response_time_secs, min_response_time_secs, max_response_time_secs) -> None: ...

class Request:
    limit: int
    offset: int
    sorting_order: SortingOrder
    sorting_field: SortingField
    method: Optional[str]
    name_filter: Optional[str]
    requested_after: Optional[datetime]
    requested_before: Optional[datetime]
    def __init__(self, limit, offset, sorting_order, sorting_field, method, name_filter, requested_after, requested_before) -> None: ...

class Response:
    measurements: List[Measurement]
    total_results: int
    request: Request
    def __init__(self, measurements, total_results, request) -> None: ...

class GetSummaryUseCase:
    archivist: measurement_archive.MeasurementArchivist
    def get_summary(self, request: Request) -> Response: ...
    def __init__(self, archivist) -> None: ...
