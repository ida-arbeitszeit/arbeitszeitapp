from dataclasses import dataclass
from typing import Optional

from flask import Response as FlaskResponse
from flask import redirect, request, url_for

from arbeitszeit.use_cases.pay_consumer_product import PayConsumerProduct
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import PayConsumerProductForm
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductPresenter,
)


@dataclass
class PayConsumerProductView:
    flask_session: FlaskSession
    pay_consumer_product: PayConsumerProduct
    controller: PayConsumerProductController
    presenter: PayConsumerProductPresenter
    template_renderer: TemplateRenderer

    def respond_to_get(self, form: PayConsumerProductForm) -> Response:
        amount: Optional[str] = request.args.get("amount")
        plan_id: Optional[str] = request.args.get("plan_id")
        if amount:
            form.amount_field().set_value(amount)
        if plan_id:
            form.plan_id_field().set_value(plan_id)
        return FlaskResponse(self._render_template(form=form))

    def respond_to_post(self, form: PayConsumerProductForm) -> Response:
        if not form.validate():
            return self._handle_invalid_form(form)
        current_user = self.flask_session.get_current_user()
        assert current_user
        try:
            use_case_request = self.controller.import_form_data(current_user, form)
        except self.controller.FormError:
            return self._handle_invalid_form(form)
        response = self.pay_consumer_product.pay_consumer_product(use_case_request)
        view_model = self.presenter.present(response)
        if view_model.status_code == 200:
            return redirect(url_for("main_member.pay_consumer_product"))
        return FlaskResponse(
            self._render_template(form=form), status=view_model.status_code
        )

    def _render_template(self, form: PayConsumerProductForm) -> str:
        return self.template_renderer.render_template(
            "member/pay_consumer_product.html", context=dict(form=form)
        )

    def _handle_invalid_form(self, form: PayConsumerProductForm) -> Response:
        return FlaskResponse(self._render_template(form), status=400)
