from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases import show_a_account_details
from arbeitszeit_web.www.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from tests.www.base_test_case import BaseTestCase

DEFAULT_INFO1 = show_a_account_details.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(10.007),
    purpose="Test purpose",
)

DEFAULT_INFO2 = show_a_account_details.TransactionInfo(
    transaction_type=TransactionTypes.payment_of_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowAAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_return_correct_info_when_one_transaction_took_place(self) -> None:
        ACCOUNT_BALANCE = Decimal("100.007")
        response = self._use_case_response(
            transactions=[DEFAULT_INFO1], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.translator.gettext("Credit"))
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

    def test_view_contains_two_navbar_items(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_company_accounts(
        self,
    ) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Accounts")
        assert navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_account_a_and_no_url(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account a")
        assert navbar_item.url is None

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: List[show_a_account_details.TransactionInfo] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: show_a_account_details.PlotDetails | None = None,
    ) -> show_a_account_details.Response:
        if transactions is None:
            transactions = []
        if plot is None:
            plot = show_a_account_details.PlotDetails([], [])
        return show_a_account_details.Response(
            company_id, transactions, account_balance, plot
        )
