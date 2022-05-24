from arbeitszeit_flask.database.repositories import AccountantRepository

from .flask import FlaskTestCase


class CreateAccountantTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(AccountantRepository)
        self.expected_email = "test@test.test"
        self.expected_name = "test name"
        self.expected_password = "test password"
        self.uuid = self.repository.create_accountant(
            email=self.expected_email,
            name=self.expected_name,
            password=self.expected_password,
        )

    def test_repository_stores_email_address_correctly(self) -> None:
        accountant = self.repository.get_by_id(self.uuid)
        assert accountant
        self.assertEqual(accountant.email_address, self.expected_email)

    def test_repository_stores_name_correctly(self) -> None:
        accountant = self.repository.get_by_id(self.uuid)
        assert accountant
        self.assertEqual(accountant.name, self.expected_name)

    def test_can_validate_password_specified_at_creation(self) -> None:
        self.assertIsNotNone(
            self.repository.validate_credentials(
                self.expected_email, self.expected_password
            )
        )

    def test_repository_has_user_with_email_after_creation(self) -> None:
        self.assertTrue(self.repository.has_accountant_with_email(self.expected_email))

    def test_repository_doesnt_have_user_with_other_email(self) -> None:
        self.assertFalse(
            self.repository.has_accountant_with_email(email="different@email.org")
        )

    def test_can_retrieve_accountant_orm_by_mail(self) -> None:
        self.assertTrue(self.repository.get_accountant_orm_by_mail(self.expected_email))

    def test_return_no_accountant_with_specified_email_exists(self) -> None:
        self.assertIsNone(
            self.repository.get_accountant_orm_by_mail("different@email.org")
        )


class ValidationTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(AccountantRepository)
        self.expected_email = "test@test.test"
        self.expected_password = "test password"
        self.uuid = self.repository.create_accountant(
            email=self.expected_email,
            name="test name",
            password=self.expected_password,
        )

    def test_cannot_validate_user_that_was_not_created(self) -> None:
        self.assertIsNone(
            self.repository.validate_credentials("non.existing@email.org", "pw123")
        )

    def test_cannot_validate_user_with_different_password(self) -> None:
        self.assertIsNone(
            self.repository.validate_credentials(self.expected_email, "pw123")
        )
