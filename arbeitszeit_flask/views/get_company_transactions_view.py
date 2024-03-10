from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.use_cases.get_company_transactions import GetCompanyTransactionsUseCase
from arbeitszeit_web.www.controllers.get_company_transactions_controller import (
    GetCompanyTransactionsController,
)
from arbeitszeit_web.www.presenters.get_company_transactions_presenter import (
    GetCompanyTransactionsPresenter,
)


@dataclass
class GetCompanyTransactionsView:
    controller: GetCompanyTransactionsController
    use_case: GetCompanyTransactionsUseCase
    presenter: GetCompanyTransactionsPresenter

    def GET(self, company_id: UUID) -> Response:
        use_case_request = self.controller.create_request(company=company_id)
        response = self.use_case.get_transactions(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/get_company_transactions.html",
                view_model=view_model,
            )
        )
