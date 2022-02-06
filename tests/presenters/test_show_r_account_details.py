from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_r_account_details import (
    ShowRAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.show_r_account_details import ShowRAccountDetailsPresenter

DEFAULT_INFO1 = TransactionInfo(
    transaction_type=TransactionTypes.credit_for_liquid_means,
    date=datetime.now(),
    transaction_volume=Decimal(10),
    purpose="Test purpose",
)

DEFAULT_INFO2 = TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.presenter = ShowRAccountDetailsPresenter()

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = ShowRAccountDetailsResponse(
            transactions=[], account_balance=Decimal(0)
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self):
        response = ShowRAccountDetailsResponse(
            transactions=[DEFAULT_INFO1], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, Decimal(100))
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, "Credit")
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, DEFAULT_INFO1.transaction_volume)
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = ShowRAccountDetailsResponse(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)
