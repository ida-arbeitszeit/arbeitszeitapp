from dataclasses import dataclass
from uuid import UUID

import flask

from arbeitszeit.interactors.deny_cooperation import (
    DenyCooperationInteractor,
    DenyCooperationRequest,
)
from arbeitszeit_db import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.presenters.deny_cooperation_presenter import (
    DenyCooperationPresenter,
)


@dataclass
class DenyCooperationView:
    interactor: DenyCooperationInteractor
    presenter: DenyCooperationPresenter
    flask_session: FlaskSession

    @commit_changes
    def POST(self) -> Response:
        form = flask.request.form
        cooperation_id = UUID(form["cooperation_id"].strip())
        plan_id = UUID(form["plan_id"].strip())
        current_user = self.flask_session.get_current_user()
        assert current_user
        deny_cooperation_response = self.interactor.execute(
            DenyCooperationRequest(
                current_user,
                plan_id,
                cooperation_id,
            )
        )
        view_model = self.presenter.render_response(deny_cooperation_response)
        return flask.redirect(view_model.redirection_url)
