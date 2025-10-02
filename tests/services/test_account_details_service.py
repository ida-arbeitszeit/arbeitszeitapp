from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.anonymization import ANONYMIZED_STR, ANONYMIZED_UUID
from arbeitszeit.records import SocialAccounting
from arbeitszeit.services.account_details import (
    AccountDetailsService,
    AccountTransfer,
    TransferParty,
    TransferPartyType,
    construct_plot_data,
)
from arbeitszeit.transfers import TransferType
from tests.datetime_service import datetime_utc
from tests.interactors.base_test_case import BaseTestCase


class ServiceBase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.service = self.injector.get(AccountDetailsService)

    def create_company_product_account(self) -> UUID:
        return self.company_generator.create_company_record().means_account

    def create_member_account(self) -> UUID:
        self.member_generator.create_member()
        member = self.database_gateway.get_members().first()
        assert member
        return member.account

    def create_social_accounting_psf_account(self) -> UUID:
        social_accounting = self.injector.get(SocialAccounting)
        return social_accounting.account_psf

    def create_cooperation_account(self) -> UUID:
        self.cooperation_generator.create_cooperation()
        cooperation = self.database_gateway.get_cooperations().first()
        assert cooperation
        return cooperation.account


class AccountTransfersTests(ServiceBase):
    def test_no_transfers_returned_when_account_does_not_exist(self) -> None:
        assert not self.service.get_account_transfers(uuid4())

    def test_no_transfers_returned_when_no_transfers_took_place(self) -> None:
        account = self.company_generator.create_company_record().product_account
        assert not self.service.get_account_transfers(account)

    def test_no_transfers_returned_when_no_transfers_to_or_from_specified_account_took_place(
        self,
    ) -> None:
        self.transfer_generator.create_transfer()
        account = self.company_generator.create_company_record().product_account
        assert not self.service.get_account_transfers(account)

    def test_that_transfers_to_account_are_returned(self) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(credit_account=account)
        assert self.service.get_account_transfers(account)

    def test_that_transfers_from_account_are_returned(self) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(debit_account=account)
        assert self.service.get_account_transfers(account)

    @parameterized.expand([(0,), (1,), (3,)])
    def test_that_correct_amount_of_transfers_from_account_are_returned(
        self, num_of_transfers: int
    ) -> None:
        account = self.create_company_product_account()
        for _ in range(num_of_transfers):
            self.transfer_generator.create_transfer(debit_account=account)
        assert len(self.service.get_account_transfers(account)) == num_of_transfers

    @parameterized.expand([(0,), (1,), (3,)])
    def test_that_correct_amount_of_transfers_to_account_are_returned(
        self, num_of_transfers: int
    ) -> None:
        account = self.create_company_product_account()
        for _ in range(num_of_transfers):
            self.transfer_generator.create_transfer(credit_account=account)
        assert len(self.service.get_account_transfers(account)) == num_of_transfers

    @parameterized.expand([(True,), (False,)])
    def test_debit_transfers_are_shown_as_such(
        self,
        is_debit: bool,
    ) -> None:
        account = self.company_generator.create_company_record().work_account
        if is_debit:
            self.transfer_generator.create_transfer(debit_account=account)
        else:
            self.transfer_generator.create_transfer(credit_account=account)
        transfers = self.service.get_account_transfers(account)
        assert transfers[0].is_debit_transfer == is_debit

    @parameterized.expand(
        [
            (TransferType.credit_p,),
            (TransferType.compensation_for_company,),
            (TransferType.work_certificates,),
        ]
    )
    def test_transfer_type_is_passed_as_such(
        self, expected_transfer_type: TransferType
    ) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(
            type=expected_transfer_type, credit_account=account
        )
        transfers = self.service.get_account_transfers(account)
        assert transfers[0].type == expected_transfer_type

    @parameterized.expand(
        [
            (datetime_utc(2025, 3, 1),),
            (datetime_utc(2024, 10, 2),),
        ]
    )
    def test_transfer_date_is_passed_as_such(self, expected_date: datetime) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(
            date=expected_date, credit_account=account
        )
        transfers = self.service.get_account_transfers(account)
        assert transfers[0].date == expected_date

    @parameterized.expand(
        [(Decimal(10),), (Decimal(12.0003),), (-Decimal(20),), (Decimal(0),)]
    )
    def test_transfer_volume_is_passed_as_such_if_transfer_is_credit_transfer(
        self, expected_volume: Decimal
    ) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(
            value=expected_volume, credit_account=account
        )
        transfers = self.service.get_account_transfers(account)
        assert transfers[0].volume == expected_volume

    @parameterized.expand(
        [(Decimal(10),), (Decimal(12.0003),), (-Decimal(20),), (Decimal(0),)]
    )
    def test_transfer_volume_is_passed_with_inverted_sign_if_transfer_is_debit_transfer(
        self, volume: Decimal
    ) -> None:
        account = self.create_company_product_account()
        self.transfer_generator.create_transfer(value=volume, debit_account=account)
        transfers = self.service.get_account_transfers(account)
        assert transfers[0].volume == -volume


class TransferPartyTests(ServiceBase):
    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_type_company_is_shown_if_transfer_party_is_company(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_member_account()
        other_party_account = self.create_company_product_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.type == TransferPartyType.company

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_type_member_is_shown_if_transfer_party_is_member(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_company_product_account()
        other_party_account = self.create_member_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.type == TransferPartyType.member

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_type_social_accounting_is_shown_if_transfer_party_is_social_Accounting(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_company_product_account()
        other_party_account = self.create_social_accounting_psf_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.type == TransferPartyType.social_accounting

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_type_cooperation_is_shown_if_transfer_party_is_cooperation(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_company_product_account()
        other_party_account = self.create_cooperation_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.type == TransferPartyType.cooperation

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_id_is_anonymized_if_transfer_party_is_member(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_company_product_account()
        other_party_account = self.create_member_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.id is ANONYMIZED_UUID

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_party_name_is_anonymized_if_transfer_party_is_member(
        self, is_debit_transfer: bool
    ) -> None:
        requesting_account = self.create_company_product_account()
        other_party_account = self.create_member_account()
        if is_debit_transfer:
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        else:
            self.transfer_generator.create_transfer(
                debit_account=other_party_account, credit_account=requesting_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.name == ANONYMIZED_STR

    @parameterized.expand(
        [
            (TransferPartyType.company,),
            (TransferPartyType.cooperation,),
            (TransferPartyType.social_accounting,),
        ]
    )
    def test_that_transfer_party_id_is_not_anonymized_if_transfer_party_is_not_member(
        self, transfer_party_type: TransferPartyType
    ) -> None:
        requesting_account = self.create_company_product_account()
        if transfer_party_type == TransferPartyType.company:
            other_party_account = self.create_company_product_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        elif transfer_party_type == TransferPartyType.cooperation:
            other_party_account = self.create_cooperation_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        elif transfer_party_type == TransferPartyType.social_accounting:
            other_party_account = self.create_social_accounting_psf_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.id is not ANONYMIZED_UUID

    @parameterized.expand(
        [
            (TransferPartyType.company,),
            (TransferPartyType.cooperation,),
            (TransferPartyType.social_accounting,),
        ]
    )
    def test_that_transfer_party_name_is_not_anonymized_if_transfer_party_is_not_member(
        self, transfer_party_type: TransferPartyType
    ) -> None:
        requesting_account = self.create_company_product_account()
        if transfer_party_type == TransferPartyType.company:
            other_party_account = self.create_company_product_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        elif transfer_party_type == TransferPartyType.cooperation:
            other_party_account = self.create_cooperation_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        elif transfer_party_type == TransferPartyType.social_accounting:
            other_party_account = self.create_social_accounting_psf_account()
            self.transfer_generator.create_transfer(
                debit_account=requesting_account, credit_account=other_party_account
            )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.name is not ANONYMIZED_STR

    def test_that_transfer_party_name_equals_company_name(self) -> None:
        self.company_generator.create_company(name="Some Company Name")
        company = self.database_gateway.get_companies().first()
        assert company
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account, credit_account=company.means_account
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.name == "Some Company Name"

    def test_that_transfer_party_id_equals_company_id(self) -> None:
        self.company_generator.create_company()
        company = self.database_gateway.get_companies().first()
        assert company
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account, credit_account=company.means_account
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.id == company.id

    def test_that_transfer_party_name_equals_cooperation_name(self) -> None:
        self.cooperation_generator.create_cooperation(name="Some Cooperation Name")
        cooperation = self.database_gateway.get_cooperations().first()
        assert cooperation
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account, credit_account=cooperation.account
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.name == "Some Cooperation Name"

    def test_that_transfer_party_id_equals_cooperation_id(self) -> None:
        self.cooperation_generator.create_cooperation()
        cooperation = self.database_gateway.get_cooperations().first()
        assert cooperation
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account, credit_account=cooperation.account
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.id == cooperation.id

    def test_that_transfer_party_name_equals_social_accounting_name(self) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account,
            credit_account=social_accounting.account_psf,
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.name == social_accounting.get_name()

    def test_that_transfer_party_id_equals_social_accounting_id(self) -> None:
        social_accounting = self.injector.get(SocialAccounting)
        requesting_account = self.create_member_account()
        self.transfer_generator.create_transfer(
            debit_account=requesting_account,
            credit_account=social_accounting.account_psf,
        )
        transfers = self.service.get_account_transfers(requesting_account)
        assert transfers[0].transfer_party.id == social_accounting.id


class AccountBalanceTests(ServiceBase):
    def test_balance_is_zero_when_no_transfers_took_place(self) -> None:
        account = self.company_generator.create_company_record().means_account
        balance = self.service.get_account_balance(account)
        assert balance == 0

    @parameterized.expand(
        [
            ([-1, 2], 1),
            ([0, 0], 0),
            ([2, 3, 5], 10),
            ([-1, -2], -3),
        ]
    )
    def test_balance_is_correctly_calculated_based_on_transfer_values(
        self, transfer_values: list[float], expected_balance: float
    ) -> None:
        account = self.company_generator.create_company_record().means_account
        for value in transfer_values:
            if value < 0:
                self.transfer_generator.create_transfer(
                    debit_account=account, value=Decimal(abs(value))
                )
            else:
                self.transfer_generator.create_transfer(
                    credit_account=account, value=Decimal(abs(value))
                )
        assert self.service.get_account_balance(account) == Decimal(expected_balance)


class PlotDataTests(ServiceBase):
    def test_that_plotting_info_is_empty_when_empty_list_is_passed_in(self) -> None:
        plot_data = construct_plot_data([])
        assert not plot_data.accumulated_volumes
        assert not plot_data.timestamps

    def test_that_timestamps_are_extracted_from_list_of_transfers_and_sorted_ascending(
        self,
    ) -> None:
        timestamps = [
            datetime_utc(2000, 1, 1),
            datetime_utc(1999, 1, 1),
            datetime_utc(2001, 1, 1),
        ]
        transfers = [self.create_account_transfer(date=date) for date in timestamps]
        plot_data = construct_plot_data(transfers)
        assert plot_data.timestamps == sorted(timestamps)

    def test_that_volumes_are_extracted_from_list_of_transfers_and_accumulated(
        self,
    ) -> None:
        transfers = [self.create_account_transfer(volume=Decimal(1)) for _ in range(3)]
        plot_data = construct_plot_data(transfers)
        assert plot_data.accumulated_volumes == [Decimal(1), Decimal(2), Decimal(3)]

    def test_that_volumes_are_extracted_from_list_of_transfers_in_ascending_order_by_date(
        self,
    ) -> None:
        transfer1 = self.create_account_transfer(
            date=datetime_utc(2000, 1, 1), volume=Decimal(10)
        )
        transfer2 = self.create_account_transfer(
            date=datetime_utc(1999, 1, 1), volume=Decimal(-10)
        )
        transfer3 = self.create_account_transfer(
            date=datetime_utc(2001, 1, 1), volume=Decimal(10)
        )
        transfers = [transfer1, transfer2, transfer3]
        plot_data = construct_plot_data(transfers)
        assert plot_data.accumulated_volumes == [Decimal(-10), Decimal(0), Decimal(10)]

    def create_account_transfer(
        self, date: datetime = datetime(2025, 5, 1), volume: Decimal = Decimal(10)
    ) -> AccountTransfer:
        return AccountTransfer(
            type=TransferType.credit_p,
            date=date,
            is_debit_transfer=False,
            volume=volume,
            transfer_party=TransferParty(
                type=TransferPartyType.company,
                id=uuid4(),
                name="Some counter party name",
            ),
            debtor_equals_creditor=False,
        )
