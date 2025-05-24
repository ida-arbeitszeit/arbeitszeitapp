from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases import show_r_account_details
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ShowRAccountDetailsPresenter:
    @dataclass
    class TransactionInfo:
        transaction_type: str
        date: str
        transaction_volume: str

    @dataclass
    class ViewModel:
        transactions: List[ShowRAccountDetailsPresenter.TransactionInfo]
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def present(self, use_case_response: show_r_account_details.Response) -> ViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transfers
        ]
        return self.ViewModel(
            transactions=transactions,
            account_balance=str(round(use_case_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_r_account(
                use_case_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=use_case_response.company_id
                    ),
                ),
                NavbarItem(text=self.translator.gettext("Account r"), url=None),
            ],
        )

    def _create_info(
        self, transfer: show_r_account_details.TransferInfo
    ) -> TransactionInfo:
        transaction_type = (
            self.translator.gettext("Consumption")
            if transfer.type == TransferType.productive_consumption_r
            else self.translator.gettext("Credit")
        )
        return self.TransactionInfo(
            transaction_type,
            self.datetime_formatter.format_datetime(
                date=transfer.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            str(round(transfer.volume, 2)),
        )
