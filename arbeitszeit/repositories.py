from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import (
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Self,
    Tuple,
    TypeVar,
)
from uuid import UUID

from arbeitszeit import records

T = TypeVar("T", covariant=True)


class QueryResult(Protocol, Generic[T]):
    def __iter__(self) -> Iterator[T]: ...

    def limit(self, n: int) -> Self: ...

    def offset(self, n: int) -> Self: ...

    def first(self) -> Optional[T]: ...

    def __len__(self) -> int: ...


class DatabaseUpdate(Protocol):
    def perform(self) -> int:
        """Peform the update and return the number of records/rows
        affected.
        """


class PlanResult(QueryResult[records.Plan], Protocol):
    def ordered_by_creation_date(self, ascending: bool = ...) -> Self: ...

    def ordered_by_activation_date(self, ascending: bool = ...) -> Self: ...

    def ordered_by_planner_name(self, ascending: bool = ...) -> Self: ...

    def with_id_containing(self, query: str) -> Self: ...

    def with_product_name_containing(self, query: str) -> Self: ...

    def that_are_approved(self) -> Self: ...

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

    def that_are_productive(self) -> Self: ...

    def that_are_public(self) -> Self: ...

    def that_are_cooperating(self) -> Self: ...

    def planned_by(self, *company: UUID) -> Self: ...

    def with_id(self, *id_: UUID) -> Self: ...

    def without_completed_review(self) -> Self: ...

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = ...
    ) -> Self: ...

    def that_are_in_same_cooperation_as(self, plan: UUID) -> Self: ...

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> Self:
        """If no cooperations are specified, then all the repository
        should return plans that are part of any cooperation.
        """

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> Self:
        """If no companies are specified then the repository should
        return all plans that request cooperation with any
        coordinator.
        """

    def get_statistics(self) -> records.PlanningStatistics:
        """Return aggregate planning information for all plans
        included in a result set.
        """

    def that_are_not_hidden(self) -> Self:
        """Filter out those plans which are hidden. The result will
        only contain plans that are not hidden.
        """

    def joined_with_planner_and_cooperation_and_cooperating_plans(
        self, timestamp: datetime
    ) -> QueryResult[
        Tuple[
            records.Plan,
            records.Company,
            Optional[records.Cooperation],
            List[records.PlanSummary],
        ]
    ]: ...

    def joined_with_cooperation(
        self,
    ) -> QueryResult[Tuple[records.Plan, Optional[records.Cooperation]]]: ...

    def joined_with_provided_product_amount(
        self,
    ) -> QueryResult[Tuple[records.Plan, int]]: ...

    def delete(self) -> None: ...

    def update(self) -> PlanUpdate:
        """Prepare an update for all selected Plans."""


class PlanUpdate(DatabaseUpdate, Protocol):
    """Aggregate updates on a previously selected set of plan rows in
    the DB and execute them all in one.
    """

    def set_cooperation(self, cooperation: Optional[UUID]) -> Self:
        """Set the associated cooperation of all matching plans to the
        one specified via the cooperation argument. Specifying `None`
        will unset the cooperation field. The return value counts all
        plans that were updated through this method.
        """

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> Self:
        """Set the `requested_cooperation` field of all matching plans
        to the specified value.  A value `None` means that these plans
        are marked as not requesting membership in any
        cooperation. The return value counts all plans that were
        updated through this method.
        """

    def set_activation_timestamp(
        self, activation_timestamp: Optional[datetime]
    ) -> Self:
        """Set the `activation_date` field of all selected plans."""

    def set_approval_date(self, approval_date: Optional[datetime]) -> Self:
        """Set the approval date of all matching plans. The return
        value counts all the plans that were changed by this methods.
        """

    def hide(self) -> Self: ...


class PlanDraftResult(QueryResult[records.PlanDraft], Protocol):
    def with_id(self, id_: UUID) -> Self: ...

    def planned_by(self, *company: UUID) -> Self: ...

    def update(self) -> PlanDraftUpdate: ...

    def joined_with_planner_and_email_address(
        self,
    ) -> QueryResult[
        tuple[records.PlanDraft, records.Company, records.EmailAddress]
    ]: ...

    def delete(self) -> int: ...


class PlanDraftUpdate(DatabaseUpdate, Protocol):
    def set_product_name(self, name: str) -> Self: ...

    def set_amount(self, n: int) -> Self: ...

    def set_description(self, description: str) -> Self: ...

    def set_labour_cost(self, costs: Decimal) -> Self: ...

    def set_means_cost(self, costs: Decimal) -> Self: ...

    def set_resource_cost(self, costs: Decimal) -> Self: ...

    def set_is_public_service(self, is_public_service: bool) -> Self: ...

    def set_timeframe(self, days: int) -> Self: ...

    def set_unit_of_distribution(self, unit: str) -> Self: ...


class CooperationResult(QueryResult[records.Cooperation], Protocol):
    def with_id(self, id_: UUID) -> Self: ...

    def with_name_ignoring_case(self, name: str) -> Self: ...

    def coordinated_by_company(self, company_id: UUID) -> Self: ...

    def joined_with_current_coordinator(
        self,
    ) -> QueryResult[Tuple[records.Cooperation, records.Company]]: ...


class CoordinationTenureResult(QueryResult[records.CoordinationTenure], Protocol):
    def with_id(self, id_: UUID) -> Self: ...

    def of_cooperation(self, cooperation_id: UUID) -> Self: ...

    def joined_with_coordinator(
        self,
    ) -> QueryResult[Tuple[records.CoordinationTenure, records.Company]]: ...

    def ordered_by_start_date(self, *, ascending: bool = ...) -> Self: ...


class CoordinationTransferRequestResult(
    QueryResult[records.CoordinationTransferRequest], Protocol
):
    def with_id(self, id_: UUID) -> Self: ...

    def requested_by(self, coordination_tenure: UUID) -> Self: ...

    def joined_with_cooperation(
        self,
    ) -> QueryResult[
        Tuple[records.CoordinationTransferRequest, records.Cooperation]
    ]: ...


class MemberResult(QueryResult[records.Member], Protocol):
    def working_at_company(self, company: UUID) -> Self: ...

    def with_id(self, id_: UUID) -> Self: ...

    def with_email_address(self, email: str) -> Self: ...

    def joined_with_email_address(
        self,
    ) -> QueryResult[Tuple[records.Member, records.EmailAddress]]: ...


class PrivateConsumptionResult(QueryResult[records.PrivateConsumption], Protocol):
    def ordered_by_creation_date(self, *, ascending: bool = ...) -> Self: ...

    def where_consumer_is_member(self, member: UUID) -> Self: ...

    def where_provider_is_company(self, company: UUID) -> Self: ...

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResult[
        Tuple[records.PrivateConsumption, records.Transaction, records.Plan]
    ]: ...

    def joined_with_transaction_and_plan_and_consumer(
        self,
    ) -> QueryResult[
        Tuple[
            records.PrivateConsumption,
            records.Transaction,
            records.Plan,
            records.Member,
        ]
    ]: ...


class ProductiveConsumptionResult(QueryResult[records.ProductiveConsumption], Protocol):
    def ordered_by_creation_date(self, *, ascending: bool = ...) -> Self: ...

    def where_consumer_is_company(self, company: UUID) -> Self: ...

    def where_provider_is_company(self, company: UUID) -> Self: ...

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResult[
        Tuple[records.ProductiveConsumption, records.Transaction, records.Plan]
    ]: ...

    def joined_with_transaction_and_provider(
        self,
    ) -> QueryResult[
        Tuple[records.ProductiveConsumption, records.Transaction, records.Company]
    ]: ...

    def joined_with_transaction(
        self,
    ) -> QueryResult[Tuple[records.ProductiveConsumption, records.Transaction]]: ...

    def joined_with_transaction_and_plan_and_consumer(
        self,
    ) -> QueryResult[
        Tuple[
            records.PrivateConsumption,
            records.Transaction,
            records.Plan,
            records.Company,
        ]
    ]: ...


class CompanyResult(QueryResult[records.Company], Protocol):
    def with_id(self, id_: UUID) -> Self: ...

    def with_email_address(self, email: str) -> Self: ...

    def that_are_workplace_of_member(self, member: UUID) -> Self: ...

    def that_is_coordinating_cooperation(self, cooperation: UUID) -> Self: ...

    def add_worker(self, member: UUID) -> int: ...

    def with_name_containing(self, query: str) -> Self: ...

    def with_email_containing(self, query: str) -> Self: ...

    def joined_with_email_address(
        self,
    ) -> QueryResult[Tuple[records.Company, records.EmailAddress]]: ...


class AccountantResult(QueryResult[records.Accountant], Protocol):
    def with_email_address(self, email: str) -> Self: ...

    def with_id(self, id_: UUID) -> Self: ...

    def joined_with_email_address(
        self,
    ) -> QueryResult[Tuple[records.Accountant, records.EmailAddress]]: ...


class TransactionResult(QueryResult[records.Transaction], Protocol):
    def where_account_is_sender_or_receiver(self, *account: UUID) -> Self: ...

    def where_account_is_sender(self, *account: UUID) -> Self: ...

    def where_account_is_receiver(self, *account: UUID) -> Self: ...

    def ordered_by_transaction_date(self, descending: bool = ...) -> Self: ...

    def where_sender_is_social_accounting(self) -> Self: ...

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        """Filter all transactions in the current result set such that
        the new result set contains only those transactions that are
        part of a "sale".

        If no `plan` argument is specified then the result set will
        contain all previously selected transactions that are part of
        any consumption.

        The `plan` argument can be specified multiple times. A
        transaction will be part of the result set if it is the
        consumption registration for any plan that was specified by its
        UUID.
        """

    def joined_with_receiver(
        self,
    ) -> QueryResult[Tuple[records.Transaction, records.AccountOwner]]: ...

    def joined_with_sender_and_receiver(
        self,
    ) -> QueryResult[
        Tuple[records.Transaction, records.AccountOwner, records.AccountOwner]
    ]: ...


class AccountResult(QueryResult[records.Account], Protocol):
    def with_id(self, *id_: UUID) -> Self: ...

    def owned_by_member(self, *member: UUID) -> Self: ...

    def owned_by_company(self, *company: UUID) -> Self: ...

    def that_are_member_accounts(self) -> Self: ...

    def that_are_product_accounts(self) -> Self: ...

    def that_are_labour_accounts(self) -> Self: ...

    def joined_with_owner(
        self,
    ) -> QueryResult[Tuple[records.Account, records.AccountOwner]]: ...

    def joined_with_balance(self) -> QueryResult[Tuple[records.Account, Decimal]]: ...


class CompanyWorkInviteResult(QueryResult[records.CompanyWorkInvite], Protocol):
    def issued_by(self, company: UUID) -> Self: ...

    def addressing(self, member: UUID) -> Self: ...

    def with_id(self, id: UUID) -> Self: ...

    def delete(self) -> None: ...


class EmailAddressResult(QueryResult[records.EmailAddress], Protocol):
    def with_address(self, *addresses: str) -> Self: ...

    def that_belong_to_member(self, member: UUID) -> Self: ...

    def that_belong_to_company(self, company: UUID) -> Self: ...

    def delete(self) -> None: ...

    def update(self) -> EmailAddressUpdate: ...


class EmailAddressUpdate(DatabaseUpdate, Protocol):
    def set_confirmation_timestamp(self, timestamp: Optional[datetime]) -> Self: ...


class AccountCredentialsResult(QueryResult[records.AccountCredentials], Protocol):
    def for_user_account_with_id(self, user_id: UUID) -> Self: ...

    def with_email_address(self, address: str) -> Self: ...

    def joined_with_accountant(
        self,
    ) -> QueryResult[
        Tuple[records.AccountCredentials, Optional[records.Accountant]]
    ]: ...

    def joined_with_email_address_and_accountant(
        self,
    ) -> QueryResult[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Accountant],
        ]
    ]: ...

    def joined_with_member(
        self,
    ) -> QueryResult[Tuple[records.AccountCredentials, Optional[records.Member]]]: ...

    def joined_with_email_address_and_member(
        self,
    ) -> QueryResult[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Member],
        ]
    ]: ...

    def joined_with_company(
        self,
    ) -> QueryResult[Tuple[records.AccountCredentials, Optional[records.Company]]]: ...

    def joined_with_email_address_and_company(
        self,
    ) -> QueryResult[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Company],
        ]
    ]: ...

    def update(self) -> AccountCredentialsUpdate: ...


class AccountCredentialsUpdate(DatabaseUpdate, Protocol):
    def change_email_address(self, new_email_address: str) -> Self: ...

    def change_password_hash(self, new_password_hash: str) -> Self: ...


class PasswordResetRequestResult(QueryResult[records.PasswordResetRequest], Protocol):
    def with_email_address(self, email_address) -> Self: ...

    def with_creation_date_after(self, creation_threshold: datetime) -> Self: ...


class LanguageRepository(Protocol):
    def get_available_language_codes(self) -> Iterable[str]: ...


class DatabaseGateway(Protocol):
    def create_private_consumption(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.PrivateConsumption: ...

    def get_private_consumptions(self) -> PrivateConsumptionResult: ...

    def create_productive_consumption(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.ProductiveConsumption: ...

    def get_productive_consumptions(self) -> ProductiveConsumptionResult: ...

    def create_plan(
        self,
        creation_timestamp: datetime,
        planner: UUID,
        production_costs: records.ProductionCosts,
        product_name: str,
        distribution_unit: str,
        amount_produced: int,
        product_description: str,
        duration_in_days: int,
        is_public_service: bool,
    ) -> records.Plan: ...

    def get_plans(self) -> PlanResult: ...

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
    ) -> records.Cooperation: ...

    def get_cooperations(self) -> CooperationResult: ...

    def create_coordination_tenure(
        self, company: UUID, cooperation: UUID, start_date: datetime
    ) -> records.CoordinationTenure: ...

    def get_coordination_tenures(self) -> CoordinationTenureResult: ...

    def create_coordination_transfer_request(
        self,
        requesting_coordination_tenure: UUID,
        candidate: UUID,
        request_date: datetime,
    ) -> records.CoordinationTransferRequest: ...

    def get_coordination_transfer_requests(
        self,
    ) -> CoordinationTransferRequestResult: ...

    def get_transactions(self) -> TransactionResult: ...

    def create_transaction(
        self,
        date: datetime,
        sending_account: UUID,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> records.Transaction: ...

    def create_company_work_invite(
        self, company: UUID, member: UUID
    ) -> records.CompanyWorkInvite: ...

    def get_company_work_invites(self) -> CompanyWorkInviteResult: ...

    def create_member(
        self,
        *,
        account_credentials: UUID,
        name: str,
        account: records.Account,
        registered_on: datetime,
    ) -> records.Member: ...

    def get_members(self) -> MemberResult: ...

    def create_company(
        self,
        account_credentials: UUID,
        name: str,
        means_account: records.Account,
        labour_account: records.Account,
        resource_account: records.Account,
        products_account: records.Account,
        registered_on: datetime,
    ) -> records.Company: ...

    def get_companies(self) -> CompanyResult: ...

    def create_accountant(
        self, account_credentials: UUID, name: str
    ) -> records.Accountant: ...

    def get_accountants(self) -> AccountantResult: ...

    def create_email_address(
        self, *, address: str, confirmed_on: Optional[datetime]
    ) -> records.EmailAddress: ...

    def get_email_addresses(self) -> EmailAddressResult: ...

    def create_plan_draft(
        self,
        planner: UUID,
        product_name: str,
        description: str,
        costs: records.ProductionCosts,
        production_unit: str,
        amount: int,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> records.PlanDraft: ...

    def get_plan_drafts(self) -> PlanDraftResult: ...

    def create_account(self) -> records.Account: ...

    def get_accounts(self) -> AccountResult: ...

    def create_account_credentials(
        self, email_address: str, password_hash: str
    ) -> records.AccountCredentials: ...

    def get_account_credentials(self) -> AccountCredentialsResult: ...

    def get_password_reset_requests(self) -> PasswordResetRequestResult: ...

    def create_password_reset_request(
        self, email_address: str, reset_token: str, created_at: datetime
    ) -> records.PasswordResetRequest: ...
