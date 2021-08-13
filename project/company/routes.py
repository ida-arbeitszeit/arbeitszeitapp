from decimal import Decimal
from typing import Optional
from uuid import UUID

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from arbeitszeit.datetime_service import DatetimeService
from project import database
from project.database import (
    AccountingRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
    with_injection,
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
    """shows workers and add workers to company."""
    if request.method == "POST":  # add worker to company
        company = company_repository.get_by_id(current_user.id)
        member = member_repository.get_member_by_id(request.form["member"])
        try:
            use_cases.add_worker_to_company(
                company_worker_repository,
                company,
                member,
            )
        except errors.CompanyDoesNotExist:
            flash("Angemeldeter Betrieb konnte nicht ermittelt werden.")
            return redirect(url_for("auth.start"))
        except errors.WorkerAlreadyAtCompany:
            flash("Mitglied ist bereits in diesem Betrieb beschäftigt.")
        except errors.WorkerDoesNotExist:
            flash("Mitglied existiert nicht.")
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
def suchen(query_products: use_cases.QueryProducts):
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
    results = list(query_products(query, product_filter))

    if not results:
        flash("Keine Ergebnisse!")
    return render_template("company/search.html", form=search_form, results=results)


@main_company.route("/company/buy/<uuid:id>", methods=["GET", "POST"])
@login_required
@with_injection
def buy(
    id: UUID,
    purchase_product: use_cases.PurchaseProduct,
    product_offer_repository: ProductOfferRepository,
    company_repository: CompanyRepository,
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
            product_offer,
            amount,
            purpose,
            buyer,
        )
        database.commit_changes()

        flash(f"Kauf von '{amount}'x '{product_offer.name}' erfolgreich!")
        return redirect("/company/suchen")

    return render_template("company/buy.html", offer=product_offer)


@main_company.route("/company/kaeufe")
@login_required
@with_injection
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
    company_repository: CompanyRepository,
):
    user_type = session["user_type"]

    if user_type == "member":
        return redirect(url_for("auth.zurueck"))
    else:
        company = company_repository.get_by_id(current_user.id)
        session["user_type"] = "company"
        purchases = list(query_purchases(company))
        return render_template("company/my_purchases.html", purchases=purchases)


@main_company.route("/company/create_plan", methods=["GET", "POST"])
@login_required
@with_injection
def create_plan(
    seek_approval: use_cases.SeekApproval,
    plan_repository: PlanRepository,
    social_accounting_repository: AccountingRepository,
):
    original_plan_id: Optional[str] = request.args.get("original_plan_id")
    original_plan = (
        plan_repository.get_by_id(UUID(original_plan_id)) if original_plan_id else None
    )

    if request.method == "POST":  # Button "Plan erstellen"
        plan_data = dict(request.form)

        new_plan_orm = Plan(
            plan_creation_date=DatetimeService().now(),
            planner=current_user.id,
            costs_p=float(plan_data["costs_p"]),
            costs_r=float(plan_data["costs_r"]),
            costs_a=float(plan_data["costs_a"]),
            prd_name=plan_data["prd_name"],
            prd_unit=plan_data["prd_unit"],
            prd_amount=int(plan_data["prd_amount"]),
            description=plan_data["description"],
            timeframe=int(plan_data["timeframe"]),
            is_public_service=True
            if plan_data["productive_or_public"] == "public"
            else False,
            social_accounting=social_accounting_repository.get_or_create_social_accounting_orm().id,
        )
        db.session.add(new_plan_orm)
        database.commit_changes()
        new_plan = plan_repository.object_from_orm(new_plan_orm)

        is_approved = seek_approval(new_plan, original_plan)
        database.commit_changes()

        if is_approved:
            flash("Plan erfolgreich erstellt und genehmigt. Kredit wurde gewährt.")
            return redirect("/company/my_plans")
        else:
            flash(f"Plan nicht genehmigt. Grund:\n{new_plan.approval_reason}")
            return redirect(
                url_for("main_company.create_plan", original_plan_id=original_plan_id)
            )

    return render_template("company/create_plan.html", original_plan=original_plan)


@main_company.route("/company/my_plans", methods=["GET", "POST"])
@login_required
@with_injection
def my_plans(
    plan_repository: PlanRepository,
):
    plans_approved = [
        plan_repository.object_from_orm(plan)
        for plan in current_user.plans.filter_by(
            approved=True,
        ).all()
    ]

    for plan in plans_approved:
        use_cases.calculate_plan_expiration_and_check_if_expired(plan)
    database.commit_changes()

    plans_expired = [plan for plan in plans_approved if plan.expired]
    plans_not_expired = [plan for plan in plans_approved if not plan.expired]

    return render_template(
        "company/my_plans.html",
        plans=plans_not_expired,
        plans_expired=plans_expired,
    )


@main_company.route("/company/create_offer/<uuid:plan_id>", methods=["GET", "POST"])
@login_required
def create_offer(plan_id):
    if request.method == "POST":  # create offer
        name = request.form["name"]
        description = request.form["description"]
        prd_amount = int(request.form["prd_amount"])

        new_offer = Offer(
            plan_id=str(plan_id),
            cr_date=DatetimeService().now(),
            name=name,
            description=description,
            amount_available=prd_amount,
            active=True,
        )

        db.session.add(new_offer)
        db.session.commit()
        return render_template("company/create_offer_in_app.html", offer=new_offer)

    plan = Plan.query.filter_by(id=str(plan_id)).first()
    return render_template("company/create_offer.html", plan=plan)


@main_company.route("/company/my_accounts")
@login_required
@with_injection
def my_accounts(
    company_repository: CompanyRepository,
    get_transaction_infos: use_cases.GetTransactionInfos,
):
    company = company_repository.object_from_orm(current_user)

    all_trans_infos = get_transaction_infos(company)

    my_balances = []
    for account in company.accounts():
        my_balances.append(account.balance)

    return render_template(
        "company/my_accounts.html",
        my_balances=my_balances,
        all_transactions=all_trans_infos,
    )


@main_company.route("/company/transfer_to_worker", methods=["GET", "POST"])
@login_required
@with_injection
def transfer_to_worker(
    send_work_certificates_to_worker: use_cases.SendWorkCertificatesToWorker,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
):
    if request.method == "POST":
        company = company_repository.get_by_id(current_user.id)
        worker = member_repository.get_member_by_id(request.form["member_id"])
        amount = Decimal(request.form["amount"])

        try:
            send_work_certificates_to_worker(
                company,
                worker,
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
    pay_means_of_production: use_cases.PayMeansOfProduction,
    company_repository: CompanyRepository,
    plan_repository: PlanRepository,
):
    if request.method == "POST":
        sender = company_repository.get_by_id(current_user.id)
        plan = plan_repository.get_by_id(request.form["plan_id"])
        receiver = company_repository.get_by_id(request.form["company_id"])
        pieces = int(request.form["amount"])
        purpose = (
            entities.PurposesOfPurchases.means_of_prod
            if request.form["category"] == "Produktionsmittel"
            else entities.PurposesOfPurchases.raw_materials
        )
        try:
            pay_means_of_production(
                sender,
                receiver,
                plan,
                pieces,
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
@with_injection
def my_offers(offer_repository: ProductOfferRepository):
    my_company = Company.query.filter_by(id=current_user.id).first()
    my_plans = my_company.plans.all()
    my_offers = []
    for plan in my_plans:
        active_offers = plan.offers.filter_by(active=True).all()
        for offer in active_offers:
            my_offers.append(offer)
    my_offers = [offer_repository.object_from_orm(offer) for offer in my_offers]

    return render_template("company/my_offers.html", offers=my_offers)


@main_company.route("/company/delete_offer", methods=["GET", "POST"])
@login_required
@with_injection
def delete_offer(
    product_offer_repository: ProductOfferRepository,
):
    offer_id = request.args.get("id")
    assert offer_id
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
