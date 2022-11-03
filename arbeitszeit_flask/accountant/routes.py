from uuid import UUID

from flask import redirect

from arbeitszeit.use_cases.approve_plan import ApprovePlanUseCase
from arbeitszeit.use_cases.list_plans_with_pending_review import (
    ListPlansWithPendingReviewUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.controllers.approve_plan_controller import ApprovePlanController
from arbeitszeit_web.presenters.approve_plan_presenter import ApprovePlanPresenter
from arbeitszeit_web.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)
from arbeitszeit_web.presenters.list_plans_with_pending_review_presenter import (
    ListPlansWithPendingReviewPresenter,
)

from .blueprint import AccountantRoute


@AccountantRoute("/accountant/dashboard")
def dashboard(
    template_renderer: UserTemplateRenderer, presenter: GetAccountantDashboardPresenter
) -> Response:
    view_model = presenter.create_dashboard_view_model()
    print(view_model)
    return template_renderer.render_template(
        "accountant/dashboard.html",
        context=dict(view_model=view_model),
    )


@AccountantRoute("/accountant/plans/unreviewed")
def list_plans_with_pending_review(
    template_renderer: UserTemplateRenderer,
    use_case: ListPlansWithPendingReviewUseCase,
    presenter: ListPlansWithPendingReviewPresenter,
) -> Response:
    response = use_case.list_plans_with_pending_review(request=use_case.Request())
    view_model = presenter.list_plans_with_pending_review(response)
    return template_renderer.render_template(
        "accountant/plans-to-review-list.html",
        context=dict(view_model=view_model),
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
