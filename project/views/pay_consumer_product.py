from dataclasses import dataclass
from uuid import UUID

from flask import Response, flash

from arbeitszeit.use_cases import PayConsumerProduct, PayConsumerProductResponse
from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductPresenter,
)
from arbeitszeit_web.template import TemplateRenderer
from project.forms import PayConsumerProductForm


@dataclass
class PayConsumerProductView:
    form: PayConsumerProductForm
    current_user: UUID
    pay_consumer_product: PayConsumerProduct
    controller: PayConsumerProductController
    presenter: PayConsumerProductPresenter
    template_renderer: TemplateRenderer

    def respond_to_get(self) -> Response:
        return Response(self._render_template())

    def respond_to_post(self) -> Response:
        if not self.form.validate():
            return self._handle_invalid_form()
        use_case_request = self.controller.import_form_data(
            self.current_user, self.form
        )
        if isinstance(use_case_request, self.controller.MalformedInputData):
            return self._handle_malformed_data(use_case_request)
        response = self.pay_consumer_product(use_case_request)
        view_model = self.presenter.present(response)
        return Response(self._render_template(), status=view_model.status_code)

    def _render_template(self) -> str:
        return self.template_renderer.render_template(
            "member/pay_consumer_product.html", context=dict(form=self.form)
        )

    def _handle_malformed_data(
        self, result: PayConsumerProductController.MalformedInputData
    ) -> Response:
        field = getattr(self.form, result.field)
        field.errors += (result.message,)
        return Response(self._render_template(), status=400)

    def _handle_invalid_form(self) -> Response:
        return Response(self._render_template(), status=400)
