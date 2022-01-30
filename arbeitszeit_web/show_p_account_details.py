from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_p_account_details import (
    ShowPAccountDetailsResponse,
    TransactionInfo,
)


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


class ShowPAccountDetailsPresenter:
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
            "Payment"
            if transaction.transaction_type == TransactionTypes.payment_of_fixed_means
            else "Credit"
        )
        return ViewModelTransactionInfo(
            transaction_type,
            transaction.date,
            round(transaction.transaction_volume, 2),
            transaction.purpose,
        )
