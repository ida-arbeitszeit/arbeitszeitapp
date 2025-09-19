from dataclasses import dataclass
from uuid import UUID

from flask import Response, render_template

from arbeitszeit.interactors.show_a_account_details import ShowAAccountDetailsInteractor
from arbeitszeit_web.www.controllers.show_a_account_details_controller import (
    ShowAAccountDetailsController,
)
from arbeitszeit_web.www.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)


@dataclass
class ShowAAccountDetailsView:
    controller: ShowAAccountDetailsController
    interactor: ShowAAccountDetailsInteractor
    presenter: ShowAAccountDetailsPresenter

    def GET(self, company_id: UUID) -> Response:
        interactor_request = self.controller.create_request(company=company_id)
        response = self.interactor.show_details(interactor_request)
        view_model = self.presenter.present(response)
        return Response(
            render_template(
                "user/company_account_a.html",
                view_model=view_model,
            )
        )
