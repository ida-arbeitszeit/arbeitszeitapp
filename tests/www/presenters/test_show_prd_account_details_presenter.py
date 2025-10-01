from decimal import Decimal
from typing import List
from uuid import UUID, uuid4

from parameterized import parameterized

from arbeitszeit.anonymization import ANONYMIZED_STR
from arbeitszeit.interactors import show_prd_account_details
from arbeitszeit.services.account_details import (
    AccountTransfer,
    TransferParty,
    TransferPartyType,
)
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.www.presenters.show_prd_account_details_presenter import (
    ShowPRDAccountDetailsPresenter,
)
from tests.datetime_service import datetime_min_utc
from tests.www.base_test_case import BaseTestCase


class ShowPRDAccountDetailsPresenterTests(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.presenter = self.injector.get(ShowPRDAccountDetailsPresenter)

    def test_return_empty_list_when_no_transfers_took_place(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        self.assertEqual(view_model.transfers, [])

    def test_do_not_show_transfers_if_no_transfers_took_place(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        self.assertFalse(view_model.show_transfers)

    @parameterized.expand(
        [
            (TransferType.credit_p),
            (TransferType.credit_r),
            (TransferType.credit_a),
        ]
    )
    def test_return_correct_info_when_one_transfer_of_granting_credit_took_place(
        self,
        transfer_type: TransferType,
    ) -> None:
        ACCOUNT_BALANCE = Decimal(100.007)
        TRANSFER_VOLUME = Decimal(5.3)
        transfer = self._get_transfer_info(
            transfer_type=transfer_type,
            volume=TRANSFER_VOLUME,
        )
        response = self._interactor_response(
            transfers=[transfer], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transfers[0]
        self.assertEqual(
            trans.transfer_type, self.translator.gettext("Debit expected sales")
        )
        self.assertEqual(
            trans.date,
            self.datetime_formatter.format_datetime(
                date=transfer.date,
                fmt="%d.%m.%Y %H:%M",
            ),
        )
        self.assertEqual(trans.transfer_volume, str(round(TRANSFER_VOLUME, 2)))

    def test_return_correct_info_when_one_private_consumption_took_place(
        self,
    ) -> None:
        ACCOUNT_BALANCE = Decimal(100.007)
        TRANSFER_VOLUME = Decimal(5.3)
        transfer = self._get_transfer_info(
            transfer_type=TransferType.private_consumption,
            volume=TRANSFER_VOLUME,
        )
        response = self._interactor_response(
            transfers=[transfer], account_balance=ACCOUNT_BALANCE
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        self.assertEqual(view_model.account_balance, str(round(ACCOUNT_BALANCE, 2)))
        trans = view_model.transfers[0]
        self.assertEqual(trans.transfer_type, self.translator.gettext("Sale"))
        self.assertEqual(
            trans.date,
            self.datetime_formatter.format_datetime(
                date=transfer.date,
                fmt="%d.%m.%Y %H:%M",
            ),
        )
        self.assertEqual(trans.transfer_volume, str(round(TRANSFER_VOLUME, 2)))

    def test_return_correct_transfer_type_info_shown_when_one_transfer_of_compensation_for_coop_took_place(
        self,
    ) -> None:
        transfer = self._get_transfer_info(
            transfer_type=TransferType.compensation_for_coop,
        )
        response = self._interactor_response(transfers=[transfer])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        trans = view_model.transfers[0]
        self.assertEqual(
            trans.transfer_type, self.translator.gettext("Cooperation compensation")
        )

    def test_return_correct_transfer_type_info_shown_when_one_transfer_of_compensation_for_company_took_place(
        self,
    ) -> None:
        transfer = self._get_transfer_info(
            transfer_type=TransferType.compensation_for_company,
        )
        response = self._interactor_response(transfers=[transfer])
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 1)
        trans = view_model.transfers[0]
        self.assertEqual(
            trans.transfer_type, self.translator.gettext("Cooperation compensation")
        )

    def test_return_two_transfers_when_two_transfers_took_place(self) -> None:
        response = self._interactor_response(
            transfers=[
                self._get_transfer_info(),
                self._get_transfer_info(),
            ],
        )
        view_model = self.presenter.present(response)
        self.assertTrue(len(view_model.transfers), 2)

    def test_presenter_returns_a_plot_url_with_company_id_as_parameter(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        self.assertTrue(view_model.plot_url)
        self.assertIn(str(response.company_id), view_model.plot_url)

    def test_name_of_other_party_is_shown_correctly_if_party_name_is_anonymized(
        self,
    ) -> None:
        response = self._interactor_response(
            transfers=[
                self._get_transfer_info(
                    transfer_party=TransferParty(
                        type=TransferPartyType.company, id=uuid4(), name=ANONYMIZED_STR
                    ),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].party_name == self.translator.gettext(
            "Anonymous worker"
        )

    def test_name_of_other_party_is_shown_correctly_if_party_name_is_not_anonymized(
        self,
    ) -> None:
        expected_name = "Some party name"
        response = self._interactor_response(
            transfers=[
                self._get_transfer_info(
                    transfer_party=TransferParty(
                        type=TransferPartyType.company, id=uuid4(), name=expected_name
                    ),
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].party_name == expected_name

    def test_that_name_of_other_party_is_empty_string_if_company_is_debtor_and_creditor(
        self,
    ) -> None:
        response = self._interactor_response(
            transfers=[self._get_transfer_info(debtor_equals_creditor=True)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].party_name == ""

    def test_that_icon_of_other_party_is_empty_string_if_company_is_debtor_and_creditor(
        self,
    ) -> None:
        response = self._interactor_response(
            transfers=[self._get_transfer_info(debtor_equals_creditor=True)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].party_icon == ""

    @parameterized.expand(
        [
            (TransferPartyType.member, "user"),
            (TransferPartyType.company, "industry"),
            (TransferPartyType.cooperation, "hands-helping"),
        ]
    )
    def test_that_correct_icon_is_shown_per_transfer_party_type(
        self, transfer_party_type: TransferPartyType, expected_icon: str
    ) -> None:
        response = self._interactor_response(
            transfers=[
                self._get_transfer_info(
                    transfer_party=TransferParty(
                        id=uuid4(),
                        name="Some party name",
                        type=transfer_party_type,
                    )
                )
            ]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].party_icon == expected_icon

    @parameterized.expand([(True,), (False,)])
    def test_that_debit_transfer_are_shown_as_such(
        self,
        is_debit: bool,
    ) -> None:
        response = self._interactor_response(
            transfers=[self._get_transfer_info(is_debit_transfer=is_debit)]
        )
        view_model = self.presenter.present(response)
        assert view_model.transfers[0].is_debit_transfer == is_debit

    def test_view_model_contains_two_navbar_items(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        assert len(view_model.navbar_items) == 2

    def test_first_navbar_item_has_text_accounts_and_url_to_my_accounts(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[0]
        assert navbar_item.text == self.translator.gettext("Accounts")
        assert navbar_item.url == self.url_index.get_company_accounts_url(
            company_id=response.company_id
        )

    def test_second_navbar_item_has_text_account_prd_and_no_url(self) -> None:
        response = self._interactor_response()
        view_model = self.presenter.present(response)
        navbar_item = view_model.navbar_items[1]
        assert navbar_item.text == self.translator.gettext("Account prd")
        assert navbar_item.url is None

    def _interactor_response(
        self,
        company_id: UUID = uuid4(),
        transfers: List[AccountTransfer] | None = None,
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
        transfer_party: TransferParty | None = None,
        volume: Decimal = Decimal(10.007),
        transfer_type: TransferType = TransferType.private_consumption,
        debtor_equals_creditor: bool = False,
        is_debit_transfer: bool = False,
    ) -> AccountTransfer:
        if transfer_party is None:
            transfer_party = TransferParty(
                id=uuid4(),
                name="Some party name",
                type=TransferPartyType.company,
            )
        return AccountTransfer(
            type=transfer_type,
            date=datetime_min_utc(),
            volume=volume,
            is_debit_transfer=is_debit_transfer,
            transfer_party=transfer_party,
            debtor_equals_creditor=debtor_equals_creditor,
        )
