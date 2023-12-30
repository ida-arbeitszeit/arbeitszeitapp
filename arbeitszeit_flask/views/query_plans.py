from dataclasses import dataclass

from flask import Response, render_template, request

from arbeitszeit.use_cases import query_plans as use_case
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import PlanSearchForm
from arbeitszeit_web.query_plans import (
    QueryPlansController,
    QueryPlansPresenter,
    QueryPlansViewModel,
)

TEMPLATE_NAME = "user/query_plans.html"


@dataclass
class QueryPlansView:
    query_plans: use_case.QueryPlans
    presenter: QueryPlansPresenter
    controller: QueryPlansController
    request: FlaskRequest

    def GET(self) -> Response:
        form = PlanSearchForm(request.form)
        if not form.validate():
            return self._get_invalid_form_response(form=form)
        use_case_request = self.controller.import_form_data(form, self.request)
        return self._handle_use_case_request(use_case_request, form=form)

    def _get_invalid_form_response(self, form: PlanSearchForm) -> Response:
        return Response(
            response=self._render_response_content(
                self.presenter.get_empty_view_model(),
                form=form,
            ),
            status=400,
        )

    def _handle_use_case_request(
        self,
        use_case_request: use_case.QueryPlansRequest,
        form: PlanSearchForm,
    ) -> Response:
        response = self.query_plans(use_case_request)
        view_model = self.presenter.present(response, self.request)
        return Response(self._render_response_content(view_model, form=form))

    def _render_response_content(
        self, view_model: QueryPlansViewModel, form: PlanSearchForm
    ) -> str:
        return render_template(
            TEMPLATE_NAME,
            form=form,
            view_model=view_model,
        )
