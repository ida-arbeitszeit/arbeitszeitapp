from _typeshed import Incomplete
from flask import Response as FlaskResponse

from .dependency_injector import DependencyInjector as DependencyInjector
from .response import HttpResponse as HttpResponse

logger: Incomplete
auth: Incomplete
flask_profiler: Incomplete

def render_response(response: HttpResponse) -> FlaskResponse: ...
@auth.verify_password
def verify_password(username: str, password: str) -> bool: ...
@auth.login_required
def summary() -> FlaskResponse: ...
@auth.login_required
def details() -> FlaskResponse: ...
@auth.login_required
def route_overview(route_name: str) -> FlaskResponse: ...
@flask_profiler.after_request
def x_robots_tag_header(response: FlaskResponse) -> FlaskResponse: ...
