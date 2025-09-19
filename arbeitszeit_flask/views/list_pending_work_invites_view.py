from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, url_for

from arbeitszeit.interactors.list_pending_work_invites import (
    ListPendingWorkInvitesInteractor,
)
from arbeitszeit.interactors.resend_work_invite import ResendWorkInviteInteractor
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
    interactor: ListPendingWorkInvitesInteractor
    presenter: ListPendingWorkInvitesPresenter
    post_controller: ResendWorkInviteController
    post_interactor: ResendWorkInviteInteractor
    post_presenter: ResendWorkInvitePresenter

    def GET(self, status: int = 200) -> Response:
        interactor_request = self.controller.create_interactor_request()
        interactor_response = self.interactor.list_pending_work_invites(
            interactor_request
        )
        view_model = self.presenter.present(interactor_response)
        return FlaskResponse(
            render_template(
                TEMPLATE_NAME,
                view_model=view_model,
            ),
            status=status,
        )

    @commit_changes
    def POST(self) -> Response:
        interactor_request = self.post_controller.create_interactor_request(
            request=FlaskRequest()
        )
        interactor_response = self.post_interactor.resend_work_invite(
            interactor_request
        )
        view_model = self.post_presenter.present(interactor_response)
        if view_model.status_code == 302:
            return redirect(url_for("main_company.list_pending_work_invites"))
        return self.GET(status=view_model.status_code)
