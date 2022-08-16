from typing import Optional
from unittest import TestCase

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.presenters.log_in_member_presenter import LogInMemberPresenter
from arbeitszeit_web.session import UserRole
from tests.session import FakeSession
from tests.translator import FakeTranslator

from ..forms import LoginForm
from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(LogInMemberPresenter)
        self.session = self.injector.get(FakeSession)
        self.translator = self.injector.get(FakeTranslator)
        self.url_index = self.injector.get(UrlIndexTestImpl)
        self.form = LoginForm()

    def test_that_user_is_logged_into_session_on_success(self) -> None:
        response = self.create_success_response()
        self.presenter.present_login_process(response, self.form)
        self.assertTrue(self.session.is_logged_in())

    def test_that_user_in_not_logged_in_on_failure(self) -> None:
        response = self.create_failure_response()
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(self.session.is_logged_in())

    def test_that_email_error_is_added_to_form_when_email_address_was_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.unknown_email_address
        )
        self.presenter.present_login_process(response, self.form)
        self.assertTrue(self.form.email_errors)

    def test_that_correct_error_message_is_added_to_form(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.unknown_email_address
        )
        self.presenter.present_login_process(response, self.form)
        self.assertIn(
            self.translator.gettext(
                "Email address incorrect. Are you already registered as a member?"
            ),
            self.form.email_errors,
        )

    def test_that_no_password_errors_are_rendered_when_email_address_is_unknown(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.unknown_email_address
        )
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(self.form.password_errors)

    def test_that_no_errors_are_rendered_to_form_if_login_was_successful(
        self,
    ) -> None:
        response = self.create_success_response()
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(self.form.has_errors())

    def test_that_correct_error_message_is_added_to_password_field_if_password_was_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.invalid_password
        )
        self.presenter.present_login_process(response, self.form)
        self.assertIn(
            self.translator.gettext("Incorrect password"),
            self.form.password_errors,
        )

    def test_that_no_email_error_is_rendered_if_password_was_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.invalid_password
        )
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(
            self.form.email_errors,
        )

    def test_that_redirect_url_is_set_to_dashboard_if_no_next_url_can_be_retrieved_from_session(
        self,
    ) -> None:
        response = self.create_success_response()
        view_model = self.presenter.present_login_process(response, self.form)
        self.assertEqual(
            view_model.redirect_url,
            self.url_index.get_member_dashboard_url(),
        )

    def test_that_no_redirect_url_is_set_when_login_failed(self) -> None:
        response = self.create_failure_response()
        view_model = self.presenter.present_login_process(response, self.form)
        self.assertIsNone(
            view_model.redirect_url,
        )

    def test_that_redirect_url_is_set_to_next_url_from_session_if_it_is_set(
        self,
    ) -> None:
        expected_url = "expected url"
        self.session.set_next_url(expected_url)
        response = self.create_success_response()
        view_model = self.presenter.present_login_process(response, self.form)
        self.assertEqual(
            view_model.redirect_url,
            expected_url,
        )

    def test_that_user_is_logged_in_with_correct_email_address(self) -> None:
        emails = ["test1@test.test", "test2@test.test"]
        for expected_email in emails:
            with self.subTest():
                response = self.create_success_response(email=expected_email)
                self.presenter.present_login_process(response, self.form)
                login_attempt = self.session.get_most_recent_login()
                assert login_attempt
                self.assertEqual(
                    login_attempt.email,
                    expected_email,
                )

    def test_that_remember_field_from_form_is_respected(self) -> None:
        for expected_remember_state in [True, False]:
            with self.subTest():
                self.form.set_remember_field(expected_remember_state)
                response = self.create_success_response()
                self.presenter.present_login_process(response, self.form)
                login_attempt = self.session.get_most_recent_login()
                assert login_attempt
                self.assertEqual(
                    login_attempt.is_remember,
                    expected_remember_state,
                )

    def test_that_user_gets_logged_in_as_member(self) -> None:
        response = self.create_success_response()
        self.presenter.present_login_process(response, self.form)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(
            login_attempt.user_role,
            UserRole.member,
        )

    def create_success_response(
        self, email: Optional[str] = None
    ) -> LogInMemberUseCase.Response:
        if email is None:
            email = "test@test.test"
        return LogInMemberUseCase.Response(
            is_logged_in=True,
            rejection_reason=None,
            email=email,
        )

    def create_failure_response(
        self, reason: Optional[LogInMemberUseCase.RejectionReason] = None
    ) -> LogInMemberUseCase.Response:
        if reason is None:
            reason = LogInMemberUseCase.RejectionReason.invalid_password
        return LogInMemberUseCase.Response(
            is_logged_in=False,
            rejection_reason=reason,
            email="test@test.test",
        )
