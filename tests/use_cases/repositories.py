from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
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
    Union,
)
from uuid import UUID, uuid4

from typing_extensions import Self

import arbeitszeit.repositories as interfaces
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
    PayoutFactor,
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

    def where_payout_counts_are_less_then_active_days(
        self, timestamp: datetime
    ) -> PlanResult:
        def plan_filter(plan: Plan) -> bool:
            if plan.activation_date is None:
                return False
            active_days = min(
                (timestamp - plan.activation_date).days,
                plan.timeframe,
            )
            payout_count = len(
                self.entities.labour_certificates_payouts_by_plan[plan.id]
            )
            return payout_count < active_days

        return self._filtered_by(plan_filter)

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
        return self._filtered_by(lambda model: model.confirmed_on is not None)

    def update(self) -> MemberUpdate:
        return MemberUpdate(
            members=self.items,
            update_functions=list(),
        )

    def _filtered_by(self, key: Callable[[Member], bool]) -> MemberResult:
        return type(self)(
            items=lambda: filter(key, self.items()),
            entities=self.entities,
        )


@dataclass
class MemberUpdate:
    members: Callable[[], Iterable[entities.Member]]
    update_functions: List[Callable[[entities.Member], None]]

    def set_confirmation_timestamp(self, timestamp: datetime) -> MemberUpdate:
        def update(member: entities.Member) -> None:
            member.confirmed_on = timestamp

        return replace(
            self,
            update_functions=self.update_functions + [update],
        )

    def perform(self) -> int:
        items_affected = 0
        for member in self.members():
            for update in self.update_functions:
                update(member)
            items_affected += 1
        return items_affected


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

    def _filtered_by(self, key: Callable[[Company], bool]) -> CompanyResult:
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
                == self.entities.social_accounting.account.id,
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

        return replace(
            self,  # type: ignore
            items=joined_items,
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


class AccountResult(QueryResultImpl[Account]):
    def with_id(self, *id_: UUID) -> AccountResult:
        return replace(
            self,
            items=lambda: filter(lambda account: account.id in id_, self.items()),
        )


class LabourCertificatesPayoutResult(
    QueryResultImpl[entities.LabourCertificatesPayout]
):
    def for_plan(self, plan: UUID) -> LabourCertificatesPayoutResult:
        return replace(
            self,
            items=lambda: filter(lambda payout: payout.plan_id == plan, self.items()),
        )


class PayoutFactorResult(QueryResultImpl[entities.PayoutFactor]):
    def ordered_by_calculation_date(
        self, *, descending: bool = False
    ) -> PayoutFactorResult:
        def sorted_factors() -> Iterable[entities.PayoutFactor]:
            return sorted(
                self.items(), key=lambda f: f.calculation_date, reverse=descending
            )

        return replace(
            self,
            items=sorted_factors,
        )


@singleton
class TransactionRepository(interfaces.TransactionRepository):
    def __init__(self, entities: EntityStorage) -> None:
        self.entities = entities

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
        self.entities.transactions[transaction.id] = transaction
        return transaction

    def get_transactions(self) -> TransactionResult:
        return TransactionResult(
            items=lambda: self.entities.transactions.values(),
            entities=self.entities,
        )


@singleton
class AccountRepository(interfaces.AccountRepository):
    def __init__(
        self, transaction_repository: TransactionRepository, entities: EntityStorage
    ):
        self.transaction_repository = transaction_repository
        self.entities = entities

    def __contains__(self, account: object) -> bool:
        if not isinstance(account, Account):
            return False
        return account in self.entities.accounts

    def create_account(self) -> Account:
        return self.entities.create_account()

    def get_accounts(self) -> AccountResult:
        return AccountResult(
            items=lambda: self.entities.accounts,
            entities=self.entities,
        )

    def get_account_balance(self, account: UUID) -> Decimal:
        transactions = self.transaction_repository.get_transactions()
        received_transactions = transactions.where_account_is_receiver(account)
        sent_transactions = transactions.where_account_is_sender(account)
        return decimal_sum(
            transaction.amount_received for transaction in received_transactions
        ) - decimal_sum(transaction.amount_sent for transaction in sent_transactions)


@singleton
class AccountOwnerRepository(interfaces.AccountOwnerRepository):
    def __init__(
        self,
        entities: EntityStorage,
        social_accounting: SocialAccounting,
    ):
        self.entities = entities
        self.social_accounting = social_accounting

    def get_account_owner(
        self, account: UUID
    ) -> Union[Member, Company, SocialAccounting]:
        if self.social_accounting.account.id == account:
            return self.social_accounting
        for member in self.entities.members.values():
            if account == member.account:
                return member
        for company in self.entities.companies.values():
            if account in company.accounts():
                return company
        # This exception is not meant to be caught. That's why we
        # raise a base exception
        raise Exception("Owner not found")


@singleton
class MemberRepository(interfaces.MemberRepository):
    def __init__(self, datetime_service: DatetimeService, entities: EntityStorage):
        self.datetime_service = datetime_service
        self.entities = entities

    def create_member(
        self,
        *,
        email: str,
        name: str,
        password: str,
        account: Account,
        registered_on: datetime,
    ) -> Member:
        id = uuid4()
        member = Member(
            id=id,
            name=name,
            email=email,
            account=account.id,
            registered_on=registered_on,
            confirmed_on=None,
        )
        self.entities.members[id] = member
        self.entities.member_passwords[id] = password
        return member

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        if member := self._get_member_by_email(email):
            if self.entities.member_passwords[member.id] == password:
                return member.id
        return None

    def get_members(self) -> MemberResult:
        return MemberResult(
            items=lambda: self.entities.members.values(),
            entities=self.entities,
        )

    def _get_member_by_email(self, email: str) -> Optional[Member]:
        for member in self.entities.members.values():
            if member.email == email:
                return member
        return None


@singleton
class CompanyRepository(interfaces.CompanyRepository):
    def __init__(self, entities: EntityStorage) -> None:
        self.entities = entities

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
        new_company = Company(
            id=uuid4(),
            email=email,
            name=name,
            means_account=means_account.id,
            raw_material_account=resource_account.id,
            work_account=labour_account.id,
            product_account=products_account.id,
            registered_on=registered_on,
            confirmed_on=None,
        )
        self.entities.companies[new_company.id] = new_company
        self.entities.company_passwords[new_company.id] = password
        return new_company

    def get_companies(self) -> CompanyResult:
        return CompanyResult(
            items=lambda: self.entities.companies.values(),
            entities=self.entities,
        )

    def validate_credentials(self, email_address: str, password: str) -> Optional[UUID]:
        for candidate in self.entities.companies.values():
            if candidate.email == email_address:
                if correct_password := self.entities.company_passwords.get(
                    candidate.id
                ):
                    if password == correct_password:
                        return candidate.id
        return None

    def confirm_company(self, company: UUID, confirmation_timestamp: datetime) -> None:
        model = self.entities.companies[company]
        model.confirmed_on = confirmation_timestamp

    def is_company_confirmed(self, company: UUID) -> bool:
        if (model := self.entities.companies.get(company)) is not None:
            if model.id == company and model.confirmed_on is not None:
                return True
        return False


@singleton
class PlanDraftRepository(interfaces.PlanDraftRepository):
    def __init__(self) -> None:
        self.drafts: List[PlanDraft] = []

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
        self.drafts.append(draft)
        return draft

    def update_draft(self, update: interfaces.PlanDraftRepository.UpdateDraft) -> None:
        draft = self.get_by_id(update.id)
        if draft is None:
            return
        if update.product_name is not None:
            draft.product_name = update.product_name
        if update.amount is not None:
            draft.amount_produced = update.amount
        if update.description is not None:
            draft.description = update.description
        if update.labour_cost is not None:
            draft.production_costs.labour_cost = update.labour_cost
        if update.means_cost is not None:
            draft.production_costs.means_cost = update.means_cost
        if update.resource_cost is not None:
            draft.production_costs.resource_cost = update.resource_cost
        if update.is_public_service is not None:
            draft.is_public_service = update.is_public_service
        if update.timeframe is not None:
            draft.timeframe = update.timeframe
        if update.unit_of_distribution is not None:
            draft.unit_of_distribution = update.unit_of_distribution
        return

    def get_by_id(self, id: UUID) -> Optional[PlanDraft]:
        for draft in self.drafts:
            if draft.id == id:
                return draft
        return None

    def __len__(self) -> int:
        return len(self.drafts)

    def delete_draft(self, id: UUID) -> None:
        self.drafts = [draft for draft in self.drafts if draft.id != id]

    def all_drafts_of_company(self, id: UUID) -> Iterable[PlanDraft]:
        result = []
        for draft in self.drafts:
            if draft.planner == id:
                result.append(draft)
        return result


@singleton
class WorkerInviteRepository(interfaces.WorkerInviteRepository):
    def __init__(
        self, company_repository: CompanyRepository, member_repository: MemberRepository
    ) -> None:
        self.invites: Dict[UUID, Tuple[UUID, UUID]] = dict()
        self.company_repository = company_repository
        self.member_repository = member_repository

    def is_worker_invited_to_company(self, company: UUID, worker: UUID) -> bool:
        return (company, worker) in self.invites.values()

    def create_company_worker_invite(
        self,
        company: UUID,
        worker: UUID,
    ) -> UUID:
        invite_id = uuid4()
        self.invites[invite_id] = (company, worker)
        return invite_id

    def get_companies_worker_is_invited_to(self, member: UUID) -> Iterable[UUID]:
        for company, invited_worker in self.invites.values():
            if invited_worker == member:
                yield company

    def get_invites_for_worker(self, member: UUID) -> Iterable[CompanyWorkInvite]:
        for invite_id in self.invites:
            if self.invites[invite_id][1] == member:
                invite = self.get_by_id(invite_id)
                if invite is None:
                    continue
                yield invite

    def get_by_id(self, id: UUID) -> Optional[CompanyWorkInvite]:
        try:
            company_id, worker_id = self.invites[id]
        except KeyError:
            return None
        company = self.company_repository.get_companies().with_id(company_id).first()
        if company is None:
            return None
        member = self.member_repository.get_members().with_id(worker_id).first()
        if member is None:
            return None
        return CompanyWorkInvite(
            id=id,
            company=company,
            member=member,
        )

    def delete_invite(self, id: UUID) -> None:
        del self.invites[id]


@singleton
class AccountantRepositoryTestImpl:
    @dataclass
    class _AccountantRecord:
        email: str
        name: str
        password: str
        id: UUID

    def __init__(self, entities: EntityStorage) -> None:
        self.accountants: Dict[
            UUID, AccountantRepositoryTestImpl._AccountantRecord
        ] = dict()
        self.entities = entities

    def create_accountant(self, email: str, name: str, password: str) -> UUID:
        id = uuid4()
        record = self._AccountantRecord(
            email=email,
            name=name,
            password=password,
            id=id,
        )
        self.accountants[id] = record
        return id

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        for uuid, record in self.accountants.items():
            if record.email == email:
                if record.password == password:
                    return uuid
                else:
                    return None
        return None

    def get_accountants(self) -> AccountantResult:
        return AccountantResult(
            items=lambda: (
                Accountant(email_address=record.email, name=record.name, id=record.id)
                for record in self.accountants.values()
            ),
            entities=self.entities,
        )


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
        self.member_passwords: Dict[UUID, str] = {}
        self.company_workers: Dict[UUID, Set[UUID]] = defaultdict(lambda: set())
        self.companies: Dict[UUID, Company] = {}
        self.company_passwords: Dict[UUID, str] = {}
        self.plans: Dict[UUID, Plan] = {}
        self.transactions: Dict[UUID, Transaction] = dict()
        self.accounts: List[Account] = []
        self.social_accounting = SocialAccounting(
            id=uuid4(),
            account=self.create_account(),
        )
        self.cooperations: Dict[UUID, Cooperation] = dict()
        self.labour_certificates_payouts_by_transaction: Dict[
            UUID, entities.LabourCertificatesPayout
        ] = dict()
        self.labour_certificates_payouts_by_plan: Dict[
            UUID, List[entities.LabourCertificatesPayout]
        ] = defaultdict(list)
        self.payout_factors: List[entities.PayoutFactor] = list()
        self.consumer_purchases: Dict[UUID, entities.ConsumerPurchase] = dict()
        self.consumer_purchase_by_transaction: Dict[
            UUID, entities.ConsumerPurchase
        ] = dict()
        self.company_purchases: Dict[UUID, entities.CompanyPurchase] = dict()
        self.company_purchase_by_transaction: Dict[
            UUID, entities.CompanyPurchase
        ] = dict()

    def create_labour_certificates_payout(
        self, transaction: UUID, plan: UUID
    ) -> entities.LabourCertificatesPayout:
        assert transaction not in self.labour_certificates_payouts_by_transaction
        payout = entities.LabourCertificatesPayout(
            transaction_id=transaction, plan_id=plan
        )
        self.labour_certificates_payouts_by_transaction[transaction] = payout
        self.labour_certificates_payouts_by_plan[plan].append(payout)
        return payout

    def get_labour_certificates_payouts(self) -> LabourCertificatesPayoutResult:
        return LabourCertificatesPayoutResult(
            items=lambda: self.labour_certificates_payouts_by_transaction.values(),
            entities=self,
        )

    def get_payout_factors(self) -> PayoutFactorResult:
        return PayoutFactorResult(
            items=lambda: self.payout_factors,
            entities=self,
        )

    def create_payout_factor(
        self, timestamp: datetime, payout_factor: Decimal
    ) -> PayoutFactor:
        factor = entities.PayoutFactor(calculation_date=timestamp, value=payout_factor)
        self.payout_factors.append(factor)
        return factor

    def create_account(self) -> Account:
        account = Account(
            id=uuid4(),
        )
        self.accounts.append(account)
        return account

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
