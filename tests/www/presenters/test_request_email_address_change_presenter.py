from arbeitszeit.use_cases import request_email_address_change as use_case
from arbeitszeit_web.www.presenters import (
    request_email_address_change_presenter as presenter,
)
from tests.forms import RequestEmailAddressChangeFormImpl

from ..base_test_case import BaseTestCase

rr = use_case.Response.RejectionReason


class RequestEmailAddressChangePresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(presenter.RequestEmailAddressChangePresenter)

    def test_on_success_redirect_to_non_empty_target(self) -> None:
        response = self._create_use_case_response(None)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url

    def test_on_success_redirect_logged_in_member_to_account_details_page(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(None)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url == self.url_index.get_user_account_details_url()

    def test_on_success_redirect_logged_in_company_to_account_details_page(
        self,
    ) -> None:
        self.session.login_company(self.company_generator.create_company())
        response = self._create_use_case_response(None)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url == self.url_index.get_user_account_details_url()

    def test_on_success_redirect_logged_in_accountant_to_account_details_page(
        self,
    ) -> None:
        self.session.login_accountant(self.accountant_generator.create_accountant())
        response = self._create_use_case_response(None)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url == self.url_index.get_user_account_details_url()

    def test_on_failure_dont_redirect_logged_in_member(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(rr.invalid_email_address)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url is None

    def test_on_failure_dont_redirect_logged_in_company(
        self,
    ) -> None:
        self.session.login_company(self.company_generator.create_company())
        response = use_case.Response(rr.invalid_email_address)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url is None

    def test_on_failure_dont_redirect_logged_in_accountant(
        self,
    ) -> None:
        self.session.login_accountant(self.accountant_generator.create_accountant())
        response = self._create_use_case_response(rr.invalid_email_address)
        view_model = self.presenter.render_response(response, self._create_form())
        assert view_model.redirect_url is None

    def test_on_failure_show_a_warning_that_the_request_was_denied(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(rr.invalid_email_address)
        self.presenter.render_response(response, self._create_form())
        expected_message = self.translator.gettext(
            "Your request for an email address change was rejected."
        )
        assert expected_message in self.notifier.warnings

    def test_on_success_dont_show_a_warning_that_the_request_was_denied(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(None)
        self.presenter.render_response(response, self._create_form())
        expected_message = self.translator.gettext(
            "Your request for an email address change was rejected."
        )
        assert expected_message not in self.notifier.warnings

    def test_on_success_show_a_info_that_a_confirmation_mail_was_sent(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(None)
        self.presenter.render_response(response, self._create_form())
        expected_message = self.translator.gettext(
            "A confirmation mail has been sent to your new email address."
        )
        assert expected_message in self.notifier.infos

    def test_that_error_message_is_added_to_new_email_field_on_rejection(self) -> None:
        self.session.login_member(self.member_generator.create_member())
        response = self._create_use_case_response(rr.invalid_email_address)
        form = self._create_form()
        self.presenter.render_response(response, form)
        assert form.new_email_field.errors

    def test_for_correct_error_message_on_new_email_field_when_request_was_rejected_due_to_invalid_email(
        self,
    ) -> None:
        response = self._create_use_case_response(rr.invalid_email_address)
        form = self._create_form()
        self.presenter.render_response(response, form)
        assert (
            self.translator.gettext("The email address seems to be invalid.")
            in form.new_email_field.errors
        )

    def test_for_correct_error_message_on_new_email_field_when_request_was_rejected_due_to_new_email_already_taken(
        self,
    ) -> None:
        response = self._create_use_case_response(rr.new_email_address_already_taken)
        form = self._create_form()
        self.presenter.render_response(response, form)
        assert (
            self.translator.gettext("The email address seems to be already taken.")
            in form.new_email_field.errors
        )

    def test_for_correct_error_message_on_current_password_field_when_request_was_rejected_due_to_incorrect_password(
        self,
    ) -> None:
        response = self._create_use_case_response(rr.incorrect_password)
        form = self._create_form()
        self.presenter.render_response(response, form)
        assert (
            self.translator.gettext("The password is incorrect.")
            in form.current_password_field.errors
        )

    def _create_form(self) -> RequestEmailAddressChangeFormImpl:
        return RequestEmailAddressChangeFormImpl.from_values("test@test.test", "pw1234")

    def _create_use_case_response(
        self,
        rejection_reason: use_case.Response.RejectionReason | None,
    ) -> use_case.Response:
        return use_case.Response(rejection_reason=rejection_reason)
