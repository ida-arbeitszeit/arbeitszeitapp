from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Iterator, List, Union
from uuid import UUID

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    ProductionCosts,
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

    @abstractmethod
    def get_member_workplaces(self, member: UUID) -> List[Company]:
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
    def create_plan(
        self,
        planner: Company,
        costs: ProductionCosts,
        product_name: str,
        production_unit: str,
        amount: int,
        description: str,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> Plan:
        pass

    @abstractmethod
    def activate_plan(self, plan: Plan, activation_date: datetime) -> None:
        pass

    @abstractmethod
    def set_plan_as_expired(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def renew_plan(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def set_expiration_relative(self, plan: Plan, days: int) -> None:
        pass

    @abstractmethod
    def set_expiration_date(self, plan: Plan, expiration_date: datetime) -> None:
        pass

    @abstractmethod
    def set_last_certificate_payout(self, plan: Plan, last_payout: datetime) -> None:
        pass

    @abstractmethod
    def get_plan_by_id(self, id: UUID) -> Plan:
        pass

    @abstractmethod
    def all_active_plans(self) -> Iterator[Plan]:
        pass

    @abstractmethod
    def count_active_plans(self) -> int:
        pass

    @abstractmethod
    def count_active_public_plans(self) -> int:
        pass

    @abstractmethod
    def avg_timeframe_of_active_plans(self) -> Decimal:
        pass

    @abstractmethod
    def sum_of_active_planned_work(self) -> Decimal:
        pass

    @abstractmethod
    def sum_of_active_planned_resources(self) -> Decimal:
        pass

    @abstractmethod
    def sum_of_active_planned_means(self) -> Decimal:
        pass

    @abstractmethod
    def all_plans_approved_and_not_expired(self) -> Iterator[Plan]:
        pass

    @abstractmethod
    def all_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        pass

    @abstractmethod
    def all_productive_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        pass

    @abstractmethod
    def all_public_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        pass

    @abstractmethod
    def get_approved_plans_created_before(self, timestamp: datetime) -> Iterator[Plan]:
        pass

    @abstractmethod
    def delete_plan(self, plan_id: UUID) -> None:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    def create_transaction(
        self,
        date: datetime,
        sending_account: Account,
        receiving_account: Account,
        amount: Decimal,
        purpose: str,
    ) -> Transaction:
        pass

    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        pass

    @abstractmethod
    def all_transactions_sent_by_account(self, account: Account) -> List[Transaction]:
        pass

    @abstractmethod
    def all_transactions_received_by_account(
        self, account: Account
    ) -> List[Transaction]:
        pass


class AccountRepository(ABC):
    @abstractmethod
    def create_account(self, account_type: AccountTypes) -> Account:
        pass

    @abstractmethod
    def get_account_balance(self, account: Account) -> Decimal:
        pass


class OfferRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: UUID) -> ProductOffer:
        pass

    @abstractmethod
    def query_offers_by_name(self, query: str) -> Iterator[ProductOffer]:
        pass

    @abstractmethod
    def query_offers_by_description(self, query: str) -> Iterator[ProductOffer]:
        pass

    @abstractmethod
    def all_active_offers(self) -> Iterator[ProductOffer]:
        pass

    @abstractmethod
    def create_offer(
        self,
        plan: Plan,
        creation_datetime: datetime,
        name: str,
        description: str,
    ) -> ProductOffer:
        pass

    @abstractmethod
    def count_active_offers_without_plan_duplicates(self) -> int:
        pass

    @abstractmethod
    def delete_offer(self, id: UUID) -> None:
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

    @abstractmethod
    def count_registered_members(self) -> int:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Member:
        pass


class AccountOwnerRepository(ABC):
    @abstractmethod
    def get_account_owner(
        self, account: Account
    ) -> Union[Member, Company, SocialAccounting]:
        pass


class CompanyRepository(ABC):
    @abstractmethod
    def create_company(
        self,
        email: str,
        name: str,
        password: str,
        means_account: Account,
        labour_account: Account,
        resource_account: Account,
        products_account: Account,
    ) -> Company:
        pass

    @abstractmethod
    def has_company_with_email(self, email: str) -> bool:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Company:
        pass

    @abstractmethod
    def count_registered_companies(self) -> int:
        pass
