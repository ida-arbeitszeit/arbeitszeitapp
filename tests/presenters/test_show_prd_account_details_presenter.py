from datetime import datetime
from decimal import Decimal
from typing import List
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.entities import Member
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_prd_account_details import ShowPRDAccountDetailsUseCase
from arbeitszeit_web.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from tests.datetime_service import FakeDatetimeService
from tests.presenters.url_index import UrlIndexTestImpl
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

DEFAULT_INFO1 = ShowPRDAccountDetailsUseCase.TransactionInfo(
    transaction_type=TransactionTypes.expected_sales,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
    buyer=None,
)

DEFAULT_INFO2 = ShowPRDAccountDetailsUseCase.TransactionInfo(
    transaction_type=TransactionTypes.sale_of_consumer_product,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
    buyer=ShowPRDAccountDetailsUseCase.Buyer(
        buyer_type=Member, buyer_id=uuid4(), buyer_name="member name"
    ),
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.translator = self.injector.get(FakeTranslator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.presenter = self.injector.get(ShowPRDAccountDetailsPresenter)
        self.url_index = self.injector.get(UrlIndexTestImpl)

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
        ACCOUNT_BALANCE = Decimal(100.007)
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transactions[0]
        self.assertEqual(
            trans.transaction_type, self.translator.gettext("Debit expected sales")
        )
        self.assertEqual(
            trans.date,
            self.datetime_service.format_datetime(
                date=DEFAULT_INFO1.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )
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
        self.assertEqual(
            trans.date,
            self.datetime_service.format_datetime(
                date=DEFAULT_INFO1.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(trans.transaction_volume, "20.00")
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = self._use_case_response(transactions=[DEFAULT_INFO1, DEFAULT_INFO2])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_name_of_buyer_is_shown_if_transaction_is_of_type_sale(self):
        response = self._use_case_response(transactions=[DEFAULT_INFO2])
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions[0].buyer_name, "member name")

    def test_name_of_buyer_is_empty_string_if_transaction_is_of_type_expected_sales(
        self,
    ):
        response = self._use_case_response(transactions=[DEFAULT_INFO1])
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions[0].buyer_name, "")

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: List[ShowPRDAccountDetailsUseCase.TransactionInfo] = [],
        account_balance: Decimal = Decimal(0),
        plot: ShowPRDAccountDetailsUseCase.PlotDetails = ShowPRDAccountDetailsUseCase.PlotDetails(
            [], []
        ),
    ):
        return ShowPRDAccountDetailsUseCase.Response(
            company_id, transactions, account_balance, plot
        )
