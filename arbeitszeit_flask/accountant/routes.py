from arbeitszeit_flask.template import UserTemplateRenderer
from arbeitszeit_flask.types import Response
from arbeitszeit_web.presenters.get_accountant_dashboard_presenter import (
    GetAccountantDashboardPresenter,
)

from .blueprint import AccountantRoute


@AccountantRoute("/accountant/dashboard")
def dashboard(
    template_renderer: UserTemplateRenderer, presenter: GetAccountantDashboardPresenter
) -> Response:
    view_model = presenter.create_dashboard_view_model()
    return template_renderer.render_template(
        "accountant/dashboard.html",
        context=dict(view_model=view_model),
    )
