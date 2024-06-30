from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from decimal import Decimal
from itertools import islice
from typing import (
    Callable,
    Dict,
    Generator,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    List,
    Optional,
    Protocol,
    Self,
    Set,
    Tuple,
    TypeVar,
)
from uuid import UUID, uuid4

from arbeitszeit import records
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.injector import singleton
from arbeitszeit.records import (
    Account,
    Accountant,
    Company,
    CompanyWorkInvite,
    Cooperation,
    CoordinationTenure,
    CoordinationTransferRequest,
    Member,
    Plan,
    PlanDraft,
    ProductionCosts,
    SocialAccounting,
    Transaction,
)

Many = TypeVar("Many", bound=Hashable)
One = TypeVar("One", bound=Hashable)
S_Hash = TypeVar("S_Hash", bound=Hashable)
T = TypeVar("T")
T_Hash = TypeVar("T_Hash", bound=Hashable)

Key = TypeVar("Key", bound=Hashable)
Value = TypeVar("Value", bound=Hashable)


class Sortable(Protocol):
    def __lt__(self, other: Self) -> bool: ...


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

    def sorted_by(self, key: Callable[[T], Sortable], reverse: bool = False) -> Self:
        return replace(
            self,
            items=lambda: sorted(list(self.items()), key=key, reverse=reverse),
        )

    def from_iterable(self, items: Callable[[], Iterable[T]]) -> Self:
        return replace(
            self,
            items=items,
        )


class PlanResult(QueryResultImpl[Plan]):
    def ordered_by_creation_date(self, ascending: bool = True) -> Self:
        return self.sorted_by(
            key=lambda plan: plan.plan_creation_date, reverse=not ascending
        )

    def ordered_by_activation_date(self, ascending: bool = True) -> Self:
        return self.sorted_by(
            key=lambda plan: (
                plan.activation_date if plan.activation_date else datetime.min
            ),
            reverse=not ascending,
        )

    def ordered_by_planner_name(self, ascending: bool = True) -> Self:
        def get_company_name(planner_id: UUID) -> str:
            planner = self.database.get_company_by_id(planner_id)
            assert planner
            planner_name = planner.name
            return planner_name.casefold()

        return self.sorted_by(
            key=lambda plan: get_company_name(plan.planner),
            reverse=not ascending,
        )

    def with_id_containing(self, query: str) -> Self:
        return self._filter_elements(lambda plan: query in str(plan.id))

    def with_product_name_containing(self, query: str) -> Self:
        return self._filter_elements(
            lambda plan: query.lower() in plan.prd_name.lower()
        )

    def that_are_approved(self) -> Self:
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

    def that_are_productive(self) -> Self:
        return self._filter_elements(lambda plan: not plan.is_public_service)

    def that_are_public(self) -> Self:
        return self._filter_elements(lambda plan: plan.is_public_service)

    def that_are_cooperating(self) -> Self:
        def cooperation_of(plan: records.Plan) -> Optional[UUID]:
            return self.database.relationships.cooperation_to_plan.get_one(plan.id)

        return self._filter_elements(lambda plan: cooperation_of(plan) is not None)

    def planned_by(self, *company: UUID) -> Self:
        return self._filter_elements(lambda plan: plan.planner in company)

    def with_id(self, *id_: UUID) -> Self:
        return self._filter_elements(lambda plan: plan.id in id_)

    def without_completed_review(self) -> Self:
        return self._filter_elements(lambda plan: plan.approval_date is None)

    def with_open_cooperation_request(
        self, *, cooperation: Optional[UUID] = None
    ) -> Self:
        return self._filter_elements(
            lambda plan: (
                plan.requested_cooperation == cooperation
                if cooperation
                else plan.requested_cooperation is not None
            )
        )

    def that_are_in_same_cooperation_as(self, plan: UUID) -> Self:
        def items_generator() -> Iterator[records.Plan]:
            cooperation_id = self.database.relationships.cooperation_to_plan.get_one(
                plan
            )
            plan_record = self.database.plans.get(plan)
            if not plan_record:
                return
            if cooperation_id is None:
                yield from (
                    other_plan for other_plan in self.items() if other_plan.id == plan
                )
            else:
                for candidate in self.items():
                    candidate_cooperation = (
                        self.database.relationships.cooperation_to_plan.get_one(
                            candidate.id
                        )
                    )
                    if candidate_cooperation == cooperation_id:
                        yield candidate

        return self.from_iterable(items_generator)

    def that_are_part_of_cooperation(self, *cooperation: UUID) -> Self:
        def cooperation_of(plan: records.Plan) -> Optional[UUID]:
            return self.database.relationships.cooperation_to_plan.get_one(plan.id)

        return self._filter_elements(
            (lambda plan: cooperation_of(plan) in cooperation)
            if cooperation
            else (lambda plan: cooperation_of(plan) is not None)
        )

    def that_request_cooperation_with_coordinator(self, *company: UUID) -> Self:
        def new_items() -> Iterator[Plan]:
            cooperations: Set[UUID] = {
                coop.id
                for coop, coordinator in self.database.get_cooperations().joined_with_current_coordinator()
                if coordinator.id in company
            }
            return filter(
                lambda plan: (
                    plan.requested_cooperation in cooperations
                    if company
                    else plan.requested_cooperation is not None
                ),
                self.items(),
            )

        return self.from_iterable(items=new_items)

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
            average_plan_duration_in_days=(
                (Decimal(duration_sum) / Decimal(plan_count))
                if plan_count > 0
                else Decimal(0)
            ),
            total_planned_costs=production_costs,
        )

    def that_are_not_hidden(self) -> Self:
        return self._filter_elements(lambda plan: not plan.hidden_by_user)

    def joined_with_planner_and_cooperation_and_cooperating_plans(
        self, timestamp: datetime
    ) -> QueryResultImpl[
        Tuple[
            records.Plan,
            records.Company,
            Optional[records.Cooperation],
            List[records.PlanSummary],
        ]
    ]:
        def items() -> Iterable[
            Tuple[
                records.Plan,
                records.Company,
                Optional[Cooperation],
                List[records.PlanSummary],
            ]
        ]:
            for plan in self.items():
                cooperation_id = (
                    self.database.relationships.cooperation_to_plan.get_one(plan.id)
                )
                if cooperation_id:
                    cooperating_plans = [
                        self.database.plans[p].to_summary()
                        for p in self.database.relationships.cooperation_to_plan.get_many(
                            cooperation_id
                        )
                        if self.database.plans[p].is_active_as_of(timestamp)
                    ]
                else:
                    cooperating_plans = []
                cooperation = (
                    self.database.cooperations[cooperation_id]
                    if cooperation_id
                    else None
                )
                yield plan, self.database.companies[
                    plan.planner
                ], cooperation, cooperating_plans

        return QueryResultImpl(
            database=self.database,
            items=items,
        )

    def joined_with_cooperation(
        self,
    ) -> QueryResultImpl[Tuple[records.Plan, Optional[records.Cooperation]]]:
        def items() -> (
            Generator[tuple[records.Plan, Optional[records.Cooperation]], None, None]
        ):
            for p in self.items():
                cooperation_id = (
                    self.database.relationships.cooperation_to_plan.get_one(p.id)
                )
                if cooperation_id:
                    yield p, self.database.cooperations[cooperation_id]
                else:
                    yield p, None

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def joined_with_provided_product_amount(
        self,
    ) -> QueryResultImpl[Tuple[records.Plan, int]]:
        def items() -> Iterable[Tuple[Plan, int]]:
            for plan in self.items():
                productive_consumptions = (
                    consumption
                    for consumption in self.database.productive_consumptions.values()
                    if consumption.plan_id == plan.id
                )
                private_consumptions = (
                    consumption
                    for consumption in self.database.private_consumptions.values()
                    if consumption.plan_id == plan.id
                )
                amount_consumed_by_companies = sum(
                    consumption.amount for consumption in productive_consumptions
                )
                amount_consumed_by_members = sum(
                    consumption.amount for consumption in private_consumptions
                )
                yield plan, amount_consumed_by_companies + amount_consumed_by_members

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def delete(self) -> None:
        plans_to_delete = [plan.id for plan in self.items()]
        for plan in plans_to_delete:
            if plan in self.database.plans:
                del self.database.plans[plan]

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

    def set_cooperation(self, cooperation: Optional[UUID]) -> Self:
        def update(plan: Plan) -> None:
            if cooperation:
                assert cooperation in self.records.cooperations
                cooperation_plans = (
                    self.records.relationships.cooperation_to_plan.get_many(cooperation)
                )
                if plan.id not in cooperation_plans:
                    self.records.relationships.cooperation_to_plan.relate(
                        cooperation, plan.id
                    )
            else:
                current_coop = self.records.relationships.cooperation_to_plan.get_one(
                    plan.id
                )
                if current_coop:
                    self.records.relationships.cooperation_to_plan.dissociate(
                        current_coop, plan.id
                    )

        return self._add_update(update)

    def set_requested_cooperation(self, cooperation: Optional[UUID]) -> Self:
        def update(plan: Plan) -> None:
            plan.requested_cooperation = cooperation

        return self._add_update(update)

    def set_approval_date(self, approval_date: Optional[datetime]) -> Self:
        def update(plan: Plan) -> None:
            plan.approval_date = approval_date

        return self._add_update(update)

    def set_activation_timestamp(
        self, activation_timestamp: Optional[datetime]
    ) -> Self:
        def update(plan: Plan) -> None:
            plan.activation_date = activation_timestamp

        return self._add_update(update)

    def hide(self) -> Self:
        def update(plan: records.Plan) -> None:
            plan.hidden_by_user = True

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
        return self._filter_elements(
            lambda draft: draft.id == id_,
        )

    def planned_by(self, *company: UUID) -> Self:
        return self._filter_elements(lambda draft: draft.planner in company)

    def delete(self) -> int:
        drafts_to_delete = [draft.id for draft in self.items()]
        drafts_deleted = 0
        for draft in drafts_to_delete:
            if draft in self.database.drafts:
                del self.database.drafts[draft]
                drafts_deleted += 1
        return drafts_deleted

    def joined_with_planner_and_email_address(
        self,
    ) -> QueryResultImpl[
        tuple[records.PlanDraft, records.Company, records.EmailAddress]
    ]:
        def items() -> (
            Iterable[tuple[records.PlanDraft, records.Company, records.EmailAddress]]
        ):
            for draft in self.items():
                planner = self.database.companies[draft.planner]
                credentials_id = self.database.relationships.account_credentials_to_company.get_left_value(
                    planner.id
                )
                if not credentials_id:
                    continue
                account_credentials = self.database.account_credentials[credentials_id]
                email_address = self.database.email_addresses[
                    account_credentials.email_address
                ]
                yield draft, planner, email_address

        return QueryResultImpl(
            database=self.database,
            items=items,
        )

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
        return self._filter_elements(lambda coop: coop.id == id_)

    def with_name_ignoring_case(self, name: str) -> Self:
        return self._filter_elements(lambda coop: coop.name.lower() == name.lower())

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

        return self.from_iterable(items)

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


class CoordinationTenureResult(QueryResultImpl[CoordinationTenure]):
    def with_id(self, id_: UUID) -> Self:
        return self._filter_elements(lambda model: model.id == id_)

    def of_cooperation(self, cooperation_id: UUID) -> Self:
        return self._filter_elements(lambda model: model.cooperation == cooperation_id)

    def joined_with_coordinator(
        self,
    ) -> QueryResultImpl[Tuple[records.CoordinationTenure, records.Company]]:
        def items() -> Iterable[Tuple[records.CoordinationTenure, records.Company]]:
            for tenure in self.items():
                company = self.database.companies[tenure.company]
                yield tenure, company

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def ordered_by_start_date(self, *, ascending: bool = True) -> Self:
        return self.sorted_by(
            key=lambda tenure: tenure.start_date, reverse=not ascending
        )


class CoordinationTransferRequestResult(QueryResultImpl[CoordinationTransferRequest]):
    def with_id(self, id_: UUID) -> Self:
        return self._filter_elements(lambda model: model.id == id_)

    def requested_by(self, coordination_tenure: UUID) -> Self:
        return self._filter_elements(
            lambda tenure_request: tenure_request.requesting_coordination_tenure
            == coordination_tenure
        )

    def joined_with_cooperation(
        self,
    ) -> QueryResultImpl[Tuple[CoordinationTransferRequest, Cooperation]]:
        def items() -> Iterable[Tuple[CoordinationTransferRequest, Cooperation]]:
            for transfer_request in self.items():
                requesting_tenure = self.database.coordination_tenures[
                    transfer_request.requesting_coordination_tenure
                ]
                cooperation = self.database.cooperations[requesting_tenure.cooperation]
                yield transfer_request, cooperation

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class MemberResult(QueryResultImpl[Member]):
    def working_at_company(self, company: UUID) -> Self:
        return self._filter_elements(
            lambda member: member.id
            in self.database.relationships.company_to_workers.get_right_values(company),
        )

    def with_id(self, member: UUID) -> Self:
        return self._filter_elements(lambda model: model.id == member)

    def with_email_address(self, email: str) -> Self:
        def items() -> Iterable[records.Member]:
            for member in self.items():
                account_id = self.database.relationships.account_credentials_to_member.get_left_value(
                    member.id
                )
                assert account_id
                account = self.database.account_credentials[account_id]
                if account.email_address.lower() == email.lower():
                    yield member

        return self.from_iterable(items=items)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[records.Member, records.EmailAddress]]:
        def items() -> Iterable[Tuple[records.Member, records.EmailAddress]]:
            for member in self.items():
                credentials_id = self.database.relationships.account_credentials_to_member.get_left_value(
                    member.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                email_address = self.database.email_addresses[credentials.email_address]
                yield member, email_address

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class CompanyResult(QueryResultImpl[Company]):
    def with_id(self, id_: UUID) -> Self:
        return self._filter_elements(lambda company: company.id == id_)

    def with_email_address(self, email: str) -> Self:
        def items() -> Iterable[records.Company]:
            for company in self.items():
                credentials_id = self.database.relationships.account_credentials_to_company.get_left_value(
                    company.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                if credentials.email_address.lower() == email.lower():
                    yield company

        return self.from_iterable(items=items)

    def that_are_workplace_of_member(self, member: UUID) -> Self:
        def items() -> Iterable[records.Company]:
            for company in self.items():
                workers = (
                    self.database.relationships.company_to_workers.get_right_values(
                        company.id
                    )
                )
                if member in workers:
                    yield company

        return self.from_iterable(items=items)

    def that_is_coordinating_cooperation(self, cooperation: UUID) -> Self:
        def items() -> Iterable[records.Company]:
            tenures = sorted(
                [
                    self.database.coordination_tenures[t]
                    for t in self.database.indices.coordination_tenure_by_cooperation.get(
                        cooperation
                    )
                ],
                key=lambda t: t.start_date,
                reverse=True,
            )
            if not tenures:
                return
            latest_tenure = tenures[0]
            for company in self.items():
                if latest_tenure.company == company.id:
                    yield company

        return self.from_iterable(items=items)

    def add_worker(self, member: UUID) -> int:
        companies_changed = 0
        for company in self.items():
            companies_changed += 1
            self.database.relationships.company_to_workers.relate(company.id, member)
        return companies_changed

    def with_name_containing(self, query: str) -> Self:
        return self._filter_elements(
            lambda company: query.lower() in company.name.lower()
        )

    def with_email_containing(self, query: str) -> Self:
        def items() -> Iterable[records.Company]:
            for company in self.items():
                credentials_id = self.database.relationships.account_credentials_to_company.get_left_value(
                    company.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                if query.lower() in credentials.email_address.lower():
                    yield company

        return self.from_iterable(items=items)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[records.Company, records.EmailAddress]]:
        def items() -> Iterable[Tuple[records.Company, records.EmailAddress]]:
            for company in self.items():
                credentials_id = self.database.relationships.account_credentials_to_company.get_left_value(
                    company.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                yield company, self.database.email_addresses[credentials.email_address]

        return QueryResultImpl(
            items=items,
            database=self.database,
        )


class AccountantResult(QueryResultImpl[Accountant]):
    def with_email_address(self, email: str) -> Self:
        def items() -> Iterable[Accountant]:
            for accountant in self.items():
                credentials_id = self.database.relationships.account_credentials_to_accountant.get_left_value(
                    accountant.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                if credentials.email_address.lower() == email.lower():
                    yield accountant

        return self.from_iterable(items=items)

    def with_id(self, id_: UUID) -> Self:
        return self._filter_elements(lambda accountant: accountant.id == id_)

    def joined_with_email_address(
        self,
    ) -> QueryResultImpl[Tuple[Accountant, records.EmailAddress]]:
        def items() -> Iterable[Tuple[Accountant, records.EmailAddress]]:
            for accountant in self.items():
                credentials_id = self.database.relationships.account_credentials_to_accountant.get_left_value(
                    accountant.id
                )
                assert credentials_id
                credentials = self.database.account_credentials[credentials_id]
                email_address = self.database.email_addresses[credentials.email_address]
                yield accountant, email_address

        return QueryResultImpl(
            database=self.database,
            items=items,
        )


class TransactionResult(QueryResultImpl[Transaction]):
    def where_account_is_sender_or_receiver(self, *account: UUID) -> Self:
        return self._filter_elements(
            lambda transaction: transaction.sending_account in account
            or transaction.receiving_account in account
        )

    def where_account_is_sender(self, *account: UUID) -> Self:
        return self._filter_elements(
            lambda transaction: transaction.sending_account in account
        )

    def where_account_is_receiver(self, *account: UUID) -> Self:
        return self._filter_elements(
            lambda transaction: transaction.receiving_account in account
        )

    def ordered_by_transaction_date(self, descending: bool = False) -> Self:
        return self.sorted_by(
            key=lambda transaction: transaction.date,
            reverse=descending,
        )

    def where_sender_is_social_accounting(self) -> Self:
        return self._filter_elements(
            lambda transaction: transaction.sending_account
            == self.database.social_accounting.account
        )

    def that_were_a_sale_for_plan(self, *plan: UUID) -> Self:
        plans = set(plan)

        def transaction_filter(transaction: Transaction) -> bool:
            private_consumptions = (
                self.database.indices.private_consumption_by_transaction.get(
                    transaction.id
                )
            )
            productive_consumptions = (
                self.database.indices.productive_consumption_by_transaction.get(
                    transaction.id
                )
            )
            transaction_plans = {
                self.database.private_consumptions[i].plan_id
                for i in private_consumptions
            } | {
                self.database.productive_consumptions[i].plan_id
                for i in productive_consumptions
            }
            return bool(transaction_plans & plans)

        return self._filter_elements(transaction_filter)

    def joined_with_receiver(
        self,
    ) -> QueryResultImpl[Tuple[records.Transaction, records.AccountOwner]]:
        def get_account_owner(account_id: UUID) -> records.AccountOwner:
            if members := self.database.indices.member_by_account.get(account_id):
                (member,) = members
                return self.database.members[member]
            if companies := self.database.indices.company_by_account.get(account_id):
                (company,) = companies
                return self.database.companies[company]
            return self.database.social_accounting

        def items() -> Iterable[Tuple[records.Transaction, records.AccountOwner]]:
            for transaction in self.items():
                yield transaction, get_account_owner(transaction.receiving_account)

        return QueryResultImpl(
            items=items,
            database=self.database,
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


class PrivateConsumptionResult(QueryResultImpl[records.PrivateConsumption]):
    def ordered_by_creation_date(self, *, ascending: bool = True) -> Self:
        def consumption_sorting_key(
            consumption: records.PrivateConsumption,
        ) -> datetime:
            transaction = self.database.transactions[consumption.transaction_id]
            return transaction.date

        return self.sorted_by(key=consumption_sorting_key, reverse=not ascending)

    def where_consumer_is_member(self, member: UUID) -> Self:
        def filtered_items() -> Iterator[records.PrivateConsumption]:
            member_account = self.database.members[member].account
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                if transaction.sending_account == member_account:
                    yield consumption

        return self.from_iterable(items=filtered_items)

    def where_provider_is_company(self, company: UUID) -> Self:
        def filtered_items() -> Iterator[records.PrivateConsumption]:
            company_record = self.database.get_company_by_id(company)
            if company_record is None:
                return None
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                if transaction.receiving_account == company_record.product_account:
                    yield consumption

        return self.from_iterable(items=filtered_items)

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[records.PrivateConsumption, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[records.PrivateConsumption, Transaction, Plan]]
        ):
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                plan = self.database.plans[consumption.plan_id]
                yield consumption, transaction, plan

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )

    def joined_with_transaction_and_plan_and_consumer(
        self,
    ) -> QueryResultImpl[
        Tuple[
            records.PrivateConsumption,
            records.Transaction,
            records.Plan,
            records.Member,
        ]
    ]:
        def joined_items() -> Iterator[
            Tuple[
                records.PrivateConsumption,
                records.Transaction,
                records.Plan,
                records.Member,
            ]
        ]:
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                plan = self.database.plans[consumption.plan_id]
                sending_account = transaction.sending_account
                members = self.database.indices.member_by_account.get(sending_account)
                (member_id,) = members
                member = self.database.members[member_id]
                yield consumption, transaction, plan, member

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )


class ProductiveConsumptionResult(QueryResultImpl[records.ProductiveConsumption]):
    def ordered_by_creation_date(self, *, ascending: bool = True) -> Self:
        def consumption_sorting_key(
            consumption: records.ProductiveConsumption,
        ) -> datetime:
            transaction = self.database.transactions[consumption.transaction_id]
            return transaction.date

        return self.sorted_by(key=consumption_sorting_key, reverse=not ascending)

    def where_consumer_is_company(self, company: UUID) -> Self:
        def filtered_items() -> Iterator[records.ProductiveConsumption]:
            company_record = self.database.get_company_by_id(company)
            if company_record is None:
                return None
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                if (
                    transaction.sending_account == company_record.means_account
                    or transaction.sending_account
                    == company_record.raw_material_account
                ):
                    yield consumption

        return self.from_iterable(filtered_items)

    def where_provider_is_company(self, company: UUID) -> Self:
        def filtered_items() -> Iterator[records.ProductiveConsumption]:
            company_record = self.database.get_company_by_id(company)
            if company_record is None:
                return None
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                if transaction.receiving_account == company_record.product_account:
                    yield consumption

        return self.from_iterable(items=filtered_items)

    def joined_with_transactions_and_plan(
        self,
    ) -> QueryResultImpl[Tuple[records.ProductiveConsumption, Transaction, Plan]]:
        def joined_items() -> (
            Iterator[Tuple[records.ProductiveConsumption, Transaction, Plan]]
        ):
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                plan = self.database.plans[consumption.plan_id]
                yield consumption, transaction, plan

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )

    def joined_with_transaction(
        self,
    ) -> QueryResultImpl[Tuple[records.ProductiveConsumption, records.Transaction]]:
        def joined_items() -> (
            Iterator[Tuple[records.ProductiveConsumption, records.Transaction]]
        ):
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                yield consumption, transaction

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )

    def joined_with_transaction_and_provider(
        self,
    ) -> QueryResultImpl[Tuple[records.ProductiveConsumption, Transaction, Company]]:
        def joined_items() -> (
            Iterator[Tuple[records.ProductiveConsumption, Transaction, Company]]
        ):
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                plan = self.database.plans[consumption.plan_id]
                provider = self.database.companies[plan.planner]
                yield consumption, transaction, provider

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )

    def joined_with_transaction_and_plan_and_consumer(
        self,
    ) -> QueryResultImpl[
        Tuple[
            records.ProductiveConsumption,
            records.Transaction,
            records.Plan,
            records.Company,
        ]
    ]:
        def joined_items() -> Iterator[
            Tuple[
                records.ProductiveConsumption,
                records.Transaction,
                records.Plan,
                records.Company,
            ]
        ]:
            for consumption in self.items():
                transaction = self.database.transactions[consumption.transaction_id]
                plan = self.database.plans[consumption.plan_id]
                sending_account = transaction.sending_account
                companies = self.database.indices.company_by_account.get(
                    sending_account
                )
                (company_id,) = companies
                company = self.database.companies[company_id]
                yield consumption, transaction, plan, company

        return QueryResultImpl(
            items=joined_items,
            database=self.database,
        )


class AccountResult(QueryResultImpl[Account]):
    def with_id(self, *id_: UUID) -> Self:
        return self._filter_elements(lambda account: account.id in id_)

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

        return self.from_iterable(items=items)

    def that_are_member_accounts(self) -> Self:
        return self._filter_elements(
            lambda account: account in self.database.member_accounts
        )

    def that_are_product_accounts(self) -> Self:
        return self._filter_elements(
            lambda account: account in self.database.prd_accounts
        )

    def that_are_labour_accounts(self) -> Self:
        return self._filter_elements(
            lambda account: account in self.database.l_accounts
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
        return self._filter_elements(lambda invite: invite.company == company)

    def addressing(self, member: UUID) -> Self:
        return self._filter_elements(lambda invite: invite.member == member)

    def with_id(self, id: UUID) -> Self:
        return self._filter_elements(lambda invite: invite.id == id)

    def delete(self) -> None:
        invites_to_delete = set(invite.id for invite in self.items())
        self.database.company_work_invites = [
            invite
            for invite in self.database.company_work_invites
            if invite.id not in invites_to_delete
        ]


class PasswordResetRequestResult(QueryResultImpl[records.PasswordResetRequest]):
    def with_email_address(self, email_address: str) -> Self:
        return self._filter_elements(
            lambda record: record.email_address == email_address
        )

    def with_creation_date_after(self, creation_threshold: datetime) -> Self:
        return self._filter_elements(
            lambda record: record.created_at > creation_threshold
        )


class EmailAddressResult(QueryResultImpl[records.EmailAddress]):
    def with_address(self, *addresses: str) -> Self:
        return self._filter_elements(lambda a: a.address in addresses)

    def that_belong_to_member(self, member: UUID) -> Self:
        def items() -> Iterable[records.EmailAddress]:
            for address in self.items():
                (credentials_id,) = (
                    self.database.indices.account_credentials_by_email_address_lowercased.get(
                        address.address.lower()
                    )
                )
                member_id = self.database.relationships.account_credentials_to_member.get_right_value(
                    credentials_id
                )
                if member_id and member_id == member:
                    yield address

        return self.from_iterable(items=items)

    def that_belong_to_company(self, company: UUID) -> Self:
        def items() -> Iterable[records.EmailAddress]:
            for address in self.items():
                (credentials_id,) = (
                    self.database.indices.account_credentials_by_email_address_lowercased.get(
                        address.address.lower()
                    )
                )
                company_id = self.database.relationships.account_credentials_to_company.get_right_value(
                    credentials_id
                )
                if company_id and company_id == company:
                    yield address

        return self.from_iterable(items=items)

    def delete(self) -> None:
        addresses_to_delete = [address.address for address in self.items()]
        for address in addresses_to_delete:
            if address in self.database.email_addresses:
                del self.database.email_addresses[address]

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


class AccountCredentialsResult(QueryResultImpl[records.AccountCredentials]):
    def for_user_account_with_id(self, user_id: UUID) -> Self:
        def items() -> Generator[records.AccountCredentials, None, None]:
            valid_accountant = self.database.relationships.account_credentials_to_accountant.get_left_value(
                user_id
            )
            valid_company = self.database.relationships.account_credentials_to_company.get_left_value(
                user_id
            )
            valid_member = self.database.relationships.account_credentials_to_member.get_left_value(
                user_id
            )
            valid_credentials = {valid_accountant, valid_company, valid_member}
            for credentials in self.items():
                if credentials.id in valid_credentials:
                    yield credentials

        return self.from_iterable(items=items)

    def with_email_address(self, address: str) -> Self:
        def items() -> Iterable[records.AccountCredentials]:
            for credentials in self.items():
                if credentials.email_address.lower() == address.lower():
                    yield credentials

        return self.from_iterable(items=items)

    def joined_with_accountant(
        self,
    ) -> QueryResultImpl[
        Tuple[records.AccountCredentials, Optional[records.Accountant]]
    ]:
        def items() -> (
            Iterable[Tuple[records.AccountCredentials, Optional[records.Accountant]]]
        ):
            for credentials in self.items():
                accountant_id = self.database.relationships.account_credentials_to_accountant.get_right_value(
                    credentials.id
                )
                if accountant_id:
                    accountant = self.database.accountants[accountant_id]
                    yield credentials, accountant
                else:
                    yield credentials, None

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def joined_with_email_address_and_accountant(
        self,
    ) -> QueryResultImpl[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Accountant],
        ]
    ]:
        def items() -> Iterable[
            Tuple[
                records.AccountCredentials,
                records.EmailAddress,
                Optional[records.Accountant],
            ]
        ]:
            for credentials in self.items():
                email_address = self.database.email_addresses[credentials.email_address]
                accountant_id = self.database.relationships.account_credentials_to_accountant.get_right_value(
                    credentials.id
                )
                if accountant_id:
                    accountant = self.database.accountants[accountant_id]
                    yield credentials, email_address, accountant
                else:
                    yield credentials, email_address, None

        return QueryResultImpl(database=self.database, items=items)

    def joined_with_member(
        self,
    ) -> QueryResultImpl[Tuple[records.AccountCredentials, Optional[records.Member]]]:
        def items() -> (
            Iterable[Tuple[records.AccountCredentials, Optional[records.Member]]]
        ):
            for credentials in self.items():
                member_id = self.database.relationships.account_credentials_to_member.get_right_value(
                    credentials.id
                )
                if member_id:
                    member = self.database.members[member_id]
                    yield credentials, member
                else:
                    yield credentials, None

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def joined_with_email_address_and_member(
        self,
    ) -> QueryResultImpl[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Member],
        ]
    ]:
        def items() -> Iterable[
            Tuple[
                records.AccountCredentials,
                records.EmailAddress,
                Optional[records.Member],
            ]
        ]:
            for credentials in self.items():
                member_id = self.database.relationships.account_credentials_to_member.get_right_value(
                    credentials.id
                )
                email_address = self.database.email_addresses[credentials.email_address]
                if member_id:
                    member = self.database.members[member_id]
                    yield credentials, email_address, member
                else:
                    yield credentials, email_address, None

        return QueryResultImpl(database=self.database, items=items)

    def joined_with_company(
        self,
    ) -> QueryResultImpl[Tuple[records.AccountCredentials, Optional[records.Company]]]:
        def items() -> (
            Iterable[Tuple[records.AccountCredentials, Optional[records.Company]]]
        ):
            for credentials in self.items():
                company_id = self.database.relationships.account_credentials_to_company.get_right_value(
                    credentials.id
                )
                if company_id:
                    company = self.database.companies[company_id]
                    yield credentials, company
                else:
                    yield credentials, None

        return QueryResultImpl(
            database=self.database,
            items=items,
        )

    def joined_with_email_address_and_company(
        self,
    ) -> QueryResultImpl[
        Tuple[
            records.AccountCredentials,
            records.EmailAddress,
            Optional[records.Company],
        ]
    ]:
        def items() -> Iterable[
            Tuple[
                records.AccountCredentials,
                records.EmailAddress,
                Optional[records.Company],
            ]
        ]:
            for credentials in self.items():
                email = self.database.email_addresses[credentials.email_address]
                company_id = self.database.relationships.account_credentials_to_company.get_right_value(
                    credentials.id
                )
                if not company_id:
                    yield credentials, email, None
                else:
                    company = self.database.companies[company_id]
                    yield credentials, email, company

        return QueryResultImpl(
            items=items,
            database=self.database,
        )

    def update(self) -> AccountCredentialsUpdate:
        return AccountCredentialsUpdate(
            items=self.items,
            database=self.database,
        )


@dataclass
class AccountCredentialsUpdate:
    items: Callable[[], Iterable[records.AccountCredentials]]
    database: MockDatabase
    actions: List[Callable[[MockDatabase, records.AccountCredentials], None]] = field(
        default_factory=list
    )

    def perform(self) -> int:
        item_count = 0
        for item in self.items():
            item_count += 1
            self.perform_all_actions(item)
        return item_count

    def perform_all_actions(self, item) -> None:
        for action in self.actions:
            action(self.database, item)

    def change_email_address(self, new_email_address: str) -> Self:
        def _change_action(db: MockDatabase, item: records.AccountCredentials) -> None:
            assert not db.indices.account_credentials_by_email_address_lowercased.get(
                new_email_address.lower()
            )
            assert new_email_address in db.email_addresses
            db.indices.account_credentials_by_email_address_lowercased.remove(
                item.email_address.lower(), item.id
            )
            item.email_address = new_email_address
            db.indices.account_credentials_by_email_address_lowercased.add(
                new_email_address.lower(), item.id
            )

        return replace(self, actions=self.actions + [_change_action])

    def change_password_hash(self, new_password_hash: str) -> Self:
        def _change_action(db: MockDatabase, item: records.AccountCredentials) -> None:
            item.password_hash = new_password_hash

        return replace(self, actions=self.actions + [_change_action])


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
        self.account_credentials: Dict[UUID, records.AccountCredentials] = dict()
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
        self.coordination_transfer_requests: Dict[
            UUID, records.CoordinationTransferRequest
        ] = dict()
        self.private_consumptions: Dict[UUID, records.PrivateConsumption] = dict()
        self.productive_consumptions: Dict[UUID, records.ProductiveConsumption] = dict()
        self.company_work_invites: List[CompanyWorkInvite] = list()
        self.email_addresses: Dict[str, records.EmailAddress] = dict()
        self.drafts: Dict[UUID, PlanDraft] = dict()
        self.reset_password_requests: List[records.PasswordResetRequest] = list()
        self.indices = Indices()
        self.relationships = Relationships()

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

    def create_private_consumption(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.PrivateConsumption:
        consumption = records.PrivateConsumption(
            id=uuid4(),
            plan_id=plan,
            transaction_id=transaction,
            amount=amount,
        )
        self.private_consumptions[consumption.id] = consumption
        self.indices.private_consumption_by_transaction.add(transaction, consumption.id)
        self.indices.private_consumption_by_plan.add(plan, consumption.id)
        return consumption

    def get_private_consumptions(self) -> PrivateConsumptionResult:
        return PrivateConsumptionResult(
            database=self,
            items=self.private_consumptions.values,
        )

    def create_productive_consumption(
        self, transaction: UUID, amount: int, plan: UUID
    ) -> records.ProductiveConsumption:
        consumption = records.ProductiveConsumption(
            id=uuid4(),
            amount=amount,
            plan_id=plan,
            transaction_id=transaction,
        )
        self.productive_consumptions[consumption.id] = consumption
        self.indices.productive_consumption_by_transaction.add(
            transaction, consumption.id
        )
        self.indices.productive_consumption_by_plan.add(plan, consumption.id)
        return consumption

    def get_productive_consumptions(self) -> ProductiveConsumptionResult:
        return ProductiveConsumptionResult(
            database=self, items=self.productive_consumptions.values
        )

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

    def get_coordination_tenures(self) -> CoordinationTenureResult:
        return CoordinationTenureResult(
            items=lambda: self.coordination_tenures.values(),
            database=self,
        )

    def create_coordination_transfer_request(
        self,
        requesting_coordination_tenure: UUID,
        candidate: UUID,
        request_date: datetime,
    ) -> records.CoordinationTransferRequest:
        request_id = uuid4()
        request = records.CoordinationTransferRequest(
            id=request_id,
            requesting_coordination_tenure=requesting_coordination_tenure,
            candidate=candidate,
            request_date=request_date,
        )
        self.coordination_transfer_requests[request_id] = request
        return request

    def get_coordination_transfer_requests(self) -> CoordinationTransferRequestResult:
        return CoordinationTransferRequestResult(
            items=lambda: self.coordination_transfer_requests.values(),
            database=self,
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

    def create_accountant(
        self, account_credentials: UUID, name: str
    ) -> records.Accountant:
        assert account_credentials in self.account_credentials
        id = uuid4()
        record = Accountant(
            name=name,
            id=id,
        )
        self.accountants[id] = record
        self.relationships.account_credentials_to_accountant.relate(
            account_credentials, id
        )
        return record

    def get_accountants(self) -> AccountantResult:
        return AccountantResult(
            items=lambda: self.accountants.values(),
            database=self,
        )

    def create_member(
        self,
        *,
        account_credentials: UUID,
        name: str,
        account: Account,
        registered_on: datetime,
    ) -> Member:
        assert account_credentials in self.account_credentials
        self.member_accounts.add(account)
        id = uuid4()
        member = Member(
            id=id,
            name=name,
            account=account.id,
            registered_on=registered_on,
        )
        self.members[id] = member
        self.indices.member_by_account.add(member.account, member.id)
        self.relationships.account_credentials_to_member.relate(account_credentials, id)
        return member

    def get_members(self) -> MemberResult:
        return MemberResult(
            items=lambda: self.members.values(),
            database=self,
        )

    def create_company(
        self,
        account_credentials: UUID,
        name: str,
        means_account: Account,
        labour_account: Account,
        resource_account: Account,
        products_account: Account,
        registered_on: datetime,
    ) -> Company:
        assert account_credentials in self.account_credentials
        self.p_accounts.add(means_account)
        self.r_accounts.add(resource_account)
        self.l_accounts.add(labour_account)
        self.prd_accounts.add(products_account)
        new_company = Company(
            id=uuid4(),
            name=name,
            means_account=means_account.id,
            raw_material_account=resource_account.id,
            work_account=labour_account.id,
            product_account=products_account.id,
            registered_on=registered_on,
        )
        self.companies[new_company.id] = new_company
        self.indices.company_by_account.add(means_account.id, new_company.id)
        self.indices.company_by_account.add(labour_account.id, new_company.id)
        self.indices.company_by_account.add(resource_account.id, new_company.id)
        self.indices.company_by_account.add(products_account.id, new_company.id)
        self.relationships.account_credentials_to_company.relate(
            account_credentials, new_company.id
        )
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

    def create_account_credentials(
        self, email_address: str, password_hash: str
    ) -> records.AccountCredentials:
        assert not self.indices.account_credentials_by_email_address_lowercased.get(
            email_address.lower()
        )
        id_ = uuid4()
        record = records.AccountCredentials(
            email_address=email_address,
            id=id_,
            password_hash=password_hash,
        )
        self.account_credentials[id_] = record
        self.indices.account_credentials_by_email_address_lowercased.add(
            email_address.lower(), id_
        )
        return record

    def get_account_credentials(self) -> AccountCredentialsResult:
        return AccountCredentialsResult(
            database=self,
            items=self.account_credentials.values,
        )

    def get_password_reset_requests(self) -> PasswordResetRequestResult:
        return PasswordResetRequestResult(
            items=lambda: self.reset_password_requests,
            database=self,
        )

    def create_password_reset_request(
        self, email_address: str, reset_token: str, created_at: datetime
    ) -> records.PasswordResetRequest:
        record = records.PasswordResetRequest(
            id=uuid4(),
            email_address=email_address,
            reset_token=reset_token,
            created_at=created_at,
        )
        self.reset_password_requests.append(record)
        return record


class Index(Generic[Key, Value]):
    def __init__(self) -> None:
        self._index: Dict[Key, Set[Value]] = defaultdict(set)

    def get(self, key: Key) -> Set[Value]:
        return self._index[key]

    def add(self, key: Key, value: Value) -> None:
        self._index[key].add(value)

    def remove(self, key: Key, value: Value) -> None:
        self._index[key].remove(value)


class OneToOne(Generic[S_Hash, T_Hash]):
    def __init__(self) -> None:
        self._forwards: Dict[S_Hash, T_Hash] = dict()
        self._backwards: Dict[T_Hash, S_Hash] = dict()

    def relate(self, s: S_Hash, t: T_Hash) -> None:
        assert s not in self._forwards
        assert t not in self._backwards
        self._forwards[s] = t
        self._backwards[t] = s

    def get_right_value(self, s: S_Hash) -> Optional[T_Hash]:
        return self._forwards.get(s)

    def get_left_value(self, t: T_Hash) -> Optional[S_Hash]:
        return self._backwards.get(t)

    def dissociate(self, s: S_Hash, t: T_Hash) -> None:
        assert self._forwards.get(s) == t
        assert self._backwards.get(t) == s
        del self._forwards[s]
        del self._backwards[t]


class OneToMany(Generic[One, Many]):
    def __init__(self) -> None:
        self._forwards: Dict[One, Set[Many]] = defaultdict(set)
        self._backwards: Dict[Many, Optional[One]] = defaultdict(lambda: None)

    def relate(self, one: One, many: Many) -> None:
        self._forwards[one].add(many)
        self._backwards[many] = one

    def get_many(self, one: One) -> Set[Many]:
        return self._forwards[one]

    def get_one(self, many: Many) -> Optional[One]:
        return self._backwards[many]

    def dissociate(self, one: One, many: Many) -> None:
        assert self._backwards[many] == one
        self._forwards[one].remove(many)
        del self._backwards[many]


class ManyToMany(Generic[S_Hash, T_Hash]):
    def __init__(self) -> None:
        self._forwards: Dict[S_Hash, Set[T_Hash]] = defaultdict(set)
        self._backwards: Dict[T_Hash, Set[S_Hash]] = defaultdict(set)

    def relate(self, s: S_Hash, t: T_Hash) -> None:
        self._forwards[s].add(t)
        self._backwards[t].add(s)

    def get_right_values(self, s: S_Hash) -> Set[T_Hash]:
        return self._forwards[s]

    def get_left_values(self, t: T_Hash) -> Set[S_Hash]:
        return self._backwards[t]

    def dissociate(self, s: S_Hash, t: T_Hash) -> None:
        self._forwards[s].remove(t)
        self._backwards[t].remove(s)


@dataclass
class Relationships:
    company_to_workers: ManyToMany[UUID, UUID] = field(default_factory=ManyToMany)
    account_credentials_to_member: OneToOne[UUID, UUID] = field(
        default_factory=OneToOne
    )
    account_credentials_to_company: OneToOne[UUID, UUID] = field(
        default_factory=OneToOne
    )
    account_credentials_to_accountant: OneToOne[UUID, UUID] = field(
        default_factory=OneToOne
    )
    cooperation_to_plan: OneToMany[UUID, UUID] = field(default_factory=OneToMany)


@dataclass
class Indices:
    member_by_account: Index[UUID, UUID] = field(default_factory=Index)
    company_by_account: Index[UUID, UUID] = field(default_factory=Index)
    private_consumption_by_transaction: Index[UUID, UUID] = field(default_factory=Index)
    private_consumption_by_plan: Index[UUID, UUID] = field(default_factory=Index)
    productive_consumption_by_transaction: Index[UUID, UUID] = field(
        default_factory=Index
    )
    productive_consumption_by_plan: Index[UUID, UUID] = field(default_factory=Index)
    coordination_tenure_by_cooperation: Index[UUID, UUID] = field(default_factory=Index)
    account_credentials_by_email_address_lowercased: Index[str, UUID] = field(
        default_factory=Index
    )
