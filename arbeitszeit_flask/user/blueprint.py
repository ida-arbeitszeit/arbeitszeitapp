from functools import wraps
from typing import Callable, TypeVar

from flask import Blueprint, redirect, request, url_for

from arbeitszeit_flask import types
from arbeitszeit_flask.dependency_injection import create_dependency_injector
from arbeitszeit_flask.views.http_error_view import http_403
from arbeitszeit_web.www.authentication import UserAuthenticator

ViewFunction = TypeVar("ViewFunction", bound=Callable)


user_blueprint = Blueprint("main_user", __name__)


class AuthenticatedUserRoute:
    def __init__(self, route_string: str, methods: list[str] | None = None) -> None:
        self.route_string = route_string
        self.methods = methods or ["GET"]

    def __call__(self, view_function: ViewFunction) -> ViewFunction:
        @wraps(view_function)
        def wrapper(*args, **kwargs) -> types.Response:
            injector = create_dependency_injector()
            authenticator = injector.get(UserAuthenticator)
            if not authenticator.is_user_authenticated():
                if request.method == "GET":
                    # Security: FlaskSession has a check implemented when we
                    # set_next_url
                    session = injector.get(FlaskSession)
                    session.set_next_url(request.url)
                    return redirect(url_for("auth.start"))
                else:
                    return http_403()
            return injector.call_with_injection(
                view_function,
                args=args,
                kwargs=kwargs,
            )

        user_blueprint.route(self.route_string, methods=self.methods)(wrapper)
        # We return the original view_function to mimic the behavior
        # of flask itself in this regard. The flask @route decorator
        # also returns the original function that was passed into it.
        return view_function
