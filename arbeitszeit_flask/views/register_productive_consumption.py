from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect

from arbeitszeit.use_cases.register_productive_consumption import (
    RegisterProductiveConsumption,
)
from arbeitszeit_flask.forms import RegisterProductiveConsumptionForm
from arbeitszeit_flask.template import UserTemplateRenderer
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
    template_renderer: UserTemplateRenderer

    def respond_to_get(self, form: RegisterProductiveConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=200)

    def respond_to_post(self, form: RegisterProductiveConsumptionForm) -> Response:
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
        return self.template_renderer.render_template(
            "company/register_productive_consumption.html", context=dict(form=form)
        )

    def _handle_invalid_form(self, form: RegisterProductiveConsumptionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
