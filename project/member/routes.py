from uuid import UUID

from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit import use_cases
from arbeitszeit_web.get_member_profile_info import GetMemberProfileInfoPresenter
from arbeitszeit_web.get_plan_summary import GetPlanSummaryPresenter
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.pay_consumer_product import (
    PayConsumerProductController,
    PayConsumerProductPresenter,
)
from arbeitszeit_web.query_products import (
    QueryProductsController,
    QueryProductsPresenter,
)
from project.database import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
    PlanRepository,
    commit_changes,
)
from project.dependency_injection import with_injection
from project.forms import PayConsumerProductForm, ProductSearchForm
from project.views import PayConsumerProductView, QueryProductsView

main_member = Blueprint(
    "main_member", __name__, template_folder="templates", static_folder="static"
)


def user_is_member():
    return True if session["user_type"] == "member" else False


@main_member.route("/member/kaeufe")
@login_required
@with_injection
def my_purchases(
    query_purchases: use_cases.QueryPurchases, member_repository: MemberRepository
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    member = member_repository.get_member_by_id(current_user.id)
    purchases = list(query_purchases(member))
    return render_template("member/my_purchases.html", purchases=purchases)


@main_member.route("/member/suchen", methods=["GET", "POST"])
@login_required
@with_injection
def suchen(
    query_products: use_cases.QueryProducts,
    presenter: QueryProductsPresenter,
    controller: QueryProductsController,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))
    template_name = "member/query_products.html"
    search_form = ProductSearchForm(request.form)
    view = QueryProductsView(
        search_form, query_products, presenter, controller, template_name
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@main_member.route("/member/pay_consumer_product", methods=["GET", "POST"])
@commit_changes
@login_required
@with_injection
def pay_consumer_product(
    pay_consumer_product: use_cases.PayConsumerProduct,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    plan_repository: PlanRepository,
    presenter: PayConsumerProductPresenter,
    controller: PayConsumerProductController,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    view = PayConsumerProductView(
        form=PayConsumerProductForm(request.form),
        current_user=current_user.id,
        pay_consumer_product=pay_consumer_product,
        controller=controller,
        presenter=presenter,
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@main_member.route("/member/profile")
@login_required
@with_injection
def profile(
    get_member_profile: use_cases.GetMemberProfileInfo,
    presenter: GetMemberProfileInfoPresenter,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))
    member_profile = get_member_profile(current_user.id)
    view_model = presenter.present(member_profile)
    return render_template(
        "member/profile.html",
        view_model=view_model,
    )


@main_member.route("/member/my_account")
@login_required
@with_injection
def my_account(
    member_repository: MemberRepository,
    get_transaction_infos: use_cases.GetTransactionInfos,
    account_repository: AccountRepository,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    member = member_repository.object_from_orm(current_user)
    list_of_trans_infos = get_transaction_infos(member)

    return render_template(
        "member/my_account.html",
        all_transactions_info=list_of_trans_infos,
        my_balance=account_repository.get_account_balance(member.account),
    )


@main_member.route("/member/statistics")
@login_required
@with_injection
def statistics(
    get_statistics: use_cases.GetStatistics,
    presenter: GetStatisticsPresenter,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return render_template("member/statistics.html", view_model=view_model)


@main_member.route("/member/plan_summary/<uuid:plan_id>")
@login_required
@with_injection
def plan_summary(
    plan_id: UUID,
    get_plan_summary: use_cases.GetPlanSummary,
    presenter: GetPlanSummaryPresenter,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    use_case_response = get_plan_summary(plan_id)
    view_model = presenter.present(use_case_response)

    return render_template("member/plan_summary.html", view_model=view_model.to_dict())


@main_member.route("/member/hilfe")
@login_required
def hilfe():
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    return render_template("member/help.html")
