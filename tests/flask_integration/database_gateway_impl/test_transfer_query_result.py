from uuid import uuid4

from parameterized import parameterized
from sqlalchemy import text

from arbeitszeit.records import AccountTypes, SocialAccounting
from arbeitszeit.transfers.transfer_type import TransferType
from tests.flask_integration.flask import FlaskTestCase


class TransferResultTests(FlaskTestCase):
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

    def test_that_transfer_type_enum_from_database_matches_enum_in_code(self) -> None:
        db_values = [
            row[0]
            for row in self.db.session.execute(
                text("SELECT unnest(enum_range(NULL::transfertype))")
            )
        ]
        code_values = [member.value for member in TransferType]
        assert set(db_values) == set(code_values)


class WhereAccountIsDebtorTests(FlaskTestCase):
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


class WhereAccountIsCreditorTests(FlaskTestCase):
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


class JoinedWithDebtorTests(FlaskTestCase):
    def test_that_joined_with_debtor_yields_member(
        self,
    ) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(debit_account=member.account)
        transfers = self.database_gateway.get_transfers().where_account_is_debtor(
            member.account
        )
        transfer_with_debtor = transfers.joined_with_debtor().first()
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
        transfers = self.database_gateway.get_transfers().where_account_is_debtor(
            account
        )
        transfer_with_debtor = transfers.joined_with_debtor().first()
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == company

    def test_that_joined_with_debtor_yields_social_accounting(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transfer_generator.create_transfer(
            debit_account=social_accounting.account_psf
        )
        transfers = self.database_gateway.get_transfers().where_account_is_debtor(
            social_accounting.account_psf
        )
        transfer_with_debtor = transfers.joined_with_debtor().first()
        assert transfer_with_debtor
        assert transfer_with_debtor[1] == social_accounting


class JoinedWithCreditorTests(FlaskTestCase):
    def test_that_joined_with_creditor_yields_member(
        self,
    ) -> None:
        member_id = self.member_generator.create_member()
        member = self.database_gateway.get_members().with_id(member_id).first()
        assert member
        self.transfer_generator.create_transfer(credit_account=member.account)
        transfers = self.database_gateway.get_transfers().where_account_is_creditor(
            member.account
        )
        transfer_with_creditor = transfers.joined_with_creditor().first()
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
        transfers = self.database_gateway.get_transfers().where_account_is_creditor(
            account
        )
        transfer_with_creditor = transfers.joined_with_creditor().first()
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == company

    def test_that_joined_with_creditor_yields_social_accounting(
        self,
    ) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        self.transfer_generator.create_transfer(
            credit_account=social_accounting.account_psf
        )
        transfers = self.database_gateway.get_transfers().where_account_is_creditor(
            social_accounting.account_psf
        )
        transfer_with_creditor = transfers.joined_with_creditor().first()
        assert transfer_with_creditor
        assert transfer_with_creditor[1] == social_accounting
