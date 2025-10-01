from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.anonymization import ANONYMIZED_STR
from arbeitszeit.interactors import show_prd_account_details
from arbeitszeit.services.account_details import (
    AccountTransfer,
    TransferParty,
)
from arbeitszeit.transfers import TransferType
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ShowPRDAccountDetailsPresenter:
    @dataclass
    class TransferInfo:
        transfer_type: str
        date: str
        transfer_volume: str
        is_debit_transfer: bool
        peer_name: str
        peer_type_icon: str

    @dataclass
    class ViewModel:
        transfers: list[ShowPRDAccountDetailsPresenter.TransferInfo]
        show_transfers: bool
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def present(
        self, interactor_response: show_prd_account_details.Response
    ) -> ViewModel:
        transfers = [
            self._create_info(transfer) for transfer in interactor_response.transfers
        ]
        return self.ViewModel(
            transfers=transfers,
            show_transfers=bool(transfers),
            account_balance=str(round(interactor_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_prd_account(
                interactor_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=interactor_response.company_id
                    ),
                ),
                NavbarItem(
                    text=self.translator.gettext("Account prd"),
                    url=None,
                ),
            ],
        )

    def _create_info(self, transfer: AccountTransfer) -> TransferInfo:
        return self.TransferInfo(
            transfer_type=self._get_transfer_type(transfer),
            date=self.datetime_formatter.format_datetime(
                date=transfer.date, fmt="%d.%m.%Y %H:%M"
            ),
            transfer_volume=str(round(transfer.volume, 2)),
            is_debit_transfer=transfer.is_debit_transfer,
            peer_name=self._get_transfer_party_name(
                transfer.transfer_party, transfer.debtor_equals_creditor
            ),
            peer_type_icon=self._get_transfer_party_type_icon(
                transfer.transfer_party, transfer.debtor_equals_creditor
            ),
        )

    def _get_transfer_type(self, transfer: AccountTransfer) -> str:
        match transfer.type:
            case TransferType.credit_p | TransferType.credit_r | TransferType.credit_a:
                return self.translator.gettext("Debit expected sales")
            case (
                TransferType.private_consumption
                | TransferType.productive_consumption_p
                | TransferType.productive_consumption_r
            ):
                return self.translator.gettext("Sale")
            case (
                TransferType.compensation_for_company
                | TransferType.compensation_for_coop
            ):
                return self.translator.gettext("Cooperation compensation")
            case _:
                return "Unknown transfer type"

    def _get_transfer_party_type_icon(
        self, transfer_party: TransferParty, debtor_equals_creditor: bool
    ) -> str:
        if debtor_equals_creditor:
            return ""
        match transfer_party.type.name:
            case "member":
                return "user"
            case "company":
                return "industry"
            case "cooperation":
                return "hands-helping"
            case _:
                return ""

    def _get_transfer_party_name(
        self, transfer_party: TransferParty, debtor_equals_creditor: bool
    ) -> str:
        if debtor_equals_creditor:
            return ""
        name = transfer_party.name
        if name is ANONYMIZED_STR:
            return self.translator.gettext("Anonymous worker")
        assert isinstance(name, str)
        return name
