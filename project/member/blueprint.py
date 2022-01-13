from functools import wraps
from typing import Any, Callable

from flask import Blueprint, Response, redirect, session, url_for
from flask_login import current_user, login_required

from project.dependency_injection import with_injection

main_member = Blueprint(
    "main_member", __name__, template_folder="templates", static_folder="static"
)


class MemberRoute:
    def __init__(self, route_string: str, methods=None):
        self.route_string = route_string
        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = methods

    def __call__(self, view_function: Callable[..., Response]):
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> Response:
            if not user_is_member():
                return redirect(url_for("auth.zurueck"))
            return view_function(*args, **kwargs)

        return self._apply_decorators(_wrapper)

    def _apply_decorators(self, function):
        return main_member.route(self.route_string, methods=self.methods)(
            with_injection()(login_required(check_confirmed(function)))
        )


def user_is_member():
    return session.get("user_type") == "member"


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not user_is_confirmed(current_user):
            return redirect(url_for("auth.unconfirmed_user"))
        return func(*args, **kwargs)

    return decorated_function


def user_is_confirmed(current_user) -> bool:
    try:
        return current_user.confirmed_on is not None
    except Exception:
        return False
