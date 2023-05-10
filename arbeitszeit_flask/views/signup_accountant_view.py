from dataclasses import dataclass

from flask import Response, redirect, request

from arbeitszeit.use_cases.register_accountant import RegisterAccountantUseCase
from arbeitszeit_flask import types
from arbeitszeit_flask.forms import RegisterAccountantForm
from arbeitszeit_flask.template import AnonymousUserTemplateRenderer
from arbeitszeit_web.controllers.register_accountant_controller import (
    RegisterAccountantController,
)
from arbeitszeit_web.presenters.register_accountant_presenter import (
    RegisterAccountantPresenter,
)


@dataclass
class SignupAccountantView:
    template_renderer: AnonymousUserTemplateRenderer
    controller: RegisterAccountantController
    presenter: RegisterAccountantPresenter
    use_case: RegisterAccountantUseCase

    def handle_request(self, token: str) -> types.Response:
        if request.method == "POST":
            return self.handle_post_request(token)
        else:
            return self.handle_get_request()

    def handle_post_request(self, token: str) -> types.Response:
        form = RegisterAccountantForm(request.form)
        if form.validate() and (
            use_case_request := self.controller.register_accountant(form, token)
        ):
            use_case_response = self.use_case.register_accountant(use_case_request)
            view_model = self.presenter.present_registration_result(use_case_response)
            if view_model.redirect_url:
                return redirect(view_model.redirect_url)
        return Response(
            response=self.template_renderer.render_template(
                "auth/signup_accountant.html",
                context=dict(form=form),
            ),
            status=400,
        )

    def handle_get_request(self) -> types.Response:
        return Response(
            response=self.template_renderer.render_template(
                "auth/signup_accountant.html",
                context=dict(
                    form=RegisterAccountantForm(),
                ),
            ),
            status=200,
        )
