from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.use_cases.get_account_p import GetAccountPResponse, TransactionInfo


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: datetime
    transaction_volume: Decimal
    purpose: str


@dataclass
class GetAccountPResponseViewModel:
    transactions: List[ViewModelTransactionInfo]
    account_balance: Decimal


class GetAccountPPresenter:
    def present(
        self, use_case_response: GetAccountPResponse
    ) -> GetAccountPResponseViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        account_balance = use_case_response.account_balance
        return GetAccountPResponseViewModel(
            transactions=transactions, account_balance=account_balance
        )

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        transaction_type = self._get_transaction_type(transaction)
        transaction_volume = self._get_transaction_volume(
            transaction.transaction_volume
        )
        return ViewModelTransactionInfo(
            transaction_type,
            transaction.date,
            transaction_volume,
            transaction.purpose,
        )

    def _get_transaction_type(self, transaction: TransactionInfo) -> str:
        return transaction.type_of_transaction.value

    def _get_transaction_volume(self, transaction_volume: Decimal) -> Decimal:
        return round(transaction_volume, 2)
