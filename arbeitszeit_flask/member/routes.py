from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import render_template
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases.get_coop_summary import GetCoopSummary, GetCoopSummaryRequest
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
)
from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    CompanyWorkInviteView,
    RegisterPrivateConsumptionView,
)
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_flask.views.query_private_consumptions import (
    QueryPrivateConsumptionsView,
)
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)
from arbeitszeit_web.www.presenters.get_member_account_presenter import (
    GetMemberAccountPresenter,
)
from arbeitszeit_web.www.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)
from arbeitszeit_web.www.presenters.get_plan_details_member_presenter import (
    GetPlanDetailsMemberMemberPresenter,
)
from arbeitszeit_web.www.presenters.get_statistics_presenter import (
    GetStatisticsPresenter,
)
from arbeitszeit_web.www.presenters.list_coordinations_of_cooperation_presenter import (
    ListCoordinationsOfCooperationPresenter,
)

from .blueprint import MemberRoute


@MemberRoute("/consumptions")
@as_flask_view()
class consumptions(QueryPrivateConsumptionsView):
    ...


@MemberRoute("/register_private_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_private_consumption(RegisterPrivateConsumptionView):
    ...


@MemberRoute("/dashboard")
@as_flask_view()
@dataclass
class dashboard:
    get_member_dashboard: use_cases.get_member_dashboard.GetMemberDashboard
    presenter: GetMemberDashboardPresenter

    def GET(self) -> Response:
        response = self.get_member_dashboard(UUID(current_user.id))
        view_model = self.presenter.present(response)
        return FlaskResponse(
            render_template(
                "member/dashboard.html",
                view_model=view_model,
            )
        )


@MemberRoute("/my_account")
@as_flask_view()
@dataclass
class my_account:
    get_member_account: use_cases.get_member_account.GetMemberAccount
    presenter: GetMemberAccountPresenter

    def GET(self) -> Response:
        response = self.get_member_account(UUID(current_user.id))
        view_model = self.presenter.present_member_account(response)
        return FlaskResponse(
            render_template(
                "member/my_account.html",
                view_model=view_model,
            )
        )


@MemberRoute("/statistics")
@as_flask_view()
@dataclass
class statistics:
    get_statistics: use_cases.get_statistics.GetStatistics
    presenter: GetStatisticsPresenter

    def GET(self) -> Response:
        use_case_response = self.get_statistics()
        view_model = self.presenter.present(use_case_response)
        return FlaskResponse(
            render_template("member/statistics.html", view_model=view_model)
        )


@MemberRoute("/plan_details/<uuid:plan_id>")
@as_flask_view()
@dataclass
class plan_details:
    use_case: GetPlanDetailsUseCase
    presenter: GetPlanDetailsMemberMemberPresenter

    def GET(self, plan_id: UUID) -> Response:
        use_case_request = GetPlanDetailsUseCase.Request(plan_id)
        use_case_response = self.use_case.get_plan_details(use_case_request)
        if use_case_response:
            view_model = self.presenter.present(use_case_response)
            return FlaskResponse(
                render_template(
                    "member/plan_details.html",
                    view_model=view_model.to_dict(),
                )
            )
        else:
            return http_404()


@MemberRoute("/cooperation_summary/<uuid:coop_id>")
@as_flask_view()
@dataclass
class coop_summary:
    get_coop_summary: GetCoopSummary
    presenter: GetCoopSummarySuccessPresenter

    def GET(self, coop_id: UUID) -> Response:
        use_case_response = self.get_coop_summary(
            GetCoopSummaryRequest(UUID(current_user.id), coop_id)
        )
        if use_case_response:
            view_model = self.presenter.present(use_case_response)
            return render_template(
                "member/coop_summary.html", view_model=view_model.to_dict()
            )
        else:
            return http_404()


@MemberRoute("/cooperation_summary/<uuid:coop_id>/coordinators", methods=["GET"])
@as_flask_view()
@dataclass
class list_coordinators_of_cooperation:
    list_coordinations_of_cooperation: ListCoordinationsOfCooperationUseCase
    presenter: ListCoordinationsOfCooperationPresenter

    def GET(self, coop_id: UUID) -> Response:
        use_case_response = self.list_coordinations_of_cooperation.list_coordinations(
            ListCoordinationsOfCooperationUseCase.Request(cooperation=coop_id)
        )
        view_model = self.presenter.list_coordinations_of_cooperation(use_case_response)
        return render_template(
            "member/list_coordinators_of_cooperation.html",
            view_model=view_model,
        )


@MemberRoute("/invite_details/<uuid:invite_id>", methods=["GET", "POST"])
@as_flask_view()
class show_company_work_invite(CompanyWorkInviteView):
    ...
