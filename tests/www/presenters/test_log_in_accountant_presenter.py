from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.interactors.log_in_accountant import (
    LogInAccountantInteractor as Interactor,
)
from arbeitszeit_web.session import UserRole
from arbeitszeit_web.www.presenters.log_in_accountant_presenter import (
    LogInAccountantPresenter,
)
from tests.forms import LoginForm
from tests.www.base_test_case import BaseTestCase


class PresenterTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LogInAccountantPresenter)

    def test_user_gets_redirected_when_login_was_successful(self) -> None:
        response = self._create_success_response()
        view_model = self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        self.assertIsNotNone(view_model.redirect_url)

    def test_user_does_not_get_redirected_when_login_failed(self) -> None:
        response = self._create_failure_response()
        view_model = self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        self.assertIsNone(view_model.redirect_url)

    def test_successful_login_attempt_logs_user_into_session(self) -> None:
        response = self._create_success_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        login = self.session.get_most_recent_login()
        self.assertIsNotNone(login)

    def test_failed_login_attempt_does_not_log_user_into_session(self) -> None:
        response = self._create_failure_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        login = self.session.get_most_recent_login()
        self.assertIsNone(login)

    def test_that_user_is_logged_in_as_accountant(self) -> None:
        response = self._create_success_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        login = self.session.get_most_recent_login()
        assert login
        self.assertEqual(
            login.user_role,
            UserRole.accountant,
        )

    def test_that_user_is_logged_in_with_correct_user_id(self) -> None:
        expected_id = uuid4()
        response = self._create_success_response(user_id=expected_id)
        self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        login = self.session.get_most_recent_login()
        assert login
        self.assertEqual(
            login.user_id,
            expected_id,
        )

    def test_that_user_is_remembered_if_form_requests_so(self) -> None:
        response = self._create_success_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form(remember=True)
        )
        login = self.session.get_most_recent_login()
        assert login
        self.assertTrue(login.is_remember)

    def test_that_user_is_not_remembered_if_form_requests_so(self) -> None:
        response = self._create_success_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form(remember=False)
        )
        login = self.session.get_most_recent_login()
        assert login
        self.assertFalse(login.is_remember)

    def test_that_user_is_redirected_to_next_url_when_login_was_successful(
        self,
    ) -> None:
        expected_url = "/a/b/c"
        self.session.set_next_url(expected_url)
        response = self._create_success_response()
        view_model = self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        self.assertEqual(view_model.redirect_url, expected_url)

    def test_that_user_is_redirected_to_dashboard_if_no_nexturl_is_set(
        self,
    ) -> None:
        response = self._create_success_response()
        view_model = self.presenter.present_login_process(
            response=response, form=self._create_form()
        )
        self.assertEqual(
            view_model.redirect_url, self.url_index.get_accountant_dashboard_url()
        )

    def test_that_password_error_is_shown_when_password_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.wrong_password
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertTrue(form.password_field().errors)

    def test_that_no_email_error_is_shown_when_password_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.wrong_password
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertFalse(form.email_field().errors)

    def test_that_proper_error_message_is_shown_when_password_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.wrong_password
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertIn(
            self.translator.gettext("Incorrect password"),
            form.password_field().errors,
        )

    def test_that_no_password_error_is_shown_when_email_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.email_is_not_accountant
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertFalse(form.password_field().errors)

    def test_that_some_email_error_is_shown_when_email_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.email_is_not_accountant
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertTrue(form.email_field().errors)

    def test_that_proper_error_message_is_shown_when_email_is_wrong(
        self,
    ) -> None:
        response = self._create_failure_response(
            reason=Interactor.RejectionReason.email_is_not_accountant
        )
        form = self._create_form()
        self.presenter.present_login_process(response=response, form=form)
        self.assertIn(
            self.translator.gettext(
                "This email address does not belong to a registered accountant"
            ),
            form.email_field().errors,
        )

    def _create_success_response(
        self, user_id: Optional[UUID] = None
    ) -> Interactor.Response:
        if user_id is None:
            user_id = uuid4()
        return Interactor.Response(user_id=user_id)

    def _create_failure_response(
        self, reason: Optional[Interactor.RejectionReason] = None
    ) -> Interactor.Response:
        if reason is None:
            reason = Interactor.RejectionReason.wrong_password
        return Interactor.Response(user_id=None, rejection_reason=reason)

    def _create_form(self, remember: bool = False, email: str = "a@b.c") -> LoginForm:
        return LoginForm(remember_value=remember, email_value=email)
