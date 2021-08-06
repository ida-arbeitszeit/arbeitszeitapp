from abc import ABC, abstractmethod
from typing import Iterator, List, Union

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    ProductOffer,
    Purchase,
    SocialAccounting,
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

    @abstractmethod
    def get_purchases_descending_by_date(
        self, user: Union[Member, Company]
    ) -> Iterator[Purchase]:
        pass


class PlanRepository(ABC):
    @abstractmethod
    def add(self, plan: Plan) -> None:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def all_transactions_sent_by_account(
        self, account: Account
    ) -> Iterator[Transaction]:
        pass

    @abstractmethod
    def all_transactions_received_by_account(
        self, account: Account
    ) -> Iterator[Transaction]:
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


class AccountOwnerRepository(ABC):
    @abstractmethod
    def get_account_owner(
        self, account: Account
    ) -> Union[Member, Company, SocialAccounting]:
        pass
