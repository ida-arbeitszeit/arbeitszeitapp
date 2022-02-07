from dataclasses import dataclass

from flask import Response

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit_flask.template import UserTemplateRenderer
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

    def respond_to_get(self, form):
        return Response(self._render_template(form), status=200)

    def respond_to_post(self, form):
        data = self.controller.process_input_data(form)
        if isinstance(data, PayMeansOfProductionController.MalformedInputData):
            self.presenter.present_malformed_data_warnings(data)
            return Response(self._render_template(form), status=400)
        use_case_response = self.pay_means_of_production(data)
        self.presenter.present(use_case_response)
        return Response(self._render_template(form), status=200)

    def _render_template(self, form) -> str:
        return self.template_renderer.render_template(
            "company/transfer_to_company.html", context=dict(form=form)
        )
