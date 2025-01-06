from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, url_for

from arbeitszeit.use_cases.list_pending_work_invites import (
    ListPendingWorkInvitesUseCase,
)
from arbeitszeit.use_cases.resend_work_invite import ResendWorkInviteUseCase
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.list_pending_work_invites_controller import (
    ListPendingWorkInvitesController,
)
from arbeitszeit_web.www.controllers.resend_work_invite_controller import (
    ResendWorkInviteController,
)
from arbeitszeit_web.www.presenters.list_pending_work_invites_presenter import (
    ListPendingWorkInvitesPresenter,
)
from arbeitszeit_web.www.presenters.resend_work_invite_presenter import (
    ResendWorkInvitePresenter,
)

TEMPLATE_NAME = "company/list_pending_work_invites.html"


@dataclass
class ListPendingWorkInvitesView:
    controller: ListPendingWorkInvitesController
    use_case: ListPendingWorkInvitesUseCase
    presenter: ListPendingWorkInvitesPresenter
    post_controller: ResendWorkInviteController
    post_use_case: ResendWorkInviteUseCase
    post_presenter: ResendWorkInvitePresenter

    def GET(self, status: int = 200) -> Response:
        use_case_request = self.controller.create_use_case_request()
        use_case_response = self.use_case.list_pending_work_invites(use_case_request)
        view_model = self.presenter.present(use_case_response)
        return FlaskResponse(
            render_template(
                TEMPLATE_NAME,
                view_model=view_model,
            ),
            status=status,
        )

    @commit_changes
    def POST(self) -> Response:
        use_case_request = self.post_controller.create_use_case_request(
            request=FlaskRequest()
        )
        use_case_response = self.post_use_case.resend_work_invite(use_case_request)
        view_model = self.post_presenter.present(use_case_response)
        if view_model.status_code == 302:
            return redirect(url_for("main_company.list_pending_work_invites"))
        return self.GET(status=view_model.status_code)
