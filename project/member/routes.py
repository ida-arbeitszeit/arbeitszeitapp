from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from project import database
from project.database import with_injection
from project.database.repositories import (
    CompanyRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
)
from project.forms import ProductSearchForm

main_member = Blueprint(
    "main_member", __name__, template_folder="templates", static_folder="static"
)


@main_member.route("/member/kaeufe")
@login_required
@with_injection
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
):
    user_type = session["user_type"]

    if user_type == "company":
        return redirect(url_for("auth.zurueck"))
    else:
        session["user_type"] = "member"
        purchases = list(query_purchases(current_user))
        return render_template("member/my_purchases.html", purchases=purchases)


@main_member.route("/member/suchen", methods=["GET", "POST"])
@login_required
@with_injection
def suchen(
    query_products: use_cases.QueryProducts, offer_repository: ProductOfferRepository
):
    """search products in catalog."""
    search_form = ProductSearchForm(request.form)
    query: Optional[str] = None
    product_filter = use_cases.ProductFilter.by_name

    if request.method == "POST":
        query = search_form.data["search"] or None
        search_field = search_form.data["select"]  # Name, Beschr., Kategorie
        if search_field == "Name":
            product_filter = use_cases.ProductFilter.by_name
        elif search_field == "Beschreibung":
            product_filter = use_cases.ProductFilter.by_description
    results = [
        offer_repository.object_to_orm(offer)
        for offer in query_products(query, product_filter)
    ]
    if not results:
        flash("Keine Ergebnisse!")
    return render_template("member/search.html", form=search_form, results=results)


@main_member.route("/member/buy/<int:id>", methods=["GET", "POST"])
@login_required
@with_injection
def buy(
    id,
    product_offer_repository: ProductOfferRepository,
    member_repository: MemberRepository,
    purchase_product: use_cases.PurchaseProduct,
):
    product_offer = product_offer_repository.get_by_id(id=id)
    buyer = member_repository.get_member_by_id(current_user.id)

    if request.method == "POST":  # if user buys
        purpose = entities.PurposesOfPurchases.consumption
        amount = int(request.form["amount"])
        purchase_product(
            product_offer,
            amount,
            purpose,
            buyer,
        )
        database.commit_changes()
        flash(f"Kauf von '{product_offer.name}' erfolgreich!")
        return redirect("/member/suchen")

    return render_template("member/buy.html", offer=product_offer)


@main_member.route("/member/pay_consumer_product", methods=["GET", "POST"])
@login_required
@with_injection
def pay_consumer_product(
    pay_consumer_product: use_cases.PayConsumerProduct,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    plan_repository: PlanRepository,
):
    if request.method == "POST":
        sender = member_repository.get_member_by_id(current_user.id)
        plan = plan_repository.get_by_id(request.form["plan_id"])
        receiver = company_repository.get_by_id(request.form["company_id"])
        pieces = int(request.form["amount"])
        try:
            pay_consumer_product(
                sender,
                receiver,
                plan,
                pieces,
            )
            database.commit_changes()
            flash("Produkt erfolgreich bezahlt.")
        except errors.CompanyIsNotPlanner:
            flash("Der angegebene Plan gehört nicht zum angegebenen Betrieb.")
        except errors.CompanyDoesNotExist:
            flash("Der Betrieb existiert nicht.")
        except errors.PlanDoesNotExist:
            flash("Der Plan existiert nicht.")
        except errors.PlanIsExpired:
            flash(
                "Der angegebene Plan ist nicht mehr aktuell. Bitte wende dich an den Verkäufer, um eine aktuelle Plan-ID zu erhalten."
            )
    return render_template("member/pay_consumer_product.html")


@main_member.route("/member/profile")
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "member":
        workplaces = current_user.workplaces.all()
        return render_template("member/profile.html", workplaces=workplaces)
    elif user_type == "company":
        return redirect(url_for("auth.zurueck"))


@main_member.route("/member/my_account")
@login_required
def my_account():

    my_account = current_user.account

    all_transactions = []  # date, sender, receiver, amount, purpose

    # all my sent transactions
    for sent_trans in my_account.transactions_sent.all():
        if sent_trans.receiving_account.account_type.name == "member":
            receiver_name = f"Mitglied: {sent_trans.receiving_account.member.name} ({sent_trans.receiving_account.member.id})"
        elif sent_trans.receiving_account.account_type.name in [
            "p",
            "r",
            "a",
            "prd",
        ]:
            receiver_name = f"Betrieb: {sent_trans.receiving_account.company.name} ({sent_trans.receiving_account.company.id})"
        else:
            receiver_name = "Öff. Buchhaltung"

        all_transactions.append(
            [
                sent_trans.date,
                "Ich",
                receiver_name,
                -sent_trans.amount,
                sent_trans.purpose,
            ]
        )

    # all my received transactions
    for received_trans in my_account.transactions_received.all():
        if received_trans.sending_account.account_type.name == "accounting":
            sender_name = "Öff. Buchhaltung"
        elif received_trans.sending_account.account_type.name == "member":
            sender_name = f"Mitglied: {received_trans.sending_account.member.name} ({received_trans.sending_account.member.id})"
        elif received_trans.sending_account.account_type.name in [
            "p",
            "r",
            "a",
            "prd",
        ]:
            sender_name = f"Betrieb: {received_trans.sending_account.company.name} ({received_trans.sending_account.company.id})"

        all_transactions.append(
            [
                received_trans.date,
                sender_name,
                "Ich",
                received_trans.amount,
                received_trans.purpose,
            ]
        )

    all_transactions_sorted = sorted(all_transactions, reverse=True)

    my_balance = current_user.account.balance

    return render_template(
        "member/my_account.html",
        all_transactions=all_transactions_sorted,
        my_balance=my_balance,
    )


@main_member.route("/member/hilfe")
@login_required
def hilfe():
    return render_template("member/help.html")
