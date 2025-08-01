from __future__ import annotations

from dataclasses import dataclass

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases import show_prd_account_details
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
        self, use_case_response: show_prd_account_details.Response
    ) -> ViewModel:
        transfers = [
            self._create_info(transfer) for transfer in use_case_response.transfers
        ]
        return self.ViewModel(
            transfers=transfers,
            show_transfers=bool(transfers),
            account_balance=str(round(use_case_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_prd_account(
                use_case_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=use_case_response.company_id
                    ),
                ),
                NavbarItem(
                    text=self.translator.gettext("Account prd"),
                    url=None,
                ),
            ],
        )

    def _create_info(
        self, transfer: show_prd_account_details.TransferInfo
    ) -> TransferInfo:
        return self.TransferInfo(
            transfer_type=self._get_transfer_type(transfer),
            date=self.datetime_formatter.format_datetime(
                date=transfer.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            transfer_volume=str(round(transfer.volume, 2)),
            peer_name=self._get_peer_name(transfer.peer),
            peer_type_icon=self._get_peer_type_icon(transfer.peer),
        )

    def _get_transfer_type(
        self, transfer: show_prd_account_details.TransferInfo
    ) -> str:
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
                raise ValueError(f"Unknown transfer type: {transfer.type}")

    def _get_peer_type_icon(
        self,
        peer: (
            show_prd_account_details.MemberPeer
            | show_prd_account_details.CompanyPeer
            | show_prd_account_details.CooperationPeer
            | None
        ),
    ) -> str:
        if isinstance(peer, show_prd_account_details.MemberPeer):
            return "user"
        elif isinstance(peer, show_prd_account_details.CompanyPeer):
            return "industry"
        elif isinstance(peer, show_prd_account_details.CooperationPeer):
            return "hands-helping"
        else:
            return ""

    def _get_peer_name(
        self,
        peer: (
            show_prd_account_details.MemberPeer
            | show_prd_account_details.CompanyPeer
            | show_prd_account_details.CooperationPeer
            | None
        ),
    ) -> str:
        if isinstance(peer, show_prd_account_details.MemberPeer):
            return self.translator.gettext("Anonymous worker")
        elif isinstance(peer, show_prd_account_details.CompanyPeer):
            return peer.name
        elif isinstance(peer, show_prd_account_details.CooperationPeer):
            return peer.name
        else:
            return ""
