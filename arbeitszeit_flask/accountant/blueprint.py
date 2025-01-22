from functools import wraps
from typing import Any, Callable, TypeVar

from flask import Blueprint, redirect, session, url_for

from arbeitszeit_flask import types
from arbeitszeit_flask.dependency_injection import create_dependency_injector

ViewFunction = TypeVar("ViewFunction", bound=Callable)

main_accountant = Blueprint(
    "main_accountant",
    __name__,
    template_folder="templates",
    static_folder="static",
)


class AccountantRoute:
    def __init__(self, route_string: str, methods: list[str] | None = None) -> None:
        self.route_string = route_string
        self.methods = methods or ["GET"]

    def __call__(self, view_function: ViewFunction) -> ViewFunction:
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> types.Response:
            injector = create_dependency_injector()
            if not user_is_accountant():
                return redirect(url_for("auth.zurueck"))
            return injector.call_with_injection(
                view_function,
                args=args,
                kwargs=kwargs,
            )

        main_accountant.route(self.route_string, methods=self.methods)(_wrapper)
        # We return the original view_function to mimic the behavior
        # of flask itself in this regard. The flask @route decorator
        # also returns the original function that was passed into it.
        return view_function


def user_is_accountant():
    return session.get("user_type") == "accountant"
