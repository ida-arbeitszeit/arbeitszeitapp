from functools import wraps
from typing import Any

from flask import request

from arbeitszeit_flask.dependency_injection import create_dependency_injector
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_501


def _not_implemented_view(*args: Any, **kwargs: Any) -> Response:
    return http_501()


class as_flask_view:
    def __call__(self, view_class):
        @wraps(view_class)
        def wrapper(*args, **kwargs):
            injector = create_dependency_injector()
            view = injector.get(view_class)
            dispatched_method = getattr(view, request.method, _not_implemented_view)
            return dispatched_method(*args, **kwargs)

        return wrapper
