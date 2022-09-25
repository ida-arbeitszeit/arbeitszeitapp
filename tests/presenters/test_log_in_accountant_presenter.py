from unittest import TestCase
from uuid import uuid4

from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase as UseCase
from arbeitszeit_web.presenters.log_in_accountant_presenter import (
    LogInAccountantPresenter,
)
from arbeitszeit_web.session import UserRole
from tests.forms import LoginForm
from tests.session import FakeSession

from .dependency_injection import get_dependency_injector
from .url_index import UrlIndexTestImpl


class PresenterTester(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(LogInAccountantPresenter)
        self.session = self.injector.get(FakeSession)
        self.url_index = self.injector.get(UrlIndexTestImpl)

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

    def test_that_user_is_logged_in_with_their_specified_email_address(self) -> None:
        expected_email = "test@mail.test"
        response = self._create_success_response()
        self.presenter.present_login_process(
            response=response, form=self._create_form(email=expected_email)
        )
        login = self.session.get_most_recent_login()
        assert login
        self.assertEqual(
            login.email,
            expected_email,
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

    def _create_success_response(self) -> UseCase.Response:
        return UseCase.Response(user_id=uuid4())

    def _create_failure_response(self) -> UseCase.Response:
        return UseCase.Response(user_id=None)

    def _create_form(self, remember: bool = False, email: str = "a@b.c") -> LoginForm:
        return LoginForm(remember_value=remember, email_value=email)
