from uuid import uuid4

from arbeitszeit.entities import SocialAccounting
from arbeitszeit_flask.database.repositories import (
    AccountRepository,
    CompanyRepository,
    MemberRepository,
)
from tests.data_generators import (
    AccountGenerator,
    CompanyGenerator,
    MemberGenerator,
    TransactionGenerator,
)

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator: AccountGenerator = self.injector.get(AccountGenerator)
        self.transaction_generator: TransactionGenerator = self.injector.get(
            TransactionGenerator
        )
        self.repository: AccountRepository = self.injector.get(AccountRepository)
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.member_repository = self.injector.get(MemberRepository)
        self.company_repository = self.injector.get(CompanyRepository)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_the_account_balance_of_newly_created_accounts_is_0(self) -> None:
        account = self.account_generator.create_account()
        assert self.repository.get_account_balance(account.id) == 0

    def test_the_account_balance_of_accounts_equals_negative_sum_of_sent_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=10
        )
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=2.5
        )
        assert self.repository.get_account_balance(account.id) == -12.5

    def test_the_account_balance_of_accounts_equals_sum_of_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_received=10
        )
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_received=2.5
        )
        assert self.repository.get_account_balance(account.id) == 12.5

    def test_the_account_balance_of_accounts_reflects_sent_and_received_transactions(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id, amount_sent=10, amount_received=0
        )
        self.transaction_generator.create_transaction(
            receiving_account=account.id, amount_sent=0, amount_received=4
        )
        assert self.repository.get_account_balance(account.id) == -6

    def test_the_account_balance_is_zero_when_sending_and_receiving_account_of_transaction_are_the_same(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(
            sending_account=account.id,
            receiving_account=account.id,
            amount_sent=10,
            amount_received=10,
        )
        assert self.repository.get_account_balance(account.id) == 0

    def test_that_a_priori_there_is_only_one_account_for_social_accounting(
        self,
    ) -> None:
        account = self.repository.get_accounts().first()
        assert len(self.repository.get_accounts()) == 1
        assert list(self.repository.get_accounts().joined_with_owner()) == [
            (account, self.social_accounting)
        ]

    def test_there_are_accounts_to_be_queried_when_one_was_created(self) -> None:
        self.account_generator.create_account()
        assert self.repository.get_accounts()

    def test_only_include_relevant_account_when_filtering_by_id(self) -> None:
        random_id = uuid4()
        actual_id = self.account_generator.create_account().id
        assert not self.repository.get_accounts().with_id(random_id)
        assert self.repository.get_accounts().with_id(actual_id)

    def test_that_account_joined_with_owner_yields_original_member(self) -> None:
        member_id = self.member_generator.create_member()
        member = self.member_repository.get_members().with_id(member_id).first()
        assert member
        result = (
            self.repository.get_accounts()
            .with_id(member.account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert member == result[1]

    def test_that_p_account_joined_with_owner_yields_original_company(self) -> None:
        self.company_generator.create_company()
        company = self.company_repository.get_companies().first()
        assert company
        result = (
            self.repository.get_accounts()
            .with_id(company.means_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_r_account_joined_with_owner_yields_original_company(self) -> None:
        self.company_generator.create_company()
        company = self.company_repository.get_companies().first()
        assert company
        result = (
            self.repository.get_accounts()
            .with_id(company.raw_material_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_a_account_joined_with_owner_yields_original_company(self) -> None:
        self.company_generator.create_company()
        company = self.company_repository.get_companies().first()
        assert company
        result = (
            self.repository.get_accounts()
            .with_id(company.work_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_prd_account_joined_with_owner_yields_original_company(self) -> None:
        self.company_generator.create_company()
        company = self.company_repository.get_companies().first()
        assert company
        result = (
            self.repository.get_accounts()
            .with_id(company.product_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_account_from_social_accounting_joined_with_owner_yields_social_accounting_itself(
        self,
    ) -> None:
        result = (
            self.repository.get_accounts()
            .with_id(self.social_accounting.account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert result[1] == self.social_accounting
