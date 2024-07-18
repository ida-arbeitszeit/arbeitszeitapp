from dataclasses import dataclass
from uuid import UUID

import flask
from flask_login import current_user

from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.accept_cooperation_request_presenter import (
    AcceptCooperationRequestPresenter,
)


@dataclass
class AcceptCooperationRequestView:
    use_case: AcceptCooperation
    presenter: AcceptCooperationRequestPresenter

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        cooperation_id = UUID(form["cooperation_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        uc_request = AcceptCooperationRequest(
            requester_id=UUID(current_user.id),
            plan_id=plan_id,
            cooperation_id=cooperation_id,
        )
        uc_response = self.use_case(uc_request)
        view_model = self.presenter.render_response(uc_response)
        return flask.redirect(view_model.redirection_url)
