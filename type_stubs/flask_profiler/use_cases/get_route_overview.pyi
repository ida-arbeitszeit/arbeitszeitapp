import enum
from _typeshed import Incomplete
from datetime import datetime
from flask_profiler.calendar import Calendar as Calendar
from flask_profiler.entities.measurement_archive import MeasurementArchivist as MeasurementArchivist, RecordedMeasurements as RecordedMeasurements
from typing import Dict, List, Optional

class GetRouteOverviewUseCase:
    archivist: MeasurementArchivist
    calendar: Calendar
    def get_route_overview(self, request: Request) -> Response: ...
    def __init__(self, archivist, calendar) -> None: ...

class Request:
    route_name: str
    interval: Interval
    start_time: Optional[datetime]
    end_time: datetime
    def __init__(self, route_name, interval, start_time, end_time) -> None: ...

class Response:
    request: Request
    timeseries: Dict[str, List[IntervalMeasurement]]
    def __init__(self, request, timeseries) -> None: ...

class Interval(enum.Enum):
    daily: Incomplete

class IntervalMeasurement:
    timestamp: datetime
    value: Optional[float]
    def __init__(self, timestamp, value) -> None: ...
