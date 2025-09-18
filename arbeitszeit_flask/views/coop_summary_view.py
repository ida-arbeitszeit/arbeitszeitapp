from dataclasses import dataclass
from uuid import UUID

from flask import render_template
from flask_login import current_user

from arbeitszeit.interactors.get_coop_summary import (
    GetCoopSummaryInteractor,
    GetCoopSummaryRequest,
)
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)


@dataclass
class CoopSummaryView:
    get_coop_summary: GetCoopSummaryInteractor
    presenter: GetCoopSummarySuccessPresenter

    def GET(self, coop_id: UUID) -> Response:
        interactor_response = self.get_coop_summary.execute(
            GetCoopSummaryRequest(UUID(current_user.id), coop_id)
        )
        if interactor_response:
            view_model = self.presenter.present(interactor_response)
            return render_template("user/coop_summary.html", view_model=view_model)
        else:
            return http_404()
