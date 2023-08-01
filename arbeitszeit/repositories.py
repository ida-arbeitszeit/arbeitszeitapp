from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Generic, Iterable, Iterator, List, Optional, Protocol, Tuple, TypeVar
from uuid import UUID

from typing_extensions import Self

from arbeitszeit import entities
from arbeitszeit.entities import (
    Account,
    Accountant,
    AccountOwner,
    Company,
    CompanyPurchase,
    CompanyWorkInvite,
    ConsumerPurchase,
    Cooperation,
    CoordinationTenure,
    EmailAddress,
    Member,
    Plan,
    PlanDraft,
    PlanningStatistics,
    ProductionCosts,
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


class DatabaseUpdate(Protocol):
    def perform(self) -> int:
        """Peform the update and return the number of records/rows
        affected.
        """


class PlanResult(QueryResult[Plan], Protocol):
    def ordered_by_creation_date(self, ascending: bool = ...) -> PlanResult:
        ...

    def ordered_by_activation_date(self, ascending: bool = ...) -> PlanResult:
        ...

    def ordered_by_planner_name(self, ascending: bool = ...) -> PlanResult:
        ...

    def with_id_containing(self, query: str) -> PlanResult:
        ...

    def with_product_name_containing(self, query: str) -> PlanResult:
        ...

    def that_are_approved(self) -> PlanResult:
        ...

    def that_were_activated_before(self, timestamp: datetime) -> Self:
        """Plans that were approved exactly at `timestamp` should also
        be included in the result.
        """

    def that_will_expire_after(self, timestamp: datetime) -> Self:
        """Plans that will expire exactly on the specified timestamp
        should not be included in the result.
        """

    def that_are_expired_as_of(self, timestamp: datetime) -> Self:
        """Plans that will be expired by a given timestamp."""

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

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> PlanResult:
        """If no cooperations are specified, then all the repository
        should return plans that are part of any cooperation.
        """

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> PlanResult:
        """If no companies are specified then the repository should
        return all plans that request cooperation with any
        coordinator.
        """

    def get_statistics(self) -> PlanningStatistics:
        """Return aggregate planning information for all plans
        included in a result set.
        """

    def that_are_not_hidden(self) -> Self:
        """Filter out those plans which are hidden. The result will
        only contain plans that are not hidden.
        """

    def joined_with_planner_and_cooperating_plans(
        self, timestamp: datetime
    ) -> QueryResult[
        Tuple[entities.Plan, entities.Company, List[entities.PlanSummary]]
    ]:
        ...

    def joined_with_provided_product_amount(
        self,
    ) -> QueryResult[Tuple[entities.Plan, int]]:
        ...

    def update(self) -> PlanUpdate:
        """Prepare an update for all selected Plans."""


class PlanUpdate(DatabaseUpdate, Protocol):
    """Aggregate updates on a previously selected set of plan rows in
    the DB and execute them all in one.
    """

    def set_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        """Set the associated cooperation of all matching plans to the
        one specified via the cooperation argument. Specifying `None`
        will unset the cooperation field. The return value counts all
        plans that were updated through this method.
        """

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        """Set the `requested_cooperation` field of all matching plans
        to the specified value.  A value `None` means that these plans
        are marked as not requesting membership in any
        cooperation. The return value counts all plans that were
        updated through this method.
        """

    def set_activation_timestamp(
        self, activation_timestamp: Optional[datetime]
    ) -> PlanUpdate:
        """Set the `activation_date` field of all selected plans."""

    def set_approval_date(self, approval_date: Optional[datetime]) -> PlanUpdate:
        """Set the approval date of all matching plans. The return
        value counts all the plans that were changed by this methods.
        """

    def hide(self) -> Self:
        ...

    def toggle_product_availability(self) -> Self:
        ...


class PlanDraftResult(QueryResult[PlanDraft], Protocol):
    def with_id(self, id_: UUID) -> Self:
        ...

    def planned_by(self, *company: UUID) -> Self:
        ...

    def update(self) -> PlanDraftUpdate:
        ...

    def delete(self) -> int:
        ...


class PlanDraftUpdate(DatabaseUpdate, Protocol):
    def set_product_name(self, name: str) -> Self:
        ...

    def set_amount(self, n: int) -> Self:
        ...

    def set_description(self, description: str) -> Self:
        ...

    def set_labour_cost(self, costs: Decimal) -> Self:
        ...

    def set_means_cost(self, costs: Decimal) -> Self:
        ...

    def set_resource_cost(self, costs: Decimal) -> Self:
        ...

    def set_is_public_service(self, is_public_service: bool) -> Self:
        ...

    def set_timeframe(self, days: int) -> Self:
        ...

    def set_unit_of_distribution(self, unit: str) -> Self:
        ...


class CooperationResult(QueryResult[Cooperation], Protocol):
    def with_id(self, id_: UUID) -> Self:
        ...

    def with_name_ignoring_case(self, name: str) -> Self:
        ...

    def coordinated_by_company(self, company_id: UUID) -> Self:
        ...

    def joined_with_current_coordinator(
        self,
    ) -> QueryResult[Tuple[Cooperation, Company]]:
        ...


class CoordinationTenureResult(QueryResult[CoordinationTenure], Protocol):
    def of_cooperation(self, cooperation: UUID) -> Self:
        ...

    def ordered_by_start_date(self, *, ascending: bool = ...) -> Self:
        ...


class MemberResult(QueryResult[Member], Protocol):
    def working_at_company(self, company: UUID) -> MemberResult:
        ...

    def with_id(self, id_: UUID) -> MemberResult:
        ...

    def with_email_address(self, email: str) -> MemberResult:
        ...

    def joined_with_email_address(self) -> QueryResult[Tuple[Member, EmailAddress]]:
        ...

    def that_are_confirmed(self) -> MemberResult:
        ...


class ConsumerPurchaseResult(QueryResult[ConsumerPurchase], Protocol):
    def ordered_by_creation_date(
        self, *, ascending: bool = ...
    ) -> ConsumerPurchaseResult:
        ...

    def where_buyer_is_member(self, member: UUID) -> ConsumerPurchaseResult:
        ...

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResult[Tuple[ConsumerPurchase, Transaction, Plan]]:
        ...


class CompanyPurchaseResult(QueryResult[CompanyPurchase], Protocol):
    def ordered_by_creation_date(
        self, *, ascending: bool = ...
    ) -> CompanyPurchaseResult:
        ...

    def where_buyer_is_company(self, company: UUID) -> CompanyPurchaseResult:
        ...

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResult[Tuple[CompanyPurchase, Transaction, Plan]]:
        ...

    def joined_with_transaction_and_provider(
        self,
    ) -> QueryResult[Tuple[CompanyPurchase, Transaction, Company]]:
        ...

    def joined_with_transaction(
        self,
    ) -> QueryResult[Tuple[CompanyPurchase, Transaction]]:
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

    def with_name_containing(self, query: str) -> CompanyResult:
        ...

    def with_email_containing(self, query: str) -> CompanyResult:
        ...

    def that_are_confirmed(self) -> Self:
        ...

    def joined_with_email_address(self) -> QueryResult[Tuple[Company, EmailAddress]]:
        ...


class AccountantResult(QueryResult[Accountant], Protocol):
    def with_email_address(self, email: str) -> Self:
        ...

    def with_id(self, id_: UUID) -> Self:
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

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        """Filter all transactions in the current result set such that
        the new result set contains only those transactions that are
        part of a "sale".

        If no `plan` argument is specified then the result set will
        contain all previously selected transactions that are part of
        any purchase.

        The `plan` argument can be specified multiple times. A
        transaction will be part of the result set if it is the
        payment for purchase for any plan that was specified by its
        UUID.
        """

    def joined_with_sender_and_receiver(
        self,
    ) -> QueryResult[Tuple[Transaction, AccountOwner, AccountOwner]]:
        ...


class AccountResult(QueryResult[Account], Protocol):
    def with_id(self, *id_: UUID) -> AccountResult:
        ...

    def owned_by_member(self, *member: UUID) -> Self:
        ...

    def owned_by_company(self, *company: UUID) -> Self:
        ...

    def that_are_member_accounts(self) -> Self:
        ...

    def that_are_product_accounts(self) -> Self:
        ...

    def that_are_labour_accounts(self) -> Self:
        ...

    def joined_with_owner(self) -> QueryResult[Tuple[Account, AccountOwner]]:
        ...

    def joined_with_balance(self) -> QueryResult[Tuple[Account, Decimal]]:
        ...


class CompanyWorkInviteResult(QueryResult[CompanyWorkInvite], Protocol):
    def issued_by(self, company: UUID) -> Self:
        ...

    def addressing(self, member: UUID) -> Self:
        ...

    def with_id(self, id: UUID) -> Self:
        ...

    def delete(self) -> None:
        ...


class EmailAddressResult(QueryResult[EmailAddress], Protocol):
    def with_address(self, *addresses: str) -> Self:
        ...

    def update(self) -> EmailAddressUpdate:
        ...


class EmailAddressUpdate(DatabaseUpdate, Protocol):
    def set_confirmation_timestamp(self, timestamp: Optional[datetime]) -> Self:
        ...


class LanguageRepository(Protocol):
    def get_available_language_codes(self) -> Iterable[str]:
        ...


class DatabaseGateway(Protocol):
    def create_consumer_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> ConsumerPurchase:
        ...

    def get_consumer_purchases(self) -> ConsumerPurchaseResult:
        ...

    def create_company_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> CompanyPurchase:
        ...

    def get_company_purchases(self) -> CompanyPurchaseResult:
        ...

    def create_plan(
        self,
        creation_timestamp: datetime,
        planner: UUID,
        production_costs: ProductionCosts,
        product_name: str,
        distribution_unit: str,
        amount_produced: int,
        product_description: str,
        duration_in_days: int,
        is_public_service: bool,
    ) -> Plan:
        ...

    def get_plans(self) -> PlanResult:
        ...

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
    ) -> Cooperation:
        ...

    def get_cooperations(self) -> CooperationResult:
        ...

    def create_coordination_tenure(
        self, company: UUID, cooperation: UUID, start_date: datetime
    ) -> CoordinationTenure:
        ...

    def get_coordination_tenures(self) -> CoordinationTenureResult:
        ...

    def get_transactions(self) -> TransactionResult:
        ...

    def create_transaction(
        self,
        date: datetime,
        sending_account: UUID,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> Transaction:
        ...

    def create_company_work_invite(
        self, company: UUID, member: UUID
    ) -> CompanyWorkInvite:
        ...

    def get_company_work_invites(self) -> CompanyWorkInviteResult:
        ...

    def create_member(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        account: Account,
        registered_on: datetime,
    ) -> Member:
        ...

    def get_members(self) -> MemberResult:
        ...

    def create_company(
        self,
        email: str,
        name: str,
        password_hash: str,
        means_account: Account,
        labour_account: Account,
        resource_account: Account,
        products_account: Account,
        registered_on: datetime,
    ) -> Company:
        ...

    def get_companies(self) -> CompanyResult:
        ...

    def create_accountant(self, email: str, name: str, password_hash: str) -> UUID:
        ...

    def get_accountants(self) -> AccountantResult:
        ...

    def create_email_address(
        self, *, address: str, confirmed_on: Optional[datetime]
    ) -> EmailAddress:
        ...

    def get_email_addresses(self) -> EmailAddressResult:
        ...

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
        ...

    def get_plan_drafts(self) -> PlanDraftResult:
        ...

    def create_account(self) -> Account:
        ...

    def get_accounts(self) -> AccountResult:
        ...
