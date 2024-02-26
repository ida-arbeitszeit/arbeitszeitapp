from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.use_cases.show_r_account_details import ShowRAccountDetailsUseCase
from arbeitszeit_web.www.controllers.show_r_account_details_controller import (
    ShowRAccountDetailsController,
)
from arbeitszeit_web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)


@dataclass
class ShowRAccountDetailsView:
    controller: ShowRAccountDetailsController
    use_case: ShowRAccountDetailsUseCase
    presenter: ShowRAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        use_case_request = self.controller.create_request(company=company_id)
        response = self.use_case.show_details(use_case_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_r.html",
                view_model=view_model,
            )
        )
