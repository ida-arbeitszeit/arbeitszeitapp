from dataclasses import dataclass

from flask import Response, render_template_string

from arbeitszeit import use_cases
from arbeitszeit_web.query_products import (
    QueryProductsController,
    QueryProductsPresenter,
    QueryProductsViewModel,
)
from project.forms import ProductSearchForm


@dataclass
class QueryProductsView:
    search_form: ProductSearchForm
    query_products: use_cases.QueryProducts
    presenter: QueryProductsPresenter
    controller: QueryProductsController
    template_name: str

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
        self, use_case_request: use_cases.QueryProductsRequest
    ) -> Response:
        response = self.query_products(use_case_request)
        view_model = self.presenter.present(response)
        return Response(self._render_response_content(view_model))

    def _render_response_content(self, view_model: QueryProductsViewModel) -> Response:
        return render_template_string(
            self.template_name, form=self.search_form, view_model=view_model
        )
