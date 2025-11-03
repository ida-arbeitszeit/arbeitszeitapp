from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.records import AccountTypes, SocialAccounting
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc
from tests.db.base_test_case import DatabaseTestCase


class TransferResultTests(DatabaseTestCase):
    def test_that_by_default_no_transfers_are_in_db(self) -> None:
        assert not self.database_gateway.get_transfers()

    def test_there_is_one_transfer_in_db_after_adding_one(self) -> None:
        self.transfer_generator.create_transfer()
        assert len(self.database_gateway.get_transfers()) == 1

    @parameterized.expand(
        [
            (TransferType.private_consumption,),
            (TransferType.credit_r,),
        ]
    )
    def test_that_transfer_with_type_is_created_with_correct_type(
        self, type: TransferType
    ) -> None:
        self.transfer_generator.create_transfer(type=type)
        transfer = self.database_gateway.get_transfers().first()
        assert transfer
        assert transfer.type == type

    def test_that_transfers_with_all_existing_transfer_types_can_be_created(
        self,
    ) -> None:
        transfer_types = [t for t in TransferType]
        for type_ in transfer_types:
            transfer = self.transfer_generator.create_transfer(type=type_)
            assert transfer.type == type_


class WhereAccountIsDebtorTests(DatabaseTestCase):
    def test_that_where_account_is_debtor_yields_none_if_debit_account_is_not_in_db(
        self,
    ) -> None:
        self.transfer_generator.create_transfer()
        transfers = self.database_gateway.get_transfers().where_account_is_debtor(
            uuid4()
        )
        assert not transfers

    def test_that_transfer_with_correct_debit_account_is_retrieved(self) -> None:
        expected_debit_account = self.database_gateway.create_account()
        expected_transfer = self.transfer_generator.create_transfer(
            debit_account=expected_debit_account.id
        )
        unexpected_transfer = self.transfer_generator.create_transfer()
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor(
                expected_debit_account.id
            )
        )
        assert unexpected_transfer not in retrieved_transfers
        assert expected_transfer in retrieved_transfers
        assert expected_transfer.debit_account == expected_debit_account.id

    def test_that_two_transfers_with_correct_debit_account_are_retrieved(self) -> None:
        expected_debit_account = self.database_gateway.create_account()
        expected_transfer1 = self.transfer_generator.create_transfer(
            debit_account=expected_debit_account.id
        )
        expected_transfer2 = self.transfer_generator.create_transfer(
            debit_account=expected_debit_account.id
        )
        unexpected_transfer = self.transfer_generator.create_transfer()
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor(
                expected_debit_account.id
            )
        )
        assert unexpected_transfer not in retrieved_transfers
        assert expected_transfer1 in retrieved_transfers
        assert expected_transfer2 in retrieved_transfers
        assert expected_transfer1.debit_account == expected_debit_account.id
        assert expected_transfer2.debit_account == expected_debit_account.id

    def test_that_several_accounts_can_be_specified(self) -> None:
        expected_debit_account = self.database_gateway.create_account()
        unexpected_debit_account = self.database_gateway.create_account()
        expected_transfer = self.transfer_generator.create_transfer(
            debit_account=expected_debit_account.id
        )
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor(
                expected_debit_account.id, unexpected_debit_account.id
            )
        )
        assert expected_transfer in retrieved_transfers
        assert expected_transfer.debit_account == expected_debit_account.id


class WhereAccountIsCreditorTests(DatabaseTestCase):
    def test_that_where_account_is_creditor_yields_none_if_credit_account_is_not_in_db(
        self,
    ) -> None:
        self.transfer_generator.create_transfer()
        transfers = self.database_gateway.get_transfers().where_account_is_creditor(
            uuid4()
        )
        assert not transfers

    def test_that_transfer_with_correct_credit_account_is_retrieved(self) -> None:
        expected_credit_account = self.database_gateway.create_account()
        expected_transfer = self.transfer_generator.create_transfer(
            credit_account=expected_credit_account.id
        )
        unexpected_transfer = self.transfer_generator.create_transfer()
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_creditor(
                expected_credit_account.id
            )
        )
        assert unexpected_transfer not in retrieved_transfers
        assert expected_transfer in retrieved_transfers


class WhereAccountIsDebtorOrCreditorTests(DatabaseTestCase):
    def test_that_transfer_of_debit_account_is_retrieved(self) -> None:
        debit_account = self.database_gateway.create_account()
        transfer = self.transfer_generator.create_transfer(
            debit_account=debit_account.id
        )
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor_or_creditor(
                debit_account.id
            )
        )
        assert transfer in retrieved_transfers

    def test_that_transfer_of_credit_account_is_retrieved(self) -> None:
        credit_account = self.database_gateway.create_account()
        transfer = self.transfer_generator.create_transfer(
            credit_account=credit_account.id
        )
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor_or_creditor(
                credit_account.id
            )
        )
        assert transfer in retrieved_transfers

    def test_that_transfer_is_retrieved_where_debit_and_credit_account_is_same_account(
        self,
    ) -> None:
        credit_account = debit_account = self.database_gateway.create_account()
        transfer = self.transfer_generator.create_transfer(
            debit_account=debit_account.id, credit_account=credit_account.id
        )
        retrieved_transfers = (
            self.database_gateway.get_transfers().where_account_is_debtor_or_creditor(
                credit_account.id
            )
        )
        assert transfer in retrieved_transfers


class JoinedWithDebtorTests(DatabaseTestCase):
    def test_that_joined_with_debtor_yields_member(
        self,
    ) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(debit_account=member.account)
        transfer_with_debtor = (
            self.database_gateway.get_transfers().joined_with_debtor().first()
        )
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == member

    @parameterized.expand(
        [
            (AccountTypes.p,),
            (AccountTypes.r,),
            (AccountTypes.a,),
            (AccountTypes.prd,),
        ]
    )
    def test_that_joined_with_debtor_yields_company(
        self,
        account_type: AccountTypes,
    ) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        account = company.get_account_by_type(account_type)
        assert account
        self.transfer_generator.create_transfer(debit_account=account)
        transfer_with_debtor = (
            self.database_gateway.get_transfers().joined_with_debtor().first()
        )
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == company

    def test_that_joined_with_debtor_yields_social_accounting(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transfer_generator.create_transfer(
            debit_account=social_accounting.account_psf
        )
        transfer_with_debtor = (
            self.database_gateway.get_transfers().joined_with_debtor().first()
        )
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == social_accounting

    def test_that_joined_with_debtor_yields_cooperation(
        self,
    ) -> None:
        cooperation_id = self.cooperation_generator.create_cooperation()
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        self.transfer_generator.create_transfer(debit_account=cooperation.account)
        transfer_with_debtor = (
            self.database_gateway.get_transfers().joined_with_debtor().first()
        )
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == cooperation


class JoinedWithCreditorTests(DatabaseTestCase):
    def test_that_joined_with_creditor_yields_member(
        self,
    ) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(credit_account=member.account)
        transfer_with_creditor = (
            self.database_gateway.get_transfers().joined_with_creditor().first()
        )
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == member

    @parameterized.expand(
        [
            (AccountTypes.p,),
            (AccountTypes.r,),
            (AccountTypes.a,),
            (AccountTypes.prd,),
        ]
    )
    def test_that_joined_with_creditor_yields_company(
        self,
        account_type: AccountTypes,
    ) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        account = company.get_account_by_type(account_type)
        assert account
        self.transfer_generator.create_transfer(credit_account=account)
        transfer_with_creditor = (
            self.database_gateway.get_transfers().joined_with_creditor().first()
        )
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == company

    def test_that_joined_with_creditor_yields_social_accounting(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transfer_generator.create_transfer(
            credit_account=social_accounting.account_psf
        )
        transfer_with_creditor = (
            self.database_gateway.get_transfers().joined_with_creditor().first()
        )
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == social_accounting

    def test_that_joined_with_creditor_yields_cooperation(
        self,
    ) -> None:
        cooperation_id = self.cooperation_generator.create_cooperation()
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        self.transfer_generator.create_transfer(credit_account=cooperation.account)
        transfer_with_creditor = (
            self.database_gateway.get_transfers().joined_with_creditor().first()
        )
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == cooperation


class OrderedByDateTests(DatabaseTestCase):
    @parameterized.expand(
        [
            (True,),
            (False,),
        ]
    )
    def test_that_transfers_can_be_ordered_in_ascending_or_descending_order(
        self, ascending: bool
    ) -> None:
        date1 = datetime_utc(2021, 1, 1)
        date2 = datetime_utc(2021, 1, 2)
        self.datetime_service.freeze_time(date1)
        self.transfer_generator.create_transfer()
        self.datetime_service.freeze_time(date2)
        self.transfer_generator.create_transfer()

        transfers = self.database_gateway.get_transfers().ordered_by_date(
            ascending=ascending
        )
        actual_dates = [transfer.date for transfer in transfers]
        expected_dates = [date1, date2] if ascending else [date2, date1]
        assert actual_dates == expected_dates


class JoinedWithDebtorAndCreditorTests(DatabaseTestCase):
    def test_that_join_yields_member_and_same_member(self) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(
            debit_account=member.account, credit_account=member.account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == member
        assert transfer_with_debtor_and_creditor[2] == member

    def test_that_join_yields_member_and_different_member(self) -> None:
        member_id_1 = self.member_generator.create_member()
        member_1 = self.database_gateway.get_members().with_id(member_id_1).first()
        assert member_1
        member_id_2 = self.member_generator.create_member()
        member_2 = self.database_gateway.get_members().with_id(member_id_2).first()
        assert member_2
        self.transfer_generator.create_transfer(
            debit_account=member_1.account, credit_account=member_2.account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == member_1
        assert transfer_with_debtor_and_creditor[2] == member_2

    @parameterized.expand(
        [
            (AccountTypes.p,),
            (AccountTypes.r,),
            (AccountTypes.a,),
            (AccountTypes.prd,),
        ]
    )
    def test_that_join_yields_member_and_company(
        self,
        company_account_type: AccountTypes,
    ) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        company_account = company.get_account_by_type(company_account_type)
        assert company_account
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(
            debit_account=member.account, credit_account=company_account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == member
        assert transfer_with_debtor_and_creditor[2] == company

    def test_that_join_yields_member_and_social_accounting(self) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(
            debit_account=member.account, credit_account=social_accounting.account_psf
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == member
        assert transfer_with_debtor_and_creditor[2] == social_accounting

    def test_that_join_yields_member_and_cooperation(self) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        cooperation_id = self.cooperation_generator.create_cooperation()
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        self.transfer_generator.create_transfer(
            debit_account=member.account, credit_account=cooperation.account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == member
        assert transfer_with_debtor_and_creditor[2] == cooperation

    def test_that_join_yields_company_and_same_company(self) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        self.transfer_generator.create_transfer(
            debit_account=company.product_account,
            credit_account=company.product_account,
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == company
        assert transfer_with_debtor_and_creditor[2] == company

    def test_that_join_yields_company_and_different_company(self) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        different_company_id = self.company_generator.create_company()
        different_company = (
            self.database_gateway.get_companies().with_id(different_company_id).first()
        )
        assert different_company
        self.transfer_generator.create_transfer(
            debit_account=company.product_account,
            credit_account=different_company.product_account,
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == company
        assert transfer_with_debtor_and_creditor[2] == different_company

    def test_that_join_yields_company_and_member(self) -> None:
        company_id = self.company_generator.create_company()
        company = self.database_gateway.get_companies().with_id(company_id).first()
        assert company
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(
            debit_account=company.product_account, credit_account=member.account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == company
        assert transfer_with_debtor_and_creditor[2] == member

    def test_that_join_yields_social_accounting_and_social_accounting(self) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transfer_generator.create_transfer(
            debit_account=social_accounting.account_psf,
            credit_account=social_accounting.account_psf,
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == social_accounting
        assert transfer_with_debtor_and_creditor[2] == social_accounting

    def test_that_join_yields_cooperation_and_same_cooperation(self) -> None:
        cooperation_id = self.cooperation_generator.create_cooperation()
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        self.transfer_generator.create_transfer(
            debit_account=cooperation.account, credit_account=cooperation.account
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == cooperation
        assert transfer_with_debtor_and_creditor[2] == cooperation

    def test_that_join_yields_cooperation_and_different_cooperation(self) -> None:
        cooperation_id = self.cooperation_generator.create_cooperation()
        cooperation = (
            self.database_gateway.get_cooperations().with_id(cooperation_id).first()
        )
        assert cooperation
        different_cooperation_id = self.cooperation_generator.create_cooperation()
        different_cooperation = (
            self.database_gateway.get_cooperations()
            .with_id(different_cooperation_id)
            .first()
        )
        assert different_cooperation
        self.transfer_generator.create_transfer(
            debit_account=cooperation.account,
            credit_account=different_cooperation.account,
        )
        transfer_with_debtor_and_creditor = (
            self.database_gateway.get_transfers()
            .joined_with_debtor_and_creditor()
            .first()
        )
        assert transfer_with_debtor_and_creditor
        assert transfer_with_debtor_and_creditor[1] == cooperation
        assert transfer_with_debtor_and_creditor[2] == different_cooperation
