from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from typing import Iterable, Iterator, List, Optional, Union
from uuid import UUID

from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    CompanyWorkInvite,
    Cooperation,
    Member,
    Message,
    Plan,
    PlanDraft,
    ProductionCosts,
    Purchase,
    PurposesOfPurchases,
    SocialAccounting,
    Transaction,
)
from arbeitszeit.user_action import UserAction


class CompanyWorkerRepository(ABC):
    @abstractmethod
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        pass

    @abstractmethod
    def get_company_workers(self, company: Company) -> Iterable[Member]:
        pass

    @abstractmethod
    def get_member_workplaces(self, member: UUID) -> Iterable[Company]:
        pass


class PurchaseRepository(ABC):
    @abstractmethod
    def create_purchase(
        self,
        purchase_date: datetime,
        plan: Plan,
        buyer: Union[Member, Company],
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        pass

    @abstractmethod
    def get_purchases_descending_by_date(
        self, user: Union[Member, Company]
    ) -> Iterator[Purchase]:
        pass


class PlanRepository(ABC):
    @abstractmethod
    def approve_plan(self, plan: PlanDraft, approval_timestamp: datetime) -> Plan:
        pass

    @abstractmethod
    def activate_plan(self, plan: Plan, activation_date: datetime) -> None:
        pass

    @abstractmethod
    def set_plan_as_expired(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def set_plan_as_renewed(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def set_expiration_relative(self, plan: Plan, days: int) -> None:
        pass

    @abstractmethod
    def set_expiration_date(self, plan: Plan, expiration_date: datetime) -> None:
        pass

    @abstractmethod
    def set_active_days(self, plan: Plan, full_active_days: int) -> None:
        pass

    @abstractmethod
    def increase_payout_count_by_one(self, plan: Plan) -> None:
        pass

    @abstractmethod
    def get_plan_by_id(self, id: UUID) -> Optional[Plan]:
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
    def delete_plan(self, plan_id: UUID) -> None:
        pass

    @abstractmethod
    def query_active_plans_by_product_name(self, query: str) -> Iterator[Plan]:
        pass

    @abstractmethod
    def query_active_plans_by_plan_id(self, query: str) -> Iterator[Plan]:
        pass

    @abstractmethod
    def get_all_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        pass

    @abstractmethod
    def get_non_active_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        pass

    @abstractmethod
    def get_active_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        pass

    @abstractmethod
    def get_expired_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        pass

    @abstractmethod
    def toggle_product_availability(self, plan: Plan) -> None:
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
    def get_by_id(self, id: UUID) -> Optional[Member]:
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
    def get_by_id(self, id: UUID) -> Optional[Company]:
        pass

    @abstractmethod
    def count_registered_companies(self) -> int:
        pass

    @abstractmethod
    def query_companies_by_name(self, query: str) -> Iterator[Company]:
        pass

    @abstractmethod
    def query_companies_by_email(self, query: str) -> Iterator[Company]:
        pass

    @abstractmethod
    def get_all_companies(self) -> Iterator[Company]:
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
    def get_by_id(self, id: UUID) -> Optional[CompanyWorkInvite]:
        pass

    @abstractmethod
    def delete_invite(self, id: UUID) -> None:
        pass


class MessageRepository(ABC):
    @abstractmethod
    def create_message(
        self,
        sender: Union[Member, Company, SocialAccounting],
        addressee: Union[Member, Company],
        title: str,
        content: str,
        sender_remarks: Optional[str],
        reference: Optional[UserAction],
    ) -> Message:
        pass

    @abstractmethod
    def get_by_id(self, id: UUID) -> Optional[Message]:
        pass

    @abstractmethod
    def mark_as_read(self, message: Message) -> None:
        pass

    @abstractmethod
    def has_unread_messages_for_user(self, user: UUID) -> bool:
        pass

    @abstractmethod
    def get_messages_to_user(self, user: UUID) -> Iterable[Message]:
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
    def add_plan_to_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        pass

    @abstractmethod
    def add_cooperation_to_plan(self, plan_id: UUID, cooperation_id: UUID) -> None:
        pass

    @abstractmethod
    def delete_plan_from_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        pass

    @abstractmethod
    def delete_cooperation_from_plan(self, plan_id: UUID, cooperation_id: UUID) -> None:
        pass

    @abstractmethod
    def set_requested_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        pass

    @abstractmethod
    def set_requested_cooperation_to_none(self, plan_id: UUID) -> None:
        pass
