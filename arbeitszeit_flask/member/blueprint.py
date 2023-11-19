from functools import wraps
from typing import Any, Callable, List, Optional

from flask import Blueprint, redirect

from arbeitszeit_flask import types
from arbeitszeit_flask.dependency_injection import with_injection
from arbeitszeit_web.www.authentication import MemberAuthenticator

main_member = Blueprint("main_member", __name__)


class MemberRoute:
    def __init__(self, route_string: str, methods: Optional[List[str]] = None) -> None:
        self.route_string = route_string
        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = methods

    def __call__(self, view_function: Callable[..., types.Response]):
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> types.Response:
            return view_function(*args, **kwargs)

        return self._apply_decorators(_wrapper)

    def _apply_decorators(self, function):
        return main_member.route(self.route_string, methods=self.methods)(
            with_injection()((self._check_is_member_and_confirmed)(function))
        )

    @with_injection()
    def _check_is_member_and_confirmed(
        self,
        func,
        authenticator: MemberAuthenticator,
    ):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            redirect_url = authenticator.redirect_user_to_member_login()
            if redirect_url:
                return redirect(redirect_url)
            else:
                return func(*args, **kwargs)

        return decorated_function
