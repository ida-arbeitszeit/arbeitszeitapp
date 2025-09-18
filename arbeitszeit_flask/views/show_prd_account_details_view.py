from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.interactors.show_prd_account_details import (
    ShowPRDAccountDetailsInteractor,
)
from arbeitszeit_web.www.controllers.show_prd_account_details_controller import (
    ShowPRDAccountDetailsController,
)
from arbeitszeit_web.www.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)


@dataclass
class ShowPRDAccountDetailsView:
    controller: ShowPRDAccountDetailsController
    interactor: ShowPRDAccountDetailsInteractor
    presenter: ShowPRDAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        interactor_request = self.controller.create_request(company=company_id)
        response = self.interactor.show_details(interactor_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_prd.html",
                view_model=view_model,
            )
        )
