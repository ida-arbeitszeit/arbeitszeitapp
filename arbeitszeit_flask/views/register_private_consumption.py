from dataclasses import dataclass
from typing import Optional

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumption,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import RegisterPrivateConsumptionForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.register_private_consumption_controller import (
    RegisterPrivateConsumptionController,
)
from arbeitszeit_web.www.presenters.register_private_consumption_presenter import (
    RegisterPrivateConsumptionPresenter,
)


@dataclass
class RegisterPrivateConsumptionView:
    flask_session: FlaskSession
    register_private_consumption: RegisterPrivateConsumption
    controller: RegisterPrivateConsumptionController
    presenter: RegisterPrivateConsumptionPresenter

    @commit_changes
    def GET(self) -> Response:
        form = RegisterPrivateConsumptionForm(request.form)
        amount: Optional[str] = request.args.get("amount")
        plan_id: Optional[str] = request.args.get("plan_id")
        if amount:
            form.amount_field().set_value(amount)
        if plan_id:
            form.plan_id_field().set_value(plan_id)
        return FlaskResponse(self._render_template(form=form))

    @commit_changes
    def POST(self) -> Response:
        form = RegisterPrivateConsumptionForm(request.form)
        if not form.validate():
            return self._handle_invalid_form(form)
        current_user = self.flask_session.get_current_user()
        assert current_user
        try:
            use_case_request = self.controller.import_form_data(current_user, form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        response = self.register_private_consumption.register_private_consumption(
            use_case_request
        )
        view_model = self.presenter.present(response)
        if view_model.status_code == 200:
            return redirect(url_for("main_member.register_private_consumption"))
        return FlaskResponse(
            self._render_template(form=form), status=view_model.status_code
        )

    def _render_template(self, form: RegisterPrivateConsumptionForm) -> str:
        return render_template("member/register_private_consumption.html", form=form)

    def _handle_invalid_form(self, form: RegisterPrivateConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
