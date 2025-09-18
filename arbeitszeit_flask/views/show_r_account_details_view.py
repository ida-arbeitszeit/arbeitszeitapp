from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.interactors.show_r_account_details import ShowRAccountDetailsInteractor
from arbeitszeit_web.www.controllers.show_r_account_details_controller import (
    ShowRAccountDetailsController,
)
from arbeitszeit_web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)


@dataclass
class ShowRAccountDetailsView:
    controller: ShowRAccountDetailsController
    interactor: ShowRAccountDetailsInteractor
    presenter: ShowRAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        interactor_request = self.controller.create_request(company=company_id)
        response = self.interactor.show_details(interactor_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_r.html",
                view_model=view_model,
            )
        )
