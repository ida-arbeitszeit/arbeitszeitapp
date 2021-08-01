from typing import Iterator, List, Union

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import Company, Member, ProductOffer, Purchase, Transaction


@singleton
class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)

    def get_purchases_descending_by_date(self, user: Union[Member, Company]):
        # order purchases by purchase_date
        self.purchases.sort(key=lambda x: x.purchase_date, reverse=True)

        for purchase in self.purchases:
            if purchase.buyer is user:
                yield purchase


@singleton
class TransactionRepository(interfaces.TransactionRepository):
    @inject
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []

    def add(self, transaction: Transaction) -> None:
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


@singleton
class CompanyWorkerRepository(interfaces.CompanyWorkerRepository):
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        if worker not in company.workers:
            company.workers.append(worker)

    def get_company_workers(self, company: Company) -> List[Member]:
        return company.workers
