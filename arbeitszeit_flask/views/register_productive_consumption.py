from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumptionUseCase,
)
from arbeitszeit.use_cases.select_productive_consumption import (
    SelectProductiveConsumptionUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import RegisterProductiveConsumptionForm
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.register_productive_consumption_controller import (
    RegisterProductiveConsumptionController,
)
from arbeitszeit_web.www.controllers.select_productive_consumption_controller import (
    SelectProductiveConsumptionController,
)
from arbeitszeit_web.www.presenters.register_productive_consumption_presenter import (
    RegisterProductiveConsumptionPresenter,
)
from arbeitszeit_web.www.presenters.select_productive_consumption_presenter import (
    SelectProductiveConsumptionPresenter,
)


@dataclass
class RegisterProductiveConsumptionView:
    select_productive_consumption_controller: SelectProductiveConsumptionController
    select_productive_consumption_use_case: SelectProductiveConsumptionUseCase
    select_productive_consumption_presenter: SelectProductiveConsumptionPresenter
    controller: RegisterProductiveConsumptionController
    register_productive_consumption: RegisterProductiveConsumptionUseCase
    presenter: RegisterProductiveConsumptionPresenter

    def GET(self) -> Response:
        try:
            use_case_request = (
                self.select_productive_consumption_controller.process_input_data(
                    FlaskRequest()
                )
            )
        except self.select_productive_consumption_controller.InputDataError:
            return self._handle_invalid_form(RegisterProductiveConsumptionForm())
        use_case_response = (
            self.select_productive_consumption_use_case.select_productive_consumption(
                use_case_request
            )
        )
        view_model = self.select_productive_consumption_presenter.render_response(
            use_case_response
        )
        form = RegisterProductiveConsumptionForm(
            plan_id=view_model.plan_id,
            amount=view_model.amount,
            type_of_consumption=(
                "fixed" if view_model.is_consumption_of_fixed_means else "liquid"
            ),
        )
        return FlaskResponse(
            render_template(
                "company/register_productive_consumption.html",
                form=form,
                view_model=view_model,
            ),
            status=view_model.status_code,
        )

    @commit_changes
    def POST(self) -> Response:
        form = RegisterProductiveConsumptionForm(request.form)
        if not form.validate():
            return self._handle_invalid_form(form)
        try:
            data = self.controller.process_input_data(form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        use_case_response = self.register_productive_consumption.execute(data)
        view_model = self.presenter.present(use_case_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(self._render_template(form), status=400)

    def _render_template(self, form: RegisterProductiveConsumptionForm) -> str:
        return render_template(
            "company/register_productive_consumption.html", form=form, view_model=None
        )

    def _handle_invalid_form(self, form: RegisterProductiveConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
