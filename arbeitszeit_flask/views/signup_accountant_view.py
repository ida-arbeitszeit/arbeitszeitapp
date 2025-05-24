from dataclasses import dataclass

from flask import Response, redirect, render_template, request

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit_flask import types
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import RegisterAccountantForm
from arbeitszeit_web.www.controllers.register_accountant_controller import (
    RegisterAccountantController,
)
from arbeitszeit_web.www.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)


@dataclass
class SignupAccountantView:
    controller: RegisterAccountantController
    presenter: RegisterAccountantPresenter
    use_case: RegisterAccountantUseCase

    def GET(self, token: str) -> types.Response:
        return Response(
            response=render_template(
                "auth/signup_accountant.html",
                form=RegisterAccountantForm(),
            ),
            status=200,
        )

    @commit_changes
    def POST(self, token: str) -> types.Response:
        form = RegisterAccountantForm(request.form)
        extracted_token = self.controller.extract_token(token=token)
        if extracted_token:
            form.extracted_token = extracted_token
            if form.validate():
                use_case_request = self.controller.create_use_case_request(form=form)
                use_case_response = self.use_case.register_accountant(use_case_request)
                view_model = self.presenter.present_registration_result(
                    use_case_response
                )
                if view_model.redirect_url:
                    return redirect(view_model.redirect_url)
        return Response(
            response=render_template(
                "auth/signup_accountant.html",
                form=form,
            ),
            status=400,
        )
