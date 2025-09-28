from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.interactors import show_r_account_details
from arbeitszeit.services.account_details import (
    PlotDetails,
    TransferParty,
    TransferPartyType,
)
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.www.presenters.show_r_account_details_presenter import (
    ShowRAccountDetailsPresenter,
)
from tests.datetime_service import datetime_min_utc
from tests.translator import FakeTranslator
from tests.www.base_test_case import BaseTestCase


class ShowRAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.trans = self.injector.get(FakeTranslator)
        self.presenter = self.injector.get(ShowRAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert not view_model.transfers

    def test_return_correct_info_when_one_transfer_took_place(self) -> None:
        EXPECTED_ACCOUNT_BALANCE = Decimal(100.007)
        EXPECTED_DATE = datetime_min_utc()
        EXPECTED_TYPE = TransferType.credit_r
        EXPECTED_VOLUME = Decimal(10.007)
        response = self.get_interactor_response(
            transfers=[
                self.get_transfer_info(
                    date=EXPECTED_DATE,
                    type=EXPECTED_TYPE,
                    volume=EXPECTED_VOLUME,
                )
            ],
            account_balance=EXPECTED_ACCOUNT_BALANCE,
        )
        view_model = self.presenter.present(response)
        assert len(view_model.transfers) == 1
        assert view_model.account_balance == str(round(EXPECTED_ACCOUNT_BALANCE, 2))
        transfer = view_model.transfers[0]
        assert transfer.transfer_type == self.trans.gettext("Credit")
        assert transfer.date == self.datetime_formatter.format_datetime(
            date=EXPECTED_DATE, fmt="%d.%m.%Y %H:%M"
        )
        assert transfer.transfer_volume == str(round(EXPECTED_VOLUME, 2))

    @parameterized.expand([(True,), (False,)])
    def test_that_debit_transfer_are_shown_as_such(
        self,
        is_debit: bool,
    ) -> None:
        response = self.get_interactor_response(
            transfers=[self.get_transfer_info(is_debit=is_debit)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self.get_interactor_response(
            transfers=[
                self.get_transfer_info(),
                self.get_transfer_info(),
            ],
            account_balance=Decimal(100),
        )
        view_model = self.presenter.present(response)
        assert len(view_model.transfers) == 2

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert view_model.plot_url
        assert str(response.company_id) in view_model.plot_url

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_my_accounts(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert view_model.navbar_items[0].text == self.translator.gettext("Accounts")
        assert view_model.navbar_items[
            0
        ].url == self.url_index.get_company_accounts_url(company_id=response.company_id)

    def test_second_navbar_item_has_text_account_r_and_no_url(self) -> None:
        response = self.get_interactor_response()
        view_model = self.presenter.present(response)
        assert view_model.navbar_items[1].text == self.translator.gettext("Account r")
        assert view_model.navbar_items[1].url is None

    def get_transfer_info(
        self,
        type: TransferType = TransferType.credit_r,
        date: datetime | None = None,
        volume=Decimal(10),
        is_debit: bool = False,
    ) -> show_r_account_details.AccountTransfer:
        if date is None:
            date = datetime_min_utc()
        return show_r_account_details.AccountTransfer(
            type=type,
            date=date,
            volume=volume,
            is_debit_transfer=is_debit,
            transfer_party=TransferParty(
                type=TransferPartyType.company,
                id=uuid4(),
                name="Some counter party name",
            ),
        )

    def get_interactor_response(
        self,
        company_id: UUID = uuid4(),
        transfers: List[show_r_account_details.AccountTransfer] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: PlotDetails | None = None,
    ) -> show_r_account_details.Response:
        if transfers is None:
            transfers = []
        if plot is None:
            plot = PlotDetails([], [])
        return show_r_account_details.Response(
            company_id, transfers, account_balance, plot
        )
