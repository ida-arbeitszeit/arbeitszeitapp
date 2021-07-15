from typing import Iterator, List

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import ProductOffer, Purchase, Transaction


@singleton
class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)


@singleton
class TransactionRepository(interfaces.TransactionRepository):
    @inject
    def __init__(self):
        self.transactions = []

    def add(self, transaction: Transaction):
        self.transactions.append(transaction)


@singleton
class OfferRepository(interfaces.OfferRepository):
    @inject
    def __init__(self) -> None:
        self.offers: List[ProductOffer] = []

    def all_active_offers(self) -> Iterator[ProductOffer]:
        yield from self.offers

    def query_offers_by_name(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.name:
                yield offer

    def query_offers_by_description(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.description:
                yield offer

    def add_offer(self, offer: ProductOffer) -> None:
        self.offers.append(offer)
