from decimal import Decimal
from arbeitszeit.entities import Account, Transaction


class TransactionFactory:
    def create_transaction(
        self,
        account_from: Account,
        account_to: Account,
        amount: Decimal,
        purpose: str,
    ) -> Transaction:
        return Transaction(account_from, account_to, amount, purpose)
