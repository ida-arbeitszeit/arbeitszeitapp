from uuid import UUID

from arbeitszeit.interactors.log_in_company import LogInCompanyInteractor
from arbeitszeit.interactors.register_company import RegisterCompany

from .base_test_case import BaseTestCase


class CorrectCredentialsTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(LogInCompanyInteractor)
        self.register_interactor = self.injector.get(RegisterCompany)
        self.email = "test user email"
        self.password = "test user password"
        self.company = self.create_company(email=self.email, password=self.password)

    def test_can_log_in_with_correct_credentials(self) -> None:
        response = self.try_log_in()
        self.assertTrue(response.is_logged_in)

    def test_can_log_in_with_correct_credentials_but_exta_whitespace(
        self,
    ) -> None:
        altered_email = " " + self.email + " "
        request = LogInCompanyInteractor.Request(
            email_address=altered_email, password=self.password
        )
        response = self.interactor.log_in_company(request)
        self.assertTrue(response.is_logged_in)

    def test_that_no_rejection_reason_is_given(self) -> None:
        response = self.try_log_in()
        self.assertIsNone(response.rejection_reason)

    def test_that_user_id_in_response_is_company_id(self) -> None:
        response = self.try_log_in()
        assert response.user_id == self.company

    def test_email_is_propagated_to_response(self) -> None:
        response = self.try_log_in()
        self.assertEqual(response.email_address, self.email)

    def try_log_in(self) -> LogInCompanyInteractor.Response:
        request = LogInCompanyInteractor.Request(
            email_address=self.email, password=self.password
        )
        return self.interactor.log_in_company(request)

    def create_company(self, email: str, password: str) -> UUID:
        return self.company_generator.create_company(email=email, password=password)


class WrongPasswordTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(LogInCompanyInteractor)
        self.register_interactor = self.injector.get(RegisterCompany)
        self.email = "test@test.test"
        self.register_interactor.register_company(
            request=RegisterCompany.Request(
                email=self.email,
                name="test company",
                password="correct password",
            )
        )

    def test_cannot_log_in_with_incorrect_password(self) -> None:
        response = self.try_log_in()
        self.assertFalse(response.is_logged_in)

    def test_that_rejection_reason_is_wrong_password(self) -> None:
        response = self.try_log_in()
        self.assertEqual(
            response.rejection_reason,
            LogInCompanyInteractor.RejectionReason.invalid_password,
        )

    def test_that_email_is_not_propagated_to_response(self) -> None:
        response = self.try_log_in()
        self.assertIsNone(response.email_address)

    def test_that_user_id_in_response_is_none(self) -> None:
        response = self.try_log_in()
        assert response.user_id is None

    def try_log_in(self) -> LogInCompanyInteractor.Response:
        request = LogInCompanyInteractor.Request(
            email_address=self.email, password="incorrect password"
        )
        return self.interactor.log_in_company(request)


class WrongEmailTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.interactor = self.injector.get(LogInCompanyInteractor)
        self.register_interactor = self.injector.get(RegisterCompany)

    def test_cannot_logged_in_without_company_being_registered(self) -> None:
        response = self.try_log_in()
        self.assertFalse(response.is_logged_in)

    def test_invalid_email_reason_is_given(self) -> None:
        response = self.try_log_in()
        self.assertEqual(
            response.rejection_reason,
            LogInCompanyInteractor.RejectionReason.invalid_email_address,
        )

    def try_log_in(self) -> LogInCompanyInteractor.Response:
        request = LogInCompanyInteractor.Request(
            email_address="test@test.test", password="testpassword"
        )
        return self.interactor.log_in_company(request)
