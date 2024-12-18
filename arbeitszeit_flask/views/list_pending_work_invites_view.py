from dataclasses import dataclass

from flask import render_template

from arbeitszeit.use_cases.list_pending_work_invites import (
    ListPendingWorkInvitesUseCase,
)
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.list_pending_work_invites_controller import (
    ListPendingWorkInvitesController,
)
from arbeitszeit_web.www.presenters.list_pending_work_invites_presenter import (
    ListPendingWorkInvitesPresenter,
)


@dataclass
class ListPendingWorkInvitesView:
    controller: ListPendingWorkInvitesController
    use_case: ListPendingWorkInvitesUseCase
    presenter: ListPendingWorkInvitesPresenter

    def GET(self) -> Response:
        use_case_request = self.controller.create_use_case_request()
        use_case_response = self.use_case.list_pending_work_invites(use_case_request)
        view_model = self.presenter.present(use_case_response)
        return render_template(
            "company/list_pending_work_invites.html",
            view_model=view_model,
        )
