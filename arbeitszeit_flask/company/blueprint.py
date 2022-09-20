from functools import wraps
from typing import Any, Callable
from uuid import UUID

from flask import Blueprint, redirect, url_for
from flask_login import current_user, login_required

from arbeitszeit_flask import types
from arbeitszeit_flask.database.repositories import CompanyRepository
from arbeitszeit_flask.dependency_injection import CompanyModule, with_injection

main_company = Blueprint(
    "main_company", __name__, template_folder="templates", static_folder="static"
)


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
            return view_function(*args, **kwargs)

        return self._apply_decorators(_wrapper)

    def _apply_decorators(self, function):
        injection = with_injection([CompanyModule()])
        return main_company.route(self.route_string, methods=self.methods)(
            injection(login_required(injection(check_confirmed)(function)))
        )


def check_confirmed(func, company_repository: CompanyRepository):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not company_repository.is_company_confirmed(UUID(current_user.id)):
            return redirect(url_for("auth.zurueck"))
        return func(*args, **kwargs)

    return decorated_function
