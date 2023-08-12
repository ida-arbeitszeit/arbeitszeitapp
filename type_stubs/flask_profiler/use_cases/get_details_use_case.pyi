from datetime import datetime
from flask_profiler.entities import measurement_archive as measurement_archive
from typing import List, Optional

class Measurement:
    name: str
    method: str
    response_time_secs: float
    started_at: datetime
    def __init__(self, name, method, response_time_secs, started_at) -> None: ...

class Request:
    limit: int
    offset: int
    name_filter: Optional[str]
    method_filter: Optional[str]
    requested_after: Optional[datetime]
    requested_before: Optional[datetime]
    def __init__(self, limit, offset, name_filter, method_filter, requested_after, requested_before) -> None: ...

class Response:
    measurements: List[Measurement]
    request: Request
    total_result_count: int
    def __init__(self, measurements, request, total_result_count) -> None: ...

class GetDetailsUseCase:
    archivist: measurement_archive.MeasurementArchivist
    def get_details(self, request: Request) -> Response: ...
    def __init__(self, archivist) -> None: ...
