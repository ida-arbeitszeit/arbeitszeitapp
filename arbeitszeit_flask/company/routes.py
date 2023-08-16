from typing import Optional
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, request, url_for
from flask_login import current_user

from arbeitszeit import use_cases
from arbeitszeit.use_cases.accept_cooperation import (
    AcceptCooperation,
    AcceptCooperationRequest,
    AcceptCooperationResponse,
)
from arbeitszeit.use_cases.cancel_cooperation_solicitation import (
    CancelCooperationSolicitation,
    CancelCooperationSolicitationRequest,
)
from arbeitszeit.use_cases.create_plan_draft import CreatePlanDraft
from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit.use_cases.deny_cooperation import (
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
)
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from arbeitszeit.use_cases.get_draft_details import GetDraftDetails
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.get_user_account_details import GetUserAccountDetailsUseCase
from arbeitszeit.use_cases.hide_plan import HidePlan
from arbeitszeit.use_cases.list_active_plans_of_company import ListActivePlansOfCompany
from arbeitszeit.use_cases.list_all_cooperations import ListAllCooperations
from arbeitszeit.use_cases.list_coordinations import (
    ListCoordinations,
    ListCoordinationsRequest,
)
from arbeitszeit.use_cases.list_inbound_coop_requests import (
    ListInboundCoopRequests,
    ListInboundCoopRequestsRequest,
)
from arbeitszeit.use_cases.list_my_cooperating_plans import (
    ListMyCooperatingPlansUseCase,
)
from arbeitszeit.use_cases.list_outbound_coop_requests import (
    ListOutboundCoopRequests,
    ListOutboundCoopRequestsRequest,
)
from arbeitszeit.use_cases.request_cooperation import RequestCooperation
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit.use_cases.toggle_product_availablity import ToggleProductAvailability
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import (
    CompanySearchForm,
    CreateCooperationForm,
    CreateDraftForm,
    InviteWorkerToCompanyForm,
    PlanSearchForm,
    RegisterProductiveConsumptionForm,
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
from arbeitszeit_flask.views.pay_means_of_production import (
    RegisterProductiveConsumptionView,
)
from arbeitszeit_flask.views.register_hours_worked_view import RegisterHoursWorkedView
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.controllers.create_draft_controller import (
    CreateDraftController,
)
from arbeitszeit_web.www.controllers.delete_draft_controller import (
    DeleteDraftController,
)
from arbeitszeit_web.www.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
)
from arbeitszeit_web.www.controllers.get_company_account_details_controller import (
    GetCompanyAccountDetailsController,
)
from arbeitszeit_web.www.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.www.controllers.request_cooperation_controller import (
    RequestCooperationController,
)
from arbeitszeit_web.www.presenters.company_purchases_presenter import (
    CompanyPurchasesPresenter,
)
from arbeitszeit_web.www.presenters.create_draft_presenter import (
    CreateDraftPresenter,
    GetPrefilledDraftDataPresenter,
)
from arbeitszeit_web.www.presenters.delete_draft_presenter import DeleteDraftPresenter
from arbeitszeit_web.www.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
)
from arbeitszeit_web.www.presenters.get_company_account_details_presenter import (
    GetCompanyAccountDetailsPresenter,
)
from arbeitszeit_web.www.presenters.get_company_summary_presenter import (
    GetCompanySummarySuccessPresenter,
)
from arbeitszeit_web.www.presenters.get_company_transactions_presenter import (
    GetCompanyTransactionsPresenter,
)
from arbeitszeit_web.www.presenters.get_coop_summary_presenter import (
    GetCoopSummarySuccessPresenter,
)
from arbeitszeit_web.www.presenters.get_plan_details_company_presenter import (
    GetPlanDetailsCompanyPresenter,
)
from arbeitszeit_web.www.presenters.get_statistics_presenter import (
    GetStatisticsPresenter,
)
from arbeitszeit_web.www.presenters.hide_plan_presenter import HidePlanPresenter
from arbeitszeit_web.www.presenters.list_all_cooperations_presenter import (
    ListAllCooperationsPresenter,
)
from arbeitszeit_web.www.presenters.list_plans_presenter import ListPlansPresenter
from arbeitszeit_web.www.presenters.query_companies_presenter import (
    QueryCompaniesPresenter,
)
from arbeitszeit_web.www.presenters.request_cooperation_presenter import (
    RequestCooperationPresenter,
)
from arbeitszeit_web.www.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from arbeitszeit_web.www.presenters.show_my_cooperations_presenter import (
    ShowMyCooperationsPresenter,
)
from arbeitszeit_web.www.presenters.show_my_plans_presenter import ShowMyPlansPresenter
from arbeitszeit_web.www.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from arbeitszeit_web.www.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from arbeitszeit_web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)

from .blueprint import CompanyRoute


@CompanyRoute("/company/dashboard")
def dashboard(view: CompanyDashboardView):
    return view.respond_to_get()


@CompanyRoute("/company/query_plans", methods=["GET"])
def query_plans(
    query_plans: use_cases.query_plans.QueryPlans,
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
    return view.respond_to_get(search_form, FlaskRequest())


@CompanyRoute("/company/query_companies", methods=["GET"])
def query_companies(
    query_companies: use_cases.query_companies.QueryCompanies,
    controller: QueryCompaniesController,
    template_renderer: UserTemplateRenderer,
    presenter: QueryCompaniesPresenter,
):
    template_name = "company/query_companies.html"
    search_form = CompanySearchForm(request.args)
    view = QueryCompaniesView(
        search_form,
        query_companies,
        presenter,
        controller,
        template_name,
        template_renderer,
    )
    return view.respond_to_get()


@CompanyRoute("/company/purchases")
def my_purchases(
    query_purchases: use_cases.query_company_purchases.QueryCompanyPurchases,
    template_renderer: UserTemplateRenderer,
    presenter: CompanyPurchasesPresenter,
):
    response = query_purchases(UUID(current_user.id))
    view_model = presenter.present(response)
    return FlaskResponse(
        template_renderer.render_template(
            "company/my_purchases.html",
            context=dict(view_model=view_model),
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
    get_plan_details_use_case: GetPlanDetailsUseCase,
    get_plan_details_presenter: GetPrefilledDraftDataPresenter,
    create_plan_draft_use_case: CreatePlanDraft,
    create_draft_controller: CreateDraftController,
    create_draft_presenter: CreateDraftPresenter,
    not_found_view: Http404View,
    template_renderer: UserTemplateRenderer,
    url_index: UrlIndex,
) -> Response:
    form = CreateDraftForm(request.form)
    if request.method == "GET":
        use_case_request_get = GetPlanDetailsUseCase.Request(plan_id)
        response = get_plan_details_use_case.get_plan_details(use_case_request_get)
        if not response:
            return not_found_view.get_response()
        view_model_get = get_plan_details_presenter.show_prefilled_draft_data(
            draft_data=response.plan_details, form=form
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
def get_draft_details(
    draft_id: str,
    use_case: GetDraftDetails,
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
    return redirect(url_for("main_company.plan_details", plan_id=plan_id))


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
    get_company_transactions: use_cases.get_company_transactions.GetCompanyTransactions,
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
    show_p_account_details: use_cases.show_p_account_details.ShowPAccountDetailsUseCase,
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
    show_r_account_details: use_cases.show_r_account_details.ShowRAccountDetailsUseCase,
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
    show_a_account_details: use_cases.show_a_account_details.ShowAAccountDetailsUseCase,
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
    show_prd_account_details: use_cases.show_prd_account_details.ShowPRDAccountDetailsUseCase,
    template_renderer: UserTemplateRenderer,
    presenter: ShowPRDAccountDetailsPresenter,
):
    response = show_prd_account_details(UUID(current_user.id))
    view_model = presenter.present(response)

    return template_renderer.render_template(
        "company/account_prd.html",
        context=dict(view_model=view_model),
    )


@CompanyRoute("/company/register_hours_worked", methods=["GET", "POST"])
@commit_changes
def register_hours_worked(view: RegisterHoursWorkedView):
    if request.method == "GET":
        return view.respond_to_get()
    elif request.method == "POST":
        return view.respond_to_post()


@CompanyRoute("/company/register_productive_consumption", methods=["GET", "POST"])
@commit_changes
def register_productive_consumption(view: RegisterProductiveConsumptionView):
    if request.method == "GET":
        form = RegisterProductiveConsumptionForm(request.args)
        return view.respond_to_get(form)
    elif request.method == "POST":
        form = RegisterProductiveConsumptionForm(request.form)
        return view.respond_to_post(form)


@CompanyRoute("/company/statistics")
def statistics(
    get_statistics: use_cases.get_statistics.GetStatistics,
    presenter: GetStatisticsPresenter,
    template_renderer: UserTemplateRenderer,
):
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return template_renderer.render_template(
        "company/statistics.html", context=dict(view_model=view_model)
    )


@CompanyRoute("/company/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    use_case: GetPlanDetailsUseCase,
    template_renderer: UserTemplateRenderer,
    presenter: GetPlanDetailsCompanyPresenter,
    http_404_view: Http404View,
):
    use_case_request = GetPlanDetailsUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_details(use_case_request)
    if not use_case_response:
        return http_404_view.get_response()
    view_model = presenter.present(use_case_response)
    return template_renderer.render_template(
        "company/plan_details.html", context=dict(view_model=view_model.to_dict())
    )


@CompanyRoute("/company/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummary,
    template_renderer: UserTemplateRenderer,
    presenter: GetCompanySummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_company_summary(company_id)
    if isinstance(
        use_case_response, use_cases.get_company_summary.GetCompanySummarySuccess
    ):
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
    get_coop_summary: use_cases.get_coop_summary.GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
    template_renderer: UserTemplateRenderer,
    http_404_view: Http404View,
):
    use_case_response = get_coop_summary(
        use_cases.get_coop_summary.GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if isinstance(use_case_response, use_cases.get_coop_summary.GetCoopSummarySuccess):
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


@CompanyRoute("/company/account")
def get_company_account_details(
    controller: GetCompanyAccountDetailsController,
    use_case: GetUserAccountDetailsUseCase,
    presenter: GetCompanyAccountDetailsPresenter,
    template_renderer: UserTemplateRenderer,
) -> Response:
    uc_request = controller.parse_web_request()
    uc_response = use_case.get_user_account_details(uc_request)
    view_model = presenter.render_company_account_details(uc_response)
    return FlaskResponse(
        template_renderer.render_template(
            "company/get_company_account_details.html", dict(view_model=view_model)
        ),
        status=200,
    )
