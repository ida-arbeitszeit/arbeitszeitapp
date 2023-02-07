from typing import Optional
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, request, url_for
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases import (
    AcceptCooperation,
    AcceptCooperationRequest,
    AcceptCooperationResponse,
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
    GetCompanySummary,
    HidePlan,
    ListActivePlansOfCompany,
    ListAllCooperations,
    ListCoordinations,
    ListCoordinationsRequest,
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
    RequestCooperation,
    ToggleProductAvailability,
)
from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.get_draft_summary import GetDraftSummary
from arbeitszeit.use_cases.get_plan_summary_company import GetPlanSummaryCompany
from arbeitszeit.use_cases.list_my_cooperating_plans import (
    ListMyCooperatingPlansUseCase,
)
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_flask.database import CompanyRepository, commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import (
    CompanySearchForm,
    CreateCooperationForm,
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
    QueryCompaniesView,
    QueryPlansView,
    RequestCooperationView,
)
from arbeitszeit_flask.views.company_dashboard_view import CompanyDashboardView
from arbeitszeit_flask.views.create_cooperation_view import CreateCooperationView
from arbeitszeit_flask.views.create_draft_view import CreateDraftView
from arbeitszeit_flask.views.pay_means_of_production import PayMeansOfProductionView
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_flask.views.transfer_to_worker_view import TransferToWorkerView
from arbeitszeit_web.controllers.delete_draft_controller import DeleteDraftController
from arbeitszeit_web.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
)
from arbeitszeit_web.create_draft import (
    CreateDraftController,
    CreateDraftPresenter,
    GetPrefilledDraftDataPresenter,
)
from arbeitszeit_web.get_company_summary import GetCompanySummarySuccessPresenter
from arbeitszeit_web.get_company_transactions import GetCompanyTransactionsPresenter
from arbeitszeit_web.get_coop_summary import GetCoopSummarySuccessPresenter
from arbeitszeit_web.get_plan_summary_company import (
    GetPlanSummaryCompanySuccessPresenter,
)
from arbeitszeit_web.get_statistics import GetStatisticsPresenter
from arbeitszeit_web.hide_plan import HidePlanPresenter
from arbeitszeit_web.list_all_cooperations import ListAllCooperationsPresenter
from arbeitszeit_web.list_plans import ListPlansPresenter
from arbeitszeit_web.presenters.company_purchases_presenter import (
    CompanyPurchasesPresenter,
)
from arbeitszeit_web.presenters.delete_draft_presenter import DeleteDraftPresenter
from arbeitszeit_web.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
)
from arbeitszeit_web.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from arbeitszeit_web.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
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
from arbeitszeit_web.url_index import UrlIndex

from .blueprint import CompanyRoute


@CompanyRoute("/company/dashboard")
def dashboard(view: CompanyDashboardView):
    return view.respond_to_get()


@CompanyRoute("/company/query_plans", methods=["GET"])
def query_plans(
    query_plans: use_cases.QueryPlans,
    controller: QueryPlansController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryPlansPresenter,
):
    template_name = "company/query_plans.html"
    search_form = PlanSearchForm(request.args)
    view = QueryPlansView(
        query_plans,
        presenter,
        controller,
        template_name,
        template_renderer,
    )
    return view.respond_to_get(search_form)


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


@CompanyRoute("/company/purchases")
def my_purchases(
    query_purchases: use_cases.QueryPurchases,
    company_repository: CompanyRepository,
    template_renderer: UserTemplateRenderer,
    presenter: CompanyPurchasesPresenter,
):
    company = company_repository.get_companies().with_id(UUID(current_user.id)).first()
    assert company is not None

    response = query_purchases(company)
    view_model = presenter.present(response)
    return FlaskResponse(
        template_renderer.render_template(
            "company/my_purchases.html",
            context=dict(purchases=view_model),
        )
    )


@CompanyRoute("/company/draft/delete/<uuid:draft_id>", methods=["POST"])
@commit_changes
def delete_draft(
    draft_id: UUID,
    controller: DeleteDraftController,
    use_case: DeleteDraftUseCase,
    presenter: DeleteDraftPresenter,
    http_404_view: Http404View,
) -> Response:
    use_case_request = controller.get_request(request=FlaskRequest(), draft=draft_id)
    try:
        use_case_response = use_case.delete_draft(use_case_request)
    except use_case.Failure:
        return http_404_view.get_response()
    view_model = presenter.present_draft_deletion(use_case_response)
    return redirect(view_model.redirect_target)


@CompanyRoute("/company/draft/from-plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def create_draft_from_plan(
    plan_id: UUID,
    session: FlaskSession,
    get_plan_summary_use_case: GetPlanSummaryCompany,
    get_plan_summary_presenter: GetPrefilledDraftDataPresenter,
    create_plan_draft_use_case: CreatePlanDraft,
    create_draft_controller: CreateDraftController,
    create_draft_presenter: CreateDraftPresenter,
    not_found_view: Http404View,
    template_renderer: UserTemplateRenderer,
    url_index: UrlIndex,
) -> Response:
    form = CreateDraftForm(request.form)
    if request.method == "GET":
        current_user = session.get_current_user()
        assert current_user
        response = get_plan_summary_use_case.get_plan_summary_for_company(
            plan_id=plan_id, company_id=current_user
        )
        if response.plan_summary is None:
            return not_found_view.get_response()
        view_model_get = get_plan_summary_presenter.show_prefilled_draft_data(
            summary_data=response.plan_summary, form=form
        )
        return FlaskResponse(
            template_renderer.render_template(
                "company/create_draft.html",
                context=dict(
                    form=form,
                    view_model=view_model_get,
                ),
            ),
            status=200,
        )
    else:
        if form.validate():
            use_case_request = create_draft_controller.import_form_data(draft_form=form)
            use_case_response = create_plan_draft_use_case(use_case_request)
            view_model_post = create_draft_presenter.present_plan_creation(
                use_case_response
            )
            if view_model_post.redirect_url is None:
                return not_found_view.get_response()
            else:
                return redirect(view_model_post.redirect_url)
        return FlaskResponse(
            template_renderer.render_template(
                "company/create_draft.html",
                context=dict(
                    form=form,
                    view_model=dict(
                        load_draft_url=url_index.get_my_plan_drafts_url(),
                        save_draft_url=url_index.get_create_draft_url(),
                        cancel_url=url_index.get_create_draft_url(),
                    ),
                ),
            ),
            status=400,
        )


@CompanyRoute("/company/create_draft", methods=["GET", "POST"])
@commit_changes
def create_draft(
    view: CreateDraftView,
):
    form = CreateDraftForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)

    elif request.method == "GET":
        return view.respond_to_get()


@CompanyRoute("/company/file_plan/<draft_id>", methods=["POST"])
@commit_changes
def file_plan(
    draft_id: str,
    session: FlaskSession,
    not_found_view: Http404View,
    controller: FilePlanWithAccountingController,
    use_case: FilePlanWithAccounting,
    presenter: FilePlanWithAccountingPresenter,
):
    try:
        request = controller.process_file_plan_with_accounting_request(
            draft_id=draft_id, session=session
        )
    except controller.InvalidRequest:
        return not_found_view.get_response()
    response = use_case.file_plan_with_accounting(request)
    view_model = presenter.present_response(response)
    return redirect(view_model.redirect_url)


@CompanyRoute("/company/draft/<draft_id>", methods=["GET"])
def get_draft_summary(
    draft_id: str,
    use_case: GetDraftSummary,
    presenter: GetPrefilledDraftDataPresenter,
    template_renderer: UserTemplateRenderer,
    not_found_view: Http404View,
) -> Response:
    use_case_response = use_case(UUID(draft_id))
    if use_case_response is None:
        return not_found_view.get_response()
    form = CreateDraftForm()
    view_model = presenter.show_prefilled_draft_data(use_case_response, form=form)
    return FlaskResponse(
        template_renderer.render_template(
            "company/create_draft.html",
            context=dict(
                view_model=view_model,
                form=form,
            ),
        )
    )


@CompanyRoute("/company/my_plans", methods=["GET"])
def my_plans(
    show_my_plans_use_case: ShowMyPlansUseCase,
    template_renderer: UserTemplateRenderer,
    show_my_plans_presenter: ShowMyPlansPresenter,
):
    request = ShowMyPlansRequest(company_id=UUID(current_user.id))
    response = show_my_plans_use_case.show_company_plans(request)
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
    show_p_account_details: use_cases.ShowPAccountDetailsUseCase,
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
    show_r_account_details: use_cases.ShowRAccountDetailsUseCase,
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
    show_a_account_details: use_cases.ShowAAccountDetailsUseCase,
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
    show_prd_account_details: use_cases.ShowPRDAccountDetailsUseCase,
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
    use_case_response = get_plan_summary_company.get_plan_summary_for_company(
        plan_id, UUID(current_user.id)
    )
    if use_case_response.plan_summary:
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
def create_cooperation(view: CreateCooperationView):
    form = CreateCooperationForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)
    elif request.method == "GET":
        return view.respond_to_get(form)


@CompanyRoute("/company/request_cooperation", methods=["GET", "POST"])
@commit_changes
def request_cooperation(
    list_plans: ListActivePlansOfCompany,
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
    list_my_cooperating_plans: ListMyCooperatingPlansUseCase,
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
    list_my_coop_plans_response = list_my_cooperating_plans.list_cooperations(
        ListMyCooperatingPlansUseCase.Request(company=UUID(current_user.id))
    )

    view_model = presenter.present(
        list_coord_response,
        list_inbound_coop_requests_response,
        accept_cooperation_response,
        deny_cooperation_response,
        list_outbound_coop_requests_response,
        cancel_cooperation_solicitation_response,
        list_my_coop_plans_response,
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


@CompanyRoute("/company/invite_worker_to_company", methods=["GET", "POST"])
def invite_worker_to_company(
    view: InviteWorkerToCompanyView,
) -> Response:
    form = InviteWorkerToCompanyForm(request.form)
    if request.method == "POST":
        return view.respond_to_post(form)
    else:
        return view.respond_to_get(form)


@CompanyRoute("/company/end_cooperation")
@commit_changes
def end_cooperation(
    view: EndCooperationView,
) -> Response:
    return view.respond_to_get()
