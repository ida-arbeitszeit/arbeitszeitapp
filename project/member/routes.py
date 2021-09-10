from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit import errors, use_cases
from arbeitszeit_web.query_products import QueryProductsPresenter
from project import database
from project.database import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
    PlanRepository,
)
from project.dependency_injection import with_injection
from project.forms import ProductSearchForm

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
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))
    template_name = "member/query_products.html"
    search_form = ProductSearchForm(request.form)
    if request.method == "POST":
        query = search_form.data["search"] or None
        search_field = search_form.data["select"]  # Name, Beschr., Kategorie
        if search_field == "Name":
            product_filter = use_cases.ProductFilter.by_name
        elif search_field == "Beschreibung":
            product_filter = use_cases.ProductFilter.by_description
        response = query_products(query, product_filter)
        view_model = presenter.present(response)
        return render_template(template_name, form=search_form, view_model=view_model)
    else:
        view_model = presenter.get_empty_view_model()
        return render_template(template_name, form=search_form, view_model=view_model)


@main_member.route("/member/pay_consumer_product", methods=["GET", "POST"])
@login_required
@with_injection
def pay_consumer_product(
    pay_consumer_product: use_cases.PayConsumerProduct,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    plan_repository: PlanRepository,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    if request.method == "POST":
        sender = member_repository.get_member_by_id(current_user.id)
        plan = plan_repository.get_plan_by_id(request.form["plan_id"])
        pieces = int(request.form["amount"])
        try:
            pay_consumer_product(
                sender,
                plan,
                pieces,
            )
            database.commit_changes()
            flash("Produkt erfolgreich bezahlt.")
        except errors.PlanIsExpired:
            flash(
                "Der angegebene Plan ist nicht mehr aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            )
    return render_template("member/pay_consumer_product.html")


@main_member.route("/member/profile")
@login_required
@with_injection
def profile(
    get_member_profile: use_cases.GetMemberProfileInfo,
):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    member = current_user.id
    member_profile = get_member_profile(member)
    return render_template(
        "member/profile.html",
        workplaces=member_profile.workplaces,
        account_balance=member_profile.account_balance,
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
def statistics(get_statistics: use_cases.GetStatistics):
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    stats = get_statistics()
    return render_template("member/statistics.html", stats=stats)


@main_member.route("/member/hilfe")
@login_required
def hilfe():
    if not user_is_member():
        return redirect(url_for("auth.zurueck"))

    return render_template("member/help.html")
