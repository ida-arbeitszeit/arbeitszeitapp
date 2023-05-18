from dataclasses import dataclass
from typing import Optional

from flask import Response as FlaskResponse
from flask import redirect, request

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit_flask.forms import PayMeansOfProductionForm
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.controllers.pay_means_of_production_controller import (
    PayMeansOfProductionController,
)
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter


@dataclass
class PayMeansOfProductionView:
    controller: PayMeansOfProductionController
    pay_means_of_production: PayMeansOfProduction
    presenter: PayMeansOfProductionPresenter
    template_renderer: UserTemplateRenderer

    def respond_to_get(self, form: PayMeansOfProductionForm) -> Response:
        plan_id: Optional[str] = request.args.get("plan_id")
        amount: Optional[str] = request.args.get("amount")
        type_of_payment: Optional[str] = request.args.get("type_of_payment")
        if plan_id:
            form.plan_id_field().set_value(plan_id)
        if amount:
            form.amount_field().set_value(amount)
        if type_of_payment:
            form.type_of_payment_field().set_value(type_of_payment)
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
