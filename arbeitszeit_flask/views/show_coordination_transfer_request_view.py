from dataclasses import dataclass
from uuid import UUID

from flask import redirect, render_template

from arbeitszeit.interactors.accept_coordination_transfer import (
    AcceptCoordinationTransferInteractor,
)
from arbeitszeit.interactors.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsInteractor,
)
from arbeitszeit_db import commit_changes
from arbeitszeit_flask import types
from arbeitszeit_flask.views.http_error_view import http_403, http_404, http_409
from arbeitszeit_web.www.controllers.accept_coordination_transfer_controller import (
    AcceptCoordinationTransferController,
)
from arbeitszeit_web.www.presenters.accept_coordination_transfer_presenter import (
    AcceptCoordinationTransferPresenter,
)
from arbeitszeit_web.www.presenters.get_coordination_transfer_request_details_presenter import (
    GetCoordinationTransferRequestDetailsPresenter,
)


@dataclass
class ShowCoordinationTransferRequestView:
    details_interactor: GetCoordinationTransferRequestDetailsInteractor
    details_presenter: GetCoordinationTransferRequestDetailsPresenter
    accept_controller: AcceptCoordinationTransferController
    accept_interactor: AcceptCoordinationTransferInteractor
    accept_presenter: AcceptCoordinationTransferPresenter

    def GET(self, transfer_request: UUID) -> types.Response:
        details_uc_response = self.details_interactor.get_details(
            request=GetCoordinationTransferRequestDetailsInteractor.Request(
                transfer_request
            )
        )
        if not details_uc_response:
            return http_404()
        transfer_request_details = self.details_presenter.present(details_uc_response)
        return render_template(
            "company/show_coordination_transfer_request.html",
            request_details=transfer_request_details,
        )

    @commit_changes
    def POST(self, transfer_request: UUID) -> types.Response:
        uc_request = self.accept_controller.create_interactor_request(
            transfer_request=transfer_request
        )
        uc_response = self.accept_interactor.accept_coordination_transfer(
            request=uc_request
        )
        view_model = self.accept_presenter.present(interactor_response=uc_response)
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url, code=view_model.status_code)
        match view_model.status_code:
            case 403:
                return http_403()
            case 409:
                return http_409()
            case _:
                return http_404()
