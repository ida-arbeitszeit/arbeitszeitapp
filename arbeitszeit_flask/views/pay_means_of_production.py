from dataclasses import dataclass

from flask import Response, redirect

from arbeitszeit.use_cases.pay_means_of_production import PayMeansOfProduction
from arbeitszeit_flask.forms import PayMeansOfProductionForm
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

    def respond_to_get(self, form: PayMeansOfProductionForm):
        return Response(self._render_template(form), status=200)

    def respond_to_post(self, form: PayMeansOfProductionForm):
        if form.validate():
            data = self.controller.process_input_data(form)
            use_case_response = self.pay_means_of_production(data)
            view_model = self.presenter.present(use_case_response)
            if view_model.redirect_url:
                return redirect(view_model.redirect_url)
            return Response(self._render_template(form), status=200)
        else:
            return Response(self._render_template(form), status=400)

    def _render_template(self, form: PayMeansOfProductionForm) -> str:
        return self.template_renderer.render_template(
            "company/transfer_to_company.html", context=dict(form=form)
        )
