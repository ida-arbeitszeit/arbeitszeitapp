from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import render_template

from arbeitszeit.use_cases.get_company_dashboard import GetCompanyDashboardUseCase
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.presenters.get_company_dashboard_presenter import (
    GetCompanyDashboardPresenter,
)


@dataclass
class CompanyDashboardView:
    get_company_dashboard_use_case: GetCompanyDashboardUseCase
    get_company_dashboard_presenter: GetCompanyDashboardPresenter
    flask_session: FlaskSession

    def respond_to_get(self) -> Response:
        current_user = self.flask_session.get_current_user()
        assert current_user
        try:
            response = self.get_company_dashboard_use_case.get_dashboard(current_user)
        except GetCompanyDashboardUseCase.Failure:
            return http_404()
        view_model = self.get_company_dashboard_presenter.present(response)
        return FlaskResponse(
            render_template(
                "company/dashboard.html",
                view_model=view_model,
            )
        )
