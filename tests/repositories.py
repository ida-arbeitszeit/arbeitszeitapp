from decimal import Decimal
from typing import Iterator, List

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    ProductOffer,
    Purchase,
    Transaction,
)


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


@singleton
class AccountRepository(interfaces.AccountRepository):
    @inject
    def __init__(self):
        self.accounts = []
        self.latest_id = 0

    def __contains__(self, account: object) -> bool:
        if not isinstance(account, Account):
            return False
        return account in self.accounts

    def add(self, account: Account) -> None:
        assert account not in self
        self.accounts.append(account)

    def create_account(self, account_type: AccountTypes) -> Account:
        account = Account(
            id=self.latest_id,
            balance=Decimal(0),
            account_type=account_type,
            change_credit=lambda _: None,
        )
        self.latest_id += 1
        self.accounts.append(account)
        return account


@singleton
class MemberRepository(interfaces.MemberRepository):
    @inject
    def __init__(self):
        self.members = []
        self.last_id = 0

    def create_member(
        self, email: str, name: str, password: str, account: Account
    ) -> Member:
        self.last_id += 1
        member = Member(
            id=self.last_id,
            name=name,
            email=email,
            account=account,
        )
        self.members.append(member)
        return member

    def has_member_with_email(self, email: str) -> bool:
        for member in self.members:
            if member.email == email:
                return True
        return False
