from functools import wraps
from typing import Any, Callable

from flask import Blueprint, redirect, url_for

from arbeitszeit_flask import types
from arbeitszeit_flask.database.repositories import CompanyRepository
from arbeitszeit_flask.dependency_injection import CompanyModule, with_injection
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_web.notification import Notifier
from arbeitszeit_web.translator import Translator

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
            injection((self._check_is_company_and_confirmed)(function))
        )

    @with_injection([CompanyModule()])
    def _check_is_company_and_confirmed(
        self,
        func,
        company_repository: CompanyRepository,
        session: FlaskSession,
        notifier: Notifier,
        translator: Translator,
    ):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            user_id = session.get_current_user()
            if not user_id:
                # not an authenticated user
                notifier.display_warning(
                    translator.gettext("Please log in to view this page.")
                )
                return redirect(url_for("auth.start", next=self.route_string))
            elif not company_repository.is_company(user_id):
                # not a company
                notifier.display_warning(
                    translator.gettext("You are not logged with the correct account.")
                )
                session.logout()
                return redirect(url_for("auth.start", next=self.route_string))
            elif not company_repository.is_company_confirmed(user_id):
                # not a confirmed company
                return redirect(url_for("auth.unconfirmed_company"))
            return func(*args, **kwargs)

        return decorated_function
