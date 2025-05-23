from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.transfers.transfer_type import TransferType
from arbeitszeit.use_cases.show_p_account_details import ShowPAccountDetailsUseCase
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ShowPAccountDetailsPresenter:
    @dataclass
    class TransactionInfo:
        transaction_type: str
        date: str
        transaction_volume: str

    @dataclass
    class ViewModel:
        transactions: List[ShowPAccountDetailsPresenter.TransactionInfo]
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def present(
        self, use_case_response: ShowPAccountDetailsUseCase.Response
    ) -> ViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transfers
        ]
        return self.ViewModel(
            transactions=transactions,
            account_balance=str(round(use_case_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_p_account(
                use_case_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=use_case_response.company_id
                    ),
                ),
                NavbarItem(text=self.translator.gettext("Account p"), url=None),
            ],
        )

    def _create_info(
        self, transfer: ShowPAccountDetailsUseCase.TransferInfo
    ) -> TransactionInfo:
        transaction_type = (
            self.translator.gettext("Consumption")
            if transfer.type == TransferType.productive_consumption_p
            else self.translator.gettext("Credit")
        )
        return self.TransactionInfo(
            transaction_type,
            self.datetime_formatter.format_datetime(
                date=transfer.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            str(round(transfer.volume, 2)),
        )
