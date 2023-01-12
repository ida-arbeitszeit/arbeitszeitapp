from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Generic, Iterable, Iterator, Optional, Protocol, TypeVar, Union
from uuid import UUID

from arbeitszeit.entities import (
    Account,
    Accountant,
    AccountTypes,
    Company,
    CompanyWorkInvite,
    Cooperation,
    Member,
    PayoutFactor,
    Plan,
    PlanDraft,
    ProductionCosts,
    Purchase,
    PurposesOfPurchases,
    SocialAccounting,
    Transaction,
)

T = TypeVar("T", covariant=True)
QueryResultT = TypeVar("QueryResultT", bound="QueryResult")


class QueryResult(Protocol, Generic[T]):
    def __iter__(self) -> Iterator[T]:
        ...

    def limit(self: QueryResultT, n: int) -> QueryResultT:
        ...

    def offset(self: QueryResultT, n: int) -> QueryResultT:
        ...

    def first(self) -> Optional[T]:
        ...

    def __len__(self) -> int:
        ...


class PlanResult(QueryResult[Plan], Protocol):
    def ordered_by_creation_date(self, ascending: bool = ...) -> PlanResult:
        ...

    def with_id_containing(self, query: str) -> PlanResult:
        ...

    def with_product_name_containing(self, query: str) -> PlanResult:
        ...

    def that_are_approved(self) -> PlanResult:
        ...

    def that_are_productive(self) -> PlanResult:
        ...

    def that_are_public(self) -> PlanResult:
        ...

    def that_are_cooperating(self) -> PlanResult:
        ...

    def planned_by(self, *company: UUID) -> PlanResult:
        ...

    def with_id(self, *id_: UUID) -> PlanResult:
        ...

    def without_completed_review(self) -> PlanResult:
        ...

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = ...
    ) -> PlanResult:
        ...

    def that_are_in_same_cooperation_as(self, plan: UUID) -> PlanResult:
        ...

    def that_are_active(self) -> PlanResult:
        ...

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> PlanResult:
        """If no cooperations are specified, then all the repository
        should return plans that are part of any cooperation.
        """

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> PlanResult:
        """If no companies are specified then the repository should
        return all plans that request cooperation with any
        coordinator.
        """

    def set_cooperation(self, cooperation: Optional[UUID]) -> int:
        """Set the associated cooperation of all matching plans to the
        one specified via the cooperation argument. Specifying `None`
        will unset the cooperation field. The return value counts all
        plans that were updated through this method.
        """

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> int:
        """Set the `requested_cooperation` field of all matching plans
        to the specified value.  A value `None` means that these plans
        are marked as not requesting membership in any
        cooperation. The return value counts all plans that were
        updated through this method.
        """

    def set_approval_date(self, approval_date: Optional[datetime]) -> int:
        """Set the approval date of all matching plans. The return
        value counts all the plans that were changed by this methods.
        """

    def set_approval_reason(self, reason: Optional[str]) -> int:
        """Set the approval reason for all matching plans. The return
        value counts all the plans that were changed by this method.
        """


class MemberResult(QueryResult[Member], Protocol):
    def working_at_company(self, company: UUID) -> MemberResult:
        ...

    def with_id(self, id_: UUID) -> MemberResult:
        ...

    def with_email_address(self, email: str) -> MemberResult:
        ...

    def set_confirmation_timestamp(self, timestamp: datetime) -> int:
        ...

    def that_are_confirmed(self) -> MemberResult:
        ...


class PurchaseResult(QueryResult[Purchase], Protocol):
    def ordered_by_creation_date(self, *, ascending: bool = ...) -> PurchaseResult:
        ...

    def where_buyer_is_company(
        self, *, company: Optional[UUID] = ...
    ) -> PurchaseResult:
        ...

    def where_buyer_is_member(self, *, member: Optional[UUID] = ...) -> PurchaseResult:
        ...


class CompanyResult(QueryResult[Company], Protocol):
    def with_id(self, id_: UUID) -> CompanyResult:
        ...

    def with_email_address(self, email: str) -> CompanyResult:
        ...

    def that_are_workplace_of_member(self, member: UUID) -> CompanyResult:
        ...

    def add_worker(self, member: UUID) -> int:
        ...


class TransactionResult(QueryResult[Transaction], Protocol):
    def where_account_is_sender_or_receiver(self, *account: UUID) -> TransactionResult:
        ...

    def where_account_is_sender(self, *account: UUID) -> TransactionResult:
        ...

    def where_account_is_receiver(self, *account: UUID) -> TransactionResult:
        ...

    def ordered_by_transaction_date(self, descending: bool = ...) -> TransactionResult:
        ...

    def where_sender_is_social_accounting(self) -> TransactionResult:
        ...


class AccountResult(QueryResult[Account], Protocol):
    def with_id(self, id_: UUID) -> AccountResult:
        ...


class PurchaseRepository(ABC):
    @abstractmethod
    def create_purchase_by_company(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        pass

    @abstractmethod
    def create_purchase_by_member(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
    ) -> Purchase:
        pass

    @abstractmethod
    def get_purchases(self) -> PurchaseResult:
        pass


class PlanRepository(ABC):
    @abstractmethod
    def create_plan_from_draft(self, draft_id: UUID) -> Optional[UUID]:
        pass

    @abstractmethod
    def activate_plan(self, plan: Plan, activation_date: datetime) -> None:
        pass

    @abstractmethod
    def set_plan_as_expired(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def set_active_days(self, plan: Plan, full_active_days: int) -> None:
        pass

    @abstractmethod
    def increase_payout_count_by_one(self, plan: Plan) -> None:
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
    def hide_plan(self, plan_id: UUID) -> None:
        pass

    @abstractmethod
    def toggle_product_availability(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def get_plans(self) -> PlanResult:
        pass


class TransactionRepository(ABC):
    @abstractmethod
    def get_transactions(self) -> TransactionResult:
        pass

    @abstractmethod
    def create_transaction(
        self,
        date: datetime,
        sending_account: UUID,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> Transaction:
        pass

    @abstractmethod
    def get_sales_balance_of_plan(self, plan: Plan) -> Decimal:
        pass


class AccountRepository(ABC):
    @abstractmethod
    def create_account(self, account_type: AccountTypes) -> Account:
        pass

    @abstractmethod
    def get_accounts(self) -> AccountResult:
        pass

    @abstractmethod
    def get_account_balance(self, account: UUID) -> Decimal:
        pass


class MemberRepository(ABC):
    @abstractmethod
    def create_member(
        self,
        *,
        email: str,
        name: str,
        password: str,
        account: Account,
        registered_on: datetime,
    ) -> Member:
        pass

    @abstractmethod
    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        pass

    @abstractmethod
    def get_members(self) -> MemberResult:
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
        registered_on: datetime,
    ) -> Company:
        pass

    @abstractmethod
    def query_companies_by_name(self, query: str) -> Iterator[Company]:
        pass

    @abstractmethod
    def query_companies_by_email(self, query: str) -> Iterator[Company]:
        pass

    @abstractmethod
    def get_companies(self) -> CompanyResult:
        pass

    @abstractmethod
    def validate_credentials(self, email_address: str, password: str) -> Optional[UUID]:
        pass

    @abstractmethod
    def is_company_confirmed(self, company: UUID) -> bool:
        pass

    @abstractmethod
    def confirm_company(self, company: UUID, confirmation_timestamp: datetime) -> None:
        pass


class PlanDraftRepository(ABC):
    @abstractmethod
    def create_plan_draft(
        self,
        planner: UUID,
        product_name: str,
        description: str,
        costs: ProductionCosts,
        production_unit: str,
        amount: int,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> PlanDraft:
        pass

    @dataclass
    class UpdateDraft:
        id: UUID
        product_name: Optional[str] = None
        amount: Optional[int] = None
        description: Optional[str] = None
        labour_cost: Optional[Decimal] = None
        means_cost: Optional[Decimal] = None
        resource_cost: Optional[Decimal] = None
        is_public_service: Optional[bool] = None
        timeframe: Optional[int] = None
        unit_of_distribution: Optional[str] = None

    @abstractmethod
    def update_draft(self, update: UpdateDraft) -> None:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[PlanDraft]:
        pass

    @abstractmethod
    def delete_draft(self, id: UUID) -> None:
        pass

    @abstractmethod
    def all_drafts_of_company(self, id: UUID) -> Iterable[PlanDraft]:
        pass


class WorkerInviteRepository(ABC):
    @abstractmethod
    def is_worker_invited_to_company(self, company: UUID, worker: UUID) -> bool:
        pass

    @abstractmethod
    def create_company_worker_invite(self, company: UUID, worker: UUID) -> UUID:
        pass

    @abstractmethod
    def get_companies_worker_is_invited_to(self, member: UUID) -> Iterable[UUID]:
        pass

    @abstractmethod
    def get_invites_for_worker(self, member: UUID) -> Iterable[CompanyWorkInvite]:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[CompanyWorkInvite]:
        pass

    @abstractmethod
    def delete_invite(self, id: UUID) -> None:
        pass


class CooperationRepository(ABC):
    @abstractmethod
    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        coordinator: Company,
    ) -> Cooperation:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Cooperation]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Iterator[Cooperation]:
        pass

    @abstractmethod
    def get_cooperations_coordinated_by_company(
        self, company_id: UUID
    ) -> Iterator[Cooperation]:
        pass

    @abstractmethod
    def get_cooperation_name(self, coop_id: UUID) -> Optional[str]:
        pass

    @abstractmethod
    def get_all_cooperations(self) -> Iterator[Cooperation]:
        pass

    @abstractmethod
    def count_cooperations(self) -> int:
        pass


class AccountantRepository(Protocol):
    def create_accountant(self, email: str, name: str, password: str) -> UUID:
        ...

    def has_accountant_with_email(self, email: str) -> bool:
        ...

    def get_by_id(self, id: UUID) -> Optional[Accountant]:
        ...

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        ...

    def get_all_accountants(self) -> QueryResult[Accountant]:
        ...


class LanguageRepository(Protocol):
    def get_available_language_codes(self) -> Iterable[str]:
        ...


class PayoutFactorRepository(Protocol):
    def store_payout_factor(self, timestamp: datetime, payout_factor: Decimal) -> None:
        ...

    def get_latest_payout_factor(self) -> Optional[PayoutFactor]:
        ...
