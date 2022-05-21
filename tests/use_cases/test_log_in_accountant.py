from unittest import TestCase

from arbeitszeit.use_cases.log_in_accountant import LogInAccountantUseCase
from tests.data_generators import AccountantGenerator

from .dependency_injection import get_dependency_injector


class UseCaseTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.log_in_use_case = self.injector.get(LogInAccountantUseCase)
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def test_that_user_can_log_in_with_same_password_they_registered_with(self) -> None:
        email = "test@test.test"
        expected_password = "1234password"
        self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        response = self.log_in_use_case.log_in_accountant(
            request=LogInAccountantUseCase.Request(
                email_address=email, password=expected_password
            )
        )
        self.assertIsNotNone(response.user_id)

    def test_that_user_cannot_log_in_with_different_password_as_they_registered_with(
        self,
    ) -> None:
        email = "test@test.test"
        self.accountant_generator.create_accountant(
            email_address=email,
            password="original password",
        )
        response = self.log_in_use_case.log_in_accountant(
            request=LogInAccountantUseCase.Request(
                email_address=email, password="different password"
            )
        )
        self.assertIsNone(
            response.user_id,
        )

    def test_that_user_is_logged_in_as_same_user_as_they_registered(self) -> None:
        email = "test@test.test"
        expected_password = "1234password"
        accountant_id = self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        login_response = self.log_in_use_case.log_in_accountant(
            request=LogInAccountantUseCase.Request(
                email_address=email, password=expected_password
            )
        )
        self.assertEqual(login_response.user_id, accountant_id)
