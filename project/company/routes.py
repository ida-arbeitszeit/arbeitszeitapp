import datetime
from decimal import Decimal
from typing import Optional

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.transaction_factory import TransactionFactory
from project import database
from project.database import with_injection
from project.database.repositories import (
    AccountingRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
    PurchaseRepository,
    TransactionRepository,
)
from project.extensions import db
from project.forms import ProductSearchForm
from project.models import Company, Offer, Plan

main_company = Blueprint(
    "main_company", __name__, template_folder="templates", static_folder="static"
)


@main_company.route("/company/profile")
@login_required
@with_injection
def profile(
    company_repository: CompanyRepository,
    company_worker_repository: CompanyWorkerRepository,
):
    user_type = session["user_type"]
    if user_type == "company":
        company = company_repository.get_by_id(current_user.id)
        worker = company_worker_repository.get_company_workers(company)
        if worker:
            having_workers = True
        else:
            having_workers = False
        return render_template("company/profile.html", having_workers=having_workers)
    elif user_type == "member":
        return redirect(url_for("auth.zurueck"))


@main_company.route("/company/work", methods=["GET", "POST"])
@login_required
@with_injection
def arbeit(
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    company_worker_repository: CompanyWorkerRepository,
):
    """shows workers and worked hours."""
    if request.method == "POST":  # (add worker to company)
        company = company_repository.get_by_id(current_user.id)
        if not company:
            flash("Angemeldeter Betrieb konnte nicht ermittelt werden.")
            return redirect(url_for("auth.start"))
        member = member_repository.get_member_by_id(request.form["member"])
        if not member:
            flash("Mitglied existiert nicht.")
            return redirect(url_for("main_company.arbeit"))
        try:
            use_cases.add_worker_to_company(
                company_worker_repository,
                company,
                member,
            )
        except errors.WorkerAlreadyAtCompany:
            flash("Mitglied ist bereits in diesem Betrieb beschäftigt.")
        database.commit_changes()
        return redirect(url_for("main_company.arbeit"))
    elif request.method == "GET":
        workers_list = company_worker_repository.get_company_workers(
            company_repository.get_by_id(current_user.id)
        )
        return render_template("company/work.html", workers_list=workers_list)


@main_company.route("/company/suchen", methods=["GET", "POST"])
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
    return render_template("company/search.html", form=search_form, results=results)


@main_company.route("/company/buy/<int:id>", methods=["GET", "POST"])
@login_required
@with_injection
def buy(
    id: int,
    purchase_product: use_cases.PurchaseProduct,
    product_offer_repository: ProductOfferRepository,
    company_repository: CompanyRepository,
    purchase_repository: PurchaseRepository,
    transaction_repository: TransactionRepository,
):
    product_offer = product_offer_repository.get_by_id(id=id)
    buyer = company_repository.get_by_id(current_user.id)

    if request.method == "POST":  # if company buys
        purpose = (
            entities.PurposesOfPurchases.means_of_prod
            if request.form["category"] == "Produktionsmittel"
            else entities.PurposesOfPurchases.raw_materials
        )
        amount = int(request.form["amount"])
        purchase_product(
            purchase_repository,
            transaction_repository,
            product_offer,
            amount,
            purpose,
            buyer,
        )
        database.commit_changes()

        flash(f"Kauf von '{amount}'x '{product_offer.name}' erfolgreich!")
        return redirect("/company/suchen")

    return render_template("company/buy.html", offer=product_offer)


@main_company.route("/company/create_plan", methods=["GET", "POST"])
@login_required
@with_injection
def create_plan(
    plan_repository: PlanRepository,
    accounting_repository: AccountingRepository,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):

    if request.args.get("renew"):
        plan_id = request.args.get("renew")
        plan_to_renew = plan_repository.get_by_id(plan_id)
    else:
        plan_to_renew = None

    if request.method == "POST":
        costs_p = float(request.form["costs_p"])
        costs_r = float(request.form["costs_r"])
        costs_a = float(request.form["costs_a"])
        prd_name = request.form["prd_name"]
        prd_unit = request.form["prd_unit"]
        prd_amount = int(request.form["prd_amount"])
        description = request.form["description"]
        timeframe = int(request.form["timeframe"])

        plan_orm = Plan(
            plan_creation_date=DatetimeService().now(),
            planner=current_user.id,
            costs_p=costs_p,
            costs_r=costs_r,
            costs_a=costs_a,
            prd_name=prd_name,
            prd_unit=prd_unit,
            prd_amount=prd_amount,
            description=description,
            timeframe=timeframe,
            social_accounting=1,
        )
        db.session.add(plan_orm)
        database.commit_changes()

        plan = plan_repository.object_from_orm(plan_orm)

        if plan_to_renew:
            # check if there have been made modifications to the plan by the user
            if (
                (costs_p == plan_to_renew.costs_p)
                and (costs_r == plan_to_renew.costs_r)
                and (costs_a == plan_to_renew.costs_a)
                and (prd_name == plan_to_renew.prd_name)
                and (prd_unit == plan_to_renew.prd_unit)
                and (prd_amount == plan_to_renew.prd_amount)
                and (description == plan_to_renew.description)
                and (timeframe == plan_to_renew.timeframe)
            ):
                plan_modifications = False
            else:
                plan_modifications = True

            plan_renewal = entities.PlanRenewal(
                original_plan=plan_to_renew,
                modifications=plan_modifications,
            )
        else:
            plan_renewal = None

        plan = use_cases.seek_approval(DatetimeService(), plan, plan_renewal)
        database.commit_changes()
        if plan.approved:
            social_accounting = accounting_repository.get_by_id(1)
            use_cases.grant_credit(
                plan, social_accounting, transaction_repository, transaction_factory
            )
            database.commit_changes()
            flash("Plan erfolgreich erstellt und genehmigt. Kredit wurde gewährt.")
            return redirect("/company/my_plans")

        else:
            flash(f"Plan nicht genehmigt. Grund:\n{plan.approval_reason}")
            return redirect("/company/create_plan")

    return render_template("company/create_plan.html", plan_to_renew=plan_to_renew)


@main_company.route("/company/my_plans", methods=["GET", "POST"])
@login_required
@with_injection
def my_plans(
    plan_repository: PlanRepository,
):
    plans_orm = current_user.plans.filter_by(approved=True, expired=False).all()
    plans = [plan_repository.object_from_orm(plan) for plan in plans_orm]

    plans = use_cases.check_plans_for_expiration(plans)
    database.commit_changes()

    plans_orm_expired = current_user.plans.filter_by(approved=True, expired=True).all()
    plans_expired = [
        plan_repository.object_from_orm(plan) for plan in plans_orm_expired
    ]

    for plan in plans:
        expiration_date = plan.plan_creation_date + datetime.timedelta(
            days=int(plan.timeframe)
        )
        expiration_relative = DatetimeService().now() - expiration_date
        seconds_until_exp = abs(expiration_relative.total_seconds())
        # days
        days = int(seconds_until_exp // 86400)
        # remaining seconds
        seconds_until_exp = seconds_until_exp - (days * 86400)
        # hours
        hours = int(seconds_until_exp // 3600)
        # remaining seconds
        seconds_until_exp = seconds_until_exp - (hours * 3600)
        # minutes
        minutes = int(seconds_until_exp // 60)

        exp_string = f"{days} T. {hours} Std. {minutes} Min."
        plan.expiration_relative = exp_string
        plan.expiration_date = expiration_date

    return render_template(
        "company/my_plans.html",
        plans=plans,
        plans_expired=plans_expired,
    )


@main_company.route("/company/create_offer/<int:plan_id>", methods=["GET", "POST"])
@login_required
def create_offer(plan_id):
    if request.method == "POST":  # create offer
        name = request.form["name"]
        description = request.form["description"]
        prd_amount = int(request.form["prd_amount"])

        new_offer = Offer(
            plan_id=plan_id,
            cr_date=DatetimeService().now(),
            name=name,
            description=description,
            amount_available=prd_amount,
            active=True,
        )

        db.session.add(new_offer)
        db.session.commit()
        return render_template("company/create_offer_in_app.html", offer=new_offer)

    plan = Plan.query.filter_by(id=plan_id).first()
    return render_template("company/create_offer.html", plan=plan)


@main_company.route("/company/my_accounts")
@login_required
def my_accounts():
    my_company = Company.query.get(current_user.id)
    my_accounts = my_company.accounts.all()

    all_transactions = []  # date, sender, receiver, p, r, a, prd, purpose

    for my_account in my_accounts:
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

            change_p, change_r, change_a, change_prd = ("", "", "", "")
            if my_account.account_type.name == "p":
                change_p = -sent_trans.amount
            elif my_account.account_type.name == "r":
                change_r = -sent_trans.amount
            elif my_account.account_type.name == "a":
                change_a = -sent_trans.amount
            elif my_account.account_type.name == "prd":
                change_prd = -sent_trans.amount

            all_transactions.append(
                [
                    sent_trans.date,
                    "Ich",
                    receiver_name,
                    change_p,
                    change_r,
                    change_a,
                    change_prd,
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

            change_p, change_r, change_a, change_prd = ("", "", "", "")
            if my_account.account_type.name == "p":
                change_p = received_trans.amount
            elif my_account.account_type.name == "r":
                change_r = received_trans.amount
            elif my_account.account_type.name == "a":
                change_a = received_trans.amount
            elif my_account.account_type.name == "prd":
                change_prd = received_trans.amount

            all_transactions.append(
                [
                    received_trans.date,
                    sender_name,
                    "Ich",
                    change_p,
                    change_r,
                    change_a,
                    change_prd,
                    received_trans.purpose,
                ]
            )

    all_transactions_sorted = sorted(all_transactions, reverse=True)

    my_balances = []
    for type in ["p", "r", "a", "prd"]:
        balance = my_company.accounts.filter_by(account_type=type).first().balance
        my_balances.append(balance)

    return render_template(
        "company/my_accounts.html",
        my_balances=my_balances,
        all_transactions=all_transactions_sorted,
    )


@main_company.route("/company/transfer_to_worker", methods=["GET", "POST"])
@login_required
@with_injection
def transfer_to_worker(
    transaction_repository: TransactionRepository,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    company_worker_repository: CompanyWorkerRepository,
):
    if request.method == "POST":
        sender = company_repository.get_by_id(current_user.id)
        receiver = member_repository.get_member_by_id(request.form["member_id"])
        amount = Decimal(request.form["amount"])

        try:
            use_cases.send_work_certificates_to_worker(
                company_worker_repository,
                transaction_repository,
                sender,
                receiver,
                amount,
            )
            database.commit_changes()
            flash("Erfolgreich überwiesen.")
        except errors.WorkerNotAtCompany:
            flash("Mitglied ist nicht in diesem Betrieb beschäftigt.")
        except errors.WorkerDoesNotExist:
            flash("Mitglied existiert nicht.")

    return render_template("company/transfer_to_worker.html")


@main_company.route("/company/transfer_to_company", methods=["GET", "POST"])
@login_required
@with_injection
def transfer_to_company(
    transaction_repository: TransactionRepository,
    company_repository: CompanyRepository,
    plan_repository: PlanRepository,
):
    if request.method == "POST":
        sender = company_repository.get_by_id(current_user.id)
        plan = plan_repository.get_by_id(request.form["plan_id"])
        receiver = company_repository.get_by_id(request.form["company_id"])
        amount = Decimal(request.form["amount"])
        purpose = (
            "means_of_prod"
            if request.form["category"] == "Produktionsmittel"
            else "raw_materials"
        )
        try:
            use_cases.pay_means_of_production(
                transaction_repository,
                sender,
                receiver,
                plan,
                amount,
                purpose,
            )
            database.commit_changes()
            flash("Erfolgreich bezahlt.")
        except errors.CompanyIsNotPlanner:
            flash("Der angegebene Plan gehört nicht zum angegebenen Betrieb.")
        except errors.CompanyDoesNotExist:
            flash("Der Betrieb existiert nicht.")
        except errors.PlanDoesNotExist:
            flash("Der Plan existiert nicht.")

    return render_template("company/transfer_to_company.html")


@main_company.route("/company/my_offers")
@login_required
def my_offers():
    my_company = Company.query.filter_by(id=current_user.id).first()
    my_plans = my_company.plans.all()
    my_offers = []
    for plan in my_plans:
        for offer in plan.offers.all():
            if offer.active == True:
                my_offers.append(offer)

    return render_template("company/my_offers.html", offers=my_offers)


@main_company.route("/company/delete_offer", methods=["GET", "POST"])
@login_required
@with_injection
def delete_offer(
    product_offer_repository: ProductOfferRepository,
):
    offer_id = request.args.get("id")
    product_offer = product_offer_repository.get_by_id(offer_id)
    if request.method == "POST":
        use_cases.deactivate_offer(product_offer)
        database.commit_changes()
        flash("Löschen des Angebots erfolgreich.")
        return redirect(url_for("main_company.my_offers"))

    return render_template("company/delete_offer.html", offer=product_offer)


@main_company.route("/company/cooperate", methods=["GET", "POST"])
@login_required
def cooperate():
    # under construction
    pass
    return render_template("company/cooperate.html")


@main_company.route("/company/hilfe")
@login_required
def hilfe():
    return render_template("company/help.html")
