from dataclasses import dataclass
from typing import List, Union

from injector import inject

from .entities import Company, Member, Transaction
from .repositories import TransactionRepository


@inject
@dataclass
class UserAccountingService:
    transaction_repository: TransactionRepository

    def _get_all_transactions_sorted(
        self, user: Union[Member, Company]
    ) -> List[Transaction]:
        all_transactions = set()
        for account in user.accounts():
            all_transactions.update(
                self.transaction_repository.all_transactions_sent_by_account(account)
            )
            all_transactions.update(
                self.transaction_repository.all_transactions_received_by_account(
                    account
                )
            )
        all_transactions_sorted = sorted(
            all_transactions, key=lambda x: x.date, reverse=True
        )
        return all_transactions_sorted
