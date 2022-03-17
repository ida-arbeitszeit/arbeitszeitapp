from typing import Optional
from uuid import UUID

from flask import flash, redirect, request, url_for
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases import (
    AcceptCooperation,
    AcceptCooperationRequest,
    AcceptCooperationResponse,
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
    CreatePlanDraft,
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
    GetCompanySummary,
    GetDraftSummary,
    GetPlanSummaryMember,
    HidePlan,
    ListAllCooperations,
    ListCoordinations,
    ListCoordinationsRequest,
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListMessages,
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    ListPlans,
    RequestCooperation,
    ToggleProductAvailability,
)
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_flask.database import (
    CompanyRepository,
    CompanyWorkerRepository,
    commit_changes,
)
from arbeitszeit_flask.forms import (
    CompanySearchForm,
    CreateDraftForm,
    InviteWorkerToCompanyForm,
    PayMeansOfProductionForm,
    PlanSearchForm,
    RequestCooperationForm,
)
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    EndCooperationView,
    Http404View,
    InviteWorkerToCompanyView,
    ListMessagesView,
    QueryCompaniesView,
    QueryPlansView,
    ReadMessageView,
    RequestCooperationView,
)
from arbeitszeit_flask.views.pay_means_of_production import PayMeansOfProductionView
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_flask.views.transfer_to_worker_view import TransferToWorkerView
from arbeitszeit_web.create_cooperation import CreateCooperationPresenter
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from arbeitszeit_web.get_prefilled_draft_data import (
    GetPrefilledDraftDataPresenter,
    PrefilledDraftDataController,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.hide_plan import HidePlanPresenter
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_drafts_of_company import ListDraftsPresenter
from arbeitszeit_web.list_messages import ListMessagesController, ListMessagesPresenter
from arbeitszeit_web.list_plans import ListPlansPresenter
from arbeitszeit_web.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
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
from arbeitszeit_web.show_p_account_details import ShowPAccountDetailsPresenter
from arbeitszeit_web.show_r_account_details import ShowRAccountDetailsPresenter
from arbeitszeit_web.translator import Translator

from .blueprint import CompanyRoute


@CompanyRoute("/company/profile")
def profile(
    company_repository: CompanyRepository,
    company_worker_repository: CompanyWorkerRepository,
    template_renderer: UserTemplateRenderer,
    translator: Translator,
):
    company = company_repository.get_by_id(UUID(current_user.id))
    assert company is not None
    worker = list(company_worker_repository.get_company_workers(company))
    if worker:
        having_workers = True
    else:
        having_workers = False
    return template_renderer.render_template(
        "company/profile.html",
        context=dict(
            having_workers=having_workers,
            welcome_message=translator.gettext("Welcome, %s!") % current_user.name,
        ),
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
    get_plan_summary_member: GetPlanSummaryMember,
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
                )
            )

    plan_summary_success = (
        get_plan_summary_member(expired_plan_uuid) if expired_plan_uuid else None
    )

    prefilled_draft_data = (
        get_prefilled_draft_data_presenter.present(
            plan_summary_success.plan_summary, from_expired_plan=True
        )
        if plan_summary_success
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

    approval_response = seek_approval(draft_uuid)

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
    return redirect(url_for("main_company.plan_summary", plan_id=plan_id))


@CompanyRoute("/company/hide_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def hide_plan(plan_id: UUID, hide_plan: HidePlan, presenter: HidePlanPresenter):
    response = hide_plan(plan_id)
    presenter.present(response)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/company/my_accounts")
def my_accounts(view: ShowMyAccountsView):
    return view.respond_to_get()


@CompanyRoute("/company/my_accounts/all_transactions")
def list_all_transactions(
    get_company_transactions: use_cases.GetCompanyTransactions,
    template_renderer: UserTemplateRenderer,
    presenter: GetCompanyTransactionsPresenter,
):
    response = get_company_transactions(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/list_all_transactions.html",
        context=dict(
            all_transactions=view_model.transactions,
        ),
    )


@CompanyRoute("/company/my_accounts/account_p")
def account_p(
    show_p_account_details: use_cases.ShowPAccountDetails,
    template_renderer: UserTemplateRenderer,
    presenter: ShowPAccountDetailsPresenter,
):
    response = show_p_account_details(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/account_p.html",
        context=dict(view_model=view_model),
    )


@CompanyRoute("/company/my_accounts/account_r")
def account_r(
    show_r_account_details: use_cases.ShowRAccountDetails,
    template_renderer: UserTemplateRenderer,
    presenter: ShowRAccountDetailsPresenter,
):
    response = show_r_account_details(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/account_r.html",
        context=dict(view_model=view_model),
    )


@CompanyRoute("/company/my_accounts/account_a")
def account_a(
    show_a_account_details: use_cases.ShowAAccountDetails,
    template_renderer: UserTemplateRenderer,
    presenter: ShowAAccountDetailsPresenter,
):
    response = show_a_account_details(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/account_a.html",
        context=dict(view_model=view_model),
    )


@CompanyRoute("/company/my_accounts/account_prd")
def account_prd(
    show_prd_account_details: use_cases.ShowPRDAccountDetails,
    template_renderer: UserTemplateRenderer,
    presenter: ShowPRDAccountDetailsPresenter,
):
    response = show_prd_account_details(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/account_prd.html",
        context=dict(view_model=view_model),
    )


@CompanyRoute("/company/transfer_to_worker", methods=["GET", "POST"])
@commit_changes
def transfer_to_worker(view: TransferToWorkerView):
    if request.method == "GET":
        return view.respond_to_get()
    elif request.method == "POST":
        return view.respond_to_post()


@CompanyRoute("/company/transfer_to_company", methods=["GET", "POST"])
@commit_changes
def transfer_to_company(view: PayMeansOfProductionView):
    form = PayMeansOfProductionForm(request.form)
    if request.method == "GET":
        return view.respond_to_get(form)
    elif request.method == "POST":
        return view.respond_to_post(form)


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
    get_plan_summary_company: use_cases.GetPlanSummaryCompany,
    template_renderer: UserTemplateRenderer,
    presenter: GetPlanSummaryCompanySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_plan_summary_company(plan_id, UUID(current_user.id))
    if isinstance(use_case_response, use_cases.PlanSummaryCompanySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/plan_summary.html", context=dict(view_model=view_model.to_dict())
        )
    else:
        return http_404_view.get_response()


@CompanyRoute("/company/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummary,
    template_renderer: UserTemplateRenderer,
    presenter: GetCompanySummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_company_summary(company_id)
    if isinstance(use_case_response, use_cases.GetCompanySummarySuccess):
        view_model = presenter.present(use_case_response)
        return template_renderer.render_template(
            "company/company_summary.html",
            context=dict(view_model=view_model.to_dict()),
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
    cancel_cooperation_solicitation: CancelCooperationSolicitation,
):
    accept_cooperation_response: Optional[AcceptCooperationResponse] = None
    deny_cooperation_response: Optional[DenyCooperationResponse] = None
    cancel_cooperation_solicitation_response: Optional[bool] = None
    if request.method == "POST":
        if request.form.get("accept"):
            coop_id, plan_id = [
                UUID(id.strip()) for id in request.form["accept"].split(",")
            ]
            accept_cooperation_response = accept_cooperation(
                AcceptCooperationRequest(UUID(current_user.id), plan_id, coop_id)
            )
        elif request.form.get("deny"):
            coop_id, plan_id = [
                UUID(id.strip()) for id in request.form["deny"].split(",")
            ]
            deny_cooperation_response = deny_cooperation(
                DenyCooperationRequest(UUID(current_user.id), plan_id, coop_id)
            )
        elif request.form.get("cancel"):
            plan_id = UUID(request.form["cancel"])
            requester_id = UUID(current_user.id)
            cancel_cooperation_solicitation_response = cancel_cooperation_solicitation(
                CancelCooperationSolicitationRequest(requester_id, plan_id)
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
        cancel_cooperation_solicitation_response,
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
def invite_worker_to_company(
    view: InviteWorkerToCompanyView,
) -> Response:
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


@CompanyRoute("/company/end_cooperation")
@commit_changes
def end_cooperation(
    view: EndCooperationView,
) -> Response:
    return view.respond_to_get()
