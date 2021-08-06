from datetime import datetime
from decimal import Decimal

from arbeitszeit.entities import Account, Transaction


class TransactionFactory:
    def create_transaction(
        self,
        date: datetime,
        account_from: Account,
        account_to: Account,
        amount: Decimal,
        purpose: str,
    ) -> Transaction:
        return Transaction(date, account_from, account_to, amount, purpose)
