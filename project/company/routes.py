from decimal import Decimal
from typing import Optional, cast
from uuid import UUID

from flask import Response, flash, redirect, request, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from arbeitszeit.use_cases import (
    CreatePlanDraft,
    DeletePlan,
    GetDraftSummary,
    GetPlanSummary,
    ListMessages,
    ToggleProductAvailability,
)
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.delete_plan import DeletePlanPresenter
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter
from arbeitszeit_web.get_prefilled_draft_data import (
    GetPrefilledDraftDataPresenter,
    PrefilledDraftDataController,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.list_drafts_of_company import ListDraftsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.query_companies import (
    QueryCompaniesController,
    QueryCompaniesPresenter,
)
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from project.database import (
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    commit_changes,
)
from project.forms import CompanySearchForm, CreateDraftForm, PlanSearchForm
from project.models import Company
from project.template import UserTemplateRenderer
from project.url_index import CompanyUrlIndex
from project.views import (
    Http404View,
    ListMessagesView,
    QueryCompaniesView,
    QueryPlansView,
)

from .blueprint import CompanyRoute


@CompanyRoute("/company/profile")
def profile(
    company_repository: CompanyRepository,
    company_worker_repository: CompanyWorkerRepository,
    template_renderer: UserTemplateRenderer,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    worker = list(company_worker_repository.get_company_workers(company))
    if worker:
        having_workers = True
    else:
        having_workers = False
    return template_renderer.render_template(
        "company/profile.html", context=dict(having_workers=having_workers)
    )


@CompanyRoute("/company/work", methods=["GET", "POST"])
@commit_changes
def arbeit(
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    company_worker_repository: CompanyWorkerRepository,
    template_renderer: UserTemplateRenderer,
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
        return template_renderer.render_template(
            "company/work.html", context=dict(workers_list=workers_list)
        )


@CompanyRoute("/company/query_plans", methods=["GET", "POST"])
def query_plans(
    query_plans: use_cases.QueryPlans,
    controller: QueryPlansController,
    template_renderer: UserTemplateRenderer,
):
    presenter = QueryPlansPresenter(CompanyUrlIndex())
    template_name = "company/query_plans.html"
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


@CompanyRoute("/company/query_companies", methods=["GET", "POST"])
def query_companies(
    query_companies: use_cases.QueryCompanies,
    controller: QueryCompaniesController,
    template_renderer: UserTemplateRenderer,
):
    presenter = QueryCompaniesPresenter()
    template_name = "company/query_companies.html"
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


@CompanyRoute("/company/kaeufe")
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
    company_repository: CompanyRepository,
    template_renderer: UserTemplateRenderer,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    purchases = list(query_purchases(company))
    return template_renderer.render_template(
        "company/my_purchases.html", context=dict(purchases=purchases)
    )


@CompanyRoute("/company/create_draft_from_expired_plan", methods=["GET", "POST"])
@commit_changes
def create_draft_from_expired_plan(
    create_draft: CreatePlanDraft,
    get_plan_summary: GetPlanSummary,
    get_prefilled_draft_data_presenter: GetPrefilledDraftDataPresenter,
    controller: PrefilledDraftDataController,
    template_renderer: UserTemplateRenderer,
):
    expired_plan_id: Optional[str] = request.args.get("expired_plan_id")
    expired_plan_uuid: Optional[UUID] = (
        UUID(expired_plan_id) if expired_plan_id else None
    )

    if request.method == "POST":
        draft_form = CreateDraftForm(request.form)
        use_case_request = controller.import_form_data(
            UUID(current_user.id), draft_form
        )

        button = request.form["action"]
        if button == "save_draft":
            create_draft(use_case_request)
            return redirect(url_for("main_company.my_drafts"))
        elif button == "file_draft":
            response = create_draft(use_case_request)
            return redirect(
                url_for(
                    "main_company.create_plan",
                    draft_uuid=response.draft_id,
                    expired_plan_uuid=expired_plan_uuid,
                )
            )

    plan_summary = get_plan_summary(expired_plan_uuid) if expired_plan_uuid else None
    prefilled_draft_data = (
        get_prefilled_draft_data_presenter.present(plan_summary, from_expired_plan=True)
        if plan_summary
        else None
    )
    return template_renderer.render_template(
        "company/create_draft.html", context=dict(prefilled=prefilled_draft_data)
    )


@CompanyRoute("/company/create_draft", methods=["GET", "POST"])
@commit_changes
def create_draft(
    create_draft: CreatePlanDraft,
    get_draft_summary: GetDraftSummary,
    get_prefilled_draft_data_presenter: GetPrefilledDraftDataPresenter,
    controller: PrefilledDraftDataController,
    template_renderer: UserTemplateRenderer,
):
    saved_draft_id: Optional[str] = request.args.get("saved_draft_id")
    saved_draft_uuid: Optional[UUID] = UUID(saved_draft_id) if saved_draft_id else None

    if request.method == "POST":
        draft_form = CreateDraftForm(request.form)
        use_case_request = controller.import_form_data(
            UUID(current_user.id), draft_form
        )

        button = request.form["action"]
        if button == "save_draft":
            create_draft(use_case_request)
            return redirect(url_for("main_company.my_drafts"))
        elif button == "file_draft":
            response = create_draft(use_case_request)
            return redirect(
                url_for(
                    "main_company.create_plan",
                    draft_uuid=response.draft_id,
                    expired_plan_uuid=None,
                )
            )

    draft_summary = get_draft_summary(saved_draft_uuid) if saved_draft_uuid else None
    prefilled_draft_data = (
        get_prefilled_draft_data_presenter.present(
            draft_summary, from_expired_plan=False
        )
        if draft_summary
        else None
    )
    return template_renderer.render_template(
        "company/create_draft.html", context=dict(prefilled=prefilled_draft_data)
    )


@CompanyRoute("/company/create_plan", methods=["GET", "POST"])
@commit_changes
def create_plan(
    seek_approval: use_cases.SeekApproval,
    activate_plan_and_grant_credit: use_cases.ActivatePlanAndGrantCredit,
    template_renderer: UserTemplateRenderer,
):
    draft_uuid: UUID = request.args.get("draft_uuid")
    expired_plan_uuid: Optional[UUID] = request.args.get("expired_plan_uuid")

    approval_response = seek_approval(draft_uuid, expired_plan_uuid)

    if approval_response.is_approved:
        flash("Plan erfolgreich erstellt und genehmigt.")
        activate_plan_and_grant_credit(approval_response.new_plan_id)
        flash(
            "Plan wurde aktiviert. Kredite für Produktionskosten wurden bereits gewährt, Kosten für Arbeit werden täglich ausgezahlt."
        )
    else:
        flash(f"Plan nicht genehmigt. Grund:\n{approval_response.reason}")

    return template_renderer.render_template("/company/create_plan_response.html")


@CompanyRoute("/company/my_drafts", methods=["GET"])
def my_drafts(
    list_drafts: use_cases.ListDraftsOfCompany,
    list_drafts_presenter: ListDraftsPresenter,
    template_renderer: UserTemplateRenderer,
):
    response = list_drafts(UUID(current_user.id))
    view_model = list_drafts_presenter.present(response)
    return template_renderer.render_template(
        "company/my_drafts.html", context=view_model.to_dict()
    )


@CompanyRoute("/company/my_plans", methods=["GET"])
def my_plans(
    show_my_plans_use_case: ShowMyPlansUseCase,
    template_renderer: UserTemplateRenderer,
):
    show_my_plans_presenter = ShowMyPlansPresenter(CompanyUrlIndex())
    request = ShowMyPlansRequest(company_id=UUID(current_user.id))
    response = show_my_plans_use_case(request)
    view_model = show_my_plans_presenter.present(response)

    return template_renderer.render_template(
        "company/my_plans.html",
        context=view_model.to_dict(),
    )


@CompanyRoute("/company/toggle_availability/<uuid:plan_id>", methods=["GET"])
@commit_changes
def toggle_availability(plan_id: UUID, toggle_availability: ToggleProductAvailability):
    toggle_availability(UUID(current_user.id), plan_id)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/company/delete_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def delete_plan(plan_id: UUID, delete_plan: DeletePlan, presenter: DeletePlanPresenter):
    response = delete_plan(plan_id)
    view_model = presenter.present(response)
    for notification in view_model.notifications:
        flash(notification)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/company/my_accounts")
def my_accounts(
    company_repository: CompanyRepository,
    get_transaction_infos: use_cases.GetTransactionInfos,
    account_repository: AccountRepository,
    template_renderer: UserTemplateRenderer,
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

    return template_renderer.render_template(
        "company/my_accounts.html",
        context=dict(
            my_balances=my_balances,
            all_transactions=all_trans_infos,
        ),
    )


@CompanyRoute("/company/transfer_to_worker", methods=["GET", "POST"])
@commit_changes
def transfer_to_worker(
    send_work_certificates_to_worker: use_cases.SendWorkCertificatesToWorker,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    template_renderer: UserTemplateRenderer,
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

    return template_renderer.render_template("company/transfer_to_worker.html")


@CompanyRoute("/company/transfer_to_company", methods=["GET", "POST"])
@commit_changes
def transfer_to_company(
    pay_means_of_production: use_cases.PayMeansOfProduction,
    presenter: PayMeansOfProductionPresenter,
    template_renderer: UserTemplateRenderer,
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
    return template_renderer.render_template("company/transfer_to_company.html")


@CompanyRoute("/company/statistics")
def statistics(
    get_statistics: use_cases.GetStatistics,
    presenter: GetStatisticsPresenter,
    template_renderer: UserTemplateRenderer,
):
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return template_renderer.render_template(
        "company/statistics.html", context=dict(view_model=view_model)
    )


@CompanyRoute("/company/plan_summary/<uuid:plan_id>")
def plan_summary(
    plan_id: UUID,
    get_plan_summary: use_cases.GetPlanSummary,
    presenter: GetPlanSummarySuccessPresenter,
    template_renderer: UserTemplateRenderer,
):
    use_case_response = get_plan_summary(plan_id)
    if isinstance(use_case_response, use_cases.PlanSummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/plan_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return Http404View("company/404.html", template_renderer).get_response()


@CompanyRoute("/company/create_cooperation", methods=["GET", "POST"])
@commit_changes
def create_cooperation(
    create_cooperation: use_cases.CreateCooperation,
    presenter: CreateCooperationPresenter,
    template_renderer: UserTemplateRenderer,
):
    if request.method == "POST":
        name = request.form["name"]
        definition = request.form["definition"]
        use_case_request = use_cases.CreateCooperationRequest(
            UUID(current_user.id), name, definition
        )
        use_case_response = create_cooperation(use_case_request)
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/create_cooperation.html", context=dict(view_model=view_model)
        )
    elif request.method == "GET":
        return template_renderer.render_template("company/create_cooperation.html")


@CompanyRoute("/company/hilfe")
@login_required
def hilfe(template_renderer: UserTemplateRenderer):
    return template_renderer.render_template("company/help.html")


@CompanyRoute("/company/messages")
def list_messages(
    template_renderer: UserTemplateRenderer,
    controller: ListMessagesController,
    presenter: ListMessagesPresenter,
    use_case: ListMessages,
) -> Response:
    http_404_view = Http404View("company/404.html", template_renderer)
    view = ListMessagesView(
        template_renderer=template_renderer,
        presenter=presenter,
        controller=controller,
        list_messages=use_case,
        not_found_view=http_404_view,
        template_name="company/list_messages.html",
    )
    return view.respond_to_get()
