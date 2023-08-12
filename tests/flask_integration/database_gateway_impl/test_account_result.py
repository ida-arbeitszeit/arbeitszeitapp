from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import SocialAccounting
from tests.data_generators import (
    AccountGenerator,
    CompanyGenerator,
    MemberGenerator,
    TransactionGenerator,
)

from ..flask import FlaskTestCase


class AccountResultTests(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.account_generator: AccountGenerator = self.injector.get(AccountGenerator)
        self.transaction_generator: TransactionGenerator = self.injector.get(
            TransactionGenerator
        )
        self.member_generator = self.injector.get(MemberGenerator)
        self.company_generator = self.injector.get(CompanyGenerator)
        self.social_accounting = self.injector.get(SocialAccounting)

    def test_that_a_priori_there_is_only_one_account_for_social_accounting(
        self,
    ) -> None:
        account = self.database_gateway.get_accounts().first()
        assert len(self.database_gateway.get_accounts()) == 1
        assert list(self.database_gateway.get_accounts().joined_with_owner()) == [
            (account, self.social_accounting)
        ]

    def test_there_are_accounts_to_be_queried_when_one_was_created(self) -> None:
        self.account_generator.create_account()
        assert self.database_gateway.get_accounts()

    def test_only_include_relevant_account_when_filtering_by_id(self) -> None:
        random_id = uuid4()
        actual_id = self.account_generator.create_account().id
        assert not self.database_gateway.get_accounts().with_id(random_id)
        assert self.database_gateway.get_accounts().with_id(actual_id)

    def test_that_account_joined_with_owner_yields_original_member(self) -> None:
        account = self.database_gateway.create_account()
        member = self.database_gateway.create_member(
            email="test@test.test",
            name="test name",
            password_hash="password",
            account=account,
            registered_on=datetime(2000, 1, 1),
        )
        result = (
            self.database_gateway.get_accounts()
            .with_id(member.account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert member == result[1]

    def test_that_p_account_joined_with_owner_yields_original_company(self) -> None:
        company = self.company_generator.create_company_record()
        assert company
        result = (
            self.database_gateway.get_accounts()
            .with_id(company.means_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_r_account_joined_with_owner_yields_original_company(self) -> None:
        company = self.company_generator.create_company_record()
        assert company
        result = (
            self.database_gateway.get_accounts()
            .with_id(company.raw_material_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_a_account_joined_with_owner_yields_original_company(self) -> None:
        company = self.company_generator.create_company_record()
        assert company
        result = (
            self.database_gateway.get_accounts()
            .with_id(company.work_account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_prd_account_joined_with_owner_yields_original_company(self) -> None:
        company = self.company_generator.create_company_record()
        assert company
        result = (
            self.database_gateway.get_accounts()
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
            self.database_gateway.get_accounts()
            .with_id(self.social_accounting.account)
            .joined_with_owner()
            .first()
        )
        assert result
        assert result[1] == self.social_accounting

    def test_with_no_members_have_no_member_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_member_accounts()

    def test_with_one_member_have_one_member_accounts(self) -> None:
        self.member_generator.create_member()
        assert len(self.database_gateway.get_accounts().that_are_member_accounts()) == 1

    def test_with_no_company_there_are_no_prd_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_product_accounts()

    def test_with_one_company_there_is_one_prd_accounts(self) -> None:
        self.company_generator.create_company()
        assert (
            len(self.database_gateway.get_accounts().that_are_product_accounts()) == 1
        )

    def test_filtering_by_prd_account_yields_the_product_account_of_previously_created_company(
        self,
    ) -> None:
        expected_account = self.database_gateway.create_account()
        self.database_gateway.create_company(
            email="",
            name="",
            password_hash="",
            means_account=self.database_gateway.create_account(),
            resource_account=self.database_gateway.create_account(),
            labour_account=self.database_gateway.create_account(),
            products_account=expected_account,
            registered_on=datetime(2000, 1, 1),
        )
        assert (
            expected_account
            in self.database_gateway.get_accounts().that_are_product_accounts()
        )

    def test_with_no_company_there_are_no_labour_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_labour_accounts()

    def test_with_one_company_there_is_one_labour_accounts(self) -> None:
        self.company_generator.create_company()
        assert len(self.database_gateway.get_accounts().that_are_labour_accounts()) == 1

    def test_filtering_by_labour_account_yields_the_labour_account_of_previously_created_company(
        self,
    ) -> None:
        expected_account = self.database_gateway.create_account()
        self.database_gateway.create_company(
            email="",
            name="",
            password_hash="",
            means_account=self.database_gateway.create_account(),
            resource_account=self.database_gateway.create_account(),
            labour_account=expected_account,
            products_account=self.database_gateway.create_account(),
            registered_on=datetime(2000, 1, 1),
        )
        assert (
            expected_account
            in self.database_gateway.get_accounts().that_are_labour_accounts()
        )

    @parameterized.expand(
        [
            ([], 0),
            ([1], 1),
            ([2], 2),
            ([1, 2, 3], 6),
            ([-1], -1),
            ([-1, 1], 0),
            ([-10, 1, 1], -8),
        ]
    )
    def test_when_joining_with_account_balance_the_proper_value_is_calculated(
        self, transactions: List[float], expected_total: float
    ) -> None:
        account = self.account_generator.create_account()
        for amount in transactions:
            if amount > 0:
                self.transaction_generator.create_transaction(
                    receiving_account=account.id, amount_received=amount
                )
            else:
                self.transaction_generator.create_transaction(
                    sending_account=account.id, amount_sent=abs(amount)
                )

        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_balance()
            .first()
        )
        assert result
        assert result[1] == Decimal(expected_total)

    def test_when_joining_with_balance_account_objects_are_deserialized_properly(
        self,
    ) -> None:
        self.company_generator.create_company()
        accounts = set(self.database_gateway.get_accounts())
        assert (
            set(
                a for a, _ in self.database_gateway.get_accounts().joined_with_balance()
            )
            == accounts
        )

    def test_when_joining_with_account_balance_and_having_multiple_transactions_we_get_one_result_for_one_account(
        self,
    ) -> None:
        account = self.account_generator.create_account()
        self.transaction_generator.create_transaction(receiving_account=account.id)
        self.transaction_generator.create_transaction(receiving_account=account.id)
        assert (
            len(
                self.database_gateway.get_accounts()
                .with_id(account.id)
                .joined_with_balance()
            )
            == 1
        )

    def test_owned_by_member_yields_no_accounts_if_no_member_was_supplied(self) -> None:
        self.member_generator.create_member()
        assert len(self.database_gateway.get_accounts().owned_by_member()) == 0

    def test_owned_by_member_yields_member_account_for_supplied_member(self) -> None:
        member = self.member_generator.create_member()
        assert len(self.database_gateway.get_accounts().owned_by_member(member)) == 1

    def test_owned_by_company_yields_no_accounts_if_no_company_was_supplied(
        self,
    ) -> None:
        self.company_generator.create_company()
        assert len(self.database_gateway.get_accounts().owned_by_company()) == 0

    def test_owned_by_company_yields_company_accounts_for_supplied_company(
        self,
    ) -> None:
        company = self.company_generator.create_company()
        assert len(self.database_gateway.get_accounts().owned_by_company(company)) == 4
