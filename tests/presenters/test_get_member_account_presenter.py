from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from unittest import TestCase

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.get_member_account import (
    GetMemberAccountResponse,
    TransactionInfo,
)
from arbeitszeit_web.presenters.get_member_account_presenter import (
    GetMemberAccountPresenter,
)
from tests.datetime_service import FakeDatetimeService
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector


class TestPresenter(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(GetMemberAccountPresenter)

    def test_that_empty_transaction_list_is_shown_if_no_transactions_took_place(
        self,
    ):
        response = self.get_use_case_response([])
        view_model = self.presenter.present_member_account(response)
        self.assertFalse(view_model.transactions)

    def test_that_one_transaction_is_shown_if_one_transaction_took_place(
        self,
    ):
        response = self.get_use_case_response([self.get_transaction()])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(len(view_model.transactions), 1)

    def test_that_two_transactions_are_shown_if_two_transactions_took_place(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(), self.get_transaction()]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(len(view_model.transactions), 2)

    def test_that_correct_balance_is_returned(
        self,
    ):
        response = self.get_use_case_response([], balance=Decimal("10"))
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.balance, "10.00")

    def test_that_balance_sign_is_shown_correctly_if_balance_is_negative(
        self,
    ):
        response = self.get_use_case_response([], balance=Decimal("-10"))
        view_model = self.presenter.present_member_account(response)
        self.assertFalse(view_model.is_balance_positive)

    def test_that_balance_sign_is_shown_correctly_if_balance_is_zero(
        self,
    ):
        response = self.get_use_case_response([], balance=Decimal("0"))
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.is_balance_positive)

    def test_that_balance_sign_is_shown_correctly_if_balance_is_positive(
        self,
    ):
        response = self.get_use_case_response([], balance=Decimal("10"))
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.is_balance_positive)

    def test_that_date_of_transaction_is_formatted_correctly_as_berlin_summertime(
        self,
    ):
        test_date = datetime(2022, 8, 1, 10, 30)
        response = self.get_use_case_response([self.get_transaction(date=test_date)])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.transactions[0].date, "01.08.2022 12:30")

    def test_that_transaction_volume_is_formatted_correctly(self):
        response = self.get_use_case_response([self.get_transaction()])
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(view_model.transactions[0].volume, "20.01")

    def test_that_transaction_volume_sign_is_shown_correctly_if_volume_is_negative(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(transaction_volume=Decimal("-1"))]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertFalse(view_model.transactions[0].is_volume_positive)

    def test_that_transaction_volume_sign_is_shown_correctly_if_volume_is_zero(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(transaction_volume=Decimal("0"))]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.transactions[0].is_volume_positive)

    def test_that_transaction_volume_sign_is_shown_correctly_if_volume_is_positive(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(transaction_volume=Decimal("2"))]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.transactions[0].is_volume_positive)

    def test_that_transaction_type_is_shown_correctly_for_incoming_wages(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(type=TransactionTypes.incoming_wages)]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(
            view_model.transactions[0].type, self.translator.gettext("Wages")
        )

    def test_that_transaction_type_is_shown_correctly_for_payment_of_consumer_product(
        self,
    ):
        response = self.get_use_case_response(
            [self.get_transaction(type=TransactionTypes.payment_of_consumer_product)]
        )
        view_model = self.presenter.present_member_account(response)
        self.assertEqual(
            view_model.transactions[0].type, self.translator.gettext("Payment")
        )

    def test_that_name_of_peer_is_shown(
        self,
    ):
        response = self.get_use_case_response([self.get_transaction()])
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.transactions[0].user_name)

    def test_that_purpose_is_shown(
        self,
    ):
        response = self.get_use_case_response([self.get_transaction()])
        view_model = self.presenter.present_member_account(response)
        self.assertTrue(view_model.transactions[0].purpose)

    def get_use_case_response(
        self, transactions: List[TransactionInfo], balance: Optional[Decimal] = None
    ) -> GetMemberAccountResponse:
        if balance is None:
            balance = Decimal("10")
        return GetMemberAccountResponse(transactions=transactions, balance=balance)

    def get_transaction(
        self,
        date: Optional[datetime] = None,
        transaction_volume: Optional[Decimal] = None,
        type: Optional[TransactionTypes] = None,
    ) -> TransactionInfo:
        if date is None:
            date = self.datetime_service.now()
        if transaction_volume is None:
            transaction_volume = Decimal("20.006")
        if type is None:
            type = TransactionTypes.incoming_wages
        return TransactionInfo(
            date=date,
            peer_name="test company",
            transaction_volume=transaction_volume,
            purpose="test purpose",
            type=type,
        )
