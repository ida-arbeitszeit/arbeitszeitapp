from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.log_in_member import LogInMemberUseCase
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.log_in_member_presenter import LogInMemberPresenter
from tests.forms import LoginForm
from tests.www.base_test_case import BaseTestCase


class PresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LogInMemberPresenter)
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
        self.assertTrue(self.form.email_field().errors)

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
            self.form.email_field().errors,
        )

    def test_that_no_password_errors_are_rendered_when_email_address_is_unknown(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.unknown_email_address
        )
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(self.form.password_field().errors)

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
            self.form.password_field().errors,
        )

    def test_that_no_email_error_is_rendered_if_password_was_invalid(
        self,
    ) -> None:
        response = self.create_failure_response(
            reason=LogInMemberUseCase.RejectionReason.invalid_password
        )
        self.presenter.present_login_process(response, self.form)
        self.assertFalse(
            self.form.email_field().errors,
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

    def test_that_user_is_logged_in_with_correct_user_id(self) -> None:
        expected_id = uuid4()
        response = self.create_success_response(user_id=expected_id)
        self.presenter.present_login_process(response, self.form)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(
            login_attempt.user_id,
            expected_id,
        )

    def test_that_remember_field_from_form_is_respected(self) -> None:
        for expected_remember_state in [True, False]:
            with self.subTest():
                self.form = LoginForm(remember_value=expected_remember_state)
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
        self, email: Optional[str] = None, user_id: Optional[UUID] = None
    ) -> LogInMemberUseCase.Response:
        if email is None:
            email = "test@test.test"
        if user_id is None:
            user_id = uuid4()
        return LogInMemberUseCase.Response(
            is_logged_in=True,
            rejection_reason=None,
            email=email,
            user_id=user_id,
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
            user_id=None,
        )
