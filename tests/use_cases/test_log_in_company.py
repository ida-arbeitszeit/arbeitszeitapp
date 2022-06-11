from unittest import TestCase

from arbeitszeit.use_cases.log_in_company import LogInCompanyUseCase
from arbeitszeit.use_cases.register_company import RegisterCompany

from .dependency_injection import get_dependency_injector


class CorrectCredentialsTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(LogInCompanyUseCase)
        self.register_use_case = self.injector.get(RegisterCompany)
        self.email = "test user email"
        self.password = "test user password"
        self.create_company(email=self.email, password=self.password)

    def test_can_log_in_with_correct_credentials(self) -> None:
        response = self.try_log_in()
        self.assertTrue(response.is_logged_in)

    def test_that_no_rejection_reason_is_given(self) -> None:
        response = self.try_log_in()
        self.assertIsNone(response.rejection_reason)

    def test_email_is_propagated_to_response(self) -> None:
        response = self.try_log_in()
        self.assertEqual(response.email_address, self.email)

    def try_log_in(self) -> LogInCompanyUseCase.Response:
        request = LogInCompanyUseCase.Request(
            email_address=self.email, password=self.password
        )
        return self.use_case.log_in_company(request)

    def create_company(self, email: str, password: str) -> None:
        name = "test company"
        response = self.register_use_case(
            request=RegisterCompany.Request(
                email=email,
                name=name,
                password=password,
            )
        )
        self.assertFalse(response.is_rejected)


class WrongPasswordTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(LogInCompanyUseCase)
        self.register_use_case = self.injector.get(RegisterCompany)
        self.email = "test@test.test"
        self.register_use_case(
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
            LogInCompanyUseCase.RejectionReason.invalid_password,
        )

    def test_that_email_is_not_propagated_to_response(self) -> None:
        response = self.try_log_in()
        self.assertIsNone(response.email_address)

    def try_log_in(self) -> LogInCompanyUseCase.Response:
        request = LogInCompanyUseCase.Request(
            email_address=self.email, password="incorrect password"
        )
        return self.use_case.log_in_company(request)


class WrongEmailTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.use_case = self.injector.get(LogInCompanyUseCase)
        self.register_use_case = self.injector.get(RegisterCompany)

    def test_cannot_logged_in_without_company_being_registered(self) -> None:
        response = self.try_log_in()
        self.assertFalse(response.is_logged_in)

    def test_invalid_email_reason_is_given(self) -> None:
        response = self.try_log_in()
        self.assertEqual(
            response.rejection_reason,
            LogInCompanyUseCase.RejectionReason.invalid_email_address,
        )

    def try_log_in(self) -> LogInCompanyUseCase.Response:
        request = LogInCompanyUseCase.Request(
            email_address="test@test.test", password="testpassword"
        )
        return self.use_case.log_in_company(request)
