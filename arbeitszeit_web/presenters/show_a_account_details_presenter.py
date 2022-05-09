from dataclasses import dataclass
from datetime import datetime
from typing import List

from arbeitszeit.transactions import TransactionTypes
from arbeitszeit.use_cases.show_a_account_details import (
    ShowAAccountDetailsResponse,
    TransactionInfo,
)
from arbeitszeit_web.translator import Translator


@dataclass
class ViewModelTransactionInfo:
    transaction_type: str
    date: datetime
    transaction_volume: str
    purpose: str


@dataclass
class ShowAAccountDetailsResponseViewModel:
    transactions: List[ViewModelTransactionInfo]
    account_balance: str


@dataclass
class ShowAAccountDetailsPresenter:
    translator: Translator

    def present(
        self, use_case_response: ShowAAccountDetailsResponse
    ) -> ShowAAccountDetailsResponseViewModel:
        transactions = [
            self._create_info(transaction)
            for transaction in use_case_response.transactions
        ]
        return ShowAAccountDetailsResponseViewModel(
            transactions=transactions,
            account_balance=str(round(use_case_response.account_balance, 2)),
        )

    def _create_info(self, transaction: TransactionInfo) -> ViewModelTransactionInfo:
        assert transaction.transaction_type in [
            TransactionTypes.payment_of_wages,
            TransactionTypes.credit_for_wages,
        ]
        transaction_type = (
            self.translator.gettext("Payment")
            if transaction.transaction_type == TransactionTypes.payment_of_wages
            else self.translator.gettext("Credit")
        )
        return ViewModelTransactionInfo(
            transaction_type,
            transaction.date,
            str(round(transaction.transaction_volume, 2)),
            transaction.purpose,
        )
