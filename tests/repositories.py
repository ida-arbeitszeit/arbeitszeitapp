from injector import inject

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import Purchase, Transaction


class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)


class TransactionRepository(interfaces.TransactionRepository):
    @inject
    def __init__(self):
        self.transactions = []

    def add(self, transaction: Transaction):
        self.transactions.append(transaction)
