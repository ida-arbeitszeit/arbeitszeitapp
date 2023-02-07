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
    query_plans: use_cases.QueryPlans
    presenter: QueryPlansPresenter
    controller: QueryPlansController
    template_name: str
    template_renderer: TemplateRenderer

    def respond_to_get(self, form: PlanSearchForm) -> Response:
        if not form.validate():
            return self._get_invalid_form_response(form=form)
        use_case_request = self.controller.import_form_data(form)
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
        self, use_case_request: use_cases.QueryPlansRequest, form: PlanSearchForm
    ) -> Response:
        response = self.query_plans(use_case_request)
        view_model = self.presenter.present(response)
        return Response(self._render_response_content(view_model, form=form))

    def _render_response_content(
        self, view_model: QueryPlansViewModel, form: PlanSearchForm
    ) -> str:
        return self.template_renderer.render_template(
            self.template_name,
            context=dict(form=form, view_model=view_model),
        )
