from dataclasses import dataclass

from flask import redirect, render_template, url_for
from flask_login import current_user

from arbeitszeit.use_cases.register_company import RegisterCompany
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import RegisterForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.controllers.register_company_controller import (
    RegisterCompanyController,
)
from arbeitszeit_web.presenters.register_company_presenter import (
    RegisterCompanyPresenter,
)


@dataclass
class SignupCompanyView:
    register_company: RegisterCompany
    controller: RegisterCompanyController
    presenter: RegisterCompanyPresenter
    flask_session: FlaskSession

    def handle_request(self, request) -> Response:
        register_form = RegisterForm(request.form)
        if request.method == "POST" and register_form.validate():
            return self._handle_successful_post_request(register_form)
        if current_user.is_authenticated:
            if self.flask_session.is_logged_in_as_company():
                return redirect(url_for("main_company.dashboard"))
            else:
                self.flask_session.logout()
        return render_template("auth/signup_company.html", form=register_form)

    def _handle_successful_post_request(self, register_form: RegisterForm) -> Response:
        use_case_request = self.controller.create_request(register_form)
        response = self.register_company.register_company(use_case_request)
        view_model = self.presenter.present_company_registration(
            response=response, form=register_form
        )
        if view_model.is_success_view:
            return redirect(url_for("auth.unconfirmed_company"))
        return render_template("auth/signup_company.html", form=register_form)
