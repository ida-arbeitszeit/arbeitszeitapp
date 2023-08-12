from .dependency_injector import DependencyInjector as DependencyInjector
from .flask_profiler import flask_profiler as flask_profiler
from .measured_route import MeasuredRouteFactory as MeasuredRouteFactory
from _typeshed import Incomplete
from flask import Flask as Flask

logger: Incomplete

class RouteWrapper:
    measured_route_factory: MeasuredRouteFactory
    def wrap_all_routes(self, app: Flask) -> None: ...
    def __init__(self, measured_route_factory) -> None: ...

def init_app(app: Flask) -> None: ...
