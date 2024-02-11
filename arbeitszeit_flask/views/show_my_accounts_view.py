from dataclasses import dataclass

from flask import Response, render_template

from arbeitszeit.use_cases.show_my_accounts import ShowMyAccounts
from arbeitszeit_web.www.controllers.show_my_accounts_controller import (
    ShowMyAccountsController,
)
from arbeitszeit_web.www.presenters.show_my_accounts_presenter import (
    ShowMyAccountsPresenter,
)


@dataclass
class ShowMyAccountsView:
    controller: ShowMyAccountsController
    use_case: ShowMyAccounts
    presenter: ShowMyAccountsPresenter

    def GET(self) -> Response:
        use_case_request = self.controller.create_request()
        response = self.use_case(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "company/my_accounts.html",
                view_model=view_model,
            )
        )
