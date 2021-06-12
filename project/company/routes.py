import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy.sql import desc

from arbeitszeit import errors, use_cases
from arbeitszeit.transaction_factory import TransactionFactory
from arbeitszeit.datetime_service import DatetimeService
from project import database
from project.database import with_injection
from project.economy import company
from project.extensions import db
from project.forms import ProductSearchForm
from project.models import (
    Company,
    Member,
    Withdrawal,
    Plan,
    Offer,
)

from project.database.repositories import (
    CompanyRepository,
    MemberRepository,
    CompanyWorkerRepository,
    PlanRepository,
    AccountingRepository,
    TransactionRepository,
    ProductOfferRepository,
)

main_company = Blueprint(
    "main_company", __name__, template_folder="templates", static_folder="static"
)


@main_company.route("/company/profile")
@login_required
def profile():
    user_type = session["user_type"]
    if user_type == "company":
        worker = database.get_workers(current_user.id)
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
def suchen():
    """search products in catalog."""

    search_form = ProductSearchForm(request.form)
    results = Offer.query.filter_by(active=True).all()

    if request.method == "POST":
        results = []
        search_string = search_form.data["search"]
        search_field = search_form.data["select"]  # Name, Beschr., Kategorie

        if search_string or search_field:
            if search_field == "Name":
                results = Offer.query.filter(
                    Offer.name.contains(search_string), Offer.active == True
                ).all()

            elif search_field == "Beschreibung":
                results = Offer.query.filter(
                    Offer.description.contains(search_string), Offer.active == True
                ).all()

        else:
            results = Offer.query.filter_by(active=True).all()

        if not results:
            flash("Keine Ergebnisse!")
        else:
            return render_template(
                "company/search.html", form=search_form, results=results
            )

    return render_template("company/search.html", form=search_form, results=results)


@main_company.route("/company/buy/<int:id>", methods=["GET", "POST"])
@login_required
def buy(id):
    offer = Offer.query.filter_by(id=id).first()

    if request.method == "POST":  # if company buys
        purpose = (
            "means_of_prod"
            if request.form["category"] == "Produktionsmittel"
            else "raw_materials"
        )
        amount = int(request.form["amount"])
        company.buy_product("company", offer, amount, purpose, current_user.id)
        flash(f"Kauf von '{amount}'x '{offer.name}' erfolgreich!")
        return redirect("/company/suchen")

    return render_template("company/buy.html", offer=offer)


@main_company.route("/company/create_plan", methods=["GET", "POST"])
@login_required
@with_injection
def create_plan(
    plan_repository: PlanRepository,
    accounting_repository: AccountingRepository,
    transaction_repository: TransactionRepository,
    transaction_factory: TransactionFactory,
):
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
        plan = use_cases.seek_approval(DatetimeService(), plan)
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

    return render_template("company/create_plan.html")


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
                sender_name = f"Mitglied: {received_trans.sending_account.member.name} (received_trans.sending_account.member.id)"
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


@main_company.route("/company/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        # to implement: check in html, if user exists and if worker in company
        receiver_id = request.form["member_id"]
        amount = Decimal(request.form["amount"])
        sender = Company.query.get(current_user.id)
        receiver = Member.query.filter_by(id=receiver_id).first()
        database.send_wages(sender, receiver, amount)

    return render_template("company/transfer.html")


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


@main_company.route("/company/sell_offer", methods=["GET", "POST"])
@login_required
def sell_offer():
    offer_id = request.args.get("id")
    offer = Offer.query.filter_by(id=offer_id).first()

    if request.method == "POST":
        code_input = request.form["code"]
        withdrawal = Withdrawal.query.filter_by(
            code=code_input, entwertet=False
        ).first()
        if not withdrawal:
            flash("Code nicht korrekt oder schon entwertet.")
        else:
            value_code = withdrawal.betrag
            if round(
                (offer.plan.costs_p + offer.plan.costs_r + offer.plan.costs_a), 2
            ) != round(value_code, 2):
                flash("Wert des Codes entspricht nicht dem Preis.")
            else:
                kaufender_type = "member" if withdrawal.type_member else "company"
                database.buy(
                    kaufender_type=kaufender_type,
                    angebot=offer,
                    kaeufer_id=withdrawal.member,
                )
                withdrawal.entwertet = True
                db.session.commit()
                flash("Verkauf erfolgreich")
                return redirect(url_for("main_company.my_offers"))

    return render_template("company/sell_offer.html", offer=offer)


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
