from __future__ import annotations

from dataclasses import dataclass
from typing import List

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_a_account_details import ShowAAccountDetailsUseCase
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
    datetime_service: DatetimeService

    def present(
        self, use_case_response: ShowAAccountDetailsUseCase.Response
    ) -> ViewModel:
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
                    url=self.url_index.get_my_accounts_url(),
                ),
                NavbarItem(text=self.translator.gettext("Account a"), url=None),
            ],
        )

    def _create_info(
        self, transaction: ShowAAccountDetailsUseCase.TransactionInfo
    ) -> TransactionInfo:
        transaction_type = (
            self.translator.gettext("Payment")
            if transaction.transaction_type == TransactionTypes.payment_of_wages
            else self.translator.gettext("Credit")
        )
        return self.TransactionInfo(
            transaction_type,
            self.datetime_service.format_datetime(
                date=transaction.date, zone="Europe/Berlin", fmt="%d.%m.%Y %H:%M"
            ),
            str(round(transaction.transaction_volume, 2)),
            transaction.purpose,
        )
