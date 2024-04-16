from typing import Optional
from uuid import UUID, uuid4

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit_web.api.presenters.interfaces import JsonBoolean, JsonObject
from arbeitszeit_web.api.presenters.login_company_api_presenter import (
    LoginCompanyApiPresenter,
)
from arbeitszeit_web.api.response_errors import Unauthorized
from arbeitszeit_web.session import UserRole
from tests.api.presenters.base_test_case import BaseTestCase
from tests.session import FakeSession


class TestViewModelCreation(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LoginCompanyApiPresenter)
        self.session = self.injector.get(FakeSession)

    def test_unauthorized_raises_if_wrong_mail_adress_was_given(self) -> None:
        response = self.create_failure_response(
            rejection_reason=LogInCompanyUseCase.RejectionReason.invalid_email_address,
        )
        with self.assertRaises(Unauthorized) as err:
            self.presenter.create_view_model(response)
        self.assertEqual(err.exception.message, "Unknown email address.")

    def test_unauthorized_raises_if_wrong_password_was_given(self) -> None:
        response = self.create_failure_response(
            rejection_reason=LogInCompanyUseCase.RejectionReason.invalid_password,
        )
        with self.assertRaises(Unauthorized) as err:
            self.presenter.create_view_model(response)
        self.assertEqual(err.exception.message, "Invalid password.")

    def test_true_is_shown_when_user_got_logged_in(self) -> None:
        response = self.create_success_response()
        view_model = self.presenter.create_view_model(response)
        self.assertEqual(view_model.success, True)

    def test_that_user_is_logged_into_session_on_success(self) -> None:
        response = self.create_success_response()
        self.presenter.create_view_model(response)
        self.assertTrue(self.session.is_logged_in())

    def test_that_user_in_not_logged_in_on_failure(self) -> None:
        response = self.create_failure_response()
        with self.assertRaises(Unauthorized):
            self.presenter.create_view_model(response)
        self.assertFalse(self.session.is_logged_in())

    def test_that_user_is_logged_in_with_correct_user_id(self) -> None:
        expected_id = uuid4()
        response = self.create_success_response(user_id=expected_id)
        self.presenter.create_view_model(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(
            login_attempt.user_id,
            expected_id,
        )

    def test_that_remember_field_is_false(self) -> None:
        response = self.create_success_response()
        self.presenter.create_view_model(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertFalse(login_attempt.is_remember)

    def test_that_user_gets_logged_in_as_company(self) -> None:
        response = self.create_success_response()
        self.presenter.create_view_model(response)
        login_attempt = self.session.get_most_recent_login()
        assert login_attempt
        self.assertEqual(
            login_attempt.user_role,
            UserRole.company,
        )

    def create_failure_response(
        self, rejection_reason: Optional[LogInCompanyUseCase.RejectionReason] = None
    ) -> LogInCompanyUseCase.Response:
        if rejection_reason is None:
            rejection_reason == LogInCompanyUseCase.RejectionReason.invalid_email_address
        return LogInCompanyUseCase.Response(
            is_logged_in=False,
            rejection_reason=rejection_reason,
            email_address="some@mail.org",
            user_id=None,
        )

    def create_success_response(
        self, email: Optional[str] = None, user_id: Optional[UUID] = None
    ) -> LogInCompanyUseCase.Response:
        if email is None:
            email = "test@test.test"
        if user_id is None:
            user_id = uuid4()
        return LogInCompanyUseCase.Response(
            is_logged_in=True,
            rejection_reason=None,
            email_address=email,
            user_id=user_id,
        )


class TestSchema(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(LoginCompanyApiPresenter)

    def test_schema_top_level(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        assert schema.name == "LoginCompanyResponse"

    def test_schema_top_level_members(self) -> None:
        schema = self.presenter.get_schema()
        assert isinstance(schema, JsonObject)
        assert isinstance(schema.members["success"], JsonBoolean)
