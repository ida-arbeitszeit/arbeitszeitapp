from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.interactors.show_company_accounts import ShowCompanyAccountsInteractor
from arbeitszeit_web.www.controllers.show_company_accounts_controller import (
    ShowCompanyAccountsController,
)
from arbeitszeit_web.www.presenters.show_company_accounts_presenter import (
    ShowCompanyAccountsPresenter,
)


@dataclass
class CompanyAccountsView:
    controller: ShowCompanyAccountsController
    interactor: ShowCompanyAccountsInteractor
    presenter: ShowCompanyAccountsPresenter

    def GET(self, company_id: UUID) -> Response:
        interactor_request = self.controller.create_request(company_id=company_id)
        response = self.interactor.execute(interactor_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_accounts.html",
                view_model=view_model,
            )
        )
