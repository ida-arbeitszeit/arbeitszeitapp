from __future__ import annotations

from uuid import UUID

from flask import Response as FlaskResponse
from flask import request
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from arbeitszeit.use_cases.get_plan_summary import GetPlanSummaryUseCase
from arbeitszeit.use_cases.get_user_account_details import GetUserAccountDetailsUseCase
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.forms import (
    AnswerCompanyWorkInviteForm,
    CompanySearchForm,
    PayConsumerProductForm,
    PlanSearchForm,
)
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    CompanyWorkInviteView,
    Http404View,
    PayConsumerProductView,
    QueryCompaniesView,
    QueryPlansView,
)
from arbeitszeit_web.controllers.get_member_account_details_controller import (
    GetMemberAccountDetailsController,
)
from arbeitszeit_web.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.presenters.get_company_summary_presenter import (
    GetCompanySummarySuccessPresenter,
)
from arbeitszeit_web.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)
from arbeitszeit_web.presenters.get_member_account_details_presenter import (
    GetMemberAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.get_member_account_presenter import (
    GetMemberAccountPresenter,
)
from arbeitszeit_web.presenters.get_member_dashboard_presenter import (
    GetMemberDashboardPresenter,
)
from arbeitszeit_web.presenters.get_plan_summary_member_presenter import (
    GetPlanSummaryMemberMemberPresenter,
)
from arbeitszeit_web.presenters.get_statistics_presenter import GetStatisticsPresenter
from arbeitszeit_web.presenters.member_purchases import MemberPurchasesPresenter
from arbeitszeit_web.presenters.query_companies_presenter import QueryCompaniesPresenter
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter

from .blueprint import MemberRoute


@MemberRoute("/member/purchases")
def my_purchases(
    query_purchases: use_cases.query_member_purchases.QueryMemberPurchases,
    template_renderer: UserTemplateRenderer,
    presenter: MemberPurchasesPresenter,
) -> Response:
    response = query_purchases(UUID(current_user.id))
    view_model = presenter.present_member_purchases(response)
    return FlaskResponse(
        template_renderer.render_template(
            "member/my_purchases.html",
            context=dict(view_model=view_model),
        )
    )


@MemberRoute("/member/query_plans", methods=["GET"])
def query_plans(
    query_plans: use_cases.query_plans.QueryPlans,
    controller: QueryPlansController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryPlansPresenter,
) -> Response:
    template_name = "member/query_plans.html"
    search_form = PlanSearchForm(request.form)
    view = QueryPlansView(
        query_plans,
        presenter,
        controller,
        template_name,
        template_renderer,
    )
    return view.respond_to_get(search_form, FlaskRequest())


@MemberRoute("/member/query_companies", methods=["GET", "POST"])
def query_companies(
    query_companies: use_cases.query_companies.QueryCompanies,
    controller: QueryCompaniesController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryCompaniesPresenter,
):
    template_name = "member/query_companies.html"
    search_form = CompanySearchForm(request.form)
    view = QueryCompaniesView(
        search_form,
        query_companies,
        presenter,
        controller,
        template_name,
        template_renderer,
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@MemberRoute("/member/pay_consumer_product", methods=["GET", "POST"])
@commit_changes
def pay_consumer_product(view: PayConsumerProductView) -> Response:
    form = PayConsumerProductForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)
    else:
        return view.respond_to_get(form)


@MemberRoute("/member/dashboard")
def dashboard(
    get_member_dashboard: use_cases.get_member_dashboard.GetMemberDashboard,
    presenter: GetMemberDashboardPresenter,
    template_renderer: UserTemplateRenderer,
) -> Response:
    response = get_member_dashboard(UUID(current_user.id))
    view_model = presenter.present(response)
    return FlaskResponse(
        template_renderer.render_template(
            "member/dashboard.html",
            dict(view_model=view_model),
        )
    )


@MemberRoute("/member/my_account")
def my_account(
    get_member_account: use_cases.get_member_account.GetMemberAccount,
    template_renderer: UserTemplateRenderer,
    presenter: GetMemberAccountPresenter,
) -> Response:
    response = get_member_account(UUID(current_user.id))
    view_model = presenter.present_member_account(response)
    return FlaskResponse(
        template_renderer.render_template(
            "member/my_account.html",
            context=dict(view_model=view_model),
        )
    )


@MemberRoute("/member/statistics")
def statistics(
    get_statistics: use_cases.get_statistics.GetStatistics,
    presenter: GetStatisticsPresenter,
    template_renderer: UserTemplateRenderer,
) -> Response:
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return FlaskResponse(
        template_renderer.render_template(
            "member/statistics.html", context=dict(view_model=view_model)
        )
    )


@MemberRoute("/member/plan_summary/<uuid:plan_id>")
def plan_summary(
    plan_id: UUID,
    use_case: GetPlanSummaryUseCase,
    template_renderer: UserTemplateRenderer,
    presenter: GetPlanSummaryMemberMemberPresenter,
    http_404_view: Http404View,
) -> Response:
    use_case_request = GetPlanSummaryUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_summary(use_case_request)
    if use_case_response:
        view_model = presenter.present(use_case_response)
        return FlaskResponse(
            template_renderer.render_template(
                "member/plan_summary.html",
                context=dict(view_model=view_model.to_dict()),
            )
        )
    else:
        return http_404_view.get_response()


@MemberRoute("/member/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummary,
    template_renderer: UserTemplateRenderer,
    presenter: GetCompanySummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_company_summary(company_id)
    if isinstance(
        use_case_response, use_cases.get_company_summary.GetCompanySummarySuccess
    ):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "member/company_summary.html",
            context=dict(view_model=view_model.to_dict()),
        )
    else:
        return http_404_view.get_response()


@MemberRoute("/member/cooperation_summary/<uuid:coop_id>")
def coop_summary(
    coop_id: UUID,
    get_coop_summary: use_cases.get_coop_summary.GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
    template_renderer: UserTemplateRenderer,
    http_404_view: Http404View,
):
    use_case_response = get_coop_summary(
        use_cases.get_coop_summary.GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if isinstance(use_case_response, use_cases.get_coop_summary.GetCoopSummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "member/coop_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return http_404_view.get_response()


@MemberRoute("/member/hilfe")
def hilfe(template_renderer: UserTemplateRenderer) -> Response:
    return FlaskResponse(template_renderer.render_template("member/help.html"))


@MemberRoute("/member/invite_details/<uuid:invite_id>", methods=["GET", "POST"])
def show_company_work_invite(invite_id: UUID, view: CompanyWorkInviteView):
    form = AnswerCompanyWorkInviteForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form, invite_id)
    else:
        return view.respond_to_get(invite_id)


@MemberRoute("/member/account")
def get_member_account_details(
    controller: GetMemberAccountDetailsController,
    presenter: GetMemberAccountDetailsPresenter,
    use_case: GetUserAccountDetailsUseCase,
    template_renderer: UserTemplateRenderer,
):
    uc_request = controller.parse_web_request()
    uc_response = use_case.get_user_account_details(uc_request)
    view_model = presenter.render_member_account_details(uc_response)
    return FlaskResponse(
        template_renderer.render_template(
            "member/get_member_account_details.html", dict(view_model=view_model)
        ),
        status=200,
    )
