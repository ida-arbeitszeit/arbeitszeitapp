from dataclasses import dataclass
from uuid import UUID

import flask
from flask_login import current_user

from arbeitszeit.use_cases.deny_cooperation import (
    DenyCooperationRequest,
    DenyCooperationUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.deny_cooperation_presenter import (
    DenyCooperationPresenter,
)


@dataclass
class DenyCooperationView:
    use_case: DenyCooperationUseCase
    presenter: DenyCooperationPresenter

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        cooperation_id = UUID(form["cooperation_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        deny_cooperation_response = self.use_case.execute(
            DenyCooperationRequest(
                UUID(current_user.id),
                plan_id,
                cooperation_id,
            )
        )
        view_model = self.presenter.render_response(deny_cooperation_response)
        return flask.redirect(view_model.redirection_url)
