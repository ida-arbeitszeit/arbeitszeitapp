from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List

from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases.get_company_transactions import (
    GetCompanyTransactionsResponse,
    TransactionInfo,
)


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: datetime
    transaction_volume: Decimal
    account: str
    purpose: str


@dataclass
class GetCompanyTransactionsViewModel:
    transactions: List[ViewModelTransactionInfo]


class GetCompanyTransactionsPresenter:
    def present(
        self, use_case_response: GetCompanyTransactionsResponse
    ) -> GetCompanyTransactionsViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]

        return GetCompanyTransactionsViewModel(transactions=transactions)

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        account = self._get_account(transaction.account_type)
        return ViewModelTransactionInfo(
            transaction.type_of_transaction.value,
            transaction.date,
            round(transaction.transaction_volume, 2),
            account,
            transaction.purpose,
        )

    def _get_account(self, account_type: AccountTypes) -> str:
        return type_to_string_dict[account_type]


type_to_string_dict = {
    AccountTypes.p: "Account p",
    AccountTypes.r: "Account r",
    AccountTypes.a: "Account a",
    AccountTypes.prd: "Account prd",
}
