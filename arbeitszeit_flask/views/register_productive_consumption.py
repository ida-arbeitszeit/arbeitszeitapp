from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import RegisterProductiveConsumptionForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.register_productive_consumption_controller import (
    RegisterProductiveConsumptionController,
)
from arbeitszeit_web.www.presenters.register_productive_consumption_presenter import (
    RegisterProductiveConsumptionPresenter,
)


@dataclass
class RegisterProductiveConsumptionView:
    controller: RegisterProductiveConsumptionController
    register_productive_consumption: RegisterProductiveConsumption
    presenter: RegisterProductiveConsumptionPresenter

    @commit_changes
    def GET(self) -> Response:
        form = RegisterProductiveConsumptionForm(request.form)
        plan_id: str | None = request.args.get("plan_id")
        if plan_id:
            form.plan_id_field().set_value(plan_id)
        return FlaskResponse(self._render_template(form), status=200)

    @commit_changes
    def POST(self) -> Response:
        form = RegisterProductiveConsumptionForm(request.form)
        if not form.validate():
            return self._handle_invalid_form(form)
        try:
            data = self.controller.process_input_data(form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        use_case_response = self.register_productive_consumption(data)
        view_model = self.presenter.present(use_case_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(self._render_template(form), status=200)

    def _render_template(self, form: RegisterProductiveConsumptionForm) -> str:
        return render_template(
            "company/register_productive_consumption.html", form=form
        )

    def _handle_invalid_form(self, form: RegisterProductiveConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
