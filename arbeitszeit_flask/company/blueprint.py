from functools import wraps
from typing import Any, Callable

from flask import Blueprint, redirect

from arbeitszeit_flask import types
from arbeitszeit_flask.dependency_injection import create_dependency_injector
from arbeitszeit_web.www.authentication import CompanyAuthenticator

main_company = Blueprint("main_company", __name__)


class CompanyRoute:
    def __init__(self, route_string: str, methods=None):
        self.route_string = route_string
        if methods is None:
            self.methods = ["GET"]
        else:
            self.methods = methods

    def __call__(self, view_function: Callable[..., types.Response]):
        @wraps(view_function)
        def _wrapper(*args: Any, **kwargs: Any) -> types.Response:
            injector = create_dependency_injector()
            authenticator = injector.get(CompanyAuthenticator)
            redirect_url = authenticator.redirect_user_to_company_login()
            if redirect_url:
                return redirect(redirect_url)
            return injector.call_with_injection(
                view_function,
                args=args,
                kwargs=kwargs,
            )

        main_company.route(self.route_string, methods=self.methods)(_wrapper)
        # We return the original view_function to mimic the behavior
        # of flask itself in this regard. The flask @route decorator
        # also returns the original function that was passed into it.
        return view_function
