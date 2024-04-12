import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from _typeshed import Incomplete
from flask_profiler.calendar import Calendar as Calendar
from flask_profiler.entities.measurement_archive import (
    MeasurementArchivist as MeasurementArchivist,
)
from flask_profiler.entities.measurement_archive import (
    RecordedMeasurements as RecordedMeasurements,
)

@dataclass
class GetRouteOverviewUseCase:
    archivist: MeasurementArchivist
    calendar: Calendar
    def get_route_overview(self, request: Request) -> Response: ...
    def __init__(self, archivist, calendar) -> None: ...

@dataclass
class Request:
    route_name: str
    interval: Interval
    start_time: datetime | None
    end_time: datetime
    def __init__(self, route_name, interval, start_time, end_time) -> None: ...

@dataclass
class Response:
    request: Request
    timeseries: Dict[str, List[IntervalMeasurement]]
    def __init__(self, request, timeseries) -> None: ...

class Interval(enum.Enum):
    daily: Incomplete

@dataclass
class IntervalMeasurement:
    timestamp: datetime
    value: float | None
    def __init__(self, timestamp, value) -> None: ...
