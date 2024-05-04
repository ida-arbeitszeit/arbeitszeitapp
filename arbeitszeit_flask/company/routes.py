from typing import Optional
from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request, url_for
from flask_login import current_user

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
from arbeitszeit.use_cases.get_draft_details import GetDraftDetails
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.hide_plan import HidePlan
from arbeitszeit.use_cases.list_coordinations_of_company import (
    ListCoordinationsOfCompany,
    ListCoordinationsOfCompanyRequest,
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
from arbeitszeit.use_cases.revoke_plan_filing import RevokePlanFilingUseCase
from arbeitszeit.use_cases.show_my_plans import ShowMyPlansRequest, ShowMyPlansUseCase
from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.forms import CreateDraftForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    EndCooperationView,
    InviteWorkerToCompanyView,
    RequestCooperationView,
)
from arbeitszeit_flask.views.company_dashboard_view import CompanyDashboardView
from arbeitszeit_flask.views.create_cooperation_view import CreateCooperationView
from arbeitszeit_flask.views.create_draft_view import CreateDraftView
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_flask.views.register_hours_worked_view import RegisterHoursWorkedView
from arbeitszeit_flask.views.register_productive_consumption import (
    RegisterProductiveConsumptionView,
)
from arbeitszeit_flask.views.request_coordination_transfer_view import (
    RequestCoordinationTransferView,
)
from arbeitszeit_flask.views.review_registered_consumptions_view import (
    ReviewRegisteredConsumptionsView,
)
from arbeitszeit_flask.views.show_coordination_transfer_request_view import (
    ShowCoordinationTransferRequestView,
)
from arbeitszeit_web.www.controllers.create_draft_from_plan_controller import (
    CreateDraftFromPlanController,
)
from arbeitszeit_web.www.controllers.delete_draft_controller import (
    DeleteDraftController,
)
from arbeitszeit_web.www.controllers.file_plan_with_accounting_controller import (
    FilePlanWithAccountingController,
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
from arbeitszeit_web.www.presenters.delete_draft_presenter import DeleteDraftPresenter
from arbeitszeit_web.www.presenters.file_plan_with_accounting_presenter import (
    FilePlanWithAccountingPresenter,
)
from arbeitszeit_web.www.presenters.get_draft_details_presenter import (
    GetDraftDetailsPresenter,
)
from arbeitszeit_web.www.presenters.get_plan_details_company_presenter import (
    GetPlanDetailsCompanyPresenter,
)
from arbeitszeit_web.www.presenters.hide_plan_presenter import HidePlanPresenter
from arbeitszeit_web.www.presenters.revoke_plan_filing_presenter import (
    RevokePlanFilingPresenter,
)
from arbeitszeit_web.www.presenters.show_my_cooperations_presenter import (
    ShowMyCooperationsPresenter,
)
from arbeitszeit_web.www.presenters.show_my_plans_presenter import ShowMyPlansPresenter

from .blueprint import CompanyRoute


@CompanyRoute("/dashboard")
@as_flask_view()
class dashboard(CompanyDashboardView): ...


@CompanyRoute("/consumptions")
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


@CompanyRoute("/draft/delete/<uuid:draft_id>", methods=["POST"])
@commit_changes
def delete_draft(
    draft_id: UUID,
    controller: DeleteDraftController,
    use_case: DeleteDraftUseCase,
    presenter: DeleteDraftPresenter,
) -> Response:
    use_case_request = controller.get_request(request=FlaskRequest(), draft=draft_id)
    try:
        use_case_response = use_case.delete_draft(use_case_request)
    except use_case.Failure:
        return http_404()
    view_model = presenter.present_draft_deletion(use_case_response)
    return redirect(view_model.redirect_target)


@CompanyRoute("/draft/from-plan/<uuid:plan_id>", methods=["POST"])
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


@CompanyRoute("/create_draft", methods=["GET", "POST"])
@as_flask_view()
class create_draft(CreateDraftView): ...


@CompanyRoute("/file_plan/<draft_id>", methods=["POST"])
@commit_changes
def file_plan(
    draft_id: str,
    session: FlaskSession,
    controller: FilePlanWithAccountingController,
    use_case: FilePlanWithAccounting,
    presenter: FilePlanWithAccountingPresenter,
):
    try:
        request = controller.process_file_plan_with_accounting_request(
            draft_id=draft_id, session=session
        )
    except controller.InvalidRequest:
        return http_404()
    response = use_case.file_plan_with_accounting(request)
    view_model = presenter.present_response(response)
    return redirect(view_model.redirect_url)


@CompanyRoute("/draft/<draft_id>", methods=["GET"])
def get_draft_details(
    draft_id: str,
    use_case: GetDraftDetails,
    presenter: GetDraftDetailsPresenter,
) -> Response:
    use_case_response = use_case(UUID(draft_id))
    if use_case_response is None:
        return http_404()
    form = CreateDraftForm()
    view_model = presenter.present_draft_details(use_case_response, form=form)
    return FlaskResponse(
        render_template(
            "company/draft_details.html",
            view_model=view_model,
            form=form,
        )
    )


@CompanyRoute("/my_plans", methods=["GET"])
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


@CompanyRoute("/plan/revoke/<uuid:plan_id>", methods=["POST"])
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


@CompanyRoute("/hide_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def hide_plan(plan_id: UUID, hide_plan: HidePlan, presenter: HidePlanPresenter):
    response = hide_plan(plan_id)
    presenter.present(response)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/register_hours_worked", methods=["GET", "POST"])
@as_flask_view()
class register_hours_worked(RegisterHoursWorkedView): ...


@CompanyRoute("/register_productive_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_productive_consumption(RegisterProductiveConsumptionView): ...


@CompanyRoute("/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    use_case: GetPlanDetailsUseCase,
    presenter: GetPlanDetailsCompanyPresenter,
):
    use_case_request = GetPlanDetailsUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_details(use_case_request)
    if not use_case_response:
        return http_404()
    view_model = presenter.present(use_case_response)
    return render_template("company/plan_details.html", view_model=view_model.to_dict())


@CompanyRoute(
    "/cooperation_summary/<uuid:coop_id>/request_coordination_transfer",
    methods=["GET", "POST"],
)
@as_flask_view()
class request_coordination_transfer(RequestCoordinationTransferView): ...


@CompanyRoute(
    "/show_coordination_transfer_request/<uuid:transfer_request>",
    methods=["GET", "POST"],
)
@as_flask_view()
class show_coordination_transfer_request(ShowCoordinationTransferRequestView): ...


@CompanyRoute("/create_cooperation", methods=["GET", "POST"])
@as_flask_view()
class create_cooperation(CreateCooperationView): ...


@CompanyRoute("/request_cooperation", methods=["GET", "POST"])
@as_flask_view()
class request_cooperation(RequestCooperationView): ...


@CompanyRoute("/my_cooperations", methods=["GET", "POST"])
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
        list_coord_response=list_coord_response,
        list_inbound_coop_requests_response=list_inbound_coop_requests_response,
        list_outbound_coop_requests_response=list_outbound_coop_requests_response,
        list_my_cooperating_plans_response=list_my_coop_plans_response,
        accept_cooperation_response=accept_cooperation_response,
        deny_cooperation_response=deny_cooperation_response,
        cancel_cooperation_solicitation_response=cancel_cooperation_solicitation_response,
    )
    return render_template("company/my_cooperations.html", **view_model.to_dict())


@CompanyRoute("/invite_worker_to_company", methods=["GET", "POST"])
@as_flask_view()
class invite_worker_to_company(InviteWorkerToCompanyView): ...


@CompanyRoute("/end_cooperation")
@as_flask_view()
class end_cooperation(EndCooperationView): ...


@CompanyRoute("/review_registered_consumptions")
@as_flask_view()
class review_registered_consumptions(ReviewRegisteredConsumptionsView): ...
