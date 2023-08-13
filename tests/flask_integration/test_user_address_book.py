from uuid import uuid4

from arbeitszeit_flask.database.repositories import UserAddressBookImpl
from tests.data_generators import AccountantGenerator, CompanyGenerator, MemberGenerator

from .flask import FlaskTestCase


class UserAddressBookTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.repository = self.injector.get(UserAddressBookImpl)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def test_get_none_when_no_users_are_registered(self) -> None:
        self.assertIsNone(self.repository.get_user_email_address(uuid4()))

    def test_that_associated_email_for_member_is_returned(self) -> None:
        expected_email = "test@test.test"
        member = self.member_generator.create_member(email=expected_email)
        self.assertEqual(
            expected_email,
            self.repository.get_user_email_address(member),
        )

    def test_that_associated_email_for_company_is_returned(self) -> None:
        company = self.company_generator.create_company_record()
        self.assertEqual(
            company.email,
            self.repository.get_user_email_address(company.id),
        )

    def test_that_associated_email_for_accountant_is_returned(self) -> None:
        expected_email = "test@test.test"
        accountant = self.accountant_generator.create_accountant(
            email_address=expected_email
        )
        self.assertEqual(
            expected_email,
            self.repository.get_user_email_address(accountant),
        )
