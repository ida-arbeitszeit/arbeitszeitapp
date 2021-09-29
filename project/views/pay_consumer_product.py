from dataclasses import dataclass
from uuid import UUID

from flask import Response, flash, render_template

from arbeitszeit.use_cases import PayConsumerProduct
from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductPresenter,
)
from project.forms import PayConsumerProductForm


@dataclass
class PayConsumerProductView:
    form: PayConsumerProductForm
    current_user: UUID
    pay_consumer_product: PayConsumerProduct
    controller: PayConsumerProductController
    presenter: PayConsumerProductPresenter

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
        for notification in view_model.notifications:
            flash(notification)
        return Response(self._render_template())

    def _render_template(self) -> str:
        return render_template("member/pay_consumer_product.html", form=self.form)

    def _handle_malformed_data(
        self, result: PayConsumerProductController.MalformedInputData
    ) -> Response:
        field = getattr(self.form, result.field)
        field.errors += (result.message,)
        return Response(self._render_template(), status=400)

    def _handle_invalid_form(self) -> Response:
        return Response(self._render_template(), status=400)
