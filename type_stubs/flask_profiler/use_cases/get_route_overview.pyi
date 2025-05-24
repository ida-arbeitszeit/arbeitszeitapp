import enum
from dataclasses import dataclass
from datetime import datetime

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

@dataclass
class Request:
    route_name: str
    interval: Interval
    start_time: datetime | None
    end_time: datetime

@dataclass
class Response:
    request: Request
    timeseries: dict[str, list[IntervalMeasurement]]

class Interval(enum.Enum):
    daily = ...

@dataclass
class IntervalMeasurement:
    timestamp: datetime
    value: float | None
