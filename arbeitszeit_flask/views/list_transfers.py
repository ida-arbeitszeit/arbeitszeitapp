from dataclasses import dataclass

from flask import Response, render_template

from arbeitszeit.interactors.list_transfers import ListTransfersInteractor
from arbeitszeit_web.www.controllers.list_transfers_controller import (
    ListTransfersController,
)
from arbeitszeit_web.www.presenters.list_transfers_presenter import (
    ListTransfersPresenter,
)

TEMPLATE_NAME = "user/list_transfers.html"


@dataclass
class ListTransfersView:
    interactor: ListTransfersInteractor
    presenter: ListTransfersPresenter
    controller: ListTransfersController

    def GET(self) -> Response:
        uc_request = self.controller.create_interactor_request()
        uc_response = self.interactor.list_transfers(uc_request)
        view_model = self.presenter.present(uc_response)
        return Response(render_template(TEMPLATE_NAME, view_model=view_model))
