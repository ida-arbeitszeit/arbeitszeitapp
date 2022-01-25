from uuid import UUID

from flask import Response, request
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases import ListMessages
from arbeitszeit_flask.database import MemberRepository, commit_changes
from arbeitszeit_flask.forms import (
    CompanySearchForm,
    PayConsumerProductForm,
    PlanSearchForm,
)
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.views import (
    Http404View,
    ListMessagesView,
    PayConsumerProductView,
    QueryCompaniesView,
    QueryPlansView,
    ReadMessageView,
)
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_member_profile_info import GetMemberProfileInfoPresenter
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductPresenter,
)
from arbeitszeit_web.query_companies import (
    QueryCompaniesController,
    QueryCompaniesPresenter,
)
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter

from .blueprint import MemberRoute


@MemberRoute("/member/kaeufe")
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
    member_repository: MemberRepository,
    template_renderer: UserTemplateRenderer,
) -> Response:
    member = member_repository.get_by_id(UUID(current_user.id))
    assert member is not None
    purchases = list(query_purchases(member))
    return Response(
        template_renderer.render_template(
            "member/my_purchases.html", context=dict(purchases=purchases)
        )
    )


@MemberRoute("/member/query_plans", methods=["GET", "POST"])
def query_plans(
    query_plans: use_cases.QueryPlans,
    controller: QueryPlansController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryPlansPresenter,
) -> Response:
    template_name = "member/query_plans.html"
    search_form = PlanSearchForm(request.form)
    view = QueryPlansView(
        search_form,
        query_plans,
        presenter,
        controller,
        template_name,
        template_renderer,
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@MemberRoute("/member/query_companies", methods=["GET", "POST"])
def query_companies(
    query_companies: use_cases.QueryCompanies,
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
def pay_consumer_product(
    pay_consumer_product: use_cases.PayConsumerProduct,
    presenter: PayConsumerProductPresenter,
    controller: PayConsumerProductController,
    template_renderer: UserTemplateRenderer,
) -> Response:
    view = PayConsumerProductView(
        form=PayConsumerProductForm(request.form),
        current_user=UUID(current_user.id),
        pay_consumer_product=pay_consumer_product,
        controller=controller,
        presenter=presenter,
        template_renderer=template_renderer,
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@MemberRoute("/member/profile")
def profile(
    get_member_profile: use_cases.GetMemberProfileInfo,
    presenter: GetMemberProfileInfoPresenter,
    template_renderer: UserTemplateRenderer,
) -> Response:
    member_profile = get_member_profile(UUID(current_user.id))
    view_model = presenter.present(member_profile)
    return Response(
        template_renderer.render_template(
            "member/profile.html",
            dict(view_model=view_model),
        )
    )


@MemberRoute("/member/my_account")
def my_account(
    get_member_account: use_cases.GetMemberAccount,
    template_renderer: UserTemplateRenderer,
) -> Response:
    response = get_member_account(UUID(current_user.id))
    return Response(
        template_renderer.render_template(
            "member/my_account.html",
            context=dict(
                all_transactions_info=response.transactions,
                my_balance=response.balance,
            ),
        )
    )


@MemberRoute("/member/statistics")
def statistics(
    get_statistics: use_cases.GetStatistics,
    presenter: GetStatisticsPresenter,
    template_renderer: UserTemplateRenderer,
) -> Response:
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return Response(
        template_renderer.render_template(
            "member/statistics.html", context=dict(view_model=view_model)
        )
    )


@MemberRoute("/member/plan_summary/<uuid:plan_id>")
def plan_summary(
    plan_id: UUID,
    get_plan_summary: use_cases.GetPlanSummary,
    template_renderer: UserTemplateRenderer,
    presenter: GetPlanSummarySuccessPresenter,
    http_404_view: Http404View,
) -> Response:
    use_case_response = get_plan_summary(plan_id)
    if isinstance(use_case_response, use_cases.PlanSummarySuccess):
        view_model = presenter.present(use_case_response)
        return Response(
            template_renderer.render_template(
                "member/plan_summary.html",
                context=dict(view_model=view_model.to_dict()),
            )
        )
    else:
        return http_404_view.get_response()


@MemberRoute("/member/cooperation_summary/<uuid:coop_id>")
def coop_summary(
    coop_id: UUID,
    get_coop_summary: use_cases.GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
    template_renderer: UserTemplateRenderer,
    http_404_view: Http404View,
):
    use_case_response = get_coop_summary(
        use_cases.GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if isinstance(use_case_response, use_cases.GetCoopSummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "member/coop_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return http_404_view.get_response()


@MemberRoute("/member/hilfe")
def hilfe(template_renderer: UserTemplateRenderer) -> Response:
    return Response(template_renderer.render_template("member/help.html"))


@MemberRoute("/member/messages")
def list_messages(
    template_renderer: UserTemplateRenderer,
    controller: ListMessagesController,
    presenter: ListMessagesPresenter,
    use_case: ListMessages,
    http_404_view: Http404View,
) -> Response:
    view = ListMessagesView(
        template_renderer=template_renderer,
        presenter=presenter,
        controller=controller,
        list_messages=use_case,
        not_found_view=http_404_view,
        template_name="member/list_messages.html",
    )
    return view.respond_to_get()


@MemberRoute("/member/messages/<uuid:message_id>")
@commit_changes
def read_message(
    message_id: UUID,
    view: ReadMessageView,
) -> Response:
    return view.respond_to_get(message_id)
