from typing import Optional
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for
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
from arbeitszeit.use_cases.create_draft_from_plan import CreateDraftFromPlanUseCase
from arbeitszeit.use_cases.delete_draft import DeleteDraftUseCase
from arbeitszeit.use_cases.deny_cooperation import (
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
)
from arbeitszeit.use_cases.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.use_cases.get_company_summary import GetCompanySummary
from arbeitszeit.use_cases.get_coop_summary import GetCoopSummary, GetCoopSummaryRequest
from arbeitszeit.use_cases.get_draft_details import GetDraftDetails
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.hide_plan import HidePlan
from arbeitszeit.use_cases.list_active_plans_of_company import ListActivePlansOfCompany
from arbeitszeit.use_cases.list_all_cooperations import ListAllCooperations
from arbeitszeit.use_cases.list_coordinations_of_company import (
    ListCoordinationsOfCompany,
    ListCoordinationsOfCompanyRequest,
)
from arbeitszeit.use_cases.list_coordinations_of_cooperation import (
    ListCoordinationsOfCooperationUseCase,
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
from arbeitszeit.use_cases.query_company_consumptions import QueryCompanyConsumptions
from arbeitszeit.use_cases.request_cooperation import RequestCooperation
from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
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
    RequestCoordinationTransferForm,
)
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
from arbeitszeit_flask.views.register_hours_worked_view import RegisterHoursWorkedView
from arbeitszeit_flask.views.register_productive_consumption import (
    RegisterProductiveConsumptionView,
)
from arbeitszeit_flask.views.request_coordination_transfer_view import (
    RequestCoordinationTransferView,
)
from arbeitszeit_flask.views.show_coordination_transfer_request_view import (
    ShowCoordinationTransferRequestView,
)
from arbeitszeit_flask.views.show_my_accounts_view import ShowMyAccountsView
from arbeitszeit_web.query_plans import QueryPlansController, QueryPlansPresenter
from arbeitszeit_web.www.controllers.create_draft_from_plan_controller import (
    CreateDraftFromPlanController,
)
from arbeitszeit_web.www.controllers.delete_draft_controller import (
    DeleteDraftController,
)
from arbeitszeit_web.www.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
)
from arbeitszeit_web.www.controllers.query_companies_controller import (
    QueryCompaniesController,
)
from arbeitszeit_web.www.controllers.request_cooperation_controller import (
    RequestCooperationController,
)
from arbeitszeit_web.www.controllers.revoke_plan_filing_controller import (
    RevokePlanFilingController,
)
from arbeitszeit_web.www.presenters.company_consumptions_presenter import (
    CompanyConsumptionsPresenter,
)
from arbeitszeit_web.www.presenters.create_draft_from_plan_presenter import (
    CreateDraftFromPlanPresenter,
)
from arbeitszeit_web.www.presenters.create_draft_presenter import (
    GetPrefilledDraftDataPresenter,
)
from arbeitszeit_web.www.presenters.delete_draft_presenter import DeleteDraftPresenter
from arbeitszeit_web.www.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
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
from arbeitszeit_web.www.presenters.list_coordinations_of_cooperation_presenter import (
    ListCoordinationsOfCooperationPresenter,
)
from arbeitszeit_web.www.presenters.list_plans_presenter import ListPlansPresenter
from arbeitszeit_web.www.presenters.query_companies_presenter import (
    QueryCompaniesPresenter,
)
from arbeitszeit_web.www.presenters.request_cooperation_presenter import (
    RequestCooperationPresenter,
)
from arbeitszeit_web.www.presenters.revoke_plan_filing_presenter import (
    RevokePlanFilingPresenter,
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
    presenter: QueryPlansPresenter,
):
    template_name = "company/query_plans.html"
    search_form = PlanSearchForm(request.args)
    view = QueryPlansView(
        query_plans,
        presenter,
        controller,
        template_name,
    )
    return view.respond_to_get(search_form, FlaskRequest())


@CompanyRoute("/company/query_companies", methods=["GET"])
def query_companies(
    query_companies: use_cases.query_companies.QueryCompanies,
    controller: QueryCompaniesController,
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
    )
    return view.respond_to_get()


@CompanyRoute("/company/consumptions")
def my_consumptions(
    query_consumptions: QueryCompanyConsumptions,
    presenter: CompanyConsumptionsPresenter,
):
    response = query_consumptions(UUID(current_user.id))
    view_model = presenter.present(response)
    return FlaskResponse(
        render_template(
            "company/my_consumptions.html",
            view_model=view_model,
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


@CompanyRoute("/company/draft/from-plan/<uuid:plan_id>", methods=["POST"])
@commit_changes
def create_draft_from_plan(
    plan_id: UUID,
    use_case: CreateDraftFromPlanUseCase,
    controller: CreateDraftFromPlanController,
    presenter: CreateDraftFromPlanPresenter,
) -> Response:
    uc_request = controller.create_use_case_request(plan_id)
    uc_response = use_case.create_draft_from_plan(uc_request)
    view_model = presenter.render_response(uc_response)
    return redirect(view_model.redirect_url)


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
    not_found_view: Http404View,
) -> Response:
    use_case_response = use_case(UUID(draft_id))
    if use_case_response is None:
        return not_found_view.get_response()
    form = CreateDraftForm()
    view_model = presenter.show_prefilled_draft_data(use_case_response, form=form)
    return FlaskResponse(
        render_template(
            "company/create_draft.html",
            view_model=view_model,
            form=form,
        )
    )


@CompanyRoute("/company/my_plans", methods=["GET"])
def my_plans(
    show_my_plans_use_case: ShowMyPlansUseCase,
    show_my_plans_presenter: ShowMyPlansPresenter,
):
    request = ShowMyPlansRequest(company_id=UUID(current_user.id))
    response = show_my_plans_use_case.show_company_plans(request)
    view_model = show_my_plans_presenter.present(response)
    return render_template(
        "company/my_plans.html",
        **view_model.to_dict(),
    )


@CompanyRoute("/company/plan/revoke/<uuid:plan_id>", methods=["POST"])
@commit_changes
def revoke_plan_filing(
    plan_id: UUID,
    controller: RevokePlanFilingController,
    use_case: RevokePlanFilingUseCase,
    presenter: RevokePlanFilingPresenter,
):
    request = controller.create_request(plan_id=plan_id)
    response = use_case.revoke_plan_filing(request=request)
    presenter.present(response)
    return redirect(url_for("main_company.my_plans"))


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
    presenter: GetCompanyTransactionsPresenter,
):
    response = get_company_transactions(UUID(current_user.id))
    view_model = presenter.present(response)
    return render_template(
        "company/list_all_transactions.html",
        all_transactions=view_model.transactions,
    )


@CompanyRoute("/company/my_accounts/account_p")
def account_p(
    show_p_account_details: use_cases.show_p_account_details.ShowPAccountDetailsUseCase,
    presenter: ShowPAccountDetailsPresenter,
):
    response = show_p_account_details(UUID(current_user.id))
    view_model = presenter.present(response)
    return render_template(
        "company/account_p.html",
        view_model=view_model,
    )


@CompanyRoute("/company/my_accounts/account_r")
def account_r(
    show_r_account_details: use_cases.show_r_account_details.ShowRAccountDetailsUseCase,
    presenter: ShowRAccountDetailsPresenter,
):
    response = show_r_account_details(UUID(current_user.id))
    view_model = presenter.present(response)
    return render_template(
        "company/account_r.html",
        view_model=view_model,
    )


@CompanyRoute("/company/my_accounts/account_a")
def account_a(
    show_a_account_details: use_cases.show_a_account_details.ShowAAccountDetailsUseCase,
    presenter: ShowAAccountDetailsPresenter,
):
    response = show_a_account_details(UUID(current_user.id))
    view_model = presenter.present(response)
    return render_template(
        "company/account_a.html",
        view_model=view_model,
    )


@CompanyRoute("/company/my_accounts/account_prd")
def account_prd(
    show_prd_account_details: use_cases.show_prd_account_details.ShowPRDAccountDetailsUseCase,
    presenter: ShowPRDAccountDetailsPresenter,
):
    response = show_prd_account_details(UUID(current_user.id))
    view_model = presenter.present(response)
    return render_template(
        "company/account_prd.html",
        view_model=view_model,
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
):
    use_case_response = get_statistics()
    view_model = presenter.present(use_case_response)
    return render_template("company/statistics.html", view_model=view_model)


@CompanyRoute("/company/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    use_case: GetPlanDetailsUseCase,
    presenter: GetPlanDetailsCompanyPresenter,
    http_404_view: Http404View,
):
    use_case_request = GetPlanDetailsUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_details(use_case_request)
    if not use_case_response:
        return http_404_view.get_response()
    view_model = presenter.present(use_case_response)
    return render_template("company/plan_details.html", view_model=view_model.to_dict())


@CompanyRoute("/company/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummary,
    presenter: GetCompanySummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_company_summary(company_id)
    if isinstance(
        use_case_response, use_cases.get_company_summary.GetCompanySummarySuccess
    ):
        view_model = presenter.present(use_case_response)
        return render_template(
            "company/company_summary.html",
            view_model=view_model.to_dict(),
        )
    else:
        return http_404_view.get_response()


@CompanyRoute("/company/cooperation_summary/<uuid:coop_id>")
def coop_summary(
    coop_id: UUID,
    get_coop_summary: GetCoopSummary,
    presenter: GetCoopSummarySuccessPresenter,
    http_404_view: Http404View,
):
    use_case_response = get_coop_summary(
        GetCoopSummaryRequest(UUID(current_user.id), coop_id)
    )
    if use_case_response:
        view_model = presenter.present(use_case_response)
        return render_template(
            "company/coop_summary.html", view_model=view_model.to_dict()
        )
    else:
        return http_404_view.get_response()


@CompanyRoute(
    "/company/cooperation_summary/<uuid:coop_id>/request_coordination_transfer",
    methods=["GET", "POST"],
)
@commit_changes
def request_coordination_transfer(
    coop_id: UUID,
    view: RequestCoordinationTransferView,
):
    if request.method == "GET":
        form = RequestCoordinationTransferForm()
        form.cooperation_field().set_value(str(coop_id))
        return view.respond_to_get(form=form, coop_id=coop_id)

    elif request.method == "POST":
        form = RequestCoordinationTransferForm(request.form)
        return view.respond_to_post(form=form, coop_id=coop_id)


@CompanyRoute(
    "/company/show_coordination_transfer_request/<uuid:transfer_request>",
    methods=["GET", "POST"],
)
@commit_changes
def show_coordination_transfer_request(
    transfer_request: UUID,
    view: ShowCoordinationTransferRequestView,
):
    if request.method == "GET":
        return view.respond_to_get(transfer_request)

    elif request.method == "POST":
        return view.respond_to_post(transfer_request)


@CompanyRoute(
    "/company/cooperation_summary/<uuid:coop_id>/coordinators", methods=["GET"]
)
def list_coordinators_of_cooperation(
    coop_id: UUID,
    list_coordinations_of_cooperation: ListCoordinationsOfCooperationUseCase,
    presenter: ListCoordinationsOfCooperationPresenter,
):
    use_case_response = list_coordinations_of_cooperation.list_coordinations(
        ListCoordinationsOfCooperationUseCase.Request(cooperation=coop_id)
    )
    view_model = presenter.list_coordinations_of_cooperation(use_case_response)
    return render_template(
        "company/list_coordinators_of_cooperation.html", view_model=view_model
    )


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
    )

    if request.method == "POST":
        return view.respond_to_post()

    elif request.method == "GET":
        return view.respond_to_get()


@CompanyRoute("/company/my_cooperations", methods=["GET", "POST"])
@commit_changes
def my_cooperations(
    list_coordinations: ListCoordinationsOfCompany,
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
        ListCoordinationsOfCompanyRequest(UUID(current_user.id))
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
    return render_template("company/my_cooperations.html", **view_model.to_dict())


@CompanyRoute("/company/list_all_cooperations")
@commit_changes
def list_all_cooperations(
    use_case: ListAllCooperations,
    presenter: ListAllCooperationsPresenter,
):
    response = use_case()
    view_model = presenter.present(response)
    return render_template("company/list_all_cooperations.html", view_model=view_model)


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
