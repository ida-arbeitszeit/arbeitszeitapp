from injector import inject

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import Purchase


class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)
