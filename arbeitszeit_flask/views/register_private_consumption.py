from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.register_private_consumption import (
    RegisterPrivateConsumption,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_web.forms import RegisterPrivateConsumptionForm
from arbeitszeit_web.www.controllers.register_private_consumption_controller import (
    RegisterPrivateConsumptionController,
)
from arbeitszeit_web.www.presenters.register_private_consumption_presenter import (
    Redirect,
    RegisterPrivateConsumptionPresenter,
    RenderForm,
)


@dataclass
class RegisterPrivateConsumptionView:
    flask_session: FlaskSession
    register_private_consumption: RegisterPrivateConsumption
    controller: RegisterPrivateConsumptionController
    presenter: RegisterPrivateConsumptionPresenter

    def GET(self) -> Response:
        form = RegisterPrivateConsumptionForm(
            amount_value=request.args.get("amount") or "",
            plan_id_value=request.args.get("plan_id") or "",
        )
        return FlaskResponse(self._render_template(form=form))

    @commit_changes
    def POST(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        try:
            use_case_request = self.controller.import_form_data(
                current_user, FlaskRequest()
            )
        except self.controller.FormError as error:
            return FlaskResponse(self._render_template(error.form), status=400)
        response = self.register_private_consumption.register_private_consumption(
            use_case_request
        )
        view_model = self.presenter.present(response, request=FlaskRequest())
        match view_model:
            case Redirect(url):
                return redirect(url)
            case RenderForm(status_code=status_code, form=form):
                return FlaskResponse(
                    render_template(
                        "member/register_private_consumption.html", form=form
                    ),
                    status=status_code,
                )

    def _render_template(self, form: RegisterPrivateConsumptionForm) -> str:
        return render_template("member/register_private_consumption.html", form=form)
