from __future__ import annotations

from uuid import UUID

from flask import Response as FlaskResponse
from flask import render_template, request
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases.get_coop_summary import GetCoopSummary, GetCoopSummaryRequest
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
)
from arbeitszeit.use_cases.query_private_consumptions import QueryPrivateConsumptions
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import (
    AnswerCompanyWorkInviteForm,
    CompanySearchForm,
    PlanSearchForm,
    RegisterPrivateConsumptionForm,
)
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    CompanyWorkInviteView,
    QueryCompaniesView,
    QueryPlansView,
    RegisterPrivateConsumptionView,
)
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.www.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.www.controllers.query_private_consumptions_controller import (
    QueryPrivateConsumptionsController,
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
from arbeitszeit_web.www.presenters.private_consumptions_presenter import (
    PrivateConsumptionsPresenter,
)
from arbeitszeit_web.www.presenters.query_companies_presenter import (
    QueryCompaniesPresenter,
)

from .blueprint import MemberRoute


@MemberRoute("/consumptions")
def consumptions(
    controller: QueryPrivateConsumptionsController,
    use_case: QueryPrivateConsumptions,
    presenter: PrivateConsumptionsPresenter,
) -> Response:
    uc_request = controller.process_request()
    if not uc_request:
        return FlaskResponse(status=403)
    response = use_case.query_private_consumptions(uc_request)
    view_model = presenter.present_private_consumptions(response)
    return FlaskResponse(
        render_template(
            "member/consumptions.html",
            view_model=view_model,
        )
    )


@MemberRoute("/query_plans", methods=["GET"])
def query_plans(
    query_plans: use_cases.query_plans.QueryPlans,
    controller: QueryPlansController,
    presenter: QueryPlansPresenter,
) -> Response:
    template_name = "member/query_plans.html"
    search_form = PlanSearchForm(request.form)
    view = QueryPlansView(
        query_plans,
        presenter,
        controller,
        template_name,
    )
    return view.respond_to_get(search_form, FlaskRequest())


@MemberRoute("/query_companies", methods=["GET", "POST"])
def query_companies(
    query_companies: use_cases.query_companies.QueryCompanies,
    controller: QueryCompaniesController,
    presenter: QueryCompaniesPresenter,
):
    template_name = "member/query_companies.html"
    search_form = CompanySearchForm(request.args)
    view = QueryCompaniesView(
        search_form,
        query_companies,
        presenter,
        controller,
        template_name,
    )
    return view.respond_to_get()


@MemberRoute("/register_private_consumption", methods=["GET", "POST"])
@commit_changes
def register_private_consumption(view: RegisterPrivateConsumptionView) -> Response:
    form = RegisterPrivateConsumptionForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)
    else:
        return view.respond_to_get(form)


@MemberRoute("/dashboard")
def dashboard(
    get_member_dashboard: use_cases.get_member_dashboard.GetMemberDashboard,
    presenter: GetMemberDashboardPresenter,
) -> Response:
    response = get_member_dashboard(UUID(current_user.id))
    view_model = presenter.present(response)
    return FlaskResponse(
        render_template(
            "member/dashboard.html",
            view_model=view_model,
        )
    )


@MemberRoute("/my_account")
def my_account(
    get_member_account: use_cases.get_member_account.GetMemberAccount,
    presenter: GetMemberAccountPresenter,
) -> Response:
    response = get_member_account(UUID(current_user.id))
    view_model = presenter.present_member_account(response)
    return FlaskResponse(
        render_template(
            "member/my_account.html",
            view_model=view_model,
        )
    )


@MemberRoute("/statistics")
def statistics(
    get_statistics: use_cases.get_statistics.GetStatistics,
    presenter: GetStatisticsPresenter,
) -> Response:
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return FlaskResponse(
        render_template("member/statistics.html", view_model=view_model)
    )


@MemberRoute("/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    use_case: GetPlanDetailsUseCase,
    presenter: GetPlanDetailsMemberMemberPresenter,
) -> Response:
    use_case_request = GetPlanDetailsUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_details(use_case_request)
    if use_case_response:
        view_model = presenter.present(use_case_response)
        return FlaskResponse(
            render_template(
                "member/plan_details.html",
                view_model=view_model.to_dict(),
            )
        )
    else:
        return http_404()


@MemberRoute("/cooperation_summary/<uuid:coop_id>")
def coop_summary(
    coop_id: UUID,
    get_coop_summary: GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
):
    use_case_response = get_coop_summary(
        GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if use_case_response:
        view_model = presenter.present(use_case_response)
        return render_template(
            "member/coop_summary.html", view_model=view_model.to_dict()
        )
    else:
        return http_404()


@MemberRoute("/cooperation_summary/<uuid:coop_id>/coordinators", methods=["GET"])
def list_coordinators_of_cooperation(
    coop_id: UUID,
    list_coordinations_of_cooperation: ListCoordinationsOfCooperationUseCase,
    presenter: ListCoordinationsOfCooperationPresenter,
):
    use_case_response = list_coordinations_of_cooperation.list_coordinations(
        ListCoordinationsOfCooperationUseCase.Request(cooperation=coop_id)
    )
    view_model = presenter.list_coordinations_of_cooperation(use_case_response)
    return render_template(
        "member/list_coordinators_of_cooperation.html",
        view_model=view_model,
    )


@MemberRoute("/invite_details/<uuid:invite_id>", methods=["GET", "POST"])
def show_company_work_invite(invite_id: UUID, view: CompanyWorkInviteView):
    form = AnswerCompanyWorkInviteForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form, invite_id)
    else:
        return view.respond_to_get(invite_id)
