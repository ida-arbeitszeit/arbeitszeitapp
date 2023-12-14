from uuid import UUID

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.get_company_summary import (
    GetCompanySummary,
    GetCompanySummarySuccess,
)
from arbeitszeit.use_cases.get_user_account_details import GetUserAccountDetailsUseCase
from arbeitszeit.use_cases.request_email_address_change import (
    RequestEmailAddressChangeUseCase,
)
from arbeitszeit_flask.forms import RequestEmailAddressChangeForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404, http_501
from arbeitszeit_web.www.controllers.request_email_address_change_controller import (
    RequestEmailAddressChangeController,
)
from arbeitszeit_web.www.controllers.user_account_details_controller import (
    UserAccountDetailsController,
)
from arbeitszeit_web.www.presenters.get_company_summary_presenter import (
    GetCompanySummarySuccessPresenter,
)
from arbeitszeit_web.www.presenters.request_email_address_change_presenter import (
    RequestEmailAddressChangePresenter,
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


@AuthenticatedUserRoute("/request-email-change", methods=["GET", "POST"])
def request_email_change(
    controller: RequestEmailAddressChangeController,
    presenter: RequestEmailAddressChangePresenter,
    use_case: RequestEmailAddressChangeUseCase,
) -> Response:
    template_name = "user/request_email_address_change.html"
    form = RequestEmailAddressChangeForm(request.form)
    match request.method:
        case "POST":
            if not form.validate():
                return FlaskResponse(
                    render_template(template_name, form=form), status=400
                )
            uc_request = controller.process_email_address_change_request(form)
            uc_response = use_case.request_email_address_change(uc_request)
            view_model = presenter.render_response(uc_response, form)
            if view_model.redirect_url:
                return redirect(view_model.redirect_url)
            else:
                return FlaskResponse(
                    render_template(template_name, form=form), status=400
                )
        case _:
            return FlaskResponse(render_template(template_name, form=form), status=200)


@AuthenticatedUserRoute("/change-email/<token>")
def change_email_address(token: str) -> Response:
    return http_501()
