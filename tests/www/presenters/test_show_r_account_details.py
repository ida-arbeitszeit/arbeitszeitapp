from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_r_account_details import (
    ShowRAccountDetailsUseCase as UseCase,
)
from arbeitszeit_web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase

DEFAULT_INFO1 = UseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_liquid_means,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
)

DEFAULT_INFO2 = UseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20.103),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.trans = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(ShowRAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self) -> None:
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

    def test_return_two_transactions_when_two_transactions_took_place(self) -> None:
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1, DEFAULT_INFO2], account_balance=Decimal(100)
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_my_accounts(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        assert view_model.navbar_items[0].text == self.translator.gettext("Accounts")
        assert view_model.navbar_items[0].url == self.url_index.get_my_accounts_url()

    def test_second_navbar_item_has_text_account_r_and_no_url(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        assert view_model.navbar_items[1].text == self.translator.gettext("Account r")
        assert view_model.navbar_items[1].url is None

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: List[UseCase.TransactionInfo] = [],
        account_balance: Decimal = Decimal(0),
        plot: UseCase.PlotDetails = UseCase.PlotDetails([], []),
    ) -> UseCase.Response:
        return UseCase.Response(company_id, transactions, account_balance, plot)
