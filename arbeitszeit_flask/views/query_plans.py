from dataclasses import dataclass

from flask import Response

from arbeitszeit import use_cases
from arbeitszeit_flask.forms import PlanSearchForm
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_web.query_plans import (
    QueryPlansController,
    QueryPlansPresenter,
    QueryPlansViewModel,
)


@dataclass
class QueryPlansView:
    search_form: PlanSearchForm
    query_plans: use_cases.QueryPlans
    presenter: QueryPlansPresenter
    controller: QueryPlansController
    template_name: str
    template_renderer: TemplateRenderer

    def respond_to_post(self) -> Response:
        if not self.search_form.validate():
            return self._get_invalid_form_response()
        use_case_request = self.controller.import_form_data(self.search_form)
        return self._handle_use_case_request(use_case_request)

    def respond_to_get(self) -> Response:
        return self._handle_use_case_request(self.controller.import_form_data(None))

    def _get_invalid_form_response(self) -> Response:
        return Response(
            response=self._render_response_content(
                self.presenter.get_empty_view_model()
            ),
            status=400,
        )

    def _handle_use_case_request(
        self, use_case_request: use_cases.QueryPlansRequest
    ) -> Response:
        response = self.query_plans(use_case_request)
        view_model = self.presenter.present(response)
        return Response(self._render_response_content(view_model))

    def _render_response_content(self, view_model: QueryPlansViewModel) -> str:
        return self.template_renderer.render_template(
            self.template_name,
            context=dict(form=self.search_form, view_model=view_model),
        )
