from dataclasses import dataclass
from datetime import datetime

from flask_profiler.entities import measurement_archive as measurement_archive

@dataclass
class Measurement:
    name: str
    method: str
    response_time_secs: float
    started_at: datetime
    def __init__(self, name, method, response_time_secs, started_at) -> None: ...

@dataclass
class Request:
    limit: int
    offset: int
    name_filter: str | None = ...
    method_filter: str | None = ...
    requested_after: datetime | None = ...
    requested_before: datetime | None = ...
    def __init__(
        self,
        limit,
        offset,
        name_filter=...,
        method_filter=...,
        requested_after=...,
        requested_before=...,
    ) -> None: ...

@dataclass
class Response:
    measurements: list[Measurement]
    request: Request
    total_result_count: int
    def __init__(self, measurements, request, total_result_count) -> None: ...

@dataclass
class GetDetailsUseCase:
    archivist: measurement_archive.MeasurementArchivist
    def get_details(self, request: Request) -> Response: ...
    def __init__(self, archivist) -> None: ...
