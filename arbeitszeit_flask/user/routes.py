from uuid import UUID

from flask import render_template

from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummary,
    GetCompanySummarySuccess,
)
from arbeitszeit.use_cases.get_user_account_details import GetUserAccountDetailsUseCase
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.www.controllers.user_account_details_controller import (
    UserAccountDetailsController,
)
from arbeitszeit_web.www.presenters.get_company_summary_presenter import (
    GetCompanySummarySuccessPresenter,
)
from arbeitszeit_web.www.presenters.user_account_details_presenter import (
    UserAccountDetailsPresenter,
)

from .blueprint import AuthenticatedUserRoute


@AuthenticatedUserRoute("/account")
def account_details(
    controller: UserAccountDetailsController,
    use_case: GetUserAccountDetailsUseCase,
    presenter: UserAccountDetailsPresenter,
) -> Response:
    uc_request = controller.parse_web_request()
    uc_response = use_case.get_user_account_details(uc_request)
    view_model = presenter.render_user_account_details(uc_response)
    return render_template("user/account_details.html", view_model=view_model)


@AuthenticatedUserRoute("/company_summary/<uuid:company_id>")
def company_summary(
    company_id: UUID,
    get_company_summary: GetCompanySummary,
    presenter: GetCompanySummarySuccessPresenter,
):
    use_case_response = get_company_summary(company_id)
    if isinstance(use_case_response, GetCompanySummarySuccess):
        view_model = presenter.present(use_case_response)
        return render_template(
            "user/company_summary.html",
            view_model=view_model.to_dict(),
        )
    else:
        return http_404()
