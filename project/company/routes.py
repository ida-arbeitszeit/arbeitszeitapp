from decimal import Decimal
from typing import Optional, cast
from uuid import UUID

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from arbeitszeit.use_cases import (
    CreateOffer,
    CreateOfferRequest,
    CreatePlanDraft,
    CreatePlanDraftRequest,
    DeleteOffer,
    DeleteOfferRequest,
    DeletePlan,
    GetPlanSummary,
)
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_web.create_offer import CreateOfferPresenter
from arbeitszeit_web.delete_offer import DeleteOfferPresenter
from arbeitszeit_web.delete_plan import DeletePlanPresenter
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.query_products import (
    QueryProductsController,
    QueryProductsPresenter,
)
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from project.database import (
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    ProductOfferRepository,
    commit_changes,
)
from project.forms import PlanSearchForm, ProductSearchForm
from project.models import Company, Plan
from project.url_index import CompanyUrlIndex
from project.views import Http404View, QueryPlansView, QueryProductsView

from .blueprint import CompanyRoute


@CompanyRoute("/company/profile")
def profile(
    company_repository: CompanyRepository,
    company_worker_repository: CompanyWorkerRepository,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    worker = list(company_worker_repository.get_company_workers(company))
    if worker:
        having_workers = True
    else:
        having_workers = False
    return render_template("company/profile.html", having_workers=having_workers)


@CompanyRoute("/company/work", methods=["GET", "POST"])
@commit_changes
def arbeit(
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    company_worker_repository: CompanyWorkerRepository,
):
    """shows workers and add workers to company."""
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    if request.method == "POST":  # add worker to company
        member = member_repository.get_by_id(request.form["member"])
        assert member is not None
        try:
            use_cases.add_worker_to_company(
                company_worker_repository,
                company,
                member,
            )
        except errors.WorkerAlreadyAtCompany:
            flash("Mitglied ist bereits in diesem Betrieb beschäftigt.")
        return redirect(url_for("main_company.arbeit"))
    elif request.method == "GET":
        workers_list = list(company_worker_repository.get_company_workers(company))
        return render_template("company/work.html", workers_list=workers_list)


@CompanyRoute("/company/suchen", methods=["GET", "POST"])
def suchen(
    query_products: use_cases.QueryProducts,
    controller: QueryProductsController,
):
    presenter = QueryProductsPresenter(
        CompanyUrlIndex(),
    )
    template_name = "company/query_products.html"
    search_form = ProductSearchForm(request.form)
    view = QueryProductsView(
        search_form, query_products, presenter, controller, template_name
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@CompanyRoute("/company/query_plans", methods=["GET", "POST"])
def query_plans(
    query_plans: use_cases.QueryPlans,
    controller: QueryPlansController,
):
    presenter = QueryPlansPresenter(CompanyUrlIndex())
    template_name = "company/query_plans.html"
    search_form = PlanSearchForm(request.form)
    view = QueryPlansView(
        search_form, query_plans, presenter, controller, template_name
    )
    if request.method == "POST":
        return view.respond_to_post()
    else:
        return view.respond_to_get()


@CompanyRoute("/company/kaeufe")
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
    company_repository: CompanyRepository,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    purchases = list(query_purchases(company))
    return render_template("company/my_purchases.html", purchases=purchases)


@CompanyRoute("/company/create_plan", methods=["GET", "POST"])
@commit_changes
def create_plan(
    create_draft_from_proposal: CreatePlanDraft,
    get_plan_summary: GetPlanSummary,
    seek_approval: use_cases.SeekApproval,
    activate_plan_and_grant_credit: use_cases.ActivatePlanAndGrantCredit,
):
    expired_plan_id: Optional[str] = request.args.get("expired_plan_id")
    expired_plan_uuid: Optional[UUID] = (
        UUID(expired_plan_id) if expired_plan_id else None
    )

    if request.method == "POST":  # Button "Plan erstellen"
        plan_data = dict(request.form)
        use_case_request = CreatePlanDraftRequest(
            planner=UUID(current_user.id),
            costs=entities.ProductionCosts(
                labour_cost=Decimal(plan_data["costs_a"]),
                resource_cost=Decimal(plan_data["costs_r"]),
                means_cost=Decimal(plan_data["costs_p"]),
            ),
            product_name=plan_data["prd_name"],
            production_unit=plan_data["prd_unit"],
            production_amount=int(plan_data["prd_amount"]),
            description=plan_data["description"],
            timeframe_in_days=plan_data["timeframe"],
            is_public_service=True
            if plan_data["productive_or_public"] == "public"
            else False,
        )
        draft = create_draft_from_proposal(use_case_request)
        approval_response = seek_approval(draft.draft_id, expired_plan_uuid)

        if approval_response.is_approved:
            flash("Plan erfolgreich erstellt und genehmigt.")
            activate_plan_and_grant_credit(approval_response.new_plan_id)
            flash(
                "Plan wurde aktiviert. Kredite für Produktionskosten wurden bereits gewährt, Kosten für Arbeit werden täglich ausgezahlt."
            )
            return redirect("/company/my_plans")
        else:
            flash(f"Plan nicht genehmigt. Grund:\n{approval_response.reason}")
            return redirect(
                url_for("main_company.create_plan", expired_plan_id=expired_plan_id)
            )

    expired_plan = (
        None if expired_plan_uuid is None else get_plan_summary(expired_plan_uuid)
    )
    return render_template("company/create_plan.html", expired_plan=expired_plan)


@CompanyRoute("/company/my_plans", methods=["GET"])
def my_plans(
    show_my_plans_use_case: ShowMyPlansUseCase,
    show_my_plans_presenter: ShowMyPlansPresenter,
):
    request = ShowMyPlansRequest(company_id=UUID(current_user.id))
    response = show_my_plans_use_case(request)
    view_model = show_my_plans_presenter.present(response)

    return render_template(
        "company/my_plans.html",
        **view_model.to_dict(),
    )


@CompanyRoute("/company/delete_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def delete_plan(plan_id: UUID, delete_plan: DeletePlan, presenter: DeletePlanPresenter):
    response = delete_plan(plan_id)
    view_model = presenter.present(response)
    for notification in view_model.notifications:
        flash(notification)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/company/create_offer/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def create_offer(
    plan_id: UUID, create_offer: CreateOffer, presenter: CreateOfferPresenter
):
    if request.method == "POST":  # create offer
        name = request.form["name"]
        description = request.form["description"]

        offer = CreateOfferRequest(
            name=name,
            description=description,
            plan_id=plan_id,
        )
        use_case_response = create_offer(offer)
        view_model = presenter.present(use_case_response)
        for notification in view_model.notifications:
            flash(notification)
        return redirect(url_for("main_company.my_offers"))

    plan = Plan.query.filter_by(id=str(plan_id)).first()
    return render_template("company/create_offer.html", plan=plan)


@CompanyRoute("/company/my_accounts")
def my_accounts(
    company_repository: CompanyRepository,
    get_transaction_infos: use_cases.GetTransactionInfos,
    account_repository: AccountRepository,
):
    # We can assume current_user to be a LocalProxy object that
    # delegates to a Company since we did the `user_is_company` check
    # earlier.
    company = company_repository.object_from_orm(cast(Company, current_user))
    all_trans_infos = get_transaction_infos(company)
    my_balances = [
        account_repository.get_account_balance(account)
        for account in company.accounts()
    ]

    return render_template(
        "company/my_accounts.html",
        my_balances=my_balances,
        all_transactions=all_trans_infos,
    )


@CompanyRoute("/company/transfer_to_worker", methods=["GET", "POST"])
@commit_changes
def transfer_to_worker(
    send_work_certificates_to_worker: use_cases.SendWorkCertificatesToWorker,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
):
    if request.method == "POST":
        company = company_repository.get_by_id(UUID(current_user.id))
        assert company is not None
        worker = member_repository.get_by_id(request.form["member_id"])
        if worker is None:
            flash("Mitglied existiert nicht.")
        else:
            try:
                amount = Decimal(request.form["amount"])
                send_work_certificates_to_worker(
                    company,
                    worker,
                    amount,
                )
            except errors.WorkerNotAtCompany:
                flash("Mitglied ist nicht in diesem Betrieb beschäftigt.")
            else:
                flash("Erfolgreich überwiesen.")

    return render_template("company/transfer_to_worker.html")


@CompanyRoute("/company/transfer_to_company", methods=["GET", "POST"])
@commit_changes
def transfer_to_company(
    pay_means_of_production: use_cases.PayMeansOfProduction,
    presenter: PayMeansOfProductionPresenter,
):
    if request.method == "POST":
        use_case_request = use_cases.PayMeansOfProductionRequest(
            buyer=UUID(current_user.id),
            plan=request.form["plan_id"],
            amount=int(request.form["amount"]),
            purpose=entities.PurposesOfPurchases.means_of_prod
            if request.form["category"] == "Produktionsmittel"
            else entities.PurposesOfPurchases.raw_materials,
        )
        use_case_response = pay_means_of_production(use_case_request)
        view_model = presenter.present(use_case_response)
        for notification in view_model.notifications:
            flash(notification)
    return render_template("company/transfer_to_company.html")


@CompanyRoute("/company/my_offers")
def my_offers(offer_repository: ProductOfferRepository):
    url_index = CompanyUrlIndex()
    my_company = Company.query.filter_by(id=current_user.id).first()
    my_plans = my_company.plans.all()
    my_offers = []
    for plan in my_plans:
        for offer in plan.offers.all():
            my_offers.append(offer)
    my_offers = [offer_repository.object_from_orm(offer) for offer in my_offers]

    return render_template(
        "company/my_offers.html",
        offers=my_offers,
        get_plan_summary_url=url_index.get_plan_summary_url,
    )


@CompanyRoute("/company/delete_offer/<uuid:offer_id>", methods=["GET", "POST"])
@commit_changes
def delete_offer(
    offer_id: UUID,
    product_offer_repository: ProductOfferRepository,
    delete_offer: DeleteOffer,
    presenter: DeleteOfferPresenter,
):
    if request.method == "POST":
        deletion_request = DeleteOfferRequest(
            requesting_company_id=UUID(current_user.id),
            offer_id=offer_id,
        )
        response = delete_offer(deletion_request)
        view_model = presenter.present(response)
        for notification in view_model.notifications:
            flash(notification)
        return redirect(url_for("main_company.my_offers"))

    offer = product_offer_repository.get_by_id(offer_id)
    return render_template("company/delete_offer.html", offer=offer)


@CompanyRoute("/company/statistics")
def statistics(
    get_statistics: use_cases.GetStatistics,
    presenter: GetStatisticsPresenter,
):
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return render_template("company/statistics.html", view_model=view_model)


@CompanyRoute("/company/plan_summary/<uuid:plan_id>")
def plan_summary(
    plan_id: UUID,
    get_plan_summary: use_cases.GetPlanSummary,
    presenter: GetPlanSummarySuccessPresenter,
):
    use_case_response = get_plan_summary(plan_id)
    if isinstance(use_case_response, use_cases.PlanSummarySuccess):
        view_model = presenter.present(use_case_response)
        return render_template(
            "company/plan_summary.html", view_model=view_model.to_dict()
        )
    else:
        return Http404View("company/404.html").get_response()


@CompanyRoute("/company/hilfe")
@login_required
def hilfe():
    return render_template("company/help.html")
