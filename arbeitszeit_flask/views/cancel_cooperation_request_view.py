from dataclasses import dataclass
from uuid import UUID

import flask
from flask_login import current_user

from arbeitszeit.interactors.cancel_cooperation_solicitation import (
    CancelCooperationSolicitationInteractor,
    CancelCooperationSolicitationRequest,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.cancel_cooperation_request_presenter import (
    CancelCooperationRequestPresenter,
)


@dataclass
class CancelCooperationRequestView:
    interactor: CancelCooperationSolicitationInteractor
    presenter: CancelCooperationRequestPresenter

    @commit_changes
    def POST(self) -> Response:
        plan_id = UUID(flask.request.form["plan_id"])
        requester_id = UUID(current_user.id)
        uc_response = self.interactor.execute(
            CancelCooperationSolicitationRequest(requester_id, plan_id)
        )
        view_model = self.presenter.render_response(uc_response)
        return flask.redirect(view_model.redirection_url)
