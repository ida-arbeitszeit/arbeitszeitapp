from dataclasses import dataclass
from uuid import UUID

from flask import Response as FlaskResponse
from flask import render_template
from flask_login import current_user

from arbeitszeit.use_cases import get_member_dashboard
from arbeitszeit.use_cases.get_member_account import GetMemberAccountUseCase
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
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
from arbeitszeit_web.www.presenters.get_member_account_presenter import (
    GetMemberAccountPresenter,
)
from arbeitszeit_web.www.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)
from arbeitszeit_web.www.presenters.get_plan_details_member_presenter import (
    GetPlanDetailsMemberMemberPresenter,
)

from .blueprint import MemberRoute


@MemberRoute("/consumptions")
@as_flask_view()
class consumptions(QueryPrivateConsumptionsView): ...


@MemberRoute("/register_private_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_private_consumption(RegisterPrivateConsumptionView): ...


@MemberRoute("/dashboard")
@as_flask_view()
@dataclass
class dashboard:
    use_case: get_member_dashboard.GetMemberDashboardUseCase
    presenter: GetMemberDashboardPresenter

    def GET(self) -> Response:
        request = get_member_dashboard.Request(member=UUID(current_user.id))
        response = self.use_case.get_member_dashboard(request)
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
    get_member_account: GetMemberAccountUseCase
    presenter: GetMemberAccountPresenter

    def GET(self) -> Response:
        response = self.get_member_account.execute(UUID(current_user.id))
        view_model = self.presenter.present_member_account(response)
        return FlaskResponse(
            render_template(
                "member/my_account.html",
                view_model=view_model,
            )
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
                    view_model=view_model,
                )
            )
        else:
            return http_404()


@MemberRoute("/invite_details/<uuid:invite_id>", methods=["GET", "POST"])
@as_flask_view()
class show_company_work_invite(CompanyWorkInviteView): ...
