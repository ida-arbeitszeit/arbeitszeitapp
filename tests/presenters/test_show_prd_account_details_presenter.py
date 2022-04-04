from datetime import datetime
from decimal import Decimal
from typing import List
from unittest import TestCase

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_prd_account_details import (
    PlotDetails,
    ShowPRDAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from tests.plotter import FakePlotter
from tests.translator import FakeTranslator

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
        self.translator = FakeTranslator()
        self.plotter = FakePlotter()
        self.presenter = ShowPRDAccountDetailsPresenter(
            translator=self.translator, plotter=self.plotter
        )

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_do_not_show_transactions_if_no_transactions_took_place(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_transactions)

    def test_return_correct_info_when_one_transaction_of_granting_credit_took_place(
        self,
    ):
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1], account_balance=Decimal(100.007)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, "100.01")
        trans = view_model.transactions[0]
        self.assertEqual(
            trans.transaction_type, self.translator.gettext("Debit expected sales")
        )
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, "10.01")
        self.assertIsInstance(trans.purpose, str)

    def test_return_correct_info_when_one_transaction_of_selling_consumer_product_took_place(
        self,
    ):
        response = self._use_case_response(
            transactions=[DEFAULT_INFO2], account_balance=Decimal(100.007)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, "100.01")
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.translator.gettext("Sale"))
        self.assertIsInstance(trans.date, datetime)
        self.assertEqual(trans.transaction_volume, "20.00")
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = self._use_case_response(transactions=[DEFAULT_INFO1, DEFAULT_INFO2])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_presenter_returns_always_a_plot(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot)

    def _use_case_response(
        self,
        transactions: List[TransactionInfo] = [],
        account_balance: Decimal = Decimal(0),
        plot: PlotDetails = PlotDetails([], []),
    ):
        return ShowPRDAccountDetailsResponse(transactions, account_balance, plot)
