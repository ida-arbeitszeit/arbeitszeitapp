from dataclasses import dataclass
from uuid import UUID

from flask import redirect, render_template

from arbeitszeit.use_cases.accept_coordination_transfer import (
    AcceptCoordinationTransferUseCase,
)
from arbeitszeit.use_cases.get_coordination_transfer_request_details import (
    GetCoordinationTransferRequestDetailsUseCase,
)
from arbeitszeit_flask import types
from arbeitszeit_flask.views.http_403_view import Http403View
from arbeitszeit_flask.views.http_404_view import Http404View
from arbeitszeit_flask.views.http_409_view import Http409View
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
    http_403_view: Http403View
    http_404_view: Http404View
    http_409_view: Http409View
    details_use_case: GetCoordinationTransferRequestDetailsUseCase
    details_presenter: GetCoordinationTransferRequestDetailsPresenter
    accept_controller: AcceptCoordinationTransferController
    accept_use_case: AcceptCoordinationTransferUseCase
    accept_presenter: AcceptCoordinationTransferPresenter

    def respond_to_get(self, transfer_request: UUID) -> types.Response:
        details_uc_response = self.details_use_case.get_details(
            request=GetCoordinationTransferRequestDetailsUseCase.Request(
                transfer_request
            )
        )
        if not details_uc_response:
            return self.http_404_view.get_response()
        transfer_request_details = self.details_presenter.present(details_uc_response)
        return render_template(
            "company/show_coordination_transfer_request.html",
            request_details=transfer_request_details,
        )

    def respond_to_post(self, transfer_request: UUID) -> types.Response:
        uc_request = self.accept_controller.create_use_case_request(
            transfer_request=transfer_request
        )
        uc_response = self.accept_use_case.accept_coordination_transfer(
            request=uc_request
        )
        view_model = self.accept_presenter.present(use_case_response=uc_response)
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url, code=view_model.status_code)
        match view_model.status_code:
            case 403:
                return self.http_403_view.get_response()
            case 409:
                return self.http_409_view.get_response()
            case _:
                return self.http_404_view.get_response()
