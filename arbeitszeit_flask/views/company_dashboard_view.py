from dataclasses import dataclass

from flask import Response as FlaskResponse

from arbeitszeit.use_cases.get_latest_activated_plans import GetLatestActivatedPlans
from arbeitszeit.use_cases.list_workers import ListWorkers, ListWorkersRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.presenters.get_latest_activated_plans_presenter import (
    GetLatestActivatedPlansPresenter,
)


@dataclass
class CompanyDashboardView:
    list_workers_use_case: ListWorkers
    get_latest_plans_use_case: GetLatestActivatedPlans
    get_latest_plans_presenter: GetLatestActivatedPlansPresenter
    template_renderer: UserTemplateRenderer
    flask_session: FlaskSession

    def respond_to_get(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        workers = self.list_workers_use_case(ListWorkersRequest(current_user)).workers
        latest_plans_use_case_response = self.get_latest_plans_use_case()
        view_model = self.get_latest_plans_presenter.show_latest_plans(
            latest_plans_use_case_response
        )
        return FlaskResponse(
            self.template_renderer.render_template(
                "company/dashboard.html",
                context=dict(
                    having_workers=bool(workers),
                    view_model=view_model,
                ),
            )
        )
