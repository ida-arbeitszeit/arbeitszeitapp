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
    Hashable,
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

from arbeitszeit import records
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.injector import singleton
from arbeitszeit.records import (
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

T = TypeVar("T")
Key = TypeVar("Key", bound=Hashable)
Value = TypeVar("Value", bound=Hashable)
QueryResultT = TypeVar("QueryResultT", bound="QueryResultImpl")


@dataclass
class QueryResultImpl(Generic[T]):
    items: Callable[[], Iterable[T]]
    database: MockDatabase

    def limit(self, n: int) -> Self:
        return replace(
            self,
            items=lambda: islice(self.items(), n),
        )

    def offset(self, n: int) -> Self:
        return replace(
            self,
            items=lambda: islice(self.items(), n, None),
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
        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: plan.plan_creation_date,
                reverse=not ascending,
            ),
        )

    def ordered_by_activation_date(self, ascending: bool = True) -> PlanResult:
        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: plan.activation_date
                if plan.activation_date
                else datetime.min,
                reverse=not ascending,
            ),
        )

    def ordered_by_planner_name(self, ascending: bool = True) -> PlanResult:
        def get_company_name(planner_id: UUID) -> str:
            planner = self.database.get_company_by_id(planner_id)
            assert planner
            planner_name = planner.name
            return planner_name.casefold()

        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=lambda plan: get_company_name(plan.planner),
                reverse=not ascending,
            ),
        )

    def with_id_containing(self, query: str) -> PlanResult:
        return self._filter_elements(lambda plan: query in str(plan.id))

    def with_product_name_containing(self, query: str) -> PlanResult:
        return self._filter_elements(
            lambda plan: query.lower() in plan.prd_name.lower()
        )

    def that_are_approved(self) -> PlanResult:
        return self._filter_elements(lambda plan: plan.approval_date is not None)

    def that_were_activated_before(self, timestamp: datetime) -> Self:
        return self._filter_elements(
            lambda plan: plan.activation_date is not None
            and plan.activation_date <= timestamp
        )

    def that_will_expire_after(self, timestamp: datetime) -> Self:
        return self._filter_elements(
            lambda plan: plan.approval_date is not None
            and plan.approval_date + timedelta(days=plan.timeframe) > timestamp
        )

    def that_are_expired_as_of(self, timestamp: datetime) -> Self:
        return self._filter_elements(
            lambda plan: plan.approval_date is not None
            and plan.approval_date + timedelta(days=plan.timeframe) <= timestamp
        )

    def that_are_productive(self) -> PlanResult:
        return self._filter_elements(lambda plan: not plan.is_public_service)

    def that_are_public(self) -> PlanResult:
        return self._filter_elements(lambda plan: plan.is_public_service)

    def that_are_cooperating(self) -> PlanResult:
        return self._filter_elements(lambda plan: plan.cooperation is not None)

    def planned_by(self, *company: UUID) -> PlanResult:
        return self._filter_elements(lambda plan: plan.planner in company)

    def with_id(self, *id_: UUID) -> PlanResult:
        return self._filter_elements(lambda plan: plan.id in id_)

    def without_completed_review(self) -> PlanResult:
        return self._filter_elements(lambda plan: plan.approval_date is None)

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = None
    ) -> PlanResult:
        return self._filter_elements(
            lambda plan: plan.requested_cooperation == cooperation
            if cooperation
            else plan.requested_cooperation is not None
        )

    def that_are_in_same_cooperation_as(self, plan: UUID) -> PlanResult:
        def items_generator() -> Iterator[records.Plan]:
            plan_record = self.database.plans.get(plan)
            if not plan_record:
                return
            if plan_record.cooperation is None:
                yield from (
                    other_plan for other_plan in self.items() if other_plan.id == plan
                )
            else:
                yield from (
                    plan
                    for plan in self.items()
                    if plan.cooperation == plan_record.cooperation
                )

        return replace(
            self,
            items=items_generator,
        )

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> PlanResult:
        return self._filter_elements(
            (lambda plan: plan.cooperation in cooperation)
            if cooperation
            else (lambda plan: plan.cooperation is not None)
        )

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> PlanResult:
        def new_items() -> Iterator[Plan]:
            cooperations: Set[UUID] = {
                coop.id
                for coop, coordinator in self.database.get_cooperations().joined_with_current_coordinator()
                if coordinator.id in company
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

    def get_statistics(self) -> records.PlanningStatistics:
        """Return aggregate planning information for all plans
        included in a result set.
        """
        duration_sum = 0
        plan_count = 0
        production_costs = records.ProductionCosts(Decimal(0), Decimal(0), Decimal(0))
        for plan in self.items():
            plan_count += 1
            production_costs += plan.production_costs
            duration_sum += plan.timeframe
        return records.PlanningStatistics(
            average_plan_duration_in_days=(Decimal(duration_sum) / Decimal(plan_count))
            if plan_count > 0
            else Decimal(0),
            total_planned_costs=production_costs,
        )

    def that_are_not_hidden(self) -> Self:
        return self._filter_elements(lambda plan: not plan.hidden_by_user)

    def joined_with_planner_and_cooperating_plans(
        self, timestamp: datetime
    ) -> QueryResultImpl[
        Tuple[records.Plan, records.Company, List[records.PlanSummary]]
    ]:
        def items() -> (
            Iterable[Tuple[records.Plan, records.Company, List[records.PlanSummary]]]
        ):
            for plan in self.items():
                if plan.cooperation:
                    cooperating_plans = [
                        self.database.plans[p].to_summary()
                        for p in self.database.indices.plan_by_cooperation.get(
                            plan.cooperation
                        )
                        if self.database.plans[p].is_active_as_of(timestamp)
                    ]
                else:
                    cooperating_plans = []
                yield plan, self.database.companies[plan.planner], cooperating_plans

        return QueryResultImpl(
            database=self.database,
            items=items,
        )

    def joined_with_provided_product_amount(
        self,
    ) -> QueryResultImpl[Tuple[records.Plan, int]]:
        def items() -> Iterable[Tuple[Plan, int]]:
            for plan in self.items():
                company_purchases = (
                    purchase
                    for purchase in self.database.company_purchases.values()
                    if purchase.plan_id == plan.id
                )
                member_purchases = (
                    purchase
                    for purchase in self.database.consumer_purchases.values()
                    if purchase.plan_id == plan.id
                )
                amount_purchased_by_companies = sum(
                    purchase.amount for purchase in company_purchases
                )
                amount_purchased_by_members = sum(
                    purchase.amount for purchase in member_purchases
                )
                yield plan, amount_purchased_by_companies + amount_purchased_by_members

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def update(self) -> PlanUpdate:
        return PlanUpdate(
            items=self.items,
            update_functions=[],
            records=self.database,
        )


@dataclass
class PlanUpdate:
    items: Callable[[], Iterable[Plan]]
    update_functions: List[Callable[[Plan], None]]
    records: MockDatabase

    def set_cooperation(self, cooperation: Optional[UUID]) -> PlanUpdate:
        def update(plan: Plan) -> None:
            if plan.cooperation:
                self.records.indices.plan_by_cooperation.remove(
                    plan.cooperation, plan.id
                )
            if cooperation:
                self.records.indices.plan_by_cooperation.add(cooperation, plan.id)
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
        def update(plan: records.Plan) -> None:
            plan.hidden_by_user = True

        return self._add_update(update)

    def toggle_product_availability(self) -> Self:
        def update(plan: records.Plan) -> None:
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


class PlanDraftResult(QueryResultImpl[records.PlanDraft]):
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
            if draft in self.database.drafts:
                del self.database.drafts[draft]
                drafts_deleted += 1
        return drafts_deleted

    def update(self) -> PlanDraftUpdate:
        return PlanDraftUpdate(
            database=self.database,
            items=self.items,
        )


@dataclass
class PlanDraftUpdate:
    database: MockDatabase
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
        def items() -> Iterable[records.Cooperation]:
            for cooperation in self.items():
                tenures = [
                    self.database.coordination_tenures[id_]
                    for id_ in self.database.indices.coordination_tenure_by_cooperation.get(
                        cooperation.id
                    )
                ]
                tenures.sort(key=lambda t: t.start_date, reverse=True)
                if tenures and tenures[0].company == company_id:
                    yield cooperation

        return replace(self, items=items)

    def joined_with_current_coordinator(
        self,
    ) -> QueryResultImpl[Tuple[Cooperation, Company]]:
        def items() -> Iterable[Tuple[records.Cooperation, Company]]:
            for cooperation in self.items():
                tenures = [
                    self.database.coordination_tenures[id_]
                    for id_ in self.database.indices.coordination_tenure_by_cooperation.get(
                        cooperation.id
                    )
                ]
                tenures.sort(key=lambda t: t.start_date, reverse=True)
                if tenures:
                    yield cooperation, self.database.companies[tenures[0].company]

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class MemberResult(QueryResultImpl[Member]):
    def working_at_company(self, company: UUID) -> MemberResult:
        return self._filter_elements(
            lambda member: member.id
            in self.database.indices.worker_by_company.get(company),
        )

    def with_id(self, member: UUID) -> MemberResult:
        return self._filter_elements(lambda model: model.id == member)

    def with_email_address(self, email: str) -> MemberResult:
        return self._filter_elements(lambda model: model.email == email)

    def that_are_confirmed(self) -> MemberResult:
        def filtered(model: records.Member) -> bool:
            email = self.database.email_addresses[model.email]
            return email.confirmed_on is not None

        return self._filter_elements(filtered)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[records.Member, records.EmailAddress]]:
        def items() -> Iterable[Tuple[records.Member, records.EmailAddress]]:
            for member in self.items():
                yield member, self.database.email_addresses[member.email]

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class CompanyResult(QueryResultImpl[Company]):
    def with_id(self, id_: UUID) -> CompanyResult:
        return replace(
            self,
            items=lambda: filter(lambda company: company.id == id_, self.items()),
        )

    def with_email_address(self, email: str) -> CompanyResult:
        return replace(
            self,
            items=lambda: filter(lambda company: company.email == email, self.items()),
        )

    def that_are_workplace_of_member(self, member: UUID) -> CompanyResult:
        def items() -> Iterable[records.Company]:
            for company in self.items():
                workers = self.database.indices.worker_by_company.get(company.id)
                if member in workers:
                    yield company

        return replace(
            self,
            items=items,
        )

    def add_worker(self, member: UUID) -> int:
        companies_changed = 0
        for company in self.items():
            companies_changed += 1
            self.database.indices.worker_by_company.add(company.id, member)
        return companies_changed

    def with_name_containing(self, query: str) -> CompanyResult:
        return self._filter_elements(
            lambda company: query.lower() in company.name.lower()
        )

    def with_email_containing(self, query: str) -> CompanyResult:
        return self._filter_elements(
            lambda company: query.lower() in company.email.lower()
        )

    def that_are_confirmed(self) -> Self:
        def filtered(company: records.Company) -> bool:
            email = self.database.email_addresses[company.email]
            return email.confirmed_on is not None

        return self._filter_elements(filtered)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[records.Company, records.EmailAddress]]:
        def items() -> Iterable[Tuple[records.Company, records.EmailAddress]]:
            for company in self.items():
                yield company, self.database.email_addresses[company.email]

        return QueryResultImpl(
            items=items,
            database=self.database,
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
                == self.database.social_accounting.account,
                self.items(),
            ),
        )

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        plans = set(plan)

        def transaction_filter(transaction: Transaction) -> bool:
            consumer_purchases = (
                self.database.indices.consumer_purchase_by_transaction.get(
                    transaction.id
                )
            )
            company_purchases = (
                self.database.indices.company_purchase_by_transaction.get(
                    transaction.id
                )
            )
            transaction_plans = {
                self.database.consumer_purchases[i].plan_id for i in consumer_purchases
            } | {self.database.company_purchases[i].plan_id for i in company_purchases}
            return bool(transaction_plans & plans)

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
        Tuple[records.Transaction, records.AccountOwner, records.AccountOwner]
    ]:
        def get_account_owner(account_id: UUID) -> records.AccountOwner:
            if members := self.database.indices.member_by_account.get(account_id):
                (member,) = members
                return self.database.members[member]
            if companies := self.database.indices.company_by_account.get(account_id):
                (company,) = companies
                return self.database.companies[company]
            return self.database.social_accounting

        def items() -> (
            Iterable[
                Tuple[records.Transaction, records.AccountOwner, records.AccountOwner]
            ]
        ):
            for transaction in self.items():
                yield transaction, get_account_owner(
                    transaction.sending_account
                ), get_account_owner(transaction.receiving_account)

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class ConsumerPurchaseResult(QueryResultImpl[records.ConsumerPurchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> ConsumerPurchaseResult:
        def purchase_sorting_key(purchase: records.ConsumerPurchase) -> datetime:
            transaction = self.database.transactions[purchase.transaction_id]
            return transaction.date

        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=purchase_sorting_key,
                reverse=not ascending,
            ),
        )

    def where_buyer_is_member(self, member: UUID) -> ConsumerPurchaseResult:
        def filtered_items() -> Iterator[records.ConsumerPurchase]:
            member_account = self.database.members[member].account
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
                if transaction.sending_account == member_account:
                    yield purchase

        return replace(
            self,
            items=filtered_items,
        )

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[records.ConsumerPurchase, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[records.ConsumerPurchase, Transaction, Plan]]
        ):
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
                plan = self.database.plans[purchase.plan_id]
                yield purchase, transaction, plan

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )


class CompanyPurchaseResult(QueryResultImpl[records.CompanyPurchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> CompanyPurchaseResult:
        def purchase_sorting_key(purchase: records.CompanyPurchase) -> datetime:
            transaction = self.database.transactions[purchase.transaction_id]
            return transaction.date

        return replace(
            self,
            items=lambda: sorted(
                list(self.items()),
                key=purchase_sorting_key,
                reverse=not ascending,
            ),
        )

    def where_buyer_is_company(self, company: UUID) -> CompanyPurchaseResult:
        def filtered_items() -> Iterator[records.CompanyPurchase]:
            company_record = self.database.get_company_by_id(company)
            if company_record is None:
                return None
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
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

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[records.CompanyPurchase, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[records.CompanyPurchase, Transaction, Plan]]
        ):
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
                plan = self.database.plans[purchase.plan_id]
                yield purchase, transaction, plan

        return replace(
            self,  # type: ignore
            items=joined_items,
        )

    def joined_with_transaction(
        self,
    ) -> QueryResultImpl[Tuple[records.CompanyPurchase, records.Transaction]]:
        def joined_items() -> (
            Iterator[Tuple[records.CompanyPurchase, records.Transaction]]
        ):
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
                yield purchase, transaction

        return replace(
            self,  # type: ignore
            items=joined_items,
        )

    def joined_with_transaction_and_provider(
        self,
    ) -> QueryResultImpl[Tuple[records.CompanyPurchase, Transaction, Company]]:
        def joined_items() -> (
            Iterator[Tuple[records.CompanyPurchase, Transaction, Company]]
        ):
            for purchase in self.items():
                transaction = self.database.transactions[purchase.transaction_id]
                plan = self.database.plans[purchase.plan_id]
                provider = self.database.companies[plan.planner]
                yield purchase, transaction, provider

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )


class AccountResult(QueryResultImpl[Account]):
    def with_id(self, *id_: UUID) -> AccountResult:
        return replace(
            self,
            items=lambda: filter(lambda account: account.id in id_, self.items()),
        )

    def owned_by_member(self, *member: UUID) -> Self:
        def items():
            memberes = set(member)
            for account in self.items():
                owner_ids = self.database.indices.member_by_account.get(account.id)
                if memberes & owner_ids:
                    yield account

        return replace(
            self,
            items=items,
        )

    def owned_by_company(self, *company: UUID) -> Self:
        def items() -> Iterable[Account]:
            companies = set(company)
            for account in self.items():
                owner_ids = self.database.indices.company_by_account.get(account.id)
                if companies & owner_ids:
                    yield account

        return replace(
            self,
            items=items,
        )

    def that_are_member_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.database.member_accounts, self.items()
            ),
        )

    def that_are_product_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.database.prd_accounts, self.items()
            ),
        )

    def that_are_labour_accounts(self) -> Self:
        return replace(
            self,
            items=lambda: filter(
                lambda account: account in self.database.l_accounts, self.items()
            ),
        )

    def joined_with_owner(
        self,
    ) -> QueryResultImpl[Tuple[Account, records.AccountOwner]]:
        def items() -> Iterable[Tuple[Account, records.AccountOwner]]:
            for account in self.items():
                if account.id == self.database.social_accounting.account:
                    yield account, self.database.social_accounting
                for member in self.database.members.values():
                    if account.id == member.account:
                        yield account, member
                for company in self.database.companies.values():
                    if account.id in [
                        company.means_account,
                        company.raw_material_account,
                        company.work_account,
                        company.product_account,
                    ]:
                        yield account, company

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def joined_with_balance(self) -> QueryResultImpl[Tuple[Account, Decimal]]:
        def items() -> Iterable[Tuple[Account, Decimal]]:
            for account in self.items():
                transactions = self.database.get_transactions()
                received_transactions = transactions.where_account_is_receiver(
                    account.id
                )
                sent_transactions = transactions.where_account_is_sender(account.id)
                yield account, decimal_sum(
                    transaction.amount_received for transaction in received_transactions
                ) - decimal_sum(
                    transaction.amount_sent for transaction in sent_transactions
                )

        return QueryResultImpl(items=items, database=self.database)


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
        self.database.company_work_invites = [
            invite
            for invite in self.database.company_work_invites
            if invite.id not in invites_to_delete
        ]


class EmailAddressResult(QueryResultImpl[records.EmailAddress]):
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
    items: Callable[[], Iterable[records.EmailAddress]]
    transformation: Callable[[records.EmailAddress], None] = field(
        default=lambda _: None
    )

    def set_confirmation_timestamp(self, timestamp: Optional[datetime]) -> Self:
        def transformation(item: records.EmailAddress) -> None:
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
class MockDatabase:
    def __init__(self) -> None:
        self.members: Dict[UUID, Member] = {}
        self.companies: Dict[UUID, Company] = {}
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
        self.cooperations: Dict[UUID, Cooperation] = dict()
        self.coordination_tenures: Dict[UUID, records.CoordinationTenure] = dict()
        self.consumer_purchases: Dict[UUID, records.ConsumerPurchase] = dict()
        self.company_purchases: Dict[UUID, records.CompanyPurchase] = dict()
        self.company_work_invites: List[CompanyWorkInvite] = list()
        self.email_addresses: Dict[str, records.EmailAddress] = dict()
        self.drafts: Dict[UUID, PlanDraft] = dict()
        self.indices = Indices()

    def create_email_address(
        self, *, address: str, confirmed_on: Optional[datetime]
    ) -> records.EmailAddress:
        assert address not in self.email_addresses
        record = records.EmailAddress(
            address=address,
            confirmed_on=confirmed_on,
        )
        self.email_addresses[address] = record
        return record

    def get_company_by_id(self, company: UUID) -> Optional[Company]:
        return self.companies.get(company)

    def create_consumer_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.ConsumerPurchase:
        purchase = records.ConsumerPurchase(
            id=uuid4(),
            plan_id=plan,
            transaction_id=transaction,
            amount=amount,
        )
        self.consumer_purchases[purchase.id] = purchase
        self.indices.consumer_purchase_by_transaction.add(transaction, purchase.id)
        self.indices.consumer_purchase_by_plan.add(plan, purchase.id)
        return purchase

    def get_consumer_purchases(self) -> ConsumerPurchaseResult:
        return ConsumerPurchaseResult(
            database=self,
            items=self.consumer_purchases.values,
        )

    def create_company_purchase(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.CompanyPurchase:
        purchase = records.CompanyPurchase(
            id=uuid4(),
            amount=amount,
            plan_id=plan,
            transaction_id=transaction,
        )
        self.company_purchases[purchase.id] = purchase
        self.indices.company_purchase_by_transaction.add(transaction, purchase.id)
        self.indices.company_purchase_by_plan.add(plan, purchase.id)
        return purchase

    def get_company_purchases(self) -> CompanyPurchaseResult:
        return CompanyPurchaseResult(database=self, items=self.company_purchases.values)

    def get_plans(self) -> PlanResult:
        return PlanResult(
            items=lambda: self.plans.values(),
            database=self,
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
    ) -> records.Plan:
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
    ) -> Cooperation:
        cooperation_id = uuid4()
        cooperation = Cooperation(
            id=cooperation_id,
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
        )
        self.cooperations[cooperation_id] = cooperation
        return cooperation

    def get_cooperations(self) -> CooperationResult:
        return CooperationResult(
            items=lambda: self.cooperations.values(),
            database=self,
        )

    def create_coordination_tenure(
        self, company: UUID, cooperation: UUID, start_date: datetime
    ) -> records.CoordinationTenure:
        tenure_id = uuid4()
        tenure = records.CoordinationTenure(
            id=tenure_id,
            company=company,
            cooperation=cooperation,
            start_date=start_date,
        )
        self.coordination_tenures[tenure_id] = tenure
        self.indices.coordination_tenure_by_cooperation.add(cooperation, tenure_id)
        return tenure

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
            database=self,
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
            database=self,
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
            database=self,
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
        self.indices.member_by_account.add(member.account, member.id)
        return member

    def get_members(self) -> MemberResult:
        return MemberResult(
            items=lambda: self.members.values(),
            database=self,
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
        self.indices.company_by_account.add(means_account.id, new_company.id)
        self.indices.company_by_account.add(labour_account.id, new_company.id)
        self.indices.company_by_account.add(resource_account.id, new_company.id)
        self.indices.company_by_account.add(products_account.id, new_company.id)
        return new_company

    def get_companies(self) -> CompanyResult:
        return CompanyResult(
            items=lambda: self.companies.values(),
            database=self,
        )

    def get_email_addresses(self) -> EmailAddressResult:
        return EmailAddressResult(
            database=self,
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
            database=self,
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
            database=self,
        )


class Index(Generic[Key, Value]):
    def __init__(self) -> None:
        self._index: Dict[Key, Set[Value]] = defaultdict(set)

    def get(self, key: Key) -> Set[Value]:
        return self._index[key]

    def add(self, key: Key, value: Value) -> None:
        self._index[key].add(value)

    def remove(self, key: Key, value: Value) -> None:
        self._index[key].remove(value)


@dataclass
class Indices:
    worker_by_company: Index[UUID, UUID] = field(default_factory=Index)
    plan_by_cooperation: Index[UUID, UUID] = field(default_factory=Index)
    member_by_account: Index[UUID, UUID] = field(default_factory=Index)
    company_by_account: Index[UUID, UUID] = field(default_factory=Index)
    consumer_purchase_by_transaction: Index[UUID, UUID] = field(default_factory=Index)
    consumer_purchase_by_plan: Index[UUID, UUID] = field(default_factory=Index)
    company_purchase_by_transaction: Index[UUID, UUID] = field(default_factory=Index)
    company_purchase_by_plan: Index[UUID, UUID] = field(default_factory=Index)
    coordination_tenure_by_cooperation: Index[UUID, UUID] = field(default_factory=Index)
