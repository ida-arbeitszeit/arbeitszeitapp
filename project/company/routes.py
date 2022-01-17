from decimal import Decimal
from typing import Optional, cast
from uuid import UUID

from flask import Response, flash, redirect, request, url_for
from flask_login import current_user, login_required

from arbeitszeit import entities, errors, use_cases
from arbeitszeit.use_cases import (
    AcceptCooperation,
    AcceptCooperationRequest,
    AcceptCooperationResponse,
    CreatePlanDraft,
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
    GetDraftSummary,
    GetPlanSummary,
    HidePlan,
    InviteWorkerToCompany,
    ListAllCooperations,
    ListCoordinations,
    ListCoordinationsRequest,
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListMessages,
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListPlans,
    ListWorkers,
    RequestCooperation,
    SendWorkCertificatesToWorker,
    ToggleProductAvailability,
)
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_plan_summary import GetPlanSummarySuccessPresenter
from arbeitszeit_web.get_prefilled_draft_data import (
    GetPrefilledDraftDataPresenter,
    PrefilledDraftDataController,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.hide_plan import HidePlanPresenter
from arbeitszeit_web.invite_worker_to_company import (
    InviteWorkerToCompanyController,
    InviteWorkerToCompanyPresenter,
)
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_drafts_of_company import ListDraftsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.list_plans import ListPlansPresenter
from arbeitszeit_web.pay_means_of_production import PayMeansOfProductionPresenter
from arbeitszeit_web.query_companies import (
    QueryCompaniesController,
    QueryCompaniesPresenter,
)
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.request_cooperation import (
    RequestCooperationController,
    RequestCooperationPresenter,
)
from arbeitszeit_web.show_my_cooperations import ShowMyCooperationsPresenter
from arbeitszeit_web.show_my_plans import ShowMyPlansPresenter
from project.database import (
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    commit_changes,
)
from project.forms import (
    CompanySearchForm,
    CreateDraftForm,
    InviteWorkerToCompanyForm,
    PlanSearchForm,
    RequestCooperationForm,
)
from project.models import Company
from project.template import UserTemplateRenderer
from project.views import (
    Http404View,
    InviteWorkerToCompanyView,
    ListMessagesView,
    QueryCompaniesView,
    QueryPlansView,
    ReadMessageView,
    RequestCooperationView,
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


@CompanyRoute("/company/query_plans", methods=["GET", "POST"])
def query_plans(
    query_plans: use_cases.QueryPlans,
    controller: QueryPlansController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryPlansPresenter,
):
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
    presenter: QueryCompaniesPresenter,
):
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
    draft_uuid: UUID = UUID(request.args.get("draft_uuid"))
    expired_plan_optional = request.args.get("expired_plan_uuid")
    expired_plan_uuid: Optional[UUID] = (
        UUID(expired_plan_optional.strip())
        if expired_plan_optional is not None
        else None
    )

    approval_response = seek_approval(draft_uuid, expired_plan_uuid)

    if approval_response.is_approved:
        flash("Plan erfolgreich erstellt und genehmigt.", "is-success")
        activate_plan_and_grant_credit(approval_response.new_plan_id)
        flash(
            "Plan wurde aktiviert. Kredite für Produktionskosten wurden bereits gewährt, Kosten für Arbeit werden täglich ausgezahlt.",
            "is-success",
        )
    else:
        flash(f"Plan nicht genehmigt. Grund:\n{approval_response.reason}", "is-danger")

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
    show_my_plans_presenter: ShowMyPlansPresenter,
):
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


@CompanyRoute("/company/hide_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def hide_plan(plan_id: UUID, hide_plan: HidePlan, presenter: HidePlanPresenter):
    response = hide_plan(plan_id)
    presenter.present(response)
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
    send_work_certificates_to_worker: SendWorkCertificatesToWorker,
    list_workers: ListWorkers,
    company_repository: CompanyRepository,
    member_repository: MemberRepository,
    template_renderer: UserTemplateRenderer,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None

    if request.method == "POST":
        try:
            worker = member_repository.get_by_id(
                UUID(str(request.form["member_id"]).strip())
            )
            if worker is None:
                flash("Mitglied existiert nicht.", "is-danger")
            else:
                amount = Decimal(request.form["amount"])
                send_work_certificates_to_worker(
                    company,
                    worker,
                    amount,
                )
        except ValueError:
            flash("Bitte Mitarbeiter wählen!", "is-danger")
        except errors.WorkerNotAtCompany:
            flash("Mitglied ist nicht in diesem Betrieb beschäftigt.", "is-danger")
        else:
            flash("Erfolgreich überwiesen.", "is-success")

    workers_list = list_workers(company.id)
    return template_renderer.render_template(
        "company/transfer_to_worker.html",
        context=dict(workers_list=workers_list.workers),
    )


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
            plan=UUID(str(request.form["plan_id"]).strip()),
            amount=int(request.form["amount"]),
            purpose=entities.PurposesOfPurchases.means_of_prod
            if request.form["category"] == "Produktionsmittel"
            else entities.PurposesOfPurchases.raw_materials,
        )
        use_case_response = pay_means_of_production(use_case_request)
        presenter.present(use_case_response)
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
    template_renderer: UserTemplateRenderer,
    presenter: GetPlanSummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_plan_summary(plan_id)
    if isinstance(use_case_response, use_cases.PlanSummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/plan_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return http_404_view.get_response()


@CompanyRoute("/company/cooperation_summary/<uuid:coop_id>")
def coop_summary(
    coop_id: UUID,
    get_coop_summary: use_cases.GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
    template_renderer: UserTemplateRenderer,
    http_404_view: Http404View,
):
    use_case_response = get_coop_summary(
        use_cases.GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if isinstance(use_case_response, use_cases.GetCoopSummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/coop_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return http_404_view.get_response()


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
        presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/create_cooperation.html", context=dict()
        )
    elif request.method == "GET":
        return template_renderer.render_template("company/create_cooperation.html")


@CompanyRoute("/company/request_cooperation", methods=["GET", "POST"])
@commit_changes
def request_cooperation(
    list_plans: ListPlans,
    list_plans_presenter: ListPlansPresenter,
    request_cooperation: RequestCooperation,
    controller: RequestCooperationController,
    presenter: RequestCooperationPresenter,
    template_renderer: UserTemplateRenderer,
    http_404_view: Http404View,
):
    form = RequestCooperationForm(request.form)
    view = RequestCooperationView(
        current_user_id=UUID(current_user.id),
        form=form,
        list_plans=list_plans,
        list_plans_presenter=list_plans_presenter,
        request_cooperation=request_cooperation,
        controller=controller,
        presenter=presenter,
        not_found_view=http_404_view,
        template_name="company/request_cooperation.html",
        template_renderer=template_renderer,
    )

    if request.method == "POST":
        return view.respond_to_post()

    elif request.method == "GET":
        return view.respond_to_get()


@CompanyRoute("/company/my_cooperations", methods=["GET", "POST"])
@commit_changes
def my_cooperations(
    template_renderer: UserTemplateRenderer,
    list_coordinations: ListCoordinations,
    list_inbound_coop_requests: ListInboundCoopRequests,
    accept_cooperation: AcceptCooperation,
    deny_cooperation: DenyCooperation,
    list_outbound_coop_requests: ListOutboundCoopRequests,
    presenter: ShowMyCooperationsPresenter,
):
    accept_cooperation_response: Optional[AcceptCooperationResponse] = None
    deny_cooperation_response: Optional[DenyCooperationResponse] = None
    if request.method == "POST":
        if request.form.get("accept"):
            coop_id, plan_id = [id.strip() for id in request.form["accept"].split(",")]
            accept_cooperation_response = accept_cooperation(
                AcceptCooperationRequest(
                    UUID(current_user.id), UUID(plan_id), UUID(coop_id)
                )
            )
        else:
            coop_id, plan_id = [id.strip() for id in request.form["deny"].split(",")]
            deny_cooperation_response = deny_cooperation(
                DenyCooperationRequest(
                    UUID(current_user.id), UUID(plan_id), UUID(coop_id)
                )
            )

    list_coord_response = list_coordinations(
        ListCoordinationsRequest(UUID(current_user.id))
    )
    list_inbound_coop_requests_response = list_inbound_coop_requests(
        ListInboundCoopRequestsRequest(UUID(current_user.id))
    )
    list_outbound_coop_requests_response = list_outbound_coop_requests(
        ListOutboundCoopRequestsRequest(UUID(current_user.id))
    )

    view_model = presenter.present(
        list_coord_response,
        list_inbound_coop_requests_response,
        accept_cooperation_response,
        deny_cooperation_response,
        list_outbound_coop_requests_response,
    )
    return template_renderer.render_template(
        "company/my_cooperations.html", context=view_model.to_dict()
    )


@CompanyRoute("/company/list_all_cooperations")
@commit_changes
def list_all_cooperations(
    use_case: ListAllCooperations,
    template_renderer: UserTemplateRenderer,
    presenter: ListAllCooperationsPresenter,
):
    response = use_case()
    view_model = presenter.present(response)
    return template_renderer.render_template(
        "company/list_all_cooperations.html", context=dict(view_model=view_model)
    )


@CompanyRoute("/company/hilfe")
@login_required
def hilfe(template_renderer: UserTemplateRenderer):
    return template_renderer.render_template("company/help.html")


@CompanyRoute("/company/messages")
def list_messages(
    template_renderer: UserTemplateRenderer,
    controller: ListMessagesController,
    use_case: ListMessages,
    presenter: ListMessagesPresenter,
    http_404_view: Http404View,
) -> Response:
    view = ListMessagesView(
        template_renderer=template_renderer,
        presenter=presenter,
        controller=controller,
        list_messages=use_case,
        not_found_view=http_404_view,
        template_name="company/list_messages.html",
    )
    return view.respond_to_get()


@CompanyRoute("/company/invite_worker_to_company", methods=["GET", "POST"])
@commit_changes
def invite_worker_to_company(
    invite_worker: InviteWorkerToCompany,
    presenter: InviteWorkerToCompanyPresenter,
    controller: InviteWorkerToCompanyController,
    template_renderer: UserTemplateRenderer,
) -> Response:
    view = InviteWorkerToCompanyView(
        invite_worker,
        presenter,
        controller,
        template_name="company/invite_worker_to_company.html",
        template_renderer=template_renderer,
    )
    form = InviteWorkerToCompanyForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)
    else:
        return view.respond_to_get(form)


@CompanyRoute("/company/messages/<uuid:message_id>")
@commit_changes
def read_message(
    message_id: UUID,
    view: ReadMessageView,
) -> Response:
    return view.respond_to_get(message_id)
