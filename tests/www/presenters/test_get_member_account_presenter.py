from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from parameterized import parameterized

from arbeitszeit.interactors.get_member_account import (
    GetMemberAccountResponse,
)
from arbeitszeit.services.account_details import (
    AccountTransfer,
    TransferParty,
    TransferPartyType,
)
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.www.presenters.get_member_account_presenter import (
    GetMemberAccountPresenter,
)
from tests.datetime_service import datetime_utc
from tests.www.base_test_case import BaseTestCase


class TestPresenter(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(GetMemberAccountPresenter)

    def test_that_empty_transfer_list_is_shown_if_no_transfers_took_place(
        self,
    ):
        response = self.get_interactor_response([])
        view_model = self.presenter.present_member_account(response)
        self.assertFalse(view_model.transfers)

    def test_that_one_transfer_is_shown_if_one_transfer_took_place(
        self,
    ):
        response = self.get_interactor_response([self.get_transfer()])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(len(view_model.transfers), 1)

    def test_that_two_transfers_are_shown_if_two_transfers_took_place(
        self,
    ):
        response = self.get_interactor_response(
            [self.get_transfer(), self.get_transfer()]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(len(view_model.transfers), 2)

    def test_that_correct_balance_is_returned(
        self,
    ):
        response = self.get_interactor_response([], balance=Decimal("10"))
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.balance, "10.00")

    def test_that_balance_sign_is_shown_correctly_if_balance_is_negative(
        self,
    ):
        response = self.get_interactor_response([], balance=Decimal("-10"))
        view_model = self.presenter.present_member_account(response)
        self.assertFalse(view_model.is_balance_positive)

    def test_that_balance_sign_is_shown_correctly_if_balance_is_zero(
        self,
    ):
        response = self.get_interactor_response([], balance=Decimal("0"))
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.is_balance_positive)

    def test_that_balance_sign_is_shown_correctly_if_balance_is_positive(
        self,
    ):
        response = self.get_interactor_response([], balance=Decimal("10"))
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.is_balance_positive)

    def test_that_date_of_transfer_is_formatted_correctly(
        self,
    ):
        test_date = datetime_utc(2022, 8, 1, 10, 30)
        response = self.get_interactor_response([self.get_transfer(date=test_date)])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.transfers[0].date, "01.08.2022 10:30")

    def test_that_transfer_volume_is_formatted_correctly(self):
        response = self.get_interactor_response([self.get_transfer()])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.transfers[0].transfer_volume, "20.01")

    @parameterized.expand([(True,), (False,)])
    def test_that_transfer_is_shown_as_debit_transfer_if_that_is_the_case(
        self, is_debit_transfer: bool
    ):
        response = self.get_interactor_response(
            [self.get_transfer(is_debit_transfer=is_debit_transfer)]
        )
        view_model = self.presenter.present_member_account(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit_transfer

    def test_that_transfer_type_is_shown_correctly_for_incoming_wages(
        self,
    ):
        response = self.get_interactor_response(
            [self.get_transfer(type=TransferType.work_certificates)]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(
            view_model.transfers[0].transfer_type,
            self.translator.gettext("Work certificates"),
        )

    def test_that_transfer_type_is_shown_correctly_for_consumption_of_consumer_product(
        self,
    ):
        response = self.get_interactor_response(
            [self.get_transfer(type=TransferType.private_consumption)]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(
            view_model.transfers[0].transfer_type,
            self.translator.gettext("Private consumption"),
        )

    def test_that_transfer_type_is_shown_correctly_for_taxes(
        self,
    ):
        response = self.get_interactor_response(
            [self.get_transfer(type=TransferType.taxes)]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(
            view_model.transfers[0].transfer_type,
            self.translator.gettext("Contribution to public sector"),
        )

    def test_that_transfer_party_name_is_translated_if_it_is_the_name_of_social_accounting(
        self,
    ) -> None:
        nontranslated_social_accounting_name = "Social Accounting"
        response = self.get_interactor_response(
            [
                self.get_transfer(
                    transfer_party=TransferParty(
                        id=uuid4(),
                        name=nontranslated_social_accounting_name,
                        type=TransferPartyType.social_accounting,
                    )
                )
            ]
        )
        view_model = self.presenter.present_member_account(response)
        assert view_model.transfers[0].party_name == self.translator.gettext(
            nontranslated_social_accounting_name
        )

    def get_interactor_response(
        self, transfers: list[AccountTransfer], balance: Optional[Decimal] = None
    ) -> GetMemberAccountResponse:
        if balance is None:
            balance = Decimal("10")
        return GetMemberAccountResponse(transfers=transfers, balance=balance)

    def get_transfer(
        self,
        date: Optional[datetime] = None,
        transfer_volume: Optional[Decimal] = None,
        type: Optional[TransferType] = None,
        is_debit_transfer: bool = False,
        transfer_party: Optional[TransferParty] = None,
    ) -> AccountTransfer:
        if date is None:
            date = self.datetime_service.now()
        if transfer_volume is None:
            transfer_volume = Decimal("20.006")
        if type is None:
            type = TransferType.work_certificates
        if transfer_party is None:
            transfer_party = TransferParty(
                id=uuid4(), name="Some party name", type=TransferPartyType.member
            )
        return AccountTransfer(
            date=date,
            volume=transfer_volume,
            type=type,
            is_debit_transfer=is_debit_transfer,
            transfer_party=transfer_party,
            debtor_equals_creditor=False,
        )
