from datetime import datetime
from decimal import Decimal
from unittest import TestCase

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_prd_account_details import (
    ShowPRDAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from tests.use_cases.dependency_injection import get_dependency_injector

DEFAULT_INFO1 = TransactionInfo(
    transaction_type=TransactionTypes.expected_sales,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
)

DEFAULT_INFO2 = TransactionInfo(
    transaction_type=TransactionTypes.sale_of_consumer_product,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.presenter = self.injector.get(ShowPRDAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = ShowPRDAccountDetailsResponse(
            transactions=[], account_balance=Decimal(0)
        )
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_do_not_show_transactions_if_no_transactions_took_place(self):
        response = ShowPRDAccountDetailsResponse(
            transactions=[], account_balance=Decimal(0)
        )
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_transactions)

    def test_return_correct_info_when_one_transaction_of_granting_credit_took_place(
        self,
    ):
        response = ShowPRDAccountDetailsResponse(
            transactions=[DEFAULT_INFO1], account_balance=Decimal(100.007)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, "100.01")
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, "Debit expected sales")
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, "10.01")
        self.assertIsInstance(trans.purpose, str)

    def test_return_correct_info_when_one_transaction_of_selling_consumer_product_took_place(
        self,
    ):
        response = ShowPRDAccountDetailsResponse(
            transactions=[DEFAULT_INFO2], account_balance=Decimal(100.007)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, "100.01")
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, "Sale")
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, "20.00")
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = ShowPRDAccountDetailsResponse(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)
