from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit_flask.forms import PayMeansOfProductionForm
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from arbeitszeit_web.www.presenters.pay_means_of_production_presenter import (
    PayMeansOfProductionPresenter,
)


@dataclass
class PayMeansOfProductionView:
    controller: PayMeansOfProductionController
    pay_means_of_production: PayMeansOfProduction
    presenter: PayMeansOfProductionPresenter
    template_renderer: UserTemplateRenderer

    def respond_to_get(self, form: PayMeansOfProductionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=200)

    def respond_to_post(self, form: PayMeansOfProductionForm) -> Response:
        if not form.validate():
            return self._handle_invalid_form(form)
        try:
            data = self.controller.process_input_data(form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        use_case_response = self.pay_means_of_production(data)
        view_model = self.presenter.present(use_case_response)
        if view_model.redirect_url:
            return redirect(view_model.redirect_url)
        return FlaskResponse(self._render_template(form), status=200)

    def _render_template(self, form: PayMeansOfProductionForm) -> str:
        return self.template_renderer.render_template(
            "company/transfer_to_company.html", context=dict(form=form)
        )

    def _handle_invalid_form(self, form: PayMeansOfProductionForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
