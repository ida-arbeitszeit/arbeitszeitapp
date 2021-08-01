from abc import ABC, abstractmethod
from typing import Iterator, List

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    ProductOffer,
    Purchase,
    Transaction,
)


class CompanyWorkerRepository(ABC):
    @abstractmethod
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        pass

    @abstractmethod
    def get_company_workers(self, company: Company) -> List[Member]:
        pass


class PurchaseRepository(ABC):
    @abstractmethod
    def add(self, purchase: Purchase) -> None:
        pass


class PlanRepository(ABC):
    @abstractmethod
    def add(self, plan: Plan) -> None:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        pass


class AccountRepository(ABC):
    @abstractmethod
    def add(self, account: Account) -> None:
        pass

    @abstractmethod
    def create_account(self, account_type: AccountTypes) -> Account:
        pass


class OfferRepository(ABC):
    @abstractmethod
    def query_offers_by_name(self, query: str) -> Iterator[ProductOffer]:
        pass

    @abstractmethod
    def query_offers_by_description(self, query: str) -> Iterator[ProductOffer]:
        pass

    @abstractmethod
    def all_active_offers(self) -> Iterator[ProductOffer]:
        pass


class MemberRepository(ABC):
    @abstractmethod
    def create_member(
        self, email: str, name: str, password: str, account: Account
    ) -> Member:
        pass

    @abstractmethod
    def has_member_with_email(self, email: str) -> bool:
        pass
