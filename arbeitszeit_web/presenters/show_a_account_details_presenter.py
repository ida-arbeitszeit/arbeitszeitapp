from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_a_account_details import ShowAAccountDetailsUseCase
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import PlotsUrlIndex


@dataclass
class ShowAAccountDetailsPresenter:
    @dataclass
    class TransactionInfo:
        transaction_type: str
        date: datetime
        transaction_volume: Decimal
        purpose: str

    @dataclass
    class ViewModel:
        transactions: List[ShowAAccountDetailsPresenter.TransactionInfo]
        account_balance: str
        plot_url: str

    trans: Translator
    url_index: PlotsUrlIndex

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
        )

    def _create_info(
        self, transaction: ShowAAccountDetailsUseCase.TransactionInfo
    ) -> TransactionInfo:
        transaction_type = (
            self.trans.gettext("Payment")
            if transaction.transaction_type == TransactionTypes.payment_of_wages
            else self.trans.gettext("Credit")
        )
        return self.TransactionInfo(
            transaction_type,
            transaction.date,
            round(transaction.transaction_volume, 2),
            transaction.purpose,
        )
