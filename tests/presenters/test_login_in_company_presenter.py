from __future__ import annotations

from unittest import TestCase

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit_web.presenters.log_in_company_presenter import LogInCompanyPresenter
from tests.session import FakeSession
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector
from .forms import LoginForm
from .url_index import CompanyUrlIndexImpl


class PresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.session = self.injector.get(FakeSession)
        self.company_url_index = self.injector.get(CompanyUrlIndexImpl)
        self.presenter = self.injector.get(LogInCompanyPresenter)
        self.translator = self.injector.get(FakeTranslator)
        self.form = LoginForm()

    def test_that_user_is_logged_into_session_on_successful_login(self) -> None:
        response = self.create_success_response()
        self.present_login_process(response)
        self.assertTrue(self.session.is_logged_in())

    def test_that_user_is_not_logged_into_session_when_login_was_rejected(self) -> None:
        response = self.create_failure_response()
        self.present_login_process(response)
        self.assertFalse(self.session.is_logged_in())

    def test_that_user_is_logged_in_as_company(self) -> None:
        response = self.create_success_response()
        self.present_login_process(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(login_attempt.user_role, FakeSession.UserRole.company)

    def test_that_email_is_correct_with_example_email(self) -> None:
        expected_email = "karl@cp.org"
        response = self.create_success_response(email=expected_email)
        self.present_login_process(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(login_attempt.email, expected_email)

    def test_that_email_is_correct_with_another_example_email(self) -> None:
        expected_email = "friedrich@cp.org"
        response = self.create_success_response(email=expected_email)
        self.present_login_process(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(login_attempt.email, expected_email)

    def test_that_redirect_url_is_dashboard_if_none_is_set_in_session(self) -> None:
        response = self.create_success_response()
        view_model = self.present_login_process(response)
        self.assertEqual(
            view_model.redirect_url,
            self.company_url_index.get_company_dashboard_url(),
        )

    def test_do_not_get_redirected_if_login_fails(self) -> None:
        response = self.create_failure_response()
        view_model = self.present_login_process(response)
        self.assertIsNone(view_model.redirect_url)

    def test_that_an_error_is_rendered_to_password_field_if_password_is_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_password
        )
        self.present_login_process(response)
        self.assertTrue(self.form.password_errors)

    def test_that_no_error_is_rendered_to_password_field_if_login_was_successful(
        self,
    ) -> None:
        response = self.create_success_response()
        self.present_login_process(response)
        self.assertFalse(self.form.password_errors)

    def test_that_no_error_is_rendered_to_password_field_if_rejection_reason_is_invalid_email_address(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_email_address
        )
        self.present_login_process(response)
        self.assertFalse(self.form.password_errors)

    def test_correct_error_message_for_incorrect_password(self) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_password
        )
        self.present_login_process(response)
        self.assertEqual(
            self.form.password_errors[-1],
            self.translator.gettext("Password is incorrect"),
        )

    def test_that_error_message_is_rendered_to_email_field_if_email_is_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_email_address
        )
        self.present_login_process(response)
        self.assertTrue(self.form.email_errors)

    def test_that_no_error_message_is_rendered_to_email_field_if_login_was_successful(
        self,
    ) -> None:
        response = self.create_success_response()
        self.present_login_process(response)
        self.assertFalse(self.form.email_errors)

    def test_that_no_error_message_is_rendered_to_email_field_if_password_is_incorrect(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_password
        )
        self.present_login_process(response)
        self.assertFalse(self.form.email_errors)

    def test_correct_error_message_for_incorrect_email_address(self) -> None:
        response = self.create_failure_response(
            reason=LogInCompanyUseCase.RejectionReason.invalid_email_address
        )
        self.present_login_process(response)
        self.assertEqual(
            self.form.email_errors[-1],
            self.translator.gettext(
                "Email address is not correct. Are you already signed up?"
            ),
        )

    def test_that_user_is_redirected_to_next_url_when_login_was_successful(
        self,
    ) -> None:
        expected_url = "test url"
        self.session.set_next_url(expected_url)
        response = self.create_success_response()
        view_model = self.present_login_process(response)
        self.assertEqual(view_model.redirect_url, expected_url)

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

    def present_login_process(
        self, response: LogInCompanyUseCase.Response
    ) -> LogInCompanyPresenter.ViewModel:
        return self.presenter.present_login_process(response, form=self.form)

    def create_success_response(
        self, email: str = "test@test.test"
    ) -> LogInCompanyUseCase.Response:
        return LogInCompanyUseCase.Response(
            is_logged_in=True,
            rejection_reason=None,
            email_address=email,
        )

    def create_failure_response(
        self,
        reason: LogInCompanyUseCase.RejectionReason = LogInCompanyUseCase.RejectionReason.invalid_password,
    ) -> LogInCompanyUseCase.Response:
        return LogInCompanyUseCase.Response(
            is_logged_in=False,
            rejection_reason=reason,
            email_address="test@test.test",
        )
