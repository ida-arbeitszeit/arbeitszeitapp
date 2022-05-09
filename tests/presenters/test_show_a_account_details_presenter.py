from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_a_account_details import (
    ShowAAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

DEFAULT_INFO1 = TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
)

DEFAULT_INFO2 = TransactionInfo(
    transaction_type=TransactionTypes.payment_of_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(ShowAAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = ShowAAccountDetailsResponse(
            transactions=[], account_balance=Decimal(0)
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self):
        response = ShowAAccountDetailsResponse(
            transactions=[DEFAULT_INFO1], account_balance=Decimal(100.007)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, "100.01")
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.translator.gettext("Credit"))
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, "10.01")
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = ShowAAccountDetailsResponse(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)
