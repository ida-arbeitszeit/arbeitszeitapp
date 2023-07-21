from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import islice
from typing import (
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    TypeVar,
)
from uuid import UUID, uuid4

from typing_extensions import Self

from arbeitszeit import entities
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import (
    Account,
    Accountant,
    Company,
    CompanyWorkInvite,
    Cooperation,
    Member,
    Plan,
    PlanDraft,
    ProductionCosts,
    SocialAccounting,
    Transaction,
)
from arbeitszeit.injector import singleton

T = TypeVar("T")
QueryResultT = TypeVar("QueryResultT", bound="QueryResultImpl")


@dataclass
class QueryResultImpl(Generic[T]):
    items: Callable[[], Iterable[T]]
    entities: EntityStorage

    def limit(self: QueryResultT, n: int) -> QueryResultT:
        return type(self)(
            items=lambda: islice(self.items(), n),
            entities=self.entities,
        )

    def offset(self: QueryResultT, n: int) -> QueryResultT:
        return type(self)(
            items=lambda: islice(self.items(), n, None),
            entities=self.entities,
        )

    def first(self) -> Optional[T]:
        try:
            item = next(iter(self))
        except StopIteration:
            return None
        return item

    def __iter__(self) -> Iterator[T]:
        return iter(self.items())

    def __len__(self) -> int:
        return len(list(self.items()))

    def _filter_elements(self, condition: Callable[[T], bool]) -> Self:
        return replace(
            self,
            items=lambda: filter(condition, self.items()),
        )


class PlanResult(QueryResultImpl[Plan]):
    def ordered_by_creation_date(self, ascending: bool = True) -> PlanResult:
        return type(self)(
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: plan.plan_creation_date,
                reverse=not ascending,
            ),
            entities=self.entities,
        )

    def ordered_by_activation_date(self, ascending: bool = True) -> PlanResult:
        return type(self)(
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: plan.activation_date
                if plan.activation_date
                else datetime.min,
                reverse=not ascending,
            ),
            entities=self.entities,
        )

    def ordered_by_planner_name(self, ascending: bool = True) -> PlanResult:
        def get_company_name(planner_id: UUID) -> str:
            planner = self.entities.get_company_by_id(planner_id)
            assert planner
            planner_name = planner.name
            return planner_name.casefold()

        return type(self)(
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: get_company_name(plan.planner),
                reverse=not ascending,
            ),
            entities=self.entities,
        )

    def with_id_containing(self, query: str) -> PlanResult:
        return self._filtered_by(lambda plan: query in str(plan.id))

    def with_product_name_containing(self, query: str) -> PlanResult:
        return self._filtered_by(lambda plan: query.lower() in plan.prd_name.lower())

    def that_are_approved(self) -> PlanResult:
        return self._filtered_by(lambda plan: plan.approval_date is not None)

    def that_were_activated_before(self, timestamp: datetime) -> Self:
        return self._filtered_by(
            lambda plan: plan.activation_date is not None
            and plan.activation_date <= timestamp
        )

    def that_will_expire_after(self, timestamp: datetime) -> Self:
        return self._filtered_by(
            lambda plan: plan.approval_date is not None
            and plan.approval_date + timedelta(days=plan.timeframe) > timestamp
        )

    def that_are_expired_as_of(self, timestamp: datetime) -> Self:
        return self._filtered_by(
            lambda plan: plan.approval_date is not None
            and plan.approval_date + timedelta(days=plan.timeframe) <= timestamp
        )

    def that_are_productive(self) -> PlanResult:
        return self._filtered_by(lambda plan: not plan.is_public_service)

    def that_are_public(self) -> PlanResult:
        return self._filtered_by(lambda plan: plan.is_public_service)

    def that_are_cooperating(self) -> PlanResult:
        return self._filtered_by(lambda plan: plan.cooperation is not None)

    def planned_by(self, *company: UUID) -> PlanResult:
        return self._filtered_by(lambda plan: plan.planner in company)

    def with_id(self, *id_: UUID) -> PlanResult:
        return self._filtered_by(lambda plan: plan.id in id_)

    def without_completed_review(self) -> PlanResult:
        return self._filtered_by(lambda plan: plan.approval_date is None)

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = None
    ) -> PlanResult:
        return self._filtered_by(
            lambda plan: plan.requested_cooperation == cooperation
            if cooperation
            else plan.requested_cooperation is not None
        )

    def that_are_in_same_cooperation_as(self, plan: UUID) -> PlanResult:
        def items_generator() -> Iterator[entities.Plan]:
            plan_entity = self.entities.plans.get(plan)
            if not plan_entity:
                return
            if plan_entity.cooperation is None:
                yield from (
                    other_plan for other_plan in self.items() if other_plan.id == plan
                )
            else:
                yield from (
                    plan
                    for plan in self.items()
                    if plan.cooperation == plan_entity.cooperation
                )

        return type(self)(
            items=items_generator,
            entities=self.entities,
        )

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> PlanResult:
        return self._filtered_by(
            (lambda plan: plan.cooperation in cooperation)
            if cooperation
            else (lambda plan: plan.cooperation is not None)
        )

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> PlanResult:
        def new_items() -> Iterator[Plan]:
            cooperations: Set[UUID] = {
                key
                for key, value in self.entities.cooperations.items()
                if value.coordinator in company
            }
            return filter(
                lambda plan: plan.requested_cooperation in cooperations
                if company
                else plan.requested_cooperation is not None,
                self.items(),
            )

        return replace(
            self,
            items=new_items,
        )

    def get_statistics(self) -> entities.PlanningStatistics:
        """Return aggregate planning information for all plans
        included in a result set.
        """
        duration_sum = 0
        plan_count = 0
        production_costs = entities.ProductionCosts(Decimal(0), Decimal(0), Decimal(0))
        for plan in self.items():
            plan_count += 1
            production_costs += plan.production_costs
            duration_sum += plan.timeframe
        return entities.PlanningStatistics(
            average_plan_duration_in_days=(Decimal(duration_sum) / Decimal(plan_count))
            if plan_count > 0
            else Decimal(0),
            total_planned_costs=production_costs,
        )

    def that_are_not_hidden(self) -> Self:
        return self._filtered_by(lambda plan: not plan.hidden_by_user)

    def update(self) -> PlanUpdate:
        return PlanUpdate(
            items=self.items,
            update_functions=[],
        )

    def _filtered_by(self, key: Callable[[Plan], bool]) -> Self:
        return type(self)(
            items=lambda: filter(key, self.items()),
            entities=self.entities,
        )


@dataclass
class PlanUpdate:
    items: Callable[[], Iterable[Plan]]
    update_functions: List[Callable[[Plan], None]]

    def set_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.cooperation = cooperation

        return self._add_update(update)

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.requested_cooperation = cooperation

        return self._add_update(update)

    def set_approval_date(self, approval_date: Optional[datetime]) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.approval_date = approval_date

        return self._add_update(update)

    def set_activation_timestamp(
        self, activation_timestamp: Optional[datetime]
    ) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.activation_date = activation_timestamp

        return self._add_update(update)

    def hide(self) -> Self:
        def update(plan: entities.Plan) -> None:
            plan.hidden_by_user = True

        return self._add_update(update)

    def toggle_product_availability(self) -> Self:
        def update(plan: entities.Plan) -> None:
            plan.is_available = not plan.is_available

        return self._add_update(update)

    def perform(self) -> int:
        items_affected = 0
        for item in self.items():
            for update in self.update_functions:
                update(item)
            items_affected += 1
        return items_affected

    def _add_update(self, update: Callable[[Plan], None]) -> Self:
        return replace(self, update_functions=self.update_functions + [update])


class PlanDraftResult(QueryResultImpl[entities.PlanDraft]):
    def with_id(self, id_: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda draft: draft.id == id_,
                self.items(),
            ),
        )

    def planned_by(self, *company: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda draft: draft.planner in company,
                self.items(),
            ),
        )

    def delete(self) -> int:
        drafts_to_delete = [draft.id for draft in self.items()]
        drafts_deleted = 0
        for draft in drafts_to_delete:
            if draft in self.entities.drafts:
                del self.entities.drafts[draft]
                drafts_deleted += 1
        return drafts_deleted

    def update(self) -> PlanDraftUpdate:
        return PlanDraftUpdate(
            entities=self.entities,
            items=self.items,
        )


@dataclass
class PlanDraftUpdate:
    entities: EntityStorage
    items: Callable[[], Iterable[PlanDraft]]
    changes: Callable[[PlanDraft], None] = lambda _: None

    def set_product_name(self, name: str) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.product_name = name

        return replace(
            self,
            changes=update,
        )

    def set_amount(self, n: int) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.amount_produced = n

        return replace(
            self,
            changes=update,
        )

    def set_description(self, description: str) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.description = description

        return replace(
            self,
            changes=update,
        )

    def set_labour_cost(self, costs: Decimal) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.production_costs.labour_cost = costs

        return replace(
            self,
            changes=update,
        )

    def set_means_cost(self, costs: Decimal) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.production_costs.means_cost = costs

        return replace(
            self,
            changes=update,
        )

    def set_resource_cost(self, costs: Decimal) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.production_costs.resource_cost = costs

        return replace(
            self,
            changes=update,
        )

    def set_is_public_service(self, is_public_service: bool) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.is_public_service = is_public_service

        return replace(
            self,
            changes=update,
        )

    def set_timeframe(self, days: int) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.timeframe = days

        return replace(
            self,
            changes=update,
        )

    def set_unit_of_distribution(self, unit: str) -> Self:
        def update(draft: PlanDraft) -> None:
            draft.unit_of_distribution = unit

        return replace(
            self,
            changes=update,
        )

    def perform(self) -> int:
        items_affected = 0
        for item in self.items():
            self.changes(item)
            items_affected += 1
        return items_affected


class CooperationResult(QueryResultImpl[Cooperation]):
    def with_id(self, id_: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(lambda coop: coop.id == id_, self.items()),
        )

    def with_name_ignoring_case(self, name: str) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda coop: coop.name.lower() == name.lower(), self.items()
            ),
        )

    def coordinated_by_company(self, company_id: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda coop: coop.coordinator == company_id, self.items()
            ),
        )

    def joined_with_coordinator(self) -> QueryResultImpl[Tuple[Cooperation, Company]]:
        def mapping(
            coop: entities.Cooperation,
        ) -> Tuple[entities.Cooperation, entities.Company]:
            coordinator = self.entities.get_company_by_id(coop.coordinator)
            assert coordinator
            return (coop, coordinator)

        return QueryResultImpl(
            items=lambda: map(
                mapping,
                self.items(),
            ),
            entities=self.entities,
        )


class MemberResult(QueryResultImpl[Member]):
    def working_at_company(self, company: UUID) -> MemberResult:
        return self._filtered_by(
            lambda member: member.id in self.entities.company_workers.get(company, []),
        )

    def with_id(self, member: UUID) -> MemberResult:
        return self._filtered_by(lambda model: model.id == member)

    def with_email_address(self, email: str) -> MemberResult:
        return self._filtered_by(lambda model: model.email == email)

    def that_are_confirmed(self) -> MemberResult:
        def filtered(model: entities.Member) -> bool:
            email = self.entities.email_addresses[model.email]
            return email.confirmed_on is not None

        return self._filtered_by(filtered)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[entities.Member, entities.EmailAddress]]:
        def items() -> Iterable[Tuple[entities.Member, entities.EmailAddress]]:
            for member in self.items():
                yield member, self.entities.email_addresses[member.email]

        return QueryResultImpl(
            items=items,
            entities=self.entities,
        )

    def _filtered_by(self, key: Callable[[Member], bool]) -> MemberResult:
        return type(self)(
            items=lambda: filter(key, self.items()),
            entities=self.entities,
        )


class CompanyResult(QueryResultImpl[Company]):
    def with_id(self, id_: UUID) -> CompanyResult:
        return type(self)(
            items=lambda: filter(lambda company: company.id == id_, self.items()),
            entities=self.entities,
        )

    def with_email_address(self, email: str) -> CompanyResult:
        return type(self)(
            items=lambda: filter(lambda company: company.email == email, self.items()),
            entities=self.entities,
        )

    def that_are_workplace_of_member(self, member: UUID) -> CompanyResult:
        return type(self)(
            items=lambda: filter(
                lambda company: member in self.entities.company_workers[company.id],
                self.items(),
            ),
            entities=self.entities,
        )

    def add_worker(self, member: UUID) -> int:
        companies_changed = 0
        for company in self.items():
            companies_changed += 1
            self.entities.company_workers[company.id].add(member)
        return companies_changed

    def with_name_containing(self, query: str) -> CompanyResult:
        return self._filtered_by(lambda company: query.lower() in company.name.lower())

    def with_email_containing(self, query: str) -> CompanyResult:
        return self._filtered_by(lambda company: query.lower() in company.email.lower())

    def that_are_confirmed(self) -> Self:
        def filtered(company: entities.Company) -> bool:
            email = self.entities.email_addresses[company.email]
            return email.confirmed_on is not None

        return self._filtered_by(filtered)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[entities.Company, entities.EmailAddress]]:
        def items() -> Iterable[Tuple[entities.Company, entities.EmailAddress]]:
            for company in self.items():
                yield company, self.entities.email_addresses[company.email]

        return QueryResultImpl(
            items=items,
            entities=self.entities,
        )

    def _filtered_by(self, key: Callable[[Company], bool]) -> Self:
        return type(self)(
            items=lambda: filter(key, self.items()),
            entities=self.entities,
        )


class AccountantResult(QueryResultImpl[Accountant]):
    def with_email_address(self, email: str) -> Self:
        return self._filter_elements(
            lambda accountant: accountant.email_address == email
        )

    def with_id(self, id_: UUID) -> Self:
        return self._filter_elements(lambda accountant: accountant.id == id_)


class TransactionResult(QueryResultImpl[Transaction]):
    def where_account_is_sender_or_receiver(self, *account: UUID) -> TransactionResult:
        return replace(
            self,
            items=lambda: filter(
                lambda transaction: transaction.sending_account in account
                or transaction.receiving_account in account,
                self.items(),
            ),
        )

    def where_account_is_sender(self, *account: UUID) -> TransactionResult:
        return replace(
            self,
            items=lambda: filter(
                lambda transaction: transaction.sending_account in account,
                self.items(),
            ),
        )

    def where_account_is_receiver(self, *account: UUID) -> TransactionResult:
        return replace(
            self,
            items=lambda: filter(
                lambda transaction: transaction.receiving_account in account,
                self.items(),
            ),
        )

    def ordered_by_transaction_date(
        self, descending: bool = False
    ) -> TransactionResult:
        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=lambda transaction: transaction.date,
                reverse=descending,
            ),
        )

    def where_sender_is_social_accounting(self) -> TransactionResult:
        return replace(
            self,
            items=lambda: filter(
                lambda transaction: transaction.sending_account
                == self.entities.social_accounting.account,
                self.items(),
            ),
        )

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        def transaction_filter(transaction: Transaction) -> bool:
            purchase = self.entities.consumer_purchase_by_transaction.get(
                transaction.id
            ) or self.entities.company_purchase_by_transaction.get(transaction.id)
            if purchase is None:
                return False
            elif not plan:
                return purchase.plan_id is not None
            else:
                return purchase.plan_id in plan

        return replace(
            self,
            items=lambda: filter(
                transaction_filter,
                self.items(),
            ),
        )

    def joined_with_sender_and_receiver(
        self,
    ) -> QueryResultImpl[
        Tuple[entities.Transaction, entities.AccountOwner, entities.AccountOwner]
    ]:
        def get_account_owner(account_id: UUID) -> entities.AccountOwner:
            owner = self.entities.account_owner_by_account.get(account_id)
            if owner:
                return owner
            raise Exception(
                f"Tried to get owner for account {account_id} but failed to find one"
            )

        def items() -> (
            Iterable[
                Tuple[
                    entities.Transaction, entities.AccountOwner, entities.AccountOwner
                ]
            ]
        ):
            for transaction in self.items():
                yield transaction, get_account_owner(
                    transaction.sending_account
                ), get_account_owner(transaction.receiving_account)

        return QueryResultImpl(
            items=items,
            entities=self.entities,
        )


class ConsumerPurchaseResult(QueryResultImpl[entities.ConsumerPurchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> ConsumerPurchaseResult:
        def purchase_sorting_key(purchase: entities.ConsumerPurchase) -> datetime:
            transaction = self.entities.transactions[purchase.transaction_id]
            return transaction.date

        return type(self)(
            items=lambda: sorted(
                list(self.items()),
                key=purchase_sorting_key,
                reverse=not ascending,
            ),
            entities=self.entities,
        )

    def where_buyer_is_member(self, member: UUID) -> ConsumerPurchaseResult:
        def filtered_items() -> Iterator[entities.ConsumerPurchase]:
            member_account = self.entities.members[member].account
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                if transaction.sending_account == member_account:
                    yield purchase

        return replace(
            self,
            items=filtered_items,
        )

    def with_transaction_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[entities.ConsumerPurchase, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[entities.ConsumerPurchase, Transaction, Plan]]
        ):
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                plan = self.entities.plans[purchase.plan_id]
                yield purchase, transaction, plan

        return QueryResultImpl(
            items=joined_items,
            entities=self.entities,
        )


class CompanyPurchaseResult(QueryResultImpl[entities.CompanyPurchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> CompanyPurchaseResult:
        def purchase_sorting_key(purchase: entities.CompanyPurchase) -> datetime:
            transaction = self.entities.transactions[purchase.transaction_id]
            return transaction.date

        return type(self)(
            items=lambda: sorted(
                list(self.items()),
                key=purchase_sorting_key,
                reverse=not ascending,
            ),
            entities=self.entities,
        )

    def where_buyer_is_company(self, company: UUID) -> CompanyPurchaseResult:
        def filtered_items() -> Iterator[entities.CompanyPurchase]:
            company_record = self.entities.get_company_by_id(company)
            if company_record is None:
                return None
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                if (
                    transaction.sending_account == company_record.means_account
                    or transaction.sending_account
                    == company_record.raw_material_account
                ):
                    yield purchase

        return replace(
            self,
            items=filtered_items,
        )

    def with_transaction_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[entities.CompanyPurchase, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[entities.CompanyPurchase, Transaction, Plan]]
        ):
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                plan = self.entities.plans[purchase.plan_id]
                yield purchase, transaction, plan

        return replace(
            self,  # type: ignore
            items=joined_items,
        )

    def with_transaction(
        self,
    ) -> QueryResultImpl[Tuple[entities.CompanyPurchase, entities.Transaction]]:
        def joined_items() -> (
            Iterator[Tuple[entities.CompanyPurchase, entities.Transaction]]
        ):
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                yield purchase, transaction

        return replace(
            self,  # type: ignore
            items=joined_items,
        )

    def with_transaction_and_provider(
        self,
    ) -> QueryResultImpl[Tuple[entities.CompanyPurchase, Transaction, Company]]:
        def joined_items() -> (
            Iterator[Tuple[entities.CompanyPurchase, Transaction, Company]]
        ):
            for purchase in self.items():
                transaction = self.entities.transactions[purchase.transaction_id]
                plan = self.entities.plans[purchase.plan_id]
                provider = self.entities.companies[plan.planner]
                yield purchase, transaction, provider

        return QueryResultImpl(
            items=joined_items,
            entities=self.entities,
        )


class AccountResult(QueryResultImpl[Account]):
    def with_id(self, *id_: UUID) -> AccountResult:
        return replace(
            self,
            items=lambda: filter(lambda account: account.id in id_, self.items()),
        )

    def owned_by_member(self, *member: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.entities.member_accounts
                and self.entities.account_owner_by_account[account.id].id in member,
                self.items(),
            ),
        )

    def owned_by_company(self, *company: UUID) -> Self:
        def items() -> Iterable[Account]:
            for account in self.items():
                owner = self.entities.account_owner_by_account.get(account.id)
                if owner is None:
                    continue
                if owner.id not in self.entities.companies:
                    continue
                if owner.id not in company:
                    continue
                yield account

        return replace(
            self,
            items=items,
        )

    def that_are_member_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.entities.member_accounts, self.items()
            ),
        )

    def that_are_product_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.entities.prd_accounts, self.items()
            ),
        )

    def that_are_labour_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.entities.l_accounts, self.items()
            ),
        )

    def joined_with_owner(
        self,
    ) -> QueryResultImpl[Tuple[Account, entities.AccountOwner]]:
        def items() -> Iterable[Tuple[Account, entities.AccountOwner]]:
            for account in self.items():
                if account.id == self.entities.social_accounting.account:
                    yield account, self.entities.social_accounting
                for member in self.entities.members.values():
                    if account.id == member.account:
                        yield account, member
                for company in self.entities.companies.values():
                    if account.id in [
                        company.means_account,
                        company.raw_material_account,
                        company.work_account,
                        company.product_account,
                    ]:
                        yield account, company

        return QueryResultImpl(
            items=items,
            entities=self.entities,
        )

    def joined_with_balance(self) -> QueryResultImpl[Tuple[Account, Decimal]]:
        def items() -> Iterable[Tuple[Account, Decimal]]:
            for account in self.items():
                transactions = self.entities.get_transactions()
                received_transactions = transactions.where_account_is_receiver(
                    account.id
                )
                sent_transactions = transactions.where_account_is_sender(account.id)
                yield account, decimal_sum(
                    transaction.amount_received for transaction in received_transactions
                ) - decimal_sum(
                    transaction.amount_sent for transaction in sent_transactions
                )

        return QueryResultImpl(items=items, entities=self.entities)


class CompanyWorkInviteResult(QueryResultImpl[CompanyWorkInvite]):
    def issued_by(self, company: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda invite: invite.company == company,
                self.items(),
            ),
        )

    def addressing(self, member: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda invite: invite.member == member,
                self.items(),
            ),
        )

    def with_id(self, id: UUID) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda invite: invite.id == id,
                self.items(),
            ),
        )

    def delete(self) -> None:
        invites_to_delete = set(invite.id for invite in self.items())
        self.entities.company_work_invites = [
            invite
            for invite in self.entities.company_work_invites
            if invite.id not in invites_to_delete
        ]


class EmailAddressResult(QueryResultImpl[entities.EmailAddress]):
    def with_address(self, *addresses: str) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda a: a.address in addresses,
                self.items(),
            ),
        )

    def update(self) -> EmailAddressUpdate:
        return EmailAddressUpdate(
            items=self.items,
        )


@dataclass
class EmailAddressUpdate:
    items: Callable[[], Iterable[entities.EmailAddress]]
    transformation: Callable[[entities.EmailAddress], None] = field(
        default=lambda _: None
    )

    def set_confirmation_timestamp(self, timestamp: Optional[datetime]) -> Self:
        def transformation(item: entities.EmailAddress) -> None:
            self.transformation(item)
            item.confirmed_on = timestamp

        return replace(self, transformation=transformation)

    def perform(self) -> int:
        email_addresses_affected = 0
        for address in self.items():
            self.transformation(address)
            email_addresses_affected += 1
        return email_addresses_affected


@singleton
class FakeLanguageRepository:
    def __init__(self) -> None:
        self._language_codes: Set[str] = set()

    def add_language(self, language_code: str) -> None:
        self._language_codes.add(language_code)

    def get_available_language_codes(self) -> Iterable[str]:
        return self._language_codes


@singleton
class EntityStorage:
    def __init__(self, datetime_service: DatetimeService) -> None:
        self.members: Dict[UUID, Member] = {}
        self.company_workers: Dict[UUID, Set[UUID]] = defaultdict(lambda: set())
        self.companies: Dict[UUID, Company] = {}
        self.company_passwords: Dict[UUID, str] = {}
        self.plans: Dict[UUID, Plan] = {}
        self.transactions: Dict[UUID, Transaction] = dict()
        self.accounts: List[Account] = []
        self.p_accounts: Set[Account] = set()
        self.r_accounts: Set[Account] = set()
        self.l_accounts: Set[Account] = set()
        self.prd_accounts: Set[Account] = set()
        self.member_accounts: Set[Account] = set()
        self.accountants: Dict[UUID, Accountant] = dict()
        self.social_accounting = SocialAccounting(
            id=uuid4(),
            account=self.create_account().id,
        )
        self.account_owner_by_account: Dict[UUID, entities.AccountOwner] = {
            self.social_accounting.account: self.social_accounting
        }
        self.cooperations: Dict[UUID, Cooperation] = dict()
        self.consumer_purchases: Dict[UUID, entities.ConsumerPurchase] = dict()
        self.consumer_purchase_by_transaction: Dict[
            UUID, entities.ConsumerPurchase
        ] = dict()
        self.company_purchases: Dict[UUID, entities.CompanyPurchase] = dict()
        self.company_purchase_by_transaction: Dict[
            UUID, entities.CompanyPurchase
        ] = dict()
        self.company_work_invites: List[CompanyWorkInvite] = list()
        self.email_addresses: Dict[str, entities.EmailAddress] = dict()
        self.drafts: Dict[UUID, PlanDraft] = dict()

    def create_email_address(
        self, *, address: str, confirmed_on: Optional[datetime]
    ) -> entities.EmailAddress:
        assert address not in self.email_addresses
        record = entities.EmailAddress(
            address=address,
            confirmed_on=confirmed_on,
        )
        self.email_addresses[address] = record
        return record

    def get_company_by_id(self, company: UUID) -> Optional[Company]:
        return self.companies.get(company)

    def create_consumer_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> entities.ConsumerPurchase:
        purchase = entities.ConsumerPurchase(
            id=uuid4(),
            plan_id=plan,
            transaction_id=transaction,
            amount=amount,
        )
        self.consumer_purchases[purchase.id] = purchase
        self.consumer_purchase_by_transaction[transaction] = purchase
        return purchase

    def get_consumer_purchases(self) -> ConsumerPurchaseResult:
        return ConsumerPurchaseResult(
            entities=self,
            items=self.consumer_purchases.values,
        )

    def create_company_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> entities.CompanyPurchase:
        purchase = entities.CompanyPurchase(
            id=uuid4(),
            amount=amount,
            plan_id=plan,
            transaction_id=transaction,
        )
        self.company_purchases[purchase.id] = purchase
        self.company_purchase_by_transaction[transaction] = purchase
        return purchase

    def get_company_purchases(self) -> CompanyPurchaseResult:
        return CompanyPurchaseResult(entities=self, items=self.company_purchases.values)

    def get_plans(self) -> PlanResult:
        return PlanResult(
            items=lambda: self.plans.values(),
            entities=self,
        )

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
    ) -> entities.Plan:
        plan = Plan(
            id=uuid4(),
            plan_creation_date=creation_timestamp,
            planner=planner,
            production_costs=production_costs,
            prd_name=product_name,
            prd_unit=distribution_unit,
            prd_amount=amount_produced,
            description=product_description,
            timeframe=duration_in_days,
            is_public_service=is_public_service,
            activation_date=None,
            approval_date=None,
            requested_cooperation=None,
            cooperation=None,
            is_available=True,
            hidden_by_user=False,
        )
        self.plans[plan.id] = plan
        return plan

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        coordinator: UUID,
    ) -> Cooperation:
        cooperation_id = uuid4()
        cooperation = Cooperation(
            id=cooperation_id,
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
            coordinator=coordinator,
        )
        self.cooperations[cooperation_id] = cooperation
        return cooperation

    def get_cooperations(self) -> CooperationResult:
        return CooperationResult(
            items=lambda: self.cooperations.values(),
            entities=self,
        )

    def create_transaction(
        self,
        date: datetime,
        sending_account: UUID,
        receiving_account: UUID,
        amount_sent: Decimal,
        amount_received: Decimal,
        purpose: str,
    ) -> Transaction:
        transaction = Transaction(
            id=uuid4(),
            date=date,
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount_sent=amount_sent,
            amount_received=amount_received,
            purpose=purpose,
        )
        self.transactions[transaction.id] = transaction
        return transaction

    def get_transactions(self) -> TransactionResult:
        return TransactionResult(
            items=lambda: self.transactions.values(),
            entities=self,
        )

    def create_company_work_invite(
        self, company: UUID, member: UUID
    ) -> CompanyWorkInvite:
        invite = CompanyWorkInvite(
            id=uuid4(),
            member=member,
            company=company,
        )
        self.company_work_invites.append(invite)
        return invite

    def get_company_work_invites(self) -> CompanyWorkInviteResult:
        return CompanyWorkInviteResult(
            items=lambda: self.company_work_invites,
            entities=self,
        )

    def create_accountant(self, email: str, name: str, password_hash: str) -> UUID:
        assert email in self.email_addresses
        id = uuid4()
        record = Accountant(
            email_address=email,
            name=name,
            password_hash=password_hash,
            id=id,
        )
        self.accountants[id] = record
        return record.id

    def get_accountants(self) -> AccountantResult:
        return AccountantResult(
            items=lambda: self.accountants.values(),
            entities=self,
        )

    def create_member(
        self,
        *,
        email: str,
        name: str,
        password_hash: str,
        account: Account,
        registered_on: datetime,
    ) -> Member:
        assert email in self.email_addresses
        self.member_accounts.add(account)
        id = uuid4()
        member = Member(
            id=id,
            name=name,
            email=email,
            account=account.id,
            registered_on=registered_on,
            password_hash=password_hash,
        )
        self.members[id] = member
        self.account_owner_by_account[member.account] = member
        return member

    def get_members(self) -> MemberResult:
        return MemberResult(
            items=lambda: self.members.values(),
            entities=self,
        )

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
        assert email in self.email_addresses
        self.p_accounts.add(means_account)
        self.r_accounts.add(resource_account)
        self.l_accounts.add(labour_account)
        self.prd_accounts.add(products_account)
        new_company = Company(
            id=uuid4(),
            email=email,
            name=name,
            means_account=means_account.id,
            raw_material_account=resource_account.id,
            work_account=labour_account.id,
            product_account=products_account.id,
            registered_on=registered_on,
            password_hash=password_hash,
        )
        self.companies[new_company.id] = new_company
        self.account_owner_by_account[means_account.id] = new_company
        self.account_owner_by_account[labour_account.id] = new_company
        self.account_owner_by_account[resource_account.id] = new_company
        self.account_owner_by_account[products_account.id] = new_company
        return new_company

    def get_companies(self) -> CompanyResult:
        return CompanyResult(
            items=lambda: self.companies.values(),
            entities=self,
        )

    def get_email_addresses(self) -> EmailAddressResult:
        return EmailAddressResult(
            entities=self,
            items=lambda: self.email_addresses.values(),
        )

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
        draft = PlanDraft(
            id=uuid4(),
            creation_date=creation_timestamp,
            planner=planner,
            product_name=product_name,
            production_costs=costs,
            unit_of_distribution=production_unit,
            amount_produced=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
        )
        self.drafts[draft.id] = draft
        return draft

    def get_plan_drafts(self) -> PlanDraftResult:
        return PlanDraftResult(
            items=lambda: self.drafts.values(),
            entities=self,
        )

    def create_account(self) -> Account:
        account = Account(
            id=uuid4(),
        )
        self.accounts.append(account)
        return account

    def get_accounts(self) -> AccountResult:
        return AccountResult(
            items=lambda: self.accounts,
            entities=self,
        )
