from datetime import datetime
from decimal import Decimal
from typing import List
from unittest import TestCase
from uuid import UUID, uuid4

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_r_account_details import ShowRAccountDetailsUseCase
from arbeitszeit_web.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)
from tests.datetime_service import FakeDatetimeService
from tests.translator import FakeTranslator

from .dependency_injection import get_dependency_injector

DEFAULT_INFO1 = ShowRAccountDetailsUseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_liquid_means,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
)

DEFAULT_INFO2 = ShowRAccountDetailsUseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20.103),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(TestCase):
    def setUp(self) -> None:
        self.injector = get_dependency_injector()
        self.trans = self.injector.get(FakeTranslator)
        self.datetime_service = self.injector.get(FakeDatetimeService)
        self.presenter = self.injector.get(ShowRAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self):
        ACCOUNT_BALANCE = Decimal(100.007)
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.trans.gettext("Credit"))
        self.assertEqual(
            trans.date,
            self.datetime_service.format_datetime(
                date=DEFAULT_INFO1.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(
            trans.transaction_volume, str(round(DEFAULT_INFO1.transaction_volume, 2))
        )
        self.assertIsInstance(trans.purpose, str)

    def test_return_two_transactions_when_two_transactions_took_place(self):
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self):
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: List[ShowRAccountDetailsUseCase.TransactionInfo] = [],
        account_balance: Decimal = Decimal(0),
        plot: ShowRAccountDetailsUseCase.PlotDetails = ShowRAccountDetailsUseCase.PlotDetails(
            [], []
        ),
    ):
        return ShowRAccountDetailsUseCase.Response(
            company_id, transactions, account_balance, plot
        )
