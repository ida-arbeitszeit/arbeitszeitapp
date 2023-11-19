from flask import render_template

from arbeitszeit.use_cases.get_user_account_details import GetUserAccountDetailsUseCase
from arbeitszeit_flask.types import Response
from arbeitszeit_web.www.controllers.user_account_details_controller import (
    UserAccountDetailsController,
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
