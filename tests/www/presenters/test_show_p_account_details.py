from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_p_account_details import (
    ShowPAccountDetailsUseCase as UseCase,
)
from arbeitszeit_web.www.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from tests.www.base_test_case import BaseTestCase

DEFAULT_INFO1 = UseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_fixed_means,
    date=datetime.now(),
    transaction_volume=Decimal(10.002),
    purpose="Test purpose",
)

DEFAULT_INFO2 = UseCase.TransactionInfo(
    transaction_type=TransactionTypes.credit_for_wages,
    date=datetime.now(),
    transaction_volume=Decimal(20),
    purpose="Test purpose",
)


class CompanyTransactionsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPAccountDetailsPresenter)

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

    def test_that_sum_of_planned_p_is_rounded_to_two_decimal_places(self) -> None:
        response = self._use_case_response(sum_of_planned_p=Decimal(10.002))
        view_model = self.presenter.present(response)
        assert view_model.sum_of_planned_p == "10.00"

    def test_that_sum_of_consumed_p_is_rounded_to_two_decimal_places(self) -> None:
        response = self._use_case_response(sum_of_consumed_p=Decimal(10.002))
        view_model = self.presenter.present(response)
        assert view_model.sum_of_consumed_p == "10.00"

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
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Accounts")
        assert navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_account_p_and_no_url_set(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account p")
        assert navbar_item.url is None

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transactions: List[UseCase.TransactionInfo] | None = None,
        sum_of_planned_p: Decimal = Decimal(0),
        sum_of_consumed_p: Decimal = Decimal(0),
        account_balance: Decimal = Decimal(0),
        plot: UseCase.PlotDetails | None = None,
    ) -> UseCase.Response:
        if transactions is None:
            transactions = []
        if plot is None:
            plot = UseCase.PlotDetails([], [])
        return UseCase.Response(
            company_id=company_id,
            transactions=transactions,
            sum_of_planned_p=sum_of_planned_p,
            sum_of_consumed_p=sum_of_consumed_p,
            account_balance=account_balance,
            plot=plot,
        )
