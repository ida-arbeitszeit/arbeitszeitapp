from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.transfers import TransferType
from arbeitszeit.use_cases import show_a_account_details
from arbeitszeit_web.formatters.datetime_formatter import DatetimeFormatter
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex
from arbeitszeit_web.www.navbar import NavbarItem


@dataclass
class ShowAAccountDetailsPresenter:
    @dataclass
    class TransactionInfo:
        transaction_type: str
        date: str
        transaction_volume: str
        purpose: str

    @dataclass
    class ViewModel:
        transactions: List[ShowAAccountDetailsPresenter.TransactionInfo]
        account_balance: str
        plot_url: str
        navbar_items: list[NavbarItem]

    translator: Translator
    url_index: UrlIndex
    datetime_formatter: DatetimeFormatter

    def present(self, use_case_response: show_a_account_details.Response) -> ViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        return self.ViewModel(
            transactions=transactions,
            account_balance=str(round(use_case_response.account_balance, 2)),
            plot_url=self.url_index.get_line_plot_of_company_a_account(
                use_case_response.company_id
            ),
            navbar_items=[
                NavbarItem(
                    text=self.translator.gettext("Accounts"),
                    url=self.url_index.get_company_accounts_url(
                        company_id=use_case_response.company_id
                    ),
                ),
                NavbarItem(text=self.translator.gettext("Account a"), url=None),
            ],
        )

    def _create_info(
        self, transaction: show_a_account_details.TransactionInfo
    ) -> TransactionInfo:
        return self.TransactionInfo(
            transaction_type=self._get_transfer_type(transaction.transaction_type),
            date=self.datetime_formatter.format_datetime(
                date=transaction.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            transaction_volume=str(round(transaction.transaction_volume, 2)),
            purpose=self._get_purpose(transaction.purpose),
        )

    def _get_transfer_type(self, transfer_type: TransferType) -> str:
        if transfer_type == TransferType.credit_a:
            return self.translator.gettext("Credit")
        else:
            return self.translator.gettext("Payment")

    def _get_purpose(self, purpose: str) -> str:
        return self.translator.gettext("Wages") if purpose == "Lohn" else purpose
