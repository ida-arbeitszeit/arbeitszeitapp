from dataclasses import dataclass

from flask import Response, render_template, request

from arbeitszeit.use_cases import query_companies as use_case
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import CompanySearchForm
from arbeitszeit_web.www.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.www.presenters.query_companies_presenter import (
    QueryCompaniesPresenter,
    QueryCompaniesViewModel,
)

TEMPLATE_NAME = "user/query_companies.html"


@dataclass
class QueryCompaniesView:
    search_form: CompanySearchForm
    query_companies: use_case.QueryCompaniesUseCase
    presenter: QueryCompaniesPresenter
    controller: QueryCompaniesController
    template_name: str

    def GET(self) -> Response:
        search_form = CompanySearchForm(request.args)
        if not search_form.validate():
            return self._get_invalid_form_response(form=search_form)
        use_case_request = self.controller.import_form_data(
            form=search_form, request=FlaskRequest()
        )
        return self._handle_use_case_request(
            use_case_request=use_case_request,
            search_form=search_form,
        )

    def _get_invalid_form_response(self, form: CompanySearchForm) -> Response:
        return Response(
            response=self._render_response_content(
                view_model=self.presenter.get_empty_view_model(),
                search_form=form,
            ),
            status=400,
        )

    def _handle_use_case_request(
        self,
        use_case_request: use_case.QueryCompaniesRequest,
        search_form: CompanySearchForm,
    ) -> Response:
        response = self.query_companies.execute(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            self._render_response_content(view_model, search_form=search_form)
        )

    def _render_response_content(
        self, view_model: QueryCompaniesViewModel, search_form: CompanySearchForm
    ) -> str:
        return render_template(
            TEMPLATE_NAME,
            form=search_form,
            view_model=view_model,
        )
