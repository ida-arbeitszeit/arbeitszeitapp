from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors.show_p_account_details import (
    ShowPAccountDetailsInteractor as Interactor,
)
from arbeitszeit.services.account_details import (
    AccountTransfer,
    PlotDetails,
    TransferParty,
    TransferPartyType,
)
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.www.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from tests.datetime_service import datetime_min_utc
from tests.www.base_test_case import BaseTestCase


class ShowPAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transfers, [])

    def test_return_correct_info_when_one_transfer_took_place(self) -> None:
        EXPECTED_ACCOUNT_BALANCE = Decimal(100.007)
        transfer = self.get_transfer_info()
        response = self.get_interactor_response(
            transfers=[transfer], account_balance=EXPECTED_ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        self.assertEqual(
            view_model.account_balance, str(round(EXPECTED_ACCOUNT_BALANCE, 2))
        )
        assert len(view_model.transfers) == 1
        view_model_transfer = view_model.transfers[0]
        self.assertEqual(
            view_model_transfer.transfer_type, self.translator.gettext("Credit")
        )
        self.assertEqual(
            view_model_transfer.date,
            self.datetime_formatter.format_datetime(
                date=transfer.date, fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(
            view_model_transfer.transfer_volume, str(round(transfer.volume, 2))
        )

    @parameterized.expand([(True,), (False,)])
    def test_that_debit_transfer_are_shown_as_such(
        self,
        is_debit: bool,
    ) -> None:
        response = self.get_interactor_response(
            transfers=[self.get_transfer_info(is_debit_transfer=is_debit)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self.get_interactor_response(
            transfers=[self.get_transfer_info(), self.get_transfer_info()],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_my_accounts(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Accounts")
        assert navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_account_p_and_no_url_set(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account p")
        assert navbar_item.url is None

    def get_transfer_info(
        self,
        type: TransferType = TransferType.credit_p,
        date: datetime = datetime_min_utc(),
        volume: Decimal = Decimal(10.002),
        is_debit_transfer: bool = False,
    ) -> AccountTransfer:
        return AccountTransfer(
            type=type,
            date=date,
            volume=volume,
            is_debit_transfer=is_debit_transfer,
            transfer_party=TransferParty(
                type=TransferPartyType.company,
                id=uuid4(),
                name="Some counter party name",
            ),
        )

    def get_interactor_response(
        self,
        company_id: UUID = uuid4(),
        transfers: list[AccountTransfer] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: PlotDetails | None = None,
    ) -> Interactor.Response:
        if transfers is None:
            transfers = []
        if plot is None:
            plot = PlotDetails([], [])
        return Interactor.Response(
            company_id=company_id,
            transfers=transfers,
            account_balance=account_balance,
            plot=plot,
        )
