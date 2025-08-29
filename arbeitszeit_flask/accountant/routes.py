from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template

from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.get_accountant_dashboard import GetAccountantDashboardUseCase
from arbeitszeit.use_cases.get_plan_details import GetPlanDetailsUseCase
from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)
from arbeitszeit.use_cases.reject_plan import RejectPlanUseCase
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.flask_session import FlaskSession
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.controllers.approve_plan_controller import (
    ApprovePlanController,
)
from arbeitszeit_web.www.controllers.reject_plan_controller import RejectPlanController
from arbeitszeit_web.www.presenters.approve_plan_presenter import ApprovePlanPresenter
from arbeitszeit_web.www.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)
from arbeitszeit_web.www.presenters.get_plan_details_accountant_presenter import (
    GetPlanDetailsAccountantPresenter,
)
from arbeitszeit_web.www.presenters.list_plans_with_pending_review_presenter import (
    ListPlansWithPendingReviewPresenter,
)
from arbeitszeit_web.www.presenters.reject_plan_presenter import RejectPlanPresenter

from .blueprint import AccountantRoute


@AccountantRoute("/accountant/dashboard")
def dashboard(
    flask_session: FlaskSession,
    use_case: GetAccountantDashboardUseCase,
    presenter: GetAccountantDashboardPresenter,
) -> Response:
    current_user = flask_session.get_current_user()
    assert current_user
    response = use_case.get_dashboard(current_user)
    view_model = presenter.create_dashboard_view_model(response)
    return render_template(
        "accountant/dashboard.html",
        view_model=view_model,
    )


@AccountantRoute("/accountant/plans/unreviewed")
def list_plans_with_pending_review(
    use_case: ListPlansWithPendingReviewUseCase,
    presenter: ListPlansWithPendingReviewPresenter,
) -> Response:
    response = use_case.list_plans_with_pending_review(request=use_case.Request())
    view_model = presenter.list_plans_with_pending_review(response)
    return render_template(
        "accountant/plans-to-review-list.html",
        view_model=view_model,
    )


@AccountantRoute("/accountant/plans/<uuid:plan>/approve", methods=["POST"])
@commit_changes
def approve_plan(
    plan: UUID,
    controller: ApprovePlanController,
    use_case: ApprovePlanUseCase,
    presenter: ApprovePlanPresenter,
) -> Response:
    request = controller.approve_plan(plan)
    response = use_case.approve_plan(request)
    view_model = presenter.approve_plan(response)
    return redirect(view_model.redirect_url)


@AccountantRoute("/accountant/plans/<uuid:plan>/reject", methods=["POST"])
@commit_changes
def reject_plan(
    plan: UUID,
    controller: RejectPlanController,
    use_case: RejectPlanUseCase,
    presenter: RejectPlanPresenter,
) -> Response:
    request = controller.reject_plan(plan)
    response = use_case.reject_plan(request)
    view_model = presenter.reject_plan(response)
    return redirect(view_model.redirect_url)


@AccountantRoute("/accountant/plan_details/<uuid:plan_id>")
def plan_details(
    plan_id: UUID,
    use_case: GetPlanDetailsUseCase,
    presenter: GetPlanDetailsAccountantPresenter,
) -> Response:
    use_case_request = GetPlanDetailsUseCase.Request(plan_id)
    use_case_response = use_case.get_plan_details(use_case_request)
    if use_case_response:
        view_model = presenter.present(use_case_response)
        return FlaskResponse(
            render_template(
                "accountant/plan_details.html",
                view_model=view_model,
            )
        )
    else:
        return http_404()
