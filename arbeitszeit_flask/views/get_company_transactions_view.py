from dataclasses import dataclass

from flask import Response, render_template

from arbeitszeit.use_cases.get_company_transactions import GetCompanyTransactionsUseCase
from arbeitszeit_web.session import Session
from arbeitszeit_web.www.controllers.get_company_transactions_controller import (
    GetCompanyTransactionsController,
)
from arbeitszeit_web.www.presenters.get_company_transactions_presenter import (
    GetCompanyTransactionsPresenter,
)


@dataclass
class GetCompanyTransactionsView:
    session: Session
    controller: GetCompanyTransactionsController
    use_case: GetCompanyTransactionsUseCase
    presenter: GetCompanyTransactionsPresenter

    def GET(self) -> Response:
        company_id = self.session.get_current_user()
        assert company_id
        use_case_request = self.controller.create_request(company=company_id)
        response = self.use_case.get_transactions(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "company/get_company_transactions.html",
                view_model=view_model,
            )
        )
