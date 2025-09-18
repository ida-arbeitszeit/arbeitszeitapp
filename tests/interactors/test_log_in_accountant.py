from arbeitszeit.interactors.log_in_accountant import LogInAccountantInteractor

from .base_test_case import BaseTestCase


class InteractorTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.log_in_interactor = self.injector.get(LogInAccountantInteractor)

    def test_that_user_can_log_in_with_same_password_they_registered_with(self) -> None:
        email = "test@test.test"
        expected_password = "1234password"
        self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=email, password=expected_password
            )
        )
        self.assertIsNotNone(response.user_id)

    def test_that_user_can_log_in_with_whitespace_surrounding_email(self) -> None:
        email = "test@test.test"
        altered_email = " " + email + " "
        expected_password = "1234password"
        self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=altered_email, password=expected_password
            )
        )
        self.assertIsNotNone(response.user_id)

    def test_no_rejection_reason_is_given_on_successful_login(self) -> None:
        email = "test@test.test"
        expected_password = "1234password"
        self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=email, password=expected_password
            )
        )
        self.assertIsNone(response.rejection_reason)

    def test_that_proper_rejection_reason_is_given_if_there_is_no_accountant_with_given_email(
        self,
    ) -> None:
        self.accountant_generator.create_accountant(
            email_address="test@test.test",
            password="password",
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address="other@test.test", password="password"
            )
        )
        self.assertEqual(
            response.rejection_reason,
            LogInAccountantInteractor.RejectionReason.email_is_not_accountant,
        )

    def test_that_user_cannot_log_in_with_different_password_as_they_registered_with(
        self,
    ) -> None:
        email = "test@test.test"
        self.accountant_generator.create_accountant(
            email_address=email,
            password="original password",
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=email, password="different password"
            )
        )
        self.assertIsNone(
            response.user_id,
        )

    def test_proper_rejection_reason_is_given_when_password_is_wrong(
        self,
    ) -> None:
        email = "test@test.test"
        self.accountant_generator.create_accountant(
            email_address=email,
            password="original password",
        )
        response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=email, password="different password"
            )
        )
        self.assertEqual(
            response.rejection_reason,
            LogInAccountantInteractor.RejectionReason.wrong_password,
        )

    def test_that_user_is_logged_in_as_same_user_as_they_registered(self) -> None:
        email = "test@test.test"
        expected_password = "1234password"
        accountant_id = self.accountant_generator.create_accountant(
            email_address=email, password=expected_password
        )
        login_response = self.log_in_interactor.log_in_accountant(
            request=LogInAccountantInteractor.Request(
                email_address=email, password=expected_password
            )
        )
        self.assertEqual(login_response.user_id, accountant_id)
