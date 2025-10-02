from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, url_for
from flask_login import current_user

from arbeitszeit.interactors.create_draft_from_plan import CreateDraftFromPlanInteractor
from arbeitszeit.interactors.delete_draft import DeleteDraftInteractor
from arbeitszeit.interactors.file_plan_with_accounting import FilePlanWithAccounting
from arbeitszeit.interactors.get_plan_details import GetPlanDetailsInteractor
from arbeitszeit.interactors.hide_plan import HidePlanInteractor
from arbeitszeit.interactors.list_coordinations_of_company import (
    ListCoordinationsOfCompanyInteractor,
    ListCoordinationsOfCompanyRequest,
)
from arbeitszeit.interactors.list_my_cooperating_plans import (
    ListMyCooperatingPlansInteractor,
)
from arbeitszeit.interactors.query_company_consumptions import (
    QueryCompanyConsumptionsInteractor,
)
from arbeitszeit.interactors.revoke_plan_filing import RevokePlanFilingInteractor
from arbeitszeit.interactors.show_company_cooperations import (
    Request,
    ShowCompanyCooperationsInteractor,
)
from arbeitszeit.interactors.show_my_plans import (
    ShowMyPlansInteractor,
    ShowMyPlansRequest,
)
from arbeitszeit_flask.class_based_view import as_flask_view
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_request import FlaskRequest
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views import (
    EndCooperationView,
    InviteWorkerToCompanyView,
    RequestCooperationView,
)
from arbeitszeit_flask.views.accept_cooperation_request_view import (
    AcceptCooperationRequestView,
)
from arbeitszeit_flask.views.cancel_cooperation_request_view import (
    CancelCooperationRequestView,
)
from arbeitszeit_flask.views.company_dashboard_view import CompanyDashboardView
from arbeitszeit_flask.views.create_cooperation_view import CreateCooperationView
from arbeitszeit_flask.views.create_draft_view import CreateDraftView
from arbeitszeit_flask.views.deny_cooperation_view import DenyCooperationView
from arbeitszeit_flask.views.draft_details_view import DraftDetailsView
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_flask.views.list_pending_work_invites_view import (
    ListPendingWorkInvitesView,
)
from arbeitszeit_flask.views.list_registered_hours_worked_view import (
    ListRegisteredHoursWorkedView,
)
from arbeitszeit_flask.views.register_hours_worked_view import RegisterHoursWorkedView
from arbeitszeit_flask.views.register_productive_consumption import (
    RegisterProductiveConsumptionView,
)
from arbeitszeit_flask.views.remove_worker_from_company_view import (
    RemoveWorkerFromCompanyView,
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
    query_consumptions: QueryCompanyConsumptionsInteractor,
    presenter: CompanyConsumptionsPresenter,
):
    response = query_consumptions.execute(UUID(current_user.id))
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
    interactor: DeleteDraftInteractor,
    presenter: DeleteDraftPresenter,
) -> Response:
    interactor_request = controller.get_request(request=FlaskRequest(), draft=draft_id)
    try:
        interactor_response = interactor.delete_draft(interactor_request)
    except interactor.Failure:
        return http_404()
    view_model = presenter.present_draft_deletion(interactor_response)
    return redirect(view_model.redirect_target)


@CompanyRoute("/draft/from-plan/<uuid:plan_id>", methods=["POST"])
@commit_changes
def create_draft_from_plan(
    plan_id: UUID,
    interactor: CreateDraftFromPlanInteractor,
    controller: CreateDraftFromPlanController,
    presenter: CreateDraftFromPlanPresenter,
) -> Response:
    uc_request = controller.create_interactor_request(plan_id)
    uc_response = interactor.create_draft_from_plan(uc_request)
    view_model = presenter.render_response(
        interactor_response=uc_response,
        request=FlaskRequest(),
    )
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
    interactor: FilePlanWithAccounting,
    presenter: FilePlanWithAccountingPresenter,
):
    try:
        request = controller.process_file_plan_with_accounting_request(
            draft_id=draft_id, session=session
        )
    except controller.InvalidRequest:
        return http_404()
    response = interactor.file_plan_with_accounting(request)
    view_model = presenter.present_response(response)
    return redirect(view_model.redirect_url)


@CompanyRoute("/draft/<uuid:draft_id>", methods=["GET", "POST"])
@as_flask_view()
class get_draft_details(DraftDetailsView): ...


@CompanyRoute("/my_plans", methods=["GET"])
def my_plans(
    show_my_plans_interactor: ShowMyPlansInteractor,
    show_my_plans_presenter: ShowMyPlansPresenter,
):
    request = ShowMyPlansRequest(company_id=UUID(current_user.id))
    response = show_my_plans_interactor.show_company_plans(request)
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
    interactor: RevokePlanFilingInteractor,
    presenter: RevokePlanFilingPresenter,
):
    request = controller.create_request(plan_id=plan_id)
    response = interactor.revoke_plan_filing(request=request)
    presenter.present(response)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/hide_plan/<uuid:plan_id>", methods=["GET", "POST"])
@commit_changes
def hide_plan(
    plan_id: UUID, hide_plan: HidePlanInteractor, presenter: HidePlanPresenter
):
    response = hide_plan.execute(plan_id)
    presenter.present(response)
    return redirect(url_for("main_company.my_plans"))


@CompanyRoute("/register_hours_worked", methods=["GET", "POST"])
@as_flask_view()
class register_hours_worked(RegisterHoursWorkedView): ...


@CompanyRoute("/registered_hours_worked")
@as_flask_view()
class registered_hours_worked(ListRegisteredHoursWorkedView): ...


@CompanyRoute("/register_productive_consumption", methods=["GET", "POST"])
@as_flask_view()
class register_productive_consumption(RegisterProductiveConsumptionView): ...


@CompanyRoute("/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    interactor: GetPlanDetailsInteractor,
    presenter: GetPlanDetailsCompanyPresenter,
):
    interactor_request = GetPlanDetailsInteractor.Request(plan_id)
    interactor_response = interactor.get_plan_details(interactor_request)
    if not interactor_response:
        return http_404()
    view_model = presenter.present(interactor_response)
    return render_template("company/plan_details.html", view_model=view_model)


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


@CompanyRoute("/my_cooperations", methods=["GET"])
def my_cooperations(
    list_coordinations: ListCoordinationsOfCompanyInteractor,
    show_company_cooperations: ShowCompanyCooperationsInteractor,
    list_my_cooperating_plans: ListMyCooperatingPlansInteractor,
    presenter: ShowMyCooperationsPresenter,
):
    list_coord_response = list_coordinations.execute(
        ListCoordinationsOfCompanyRequest(UUID(current_user.id))
    )
    show_company_cooperations_response = (
        show_company_cooperations.show_company_cooperations(
            Request(UUID(current_user.id))
        )
    )
    list_my_coop_plans_response = list_my_cooperating_plans.list_cooperations(
        ListMyCooperatingPlansInteractor.Request(company=UUID(current_user.id))
    )
    view_model = presenter.present(
        list_coord_response=list_coord_response,
        show_company_cooperations_response=show_company_cooperations_response,
        list_my_cooperating_plans_response=list_my_coop_plans_response,
    )
    return render_template("company/my_cooperations.html", **view_model.to_dict())


@CompanyRoute("/accept_cooperation_request", methods=["POST"])
@as_flask_view()
class accept_cooperation_request(AcceptCooperationRequestView): ...


@CompanyRoute("/deny_cooperation_request", methods=["POST"])
@as_flask_view()
class deny_cooperation_request(DenyCooperationView): ...


@CompanyRoute("/cancel_cooperation_request", methods=["POST"])
@as_flask_view()
class cancel_cooperation_request(CancelCooperationRequestView): ...


@CompanyRoute("/invite_worker_to_company", methods=["GET", "POST"])
@as_flask_view()
class invite_worker_to_company(InviteWorkerToCompanyView): ...


@CompanyRoute("/remove_worker_from_company", methods=["GET", "POST"])
@as_flask_view()
class remove_worker_from_company(RemoveWorkerFromCompanyView): ...


@CompanyRoute("/list_pending_work_invites", methods=["GET", "POST"])
@as_flask_view()
class list_pending_work_invites(ListPendingWorkInvitesView): ...


@CompanyRoute("/end_cooperation", methods=["POST"])
@as_flask_view()
class end_cooperation(EndCooperationView): ...


@CompanyRoute("/review_registered_consumptions")
@as_flask_view()
class review_registered_consumptions(ReviewRegisteredConsumptionsView): ...
