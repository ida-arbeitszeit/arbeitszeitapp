from dataclasses import dataclass
from uuid import UUID

from flask import render_template
from flask_login import current_user

from arbeitszeit.use_cases.get_coop_summary import GetCoopSummary, GetCoopSummaryRequest
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)


@dataclass
class CoopSummaryView:
    get_coop_summary: GetCoopSummary
    presenter: GetCoopSummarySuccessPresenter

    def GET(self, coop_id: UUID) -> Response:
        use_case_response = self.get_coop_summary(
            GetCoopSummaryRequest(UUID(current_user.id), coop_id)
        )
        if use_case_response:
            view_model = self.presenter.present(use_case_response)
            return render_template(
                "user/coop_summary.html", view_model=view_model.to_dict()
            )
        else:
            return http_404()
