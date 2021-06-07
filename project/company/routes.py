import datetime
from decimal import Decimal

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy.sql import desc

from arbeitszeit import errors, use_cases
from project import database
from project.database import with_injection
from project.economy import company, accounting
from project.extensions import db
from project.forms import ProductSearchForm
from project.models import (
    Company,
    Kaeufe,
    Member,
    TransactionsAccountingToCompany,
    TransactionsCompanyToCompany,
    TransactionsCompanyToMember,
    Withdrawal,
    Plan,
    Offer,
)
from project.tables import (
    Preiszusammensetzung,
    WorkersTable,
)
from project.database.repositories import (
    CompanyRepository,
    MemberRepository,
    CompanyWorkerRepository,
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
        workers_list = database.get_workers(current_user.id)
        workers_table = WorkersTable(workers_list, no_items="(Noch keine Mitarbeiter.)")
        return render_template("company/work.html", workers_table=workers_table)


@main_company.route("/company/suchen", methods=["GET", "POST"])
@login_required
def suchen():
    """search products in catalog."""

    search_form = ProductSearchForm(request.form)
    # srch = database.SearchProducts()
    results = Offer.query.filter_by(active=True).all()
    # results = srch.get_active_offers()

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


@main_company.route("/company/details/<int:id>", methods=["GET", "POST"])
@login_required
def details(id):
    """show details of selected product."""
    comp = database.CompositionOfPrices()
    table_of_composition = comp.get_table_of_composition(id)
    cols_dict = comp.get_positions_in_table(table_of_composition)
    dot = comp.create_dots(cols_dict, table_of_composition)
    piped = dot.pipe().decode("utf-8")
    table_preiszus = Preiszusammensetzung(table_of_composition)
    srch = database.SearchProducts()
    angebot_ = srch.get_offer_by_id(id)
    preise = (angebot_.preis, angebot_.koop_preis)

    if request.method == "POST":
        return redirect("/company/suchen")

    return render_template(
        "company/details.html",
        table_preiszus=table_preiszus,
        piped=piped,
        preise=preise,
    )


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
def create_plan():
    if request.method == "POST":
        costs_p = float(request.form["costs_p"])
        costs_r = float(request.form["costs_r"])
        costs_a = float(request.form["costs_a"])
        prd_name = request.form["prd_name"]
        prd_unit = request.form["prd_unit"]
        prd_amount = int(request.form["prd_amount"])
        description = request.form["description"]
        timeframe = int(request.form["timeframe"])
        social_accounting_id = accounting.id

        plan_details = (
            costs_p,
            costs_r,
            costs_a,
            prd_name,
            prd_unit,
            prd_amount,
            description,
            timeframe,
        )

        plan = database.planning(
            planner_id=current_user.id,
            plan_details=plan_details,
            social_accounting_id=social_accounting_id,
        )

        plan = database.seek_approval(plan)
        if plan.approved:
            database.grant_credit(plan)
            flash("Plan erfolgreich erstellt und genehmigt. Kredit wurde gewährt.")
            return redirect("/company/my_plans")

        else:
            flash(f"Plan nicht genehmigt. Grund:\n{plan.approval_reason}")
            return redirect("/company/create_plan")

    return render_template("company/create_plan.html")


@main_company.route("/company/my_plans", methods=["GET", "POST"])
@login_required
def my_plans():
    my_company = Company.query.get(current_user.id)
    plans = (
        my_company.plans.filter_by(approved=True)
        .order_by(desc(Plan.plan_creation_date))
        .all()
    )
    return render_template("company/my_plans.html", plans=plans)


@main_company.route("/company/create_offer/<int:plan_id>", methods=["GET", "POST"])
@login_required
def create_offer(plan_id):
    if request.method == "POST":  # create offer
        name = request.form["name"]
        description = request.form["description"]
        prd_amount = int(request.form["prd_amount"])

        new_offer = Offer(
            plan_id=plan_id,
            cr_date=datetime.datetime.now(),
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

    received_from_accounting = (
        TransactionsAccountingToCompany.query.filter_by(receiver_id=current_user.id)
        .order_by(desc(TransactionsAccountingToCompany.date))
        .all()
    )

    sent_to_company = (
        TransactionsCompanyToCompany.query.filter_by(account_owner=current_user.id)
        .order_by(desc(TransactionsCompanyToCompany.date))
        .all()
    )

    received_from_company = (
        TransactionsCompanyToCompany.query.filter_by(receiver_id=current_user.id)
        .order_by(desc(TransactionsCompanyToCompany.date))
        .all()
    )

    sent_to_workers = (
        TransactionsCompanyToMember.query.filter_by(account_owner=current_user.id)
        .order_by(desc(TransactionsCompanyToMember.date))
        .all()
    )

    return render_template(
        "company/my_accounts.html",
        my_company=my_company,
        received_from_accounting=received_from_accounting,
        sent_to_company=sent_to_company,
        received_from_company=received_from_company,
        sent_to_workers=sent_to_workers,
    )


@main_company.route("/company/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        receiver_id = request.form["member_id"]
        amount = Decimal(request.form["amount"])
        sender = Company.query.get(current_user.id)
        receiver = Member.query.get(receiver_id)
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
def delete_offer():
    offer_id = request.args.get("id")
    offer = Offer.query.filter_by(id=offer_id).first()
    if request.method == "POST":
        company.delete_product(offer_id)
        flash("Löschen des Angebots erfolgreich.")
        return redirect(url_for("main_company.my_offers"))

    return render_template("company/delete_offer.html", offer=offer)


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
