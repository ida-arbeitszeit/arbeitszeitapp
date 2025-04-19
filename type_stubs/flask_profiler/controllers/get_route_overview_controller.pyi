from dataclasses import dataclass

from flask_profiler.clock import Clock as Clock
from flask_profiler.request import HttpRequest as HttpRequest
from flask_profiler.use_cases import get_route_overview as uc

@dataclass
class GetRouteOverviewController:
    clock: Clock
    http_request: HttpRequest
    def handle_request(self) -> uc.Request: ...
