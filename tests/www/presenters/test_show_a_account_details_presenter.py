from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.transfers import TransferType
from arbeitszeit.use_cases import show_a_account_details
from arbeitszeit_web.www.presenters.show_a_account_details_presenter import (
    ShowAAccountDetailsPresenter,
)
from tests.www.base_test_case import BaseTestCase


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
        transaction = self._get_use_case_transaction_info()
        response = self._use_case_response(
            transactions=[transaction], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.translator.gettext("Credit"))
        self.assertEqual(
            trans.date,
            self.datetime_service.format_datetime(
                date=transaction.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(
            trans.transaction_volume, str(round(transaction.transfer_volume, 2))
        )

    def test_return_two_transactions_when_two_transactions_took_place(self) -> None:
        response = self._use_case_response(
            transactions=[
                self._get_use_case_transaction_info(),
                self._get_use_case_transaction_info(),
            ],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    @parameterized.expand(
        [
            (TransferType.credit_a, "Credit"),
            (TransferType.credit_public_a, "Credit"),
            (TransferType.work_certificates, "Payment"),
        ]
    )
    def test_presenter_shows_correct_string_for_each_transfer_type(
        self,
        transaction_type: TransferType,
        expected_transaction_type: str,
    ) -> None:
        transaction = self._get_use_case_transaction_info(
            transaction_type=transaction_type
        )
        response = self._use_case_response(transactions=[transaction])
        view_model = self.presenter.present(response)
        self.assertEqual(
            view_model.transactions[0].transaction_type,
            self.translator.gettext(expected_transaction_type),
        )

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

    def _get_use_case_transaction_info(
        self,
        transaction_type: TransferType = TransferType.credit_a,
        date: datetime | None = None,
        transaction_volume: Decimal = Decimal(10),
    ) -> show_a_account_details.TransferInfo:
        if date is None:
            date = self.datetime_service.now()
        return show_a_account_details.TransferInfo(
            transaction_type, date, transaction_volume
        )

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: list[show_a_account_details.TransferInfo] | None = None,
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
