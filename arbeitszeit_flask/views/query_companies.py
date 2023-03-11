from dataclasses import dataclass

from flask import Response

from arbeitszeit.use_cases import query_companies as use_case
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import CompanySearchForm
from arbeitszeit_flask.template import TemplateRenderer
from arbeitszeit_web.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.presenters.query_companies_presenter import (
    QueryCompaniesPresenter,
    QueryCompaniesViewModel,
)


@dataclass
class QueryCompaniesView:
    search_form: CompanySearchForm
    query_companies: use_case.QueryCompanies
    presenter: QueryCompaniesPresenter
    controller: QueryCompaniesController
    template_name: str
    template_renderer: TemplateRenderer

    def respond_to_post(self, flask_request: FlaskRequest) -> Response:
        if not self.search_form.validate():
            return self._get_invalid_form_response()
        use_case_request = self.controller.import_form_data(
            self.search_form, flask_request
        )
        return self._handle_use_case_request(use_case_request, flask_request)

    def respond_to_get(self, flask_request: FlaskRequest) -> Response:
        return self._handle_use_case_request(
            self.controller.import_form_data(None, flask_request), flask_request
        )

    def _get_invalid_form_response(self) -> Response:
        return Response(
            response=self._render_response_content(
                self.presenter.get_empty_view_model()
            ),
            status=400,
        )

    def _handle_use_case_request(
        self,
        use_case_request: use_case.QueryCompaniesRequest,
        flask_request: FlaskRequest,
    ) -> Response:
        response = self.query_companies(use_case_request)
        view_model = self.presenter.present(response, flask_request)
        return Response(self._render_response_content(view_model))

    def _render_response_content(self, view_model: QueryCompaniesViewModel) -> str:
        return self.template_renderer.render_template(
            self.template_name,
            context=dict(form=self.search_form, view_model=view_model),
        )
