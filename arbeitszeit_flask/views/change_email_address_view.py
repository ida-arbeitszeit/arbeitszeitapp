from dataclasses import dataclass

from flask import Response as FlaskResponse
from flask import redirect, render_template, request

from arbeitszeit.use_cases.change_user_email_address import (
    ChangeUserEmailAddressUseCase,
)
from arbeitszeit_flask.database import commit_changes
from arbeitszeit_flask.forms import ConfirmEmailAddressChangeForm
from arbeitszeit_flask.types import Response
from arbeitszeit_flask.views.http_error_view import http_404
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.controllers.change_user_email_address_controller import (
    ChangeUserEmailAddressController,
)
from arbeitszeit_web.www.presenters.change_user_email_address_presenter import (
    ChangeUserEmailAddressPresenter,
)

TEMPLATE_NAME = "user/confirm_email_address_change.html"


@dataclass
class ChangeEmailAddressView:
    url_index: UrlIndex
    controller: ChangeUserEmailAddressController
    use_case: ChangeUserEmailAddressUseCase
    presenter: ChangeUserEmailAddressPresenter

    def GET(self, token: str) -> Response:
        form = ConfirmEmailAddressChangeForm(request.form)
        email_addresses = self._extract_old_and_new_email_addresses_from_token(token)
        if email_addresses is None:
            return http_404()
        old_email, new_email = email_addresses
        return FlaskResponse(
            render_template(
                TEMPLATE_NAME, form=form, old_email=old_email, new_email=new_email
            ),
            status=200,
        )

    @commit_changes
    def POST(self, token: str) -> Response:
        form = ConfirmEmailAddressChangeForm(request.form)
        email_addresses = self._extract_old_and_new_email_addresses_from_token(token)
        if email_addresses is None:
            return http_404()
        old_email, new_email = email_addresses
        if not form.validate():
            return FlaskResponse(
                render_template(
                    TEMPLATE_NAME,
                    form=form,
                    old_email=old_email,
                    new_email=new_email,
                ),
                status=400,
            )
        uc_request = self.controller.create_use_case_request(
            new_email_address=new_email, form=form
        )
        if uc_request is None:
            return redirect(self.url_index.get_user_account_details_url())
        uc_response = self.use_case.change_user_email_address(uc_request)
        view_model = self.presenter.render_response(uc_response)
        if view_model.redirect_url is not None:
            return redirect(view_model.redirect_url)
        else:
            return FlaskResponse(
                render_template(
                    TEMPLATE_NAME,
                    form=form,
                    old_email=old_email,
                    new_email=new_email,
                ),
                status=400,
            )

    def _extract_old_and_new_email_addresses_from_token(
        self, token: str
    ) -> tuple[str, str] | None:
        email_addresses = self.controller.extract_email_addresses_from_token(token)
        return email_addresses
