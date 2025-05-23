from datetime import datetime
from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases import show_prd_account_details
from arbeitszeit_web.www.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from tests.www.base_test_case import BaseTestCase


class CompanyTransactionsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPRDAccountDetailsPresenter)

    def test_return_empty_list_when_no_transactions_took_place(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transactions, [])

    def test_do_not_show_transactions_if_no_transactions_took_place(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_transactions)

    @parameterized.expand(
        [
            (TransferType.credit_p),
            (TransferType.credit_r),
            (TransferType.credit_a),
        ]
    )
    def test_return_correct_info_when_one_transaction_of_granting_credit_took_place(
        self,
        transfer_type: TransferType,
    ) -> None:
        ACCOUNT_BALANCE = Decimal(100.007)
        TRANSFER_VOLUME = Decimal(5.3)
        transfer = self._get_transfer_info(
            transfer_type=transfer_type,
            volume=TRANSFER_VOLUME,
        )
        response = self._use_case_response(
            transfers=[transfer], account_balance=ACCOUNT_BALANCE
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
                date=transfer.date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
        )
        self.assertEqual(trans.transaction_volume, str(round(TRANSFER_VOLUME, 2)))

    def test_return_correct_info_when_one_private_consumption_took_place(
        self,
    ) -> None:
        ACCOUNT_BALANCE = Decimal(100.007)
        TRANSFER_VOLUME = Decimal(5.3)
        transfer = self._get_transfer_info(
            transfer_type=TransferType.private_consumption,
            volume=TRANSFER_VOLUME,
        )
        response = self._use_case_response(
            transfers=[transfer], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transactions[0]
        self.assertEqual(trans.transaction_type, self.translator.gettext("Sale"))
        self.assertEqual(
            trans.date,
            self.datetime_service.format_datetime(
                date=transfer.date,
                zone="Europe/Berlin",
                fmt="%d.%m.%Y %H:%M",
            ),
        )
        self.assertEqual(trans.transaction_volume, str(round(TRANSFER_VOLUME, 2)))

    def test_return_two_transactions_when_two_transactions_took_place(self) -> None:
        response = self._use_case_response(
            transfers=[
                self._get_transfer_info(),
                self._get_transfer_info(),
            ],
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transactions), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_name_of_peer_is_shown_if_transaction_is_productive_consumption(
        self,
    ) -> None:
        expected_user_name = "some user name"
        response = self._use_case_response(
            transfers=[
                self._get_transfer_info(
                    transfer_type=TransferType.productive_consumption_p,
                    peer=show_prd_account_details.CompanyPeer(
                        id=uuid4(), name=expected_user_name
                    ),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_name == expected_user_name

    def test_name_of_peer_is_anonymized_if_transaction_is_private_consumption(
        self,
    ) -> None:
        expected_user_name = self.translator.gettext("Anonymous worker")
        response = self._use_case_response(
            transfers=[
                self._get_transfer_info(
                    transfer_type=TransferType.private_consumption,
                    peer=show_prd_account_details.MemberPeer(),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_name == expected_user_name

    def test_member_peer_icon_is_shown_if_transaction_was_with_member(
        self,
    ) -> None:
        response = self._use_case_response(
            transfers=[
                self._get_transfer_info(
                    transfer_type=TransferType.private_consumption,
                    peer=show_prd_account_details.MemberPeer(),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_type_icon == "user"

    def test_company_peer_icon_is_shown_if_transaction_was_with_company(
        self,
    ) -> None:
        response = self._use_case_response(
            transfers=[
                self._get_transfer_info(
                    transfer_type=TransferType.productive_consumption_p,
                    peer=show_prd_account_details.CompanyPeer(
                        id=uuid4(), name="company name"
                    ),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_type_icon == "industry"

    def test_peer_type_icon_is_empty_string_if_peer_is_none(
        self,
    ) -> None:
        transfer = show_prd_account_details.TransferInfo(
            type=TransferType.credit_p,
            date=datetime.now(),
            volume=Decimal(10.007),
            peer=None,
        )
        response = self._use_case_response(transfers=[transfer])
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_type_icon == ""

    def test_name_of_peer_is_empty_string_if_peer_is_none(
        self,
    ) -> None:
        transfer = show_prd_account_details.TransferInfo(
            type=TransferType.credit_p,
            date=datetime.now(),
            volume=Decimal(10.007),
            peer=None,
        )
        response = self._use_case_response(transfers=[transfer])
        view_model = self.presenter.present(response)
        assert view_model.transactions[0].peer_name == ""

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

    def test_second_navbar_item_has_text_account_prd_and_no_url(self) -> None:
        response = self._use_case_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account prd")
        assert navbar_item.url is None

    def _use_case_response(
        self,
        company_id: UUID = uuid4(),
        transfers: List[show_prd_account_details.TransferInfo] | None = None,
        account_balance: Decimal = Decimal(0),
        plot: show_prd_account_details.PlotDetails | None = None,
    ) -> show_prd_account_details.Response:
        if transfers is None:
            transfers = []
        if plot is None:
            plot = show_prd_account_details.PlotDetails([], [])
        return show_prd_account_details.Response(
            company_id, transfers, account_balance, plot
        )

    def _get_transfer_info(
        self,
        transfer_type: TransferType | None = None,
        peer: (
            show_prd_account_details.MemberPeer
            | show_prd_account_details.CompanyPeer
            | None
        ) = None,
        volume: Decimal = Decimal(10.007),
    ) -> show_prd_account_details.TransferInfo:
        if transfer_type is None:
            transfer_type = TransferType.private_consumption
        if peer is None:
            peer = show_prd_account_details.MemberPeer()
        return show_prd_account_details.TransferInfo(
            type=transfer_type,
            date=datetime.now(),
            volume=volume,
            peer=peer,
        )
