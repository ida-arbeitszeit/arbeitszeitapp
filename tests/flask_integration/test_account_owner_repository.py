from arbeitszeit.entities import AccountTypes, SocialAccounting
from arbeitszeit_flask.database.repositories import AccountOwnerRepository
from tests.data_generators import AccountGenerator, CompanyGenerator, MemberGenerator

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator = self.injector.get(AccountGenerator)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.repository = self.injector.get(AccountOwnerRepository)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_can_retrieve_owner_of_member_accounts(self) -> None:
        account = self.account_generator.create_account(AccountTypes.member)
        member = self.member_generator.create_member(account=account)
        assert self.repository.get_account_owner(account) == member

    def test_can_retrieve_owner_of_company_accounts(self) -> None:
        account = self.account_generator.create_account(AccountTypes.a)
        company = self.company_generator.create_company(labour_account=account)
        assert self.repository.get_account_owner(account) == company

    def test_can_get_owner_of_public_account(self) -> None:
        assert (
            self.repository.get_account_owner(self.social_accounting.account)
            == self.social_accounting
        )
