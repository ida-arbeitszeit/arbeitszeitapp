from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit import records
from arbeitszeit.records import SocialAccounting

from ..flask import FlaskTestCase


class AccountResultTests(FlaskTestCase):
    def test_that_by_default_there_is_one_account_for_social_accounting(
        self,
    ) -> None:
        self.injector.get(SocialAccounting)
        assert len(self.database_gateway.get_accounts()) == 1

    def test_there_are_accounts_to_be_queried_when_one_was_created(self) -> None:
        self.database_gateway.create_account()
        assert self.database_gateway.get_accounts()

    def test_only_include_relevant_account_when_filtering_by_id(self) -> None:
        random_id = uuid4()
        actual_id = self.database_gateway.create_account().id
        assert not self.database_gateway.get_accounts().with_id(random_id)
        assert self.database_gateway.get_accounts().with_id(actual_id)

    def test_that_account_joined_with_owner_yields_original_member(self) -> None:
        account = self.database_gateway.create_account()
        credentials = self.create_account_credentials()
        member = self.database_gateway.create_member(
            account_credentials=credentials.id,
            name="test name",
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
        account = self.database_gateway.create_account()
        company = self.create_company(means_account=account)
        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_r_account_joined_with_owner_yields_original_company(self) -> None:
        account = self.database_gateway.create_account()
        company = self.create_company(resource_account=account)
        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_a_account_joined_with_owner_yields_original_company(self) -> None:
        account = self.database_gateway.create_account()
        company = self.create_company(labour_account=account)
        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_that_prd_account_joined_with_owner_yields_original_company(self) -> None:
        account = self.database_gateway.create_account()
        company = self.create_company(products_account=account)
        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_owner()
            .first()
        )
        assert result
        assert company == result[1]

    def test_psf_account_from_social_accounting_joined_with_owner_yields_psf_account_and_social_accounting_itself(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        result = (
            self.database_gateway.get_accounts()
            .with_id(social_accounting.account_psf)
            .joined_with_owner()
            .first()
        )
        assert result
        assert result[0].id == social_accounting.account_psf
        assert result[1] == social_accounting

    def test_that_account_joined_with_owner_yields_original_cooperation(self) -> None:
        account = self.database_gateway.create_account()
        cooperation = self.create_cooperation(account=account.id)
        result = (
            self.database_gateway.get_accounts()
            .with_id(account.id)
            .joined_with_owner()
            .first()
        )
        assert result
        assert cooperation == result[1]

    def test_with_no_members_have_no_member_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_member_accounts()

    def test_with_one_member_have_one_member_accounts(self) -> None:
        self.member_generator.create_member()
        assert len(self.database_gateway.get_accounts().that_are_member_accounts()) == 1

    def test_with_no_company_there_are_no_prd_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_product_accounts()

    def test_with_one_company_there_is_one_prd_accounts(self) -> None:
        self.create_company()
        assert (
            len(self.database_gateway.get_accounts().that_are_product_accounts()) == 1
        )

    def test_filtering_by_prd_account_yields_the_product_account_of_previously_created_company(
        self,
    ) -> None:
        expected_account = self.database_gateway.create_account()
        self.create_company(products_account=expected_account)
        assert (
            expected_account
            in self.database_gateway.get_accounts().that_are_product_accounts()
        )

    def test_with_no_company_there_are_no_labour_accounts(self) -> None:
        assert not self.database_gateway.get_accounts().that_are_labour_accounts()

    def test_with_one_company_there_is_one_labour_accounts(self) -> None:
        self.create_company()
        assert len(self.database_gateway.get_accounts().that_are_labour_accounts()) == 1

    def test_filtering_by_labour_account_yields_the_labour_account_of_previously_created_company(
        self,
    ) -> None:
        expected_account = self.database_gateway.create_account()
        self.create_company(labour_account=expected_account)
        assert (
            expected_account
            in self.database_gateway.get_accounts().that_are_labour_accounts()
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
        self.create_company()
        assert len(self.database_gateway.get_accounts().owned_by_company()) == 0

    def test_owned_by_company_yields_company_accounts_for_supplied_company(
        self,
    ) -> None:
        company = self.create_company()
        assert (
            len(self.database_gateway.get_accounts().owned_by_company(company.id)) == 4
        )

    def create_account_credentials(
        self, address: str = "test@test.test"
    ) -> records.AccountCredentials:
        self.database_gateway.create_email_address(address=address, confirmed_on=None)
        return self.database_gateway.create_account_credentials(
            email_address=address,
            password_hash="",
        )

    def create_company(
        self,
        means_account: Optional[records.Account] = None,
        labour_account: Optional[records.Account] = None,
        resource_account: Optional[records.Account] = None,
        products_account: Optional[records.Account] = None,
    ) -> records.Company:
        return self.database_gateway.create_company(
            account_credentials=self.create_account_credentials().id,
            name="test company",
            means_account=means_account or self.database_gateway.create_account(),
            labour_account=labour_account or self.database_gateway.create_account(),
            resource_account=resource_account or self.database_gateway.create_account(),
            products_account=products_account or self.database_gateway.create_account(),
            registered_on=datetime(2000, 1, 1),
        )

    def create_cooperation(
        self,
        account: UUID,
    ) -> records.Cooperation:
        return self.database_gateway.create_cooperation(
            creation_timestamp=datetime(2000, 1, 1),
            name="test cooperation",
            definition="some product definition",
            account=account,
        )


class JoinedWithBalanceTests(FlaskTestCase):
    @parameterized.expand(
        [
            ([], 0),
            ([-1, 1], 0),
            ([1], 1),
            ([-1], -1),
            ([1, 2, 3], 6),
            ([-10, 1, 1], -8),
        ]
    )
    def test_when_joining_with_account_balance_the_proper_value_is_calculated(
        self, transfer_values: List[float], expected_total: float
    ) -> None:
        account = self.database_gateway.create_account()
        for value in transfer_values:
            if value > 0:
                # credit
                self.transfer_generator.create_transfer(
                    credit_account=account.id, value=Decimal(value)
                )
            else:
                # debit
                self.transfer_generator.create_transfer(
                    debit_account=account.id, value=Decimal(abs(value))
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
        assert accounts
        assert (
            set(
                a for a, _ in self.database_gateway.get_accounts().joined_with_balance()
            )
            == accounts
        )

    def test_when_joining_with_balance_and_having_multiple_transfers_we_get_one_result_for_one_account(
        self,
    ) -> None:
        account = self.database_gateway.create_account()
        self.transfer_generator.create_transfer(debit_account=account.id)
        self.transfer_generator.create_transfer(debit_account=account.id)
        assert (
            len(
                self.database_gateway.get_accounts()
                .with_id(account.id)
                .joined_with_balance()
            )
            == 1
        )
