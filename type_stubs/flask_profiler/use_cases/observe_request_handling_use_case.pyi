from dataclasses import dataclass
from typing import Any

from flask_profiler.clock import Clock as Clock
from flask_profiler.entities.measurement_archive import Measurement as Measurement
from flask_profiler.entities.measurement_archive import (
    MeasurementArchivist as MeasurementArchivist,
)
from flask_profiler.entities.request_handler import RequestHandler as RequestHandler

@dataclass
class Request:
    request_args: Any
    request_kwargs: Any
    method: str
    def __init__(self, request_args, request_kwargs, method) -> None: ...

@dataclass
class Response:
    request_handler_response: Any
    def __init__(self, request_handler_response) -> None: ...

@dataclass
class ObserveRequestHandlingUseCase:
    archivist: MeasurementArchivist
    clock: Clock
    request_handler: RequestHandler
    def record_measurement(self, request: Request) -> Response: ...
    def __init__(self, archivist, clock, request_handler) -> None: ...
