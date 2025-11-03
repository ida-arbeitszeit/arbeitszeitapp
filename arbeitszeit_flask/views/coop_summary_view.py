from dataclasses import dataclass
from uuid import UUID

from flask import render_template

from arbeitszeit.interactors.get_coop_summary import (
    GetCoopSummaryInteractor,
    GetCoopSummaryRequest,
)
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)


@dataclass
class CoopSummaryView:
    get_coop_summary: GetCoopSummaryInteractor
    presenter: GetCoopSummarySuccessPresenter
    flask_session: FlaskSession

    def GET(self, coop_id: UUID) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        interactor_response = self.get_coop_summary.execute(
            GetCoopSummaryRequest(current_user, coop_id)
        )
        if interactor_response:
            view_model = self.presenter.present(interactor_response)
            return render_template("user/coop_summary.html", view_model=view_model)
        else:
            return http_404()
