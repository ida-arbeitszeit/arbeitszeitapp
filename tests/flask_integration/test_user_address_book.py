from unittest import TestCase
from uuid import uuid4

from arbeitszeit_flask.database.repositories import UserAddressBookImpl
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import get_dependency_injector


class UserAddressBookTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.repository = self.injector.get(UserAddressBookImpl)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)

    def test_get_none_when_no_users_are_registered(self) -> None:
        self.assertIsNone(self.repository.get_user_email_address(uuid4()))

    def test_that_associated_email_for_member_is_returned(self) -> None:
        member = self.member_generator.create_member()
        self.assertEqual(
            member.email,
            self.repository.get_user_email_address(member.id),
        )

    def test_that_associated_email_for_company_is_returned(self) -> None:
        company = self.company_generator.create_company()
        self.assertEqual(
            company.email,
            self.repository.get_user_email_address(company.id),
        )
