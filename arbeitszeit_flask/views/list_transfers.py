from dataclasses import dataclass

from flask import Response, render_template

from arbeitszeit.use_cases.list_transfers import ListTransfersUseCase
from arbeitszeit_web.www.controllers.list_transfers_controller import (
    ListTransfersController,
)
from arbeitszeit_web.www.presenters.list_transfers_presenter import (
    ListTransfersPresenter,
)

TEMPLATE_NAME = "user/list_transfers.html"


@dataclass
class ListTransfersView:
    use_case: ListTransfersUseCase
    presenter: ListTransfersPresenter
    controller: ListTransfersController

    def GET(self) -> Response:
        uc_request = self.controller.create_use_case_request()
        uc_response = self.use_case.list_transfers(uc_request)
        view_model = self.presenter.present(uc_response)
        return Response(render_template(TEMPLATE_NAME, view_model=view_model))
