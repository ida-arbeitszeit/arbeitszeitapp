from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases.show_p_account_details import (
    ShowPAccountDetailsUseCase as UseCase,
)
from arbeitszeit_web.www.presenters.show_p_account_details_presenter import (
    ShowPAccountDetailsPresenter,
)
from tests.www.base_test_case import BaseTestCase


class ShowPAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transfers, [])

    def test_return_correct_info_when_one_transfer_took_place(self) -> None:
        EXPECTED_ACCOUNT_BALANCE = Decimal(100.007)
        transfer = self.get_transfer_info()
        response = self.get_use_case_response(
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
            self.datetime_service.format_datetime(
                date=transfer.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
        )
        self.assertEqual(
            view_model_transfer.transfer_volume, str(round(transfer.volume, 2))
        )

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self.get_use_case_response(
            transfers=[self.get_transfer_info(), self.get_transfer_info()],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_my_accounts(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Accounts")
        assert navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_account_p_and_no_url_set(self) -> None:
        response = self.get_use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account p")
        assert navbar_item.url is None

    def get_transfer_info(
        self,
        type: TransferType = TransferType.credit_p,
        date: datetime = datetime.min,
        volume: Decimal = Decimal(10.002),
    ) -> UseCase.TransferInfo:
        return UseCase.TransferInfo(type=type, date=date, volume=volume)

    def get_use_case_response(
        self,
        company_id: UUID = uuid4(),
        transfers: list[UseCase.TransferInfo] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: UseCase.PlotDetails | None = None,
    ) -> UseCase.Response:
        if transfers is None:
            transfers = []
        if plot is None:
            plot = UseCase.PlotDetails([], [])
        return UseCase.Response(
            company_id=company_id,
            transfers=transfers,
            account_balance=account_balance,
            plot=plot,
        )
