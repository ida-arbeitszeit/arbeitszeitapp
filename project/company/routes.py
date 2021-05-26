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
    Angebote,
    Arbeit,
    Company,
    Kaeufe,
    Member,
    Produktionsmittel,
    TransactionsAccountingToCompany,
    Withdrawal,
    Plan,
)
from project.tables import (
    HoursTable,
    Preiszusammensetzung,
    ProduktionsmittelTable,
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
        hours_worked = database.get_hours_worked(current_user.id)
        hours_table = HoursTable(
            hours_worked, no_items="(Noch keine Stunden gearbeitet.)"
        )
        return render_template(
            "company/work.html", workers_table=workers_table, hours_table=hours_table
        )


@main_company.route("/company/produktionsmittel")
@login_required
def produktionsmittel():
    """shows means of production."""
    (
        means_of_production_in_use,
        means_of_production_consumed,
    ) = database.get_means_of_prod(current_user.id)

    table_in_use = ProduktionsmittelTable(
        means_of_production_in_use, no_items="(Keine Produktionsmittel vorhanden.)"
    )
    table_consumed = ProduktionsmittelTable(
        means_of_production_consumed,
        no_items="(Noch keine Produktionsmittel verbraucht.)",
    )

    return render_template(
        "company/means_of_production.html",
        table_aktiv=table_in_use,
        table_inaktiv=table_consumed,
    )


@main_company.route("/company/suchen", methods=["GET", "POST"])
@login_required
def suchen():
    """search products in catalog."""
    search_form = ProductSearchForm(request.form)
    srch = database.SearchProducts()
    results = srch.get_active_offers()

    if request.method == "POST":
        results = []
        search_string = search_form.data["search"]
        search_field = search_form.data["select"]  # Name, Beschr., Kategorie

        if search_string:
            results = srch.get_active_offers(search_string, search_field)
        else:
            results = srch.get_active_offers()

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
    srch = database.SearchProducts()
    angebot = srch.get_offer_by_id(id)
    if request.method == "POST":  # if company buys
        company.buy_product("company", database.get_offer_by_id(id), current_user.id)
        flash(f"Kauf von '{angebot.angebot_name}' erfolgreich!")
        return redirect("/company/suchen")

    return render_template("company/buy.html", angebot=angebot)


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


@main_company.route("/company/my_plans")
@login_required
def my_plans():
    my_company = Company.query.get(current_user.id)
    plans = (
        my_company.plans.filter_by(approved=True)
        .order_by(desc(Plan.plan_creation_date))
        .all()
    )
    return render_template("company/my_plans.html", plans=plans)


@main_company.route("/company/my_accounts")
@login_required
def my_accounts():
    my_company = Company.query.get(current_user.id)
    received_from_accounting = (
        TransactionsAccountingToCompany.query.filter_by(receiver_id=current_user.id)
        .order_by(desc(TransactionsAccountingToCompany.date))
        .all()
    )
    return render_template(
        "company/my_accounts.html",
        my_company=my_company,
        received_from_accounting=received_from_accounting,
    )


@main_company.route("/company/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    if request.method == "POST":
        receiver_id = request.form["member_id"]
        amount = request.form["amount"]
        sender = Company.query.get(current_user.id)
        receiver = Member.query.get(receiver_id)
        database.send_wages(sender, receiver, amount)

    return render_template("company/transfer.html")


@main_company.route("/company/anbieten", methods=["GET", "POST"])
@login_required
def new_offer():
    """
    Ein neues Angebot hinzufügen
    """
    produktionsmittel_aktiv, _ = database.get_means_of_prod(current_user.id)
    workers_list = database.get_workers(current_user.id)

    if request.method == "POST":
        quantity = int(request.form["quantity"])
        # create request dictionary
        request_dict = request.form.to_dict()

        # arbeit
        # dict with arbeit values
        arbeit_dict = dict(
            filter(lambda elem: elem[0][:7] == "member_", request_dict.items())
        )
        # arbeit dict entries that are not zero
        arbeit_dict_not_zero = dict(
            filter(lambda elem: Decimal(elem[1]) != 0, arbeit_dict.items())
        )
        kosten_arbeit = 0
        if arbeit_dict_not_zero:
            # calculate kosten arbeit
            member_id_list = []
            stunden_list = []
            for key in list(arbeit_dict_not_zero.keys()):
                member_id_list.append(key[7:])
            for value in list(arbeit_dict_not_zero.values()):
                stunden_list.append(Decimal(value))
            assert len(member_id_list) == len(stunden_list)
            kosten_arbeit = sum(stunden_list) / quantity

        # produktionsmittel
        # dict with produktionsmittel values
        pm_dict = dict(filter(lambda elem: elem[0][:3] == "id_", request_dict.items()))
        # pm dict entries that are not zero
        pm_dict_not_zero = dict(
            filter(lambda elem: Decimal(elem[1]) != 0, pm_dict.items())
        )
        kosten_pm = 0
        if pm_dict_not_zero:
            # calculate kosten pm
            # turning pm-dict into two lists
            kauf_id_list = []
            prozent_list = []
            for key in list(pm_dict_not_zero.keys()):
                kauf_id_list.append(key[3:])
            for value in list(pm_dict_not_zero.values()):
                prozent_list.append(Decimal(value) / 100)

            # preise
            preise_list = []
            for idx in kauf_id_list:
                # HIER WERDEN DIE ORIGINALEN KAUFPREISE ANGERECHNET,
                # NICHT DIE AKTUELLEN MARKTPREISE!
                qry = (
                    db.session.query(Kaeufe.kaufpreis)
                    .select_from(Kaeufe)
                    .filter(Kaeufe.id == idx)
                    .first()
                )
                preise_list.append(Decimal(qry.kaufpreis))
            kosten_einzeln = []
            for num1, num2 in zip(prozent_list, preise_list):
                kosten_einzeln.append(num1 * num2)
            kosten_pm = sum(kosten_einzeln) / quantity

        # TO DO LATER: validate input/check if enough guthaben
        # if current_user.guthaben < sum(stunden_list):
        #     flash("Dein Guthaben reicht nicht aus, um die Arbeit zu bezahlen.")

        # save new angebot(e), pay workers and register arbeit
        # and produktionsmittel
        current_time = datetime.datetime.now()
        for quant in range(quantity):
            new_angebot = Angebote(
                name=request.form["name"],
                cr_date=current_time,
                company=current_user.id,
                beschreibung=request.form["beschreibung"],
                kategorie=request.form["kategorie"],
                p_kosten=kosten_pm,
                v_kosten=kosten_arbeit,
                preis=kosten_arbeit + kosten_pm,
            )
            db.session.add(new_angebot)
            db.session.commit()

            # create rows in table "arbeit"
            if arbeit_dict_not_zero:
                assert len(member_id_list) == len(stunden_list)
                for count, i in enumerate(member_id_list):
                    new_arbeit = Arbeit(
                        angebot=new_angebot.id,
                        member=i,
                        stunden=stunden_list[count] / quantity,
                    )
                    db.session.add(new_arbeit)
                    # guthaben der arbeiter erhöhen
                    # TO DO: check if it's inefficient
                    # doing this for every quant
                    Member.query.filter_by(id=i).first().guthaben += (
                        stunden_list[count] / quantity
                    )

            # create new row in produktionsmittel (um gesamten verbrauch
            # zu erhalten, muss gruppiert/summiert werden!)
            if pm_dict_not_zero:
                assert len(kauf_id_list) == len(prozent_list)
                for count, i in enumerate(kauf_id_list):
                    new_produktionsmittel_prd = Produktionsmittel(
                        angebot=new_angebot.id,
                        kauf=i,
                        prozent_gebraucht=(prozent_list[count] * 100 / quantity),
                    )
                    db.session.add(new_produktionsmittel_prd)
            db.session.commit()

        # TO DO: kosten zusammenfassen und bestätigen lassen!
        flash("Angebot erfolgreich gespeichert!")
        return redirect(url_for("main_company.my_offers"))

    categ = [
        "Dienstleistungen",
        "Elektronik",
        "Freizeit & Hobby",
        "Haus & Garten",
        "Haustiere",
        "Nahrungsmittel",
        "Musik, Filme und Bücher",
        "Nachbarschaftshilfe",
        "Unterricht und Kurse",
    ]

    return render_template(
        "company/new_offer.html",
        produktionsmittel_aktiv=produktionsmittel_aktiv,
        workers_list=workers_list,
        categ=categ,
    )


@main_company.route("/company/my_offers")
@login_required
def my_offers():
    srch = database.SearchProducts()
    qry = srch.get_offers()
    current_offers = qry.filter(
        Angebote.aktiv == True, Company.id == current_user.id
    ).all()
    past_offers = qry.filter(
        Angebote.aktiv == False, Company.id == current_user.id
    ).all()
    return render_template(
        "company/my_offers.html", current_offers=current_offers, past_offers=past_offers
    )


@main_company.route("/company/delete_offer", methods=["GET", "POST"])
@login_required
def delete_offer():
    angebot_id = request.args.get("id")
    angebot = Angebote.query.filter_by(id=angebot_id).first()
    if request.method == "POST":
        company.delete_product(angebot_id)
        flash("Löschen des Angebots erfolgreich.")
        return redirect(url_for("main_company.my_offers"))

    return render_template("company/delete_offer.html", angebot=angebot)


@main_company.route("/company/sell_offer", methods=["GET", "POST"])
@login_required
def sell_offer():
    angebot_id = request.args.get("id")
    angebot = Angebote.query.filter_by(id=angebot_id).first()

    if request.method == "POST":
        code_input = request.form["code"]
        withdrawal = Withdrawal.query.filter_by(
            code=code_input, entwertet=False
        ).first()
        if not withdrawal:
            flash("Code nicht korrekt oder schon entwertet.")
        else:
            value_code = withdrawal.betrag
            if round(angebot.preis, 2) != round(value_code, 2):
                flash("Wert des Codes entspricht nicht dem Preis.")
            else:
                kaufender_type = "member" if withdrawal.type_member else "company"
                database.buy(
                    kaufender_type=kaufender_type,
                    angebot=angebot,
                    kaeufer_id=withdrawal.member,
                )
                withdrawal.entwertet = True
                db.session.commit()
                flash("Verkauf erfolgreich")
                return redirect(url_for("main_company.my_offers"))

    return render_template("company/sell_offer.html", angebot=angebot)


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
