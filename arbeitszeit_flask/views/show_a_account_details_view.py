from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.use_cases.show_a_account_details import ShowAAccountDetailsUseCase
from arbeitszeit_web.www.controllers.show_a_account_details_controller import (
    ShowAAccountDetailsController,
)
from arbeitszeit_web.www.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)


@dataclass
class ShowAAccountDetailsView:
    controller: ShowAAccountDetailsController
    use_case: ShowAAccountDetailsUseCase
    presenter: ShowAAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        use_case_request = self.controller.create_request(company=company_id)
        response = self.use_case.show_details(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_a.html",
                view_model=view_model,
            )
        )
