from dataclasses import dataclass

from flask import Response as FlaskResponse
from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase

from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)


@dataclass
class CompanyDashboardView:
    get_company_dashboard_use_case: GetCompanyDashboardUseCase
    get_company_dashboard_presenter: GetCompanyDashboardPresenter
    template_renderer: UserTemplateRenderer
    flask_session: FlaskSession

    def respond_to_get(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        response = self.get_company_dashboard_use_case.get_dashboard(current_user)
        view_model = self.get_company_dashboard_presenter.present(response)
        return FlaskResponse(
            self.template_renderer.render_template(
                "company/dashboard.html",
                context=dict(view_model=view_model),
            )
        )
