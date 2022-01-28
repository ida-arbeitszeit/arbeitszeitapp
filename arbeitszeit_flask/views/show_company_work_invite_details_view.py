from dataclasses import dataclass
from uuid import UUID

from flask import Response

from arbeitszeit.use_cases import ShowCompanyWorkInviteDetailsUseCase
from arbeitszeit_web.controllers.show_company_work_invite_details_controller import (
    ShowCompanyWorkInviteDetailsController,
)
from arbeitszeit_web.presenters.show_company_work_invite_details_presenter import (
    ShowCompanyWorkInviteDetailsPresenter,
)

from .http_404_view import Http404View


@dataclass
class ShowCompanyWorkInviteDetailsView:
    use_case: ShowCompanyWorkInviteDetailsUseCase
    presenter: ShowCompanyWorkInviteDetailsPresenter
    controller: ShowCompanyWorkInviteDetailsController
    http_404_view: Http404View

    def respond_to_get(self, invite_id: UUID) -> Response:
        use_case_request = self.controller.create_use_case_request(invite_id)
        if use_case_request is None:
            return self.http_404_view.get_response()
        use_case_response = self.use_case.show_company_work_invite_details(
            use_case_request
        )
        view_model = self.presenter.render_response(use_case_response)
        if view_model is None:
            return self.http_404_view.get_response()
        return Response(status=200)
