from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_p_account_details import (
    ShowPAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: datetime
    transaction_volume: Decimal
    purpose: str


@dataclass
class ShowPAccountDetailsResponseViewModel:
    transactions: List[ViewModelTransactionInfo]
    account_balance: Decimal


@dataclass
class ShowPAccountDetailsPresenter:
    translator: Translator

    def present(
        self, use_case_response: ShowPAccountDetailsResponse
    ) -> ShowPAccountDetailsResponseViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        return ShowPAccountDetailsResponseViewModel(
            transactions=transactions, account_balance=use_case_response.account_balance
        )

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        transaction_type = (
            self.translator.gettext("Payment")
            if transaction.transaction_type == TransactionTypes.payment_of_fixed_means
            else self.translator.gettext("Credit")
        )
        return ViewModelTransactionInfo(
            transaction_type,
            transaction.date,
            round(transaction.transaction_volume, 2),
            transaction.purpose,
        )
