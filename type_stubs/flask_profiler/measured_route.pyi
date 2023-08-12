from .clock import Clock as Clock
from .configuration import Configuration as Configuration
from .entities.measurement_archive import MeasurementArchivist as MeasurementArchivist
from .use_cases import observe_request_handling_use_case as use_case
from _typeshed import Incomplete
from flask import Response as FlaskResponse
from typing import Any, Callable, Union

ResponseT = Union[str, FlaskResponse]
logger: Incomplete

class RequestHandler:
    original_route: Incomplete
    def __init__(self, route_name: str, original_route: Callable) -> None: ...
    def handle_request(self, args: Any, kwargs: Any) -> Any: ...
    def name(self) -> str: ...

class MeasuredRoute:
    use_case: use_case.ObserveRequestHandlingUseCase
    request_handler: RequestHandler
    def __call__(self, *args: Any, **kwargs: Any) -> ResponseT: ...
    def __init__(self, use_case, request_handler) -> None: ...

class MeasuredRouteFactory:
    clock: Clock
    config: Configuration
    archivist: MeasurementArchivist
    def create_measured_route(self, route_name: str, original_route: Callable[..., ResponseT]) -> MeasuredRoute: ...
    def __init__(self, clock, config, archivist) -> None: ...
