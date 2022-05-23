from functools import wraps
from typing import Any, Callable, Iterable, Optional

from flask import Blueprint, redirect, session, url_for
from flask_login import login_required

from arbeitszeit_flask import types
from arbeitszeit_flask.dependency_injection import with_injection

main_accountant = Blueprint(
    "main_accountant",
    __name__,
    template_folder="templates",
    static_folder="static",
)


class AccountantRoute:
    def __init__(self, route_string: str, methods: Optional[Iterable[str]] = None):
        self.route_string = route_string
        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = list(methods)

    def __call__(self, view_function: Callable[..., types.Response]):
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> types.Response:
            if not user_is_accountant():
                return redirect(url_for("auth.zurueck"))
            return view_function(*args, **kwargs)

        return self._apply_decorators(_wrapper)

    def _apply_decorators(self, function):
        return main_accountant.route(self.route_string, methods=self.methods)(
            with_injection()(login_required(function))
        )


def user_is_accountant():
    return session.get("user_type") == "accountant"
