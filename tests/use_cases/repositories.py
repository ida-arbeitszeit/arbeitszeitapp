from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, replace
from datetime import datetime
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

import arbeitszeit.repositories as interfaces
from arbeitszeit import entities
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
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
        def get_company_name(planner_id: UUID):
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
        def items_generator():
            plan_entity = self.entities.plans.get(plan)
            if not plan_entity:
                return
            if plan_entity.cooperation is None:
                yield from filter(lambda p: p.id == plan, self.items())
            else:
                yield from filter(
                    lambda p: p.cooperation == plan_entity.cooperation, self.items()
                )

        return type(self)(
            items=items_generator,
            entities=self.entities,
        )

    def that_are_active(self) -> PlanResult:
        return self._filtered_by(lambda plan: plan.is_active)

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
                if value.coordinator.id in company
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

    def update(self) -> PlanUpdate:
        return PlanUpdate(
            items=self.items,
            update_functions=[],
        )

    def _filtered_by(self, key: Callable[[Plan], bool]) -> PlanResult:
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

    def set_activation_status(self, *, is_active: bool) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.is_active = is_active

        return self._add_update(update)

    def set_expiration_status(self, *, is_expired: bool) -> PlanUpdate:
        def update(plan: Plan) -> None:
            plan.expired = is_expired

        return self._add_update(update)

    def perform(self) -> int:
        items_affected = 0
        for item in self.items():
            for update in self.update_functions:
                update(item)
            items_affected += 1
        return items_affected

    def _add_update(self, update: Callable[[Plan], None]) -> PlanUpdate:
        return replace(self, update_functions=self.update_functions + [update])


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


class ConsumerPurchaseResult(QueryResultImpl[entities.ConsumerPurchase]):
    def ordered_by_creation_date(
        self, *, ascending: bool = True
    ) -> ConsumerPurchaseResult:
        def purchase_sorting_key(purchase):
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
        def filtered_items():
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
        def joined_items() -> Iterator[
            Tuple[entities.ConsumerPurchase, Transaction, Plan]
        ]:
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
        def purchase_sorting_key(purchase):
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
        def filtered_items():
            company_record = self.entities.get_company_by_id(company)
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
        def joined_items() -> Iterator[
            Tuple[entities.CompanyPurchase, Transaction, Plan]
        ]:
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
        def joined_items() -> Iterator[
            Tuple[entities.CompanyPurchase, entities.Transaction]
        ]:
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

    def get_sales_balance_of_plan(self, plan: Plan) -> Decimal:
        balance = Decimal(0)
        planner = self.entities.get_company_by_id(plan.planner)
        assert planner
        for transaction in self.entities.transactions.values():
            if (transaction.receiving_account == planner.product_account) and (
                str(plan.id) in transaction.purpose
            ):
                balance += transaction.amount_received
        return balance


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

    def create_account(self, account_type: AccountTypes) -> Account:
        return self.entities.create_account(account_type)

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
        self, account: Account
    ) -> Union[Member, Company, SocialAccounting]:
        if account.account_type == AccountTypes.accounting:
            return self.social_accounting
        for member in self.entities.members.values():
            if account.id == member.account:
                return member
        for company in self.entities.companies.values():
            if account.id in company.accounts():
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
        self.entities.companies[email] = new_company
        self.entities.company_passwords[new_company.id] = password
        return new_company

    def get_companies(self) -> CompanyResult:
        return CompanyResult(
            items=lambda: self.entities.companies.values(),
            entities=self.entities,
        )

    def validate_credentials(self, email_address: str, password: str) -> Optional[UUID]:
        if company := self.entities.companies.get(email_address):
            if correct_password := self.entities.company_passwords.get(company.id):
                if password == correct_password:
                    return company.id
        return None

    def confirm_company(self, company: UUID, confirmation_timestamp: datetime) -> None:
        for model in self.entities.companies.values():
            if model.id == company:
                model.confirmed_on = confirmation_timestamp

    def is_company_confirmed(self, company: UUID) -> bool:
        for model in self.entities.companies.values():
            if model.id == company and model.confirmed_on is not None:
                return True
        return False


@singleton
class PlanRepository(interfaces.PlanRepository):
    def __init__(
        self,
        draft_repository: PlanDraftRepository,
        entities: EntityStorage,
    ) -> None:
        self.draft_repository = draft_repository
        self.entities = entities

    def get_plans(self) -> PlanResult:
        return PlanResult(
            items=lambda: self.entities.plans.values(),
            entities=self.entities,
        )

    def create_plan_from_draft(self, draft_id: UUID) -> Optional[UUID]:
        draft = self.draft_repository.get_by_id(draft_id)
        assert draft
        plan = self._create_plan(
            id=draft.id,
            planner=draft.planner,
            costs=draft.production_costs,
            product_name=draft.product_name,
            production_unit=draft.unit_of_distribution,
            amount=draft.amount_produced,
            description=draft.description,
            timeframe_in_days=draft.timeframe,
            is_public_service=draft.is_public_service,
            creation_timestamp=draft.creation_date,
        )
        return plan.id

    def __len__(self) -> int:
        return len(self.entities.plans)

    def hide_plan(self, plan_id: UUID) -> None:
        plan = self.entities.plans.get(plan_id)
        assert plan
        plan.hidden_by_user = True

    def _create_plan(
        self,
        id: UUID,
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
        plan = Plan(
            id=id,
            plan_creation_date=creation_timestamp,
            planner=planner.id,
            production_costs=costs,
            prd_name=product_name,
            prd_unit=production_unit,
            prd_amount=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
            is_active=False,
            activation_date=None,
            approval_date=None,
            expired=False,
            requested_cooperation=None,
            cooperation=None,
            is_available=True,
            hidden_by_user=False,
        )
        self.entities.plans[plan.id] = plan
        return plan

    def toggle_product_availability(self, plan: Plan) -> None:
        plan.is_available = True if (plan.is_available == False) else False


@singleton
class PlanDraftRepository(interfaces.PlanDraftRepository):
    def __init__(
        self,
        datetime_service: DatetimeService,
        company_repository: interfaces.CompanyRepository,
    ) -> None:
        self.drafts: List[PlanDraft] = []
        self.datetime_service = datetime_service
        self.company_repository = company_repository

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
        company = self.company_repository.get_companies().with_id(planner).first()
        assert company is not None
        draft = PlanDraft(
            id=uuid4(),
            creation_date=creation_timestamp,
            planner=company,
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
            if draft.planner.id == id:
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
class CooperationRepository(interfaces.CooperationRepository):
    def __init__(self, entities: EntityStorage) -> None:
        self.entities = entities

    def create_cooperation(
        self,
        creation_timestamp: datetime,
        name: str,
        definition: str,
        coordinator: Company,
    ) -> Cooperation:
        cooperation_id = uuid4()
        cooperation = Cooperation(
            id=cooperation_id,
            creation_date=creation_timestamp,
            name=name,
            definition=definition,
            coordinator=coordinator,
        )
        self.entities.cooperations[cooperation_id] = cooperation
        return cooperation

    def get_by_id(self, id: UUID) -> Optional[Cooperation]:
        return self.entities.cooperations.get(id)

    def get_by_name(self, name: str) -> Iterator[Cooperation]:
        for cooperation in self.entities.cooperations.values():
            if cooperation.name.lower() == name.lower():
                yield cooperation

    def get_cooperations_coordinated_by_company(
        self, company_id: UUID
    ) -> Iterator[Cooperation]:
        for cooperation in self.entities.cooperations.values():
            if cooperation.coordinator.id == company_id:
                yield cooperation

    def get_cooperation_name(self, coop_id: UUID) -> Optional[str]:
        coop = self.entities.cooperations.get(coop_id)
        if coop is None:
            return None
        return coop.name

    def get_all_cooperations(self) -> Iterator[Cooperation]:
        return (cooperation for cooperation in self.entities.cooperations.values())

    def count_cooperations(self) -> int:
        return len(self.entities.cooperations)

    def __len__(self) -> int:
        return len(self.entities.cooperations)


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

    def has_accountant_with_email(self, email: str) -> bool:
        return any(record.email == email for record in self.accountants.values())

    def get_by_id(self, id: UUID) -> Optional[Accountant]:
        record = self.accountants.get(id)
        if record is None:
            return None
        return Accountant(email_address=record.email, name=record.name, id=id)

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        for uuid, record in self.accountants.items():
            if record.email == email:
                if record.password == password:
                    return uuid
                else:
                    return None
        return None

    def get_all_accountants(self) -> QueryResultImpl[Accountant]:
        return QueryResultImpl(
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
        self.companies: Dict[str, Company] = {}
        self.company_passwords: Dict[UUID, str] = {}
        self.plans: Dict[UUID, Plan] = {}
        self.transactions: Dict[UUID, Transaction] = dict()
        self.accounts: List[Account] = []
        self.social_accounting = SocialAccounting(
            id=uuid4(),
            account=self.create_account(account_type=AccountTypes.accounting),
        )
        self.cooperations: Dict[UUID, Cooperation] = dict()
        self.labour_certificates_payouts: Dict[
            UUID, entities.LabourCertificatesPayout
        ] = dict()
        self.payout_factors: List[entities.PayoutFactor] = list()
        self.consumer_purchases: Dict[UUID, entities.ConsumerPurchase] = dict()
        self.company_purchases: Dict[UUID, entities.CompanyPurchase] = dict()

    def create_labour_certificates_payout(
        self, transaction: UUID, plan: UUID
    ) -> entities.LabourCertificatesPayout:
        assert transaction not in self.labour_certificates_payouts
        payout = entities.LabourCertificatesPayout(
            transaction_id=transaction, plan_id=plan
        )
        self.labour_certificates_payouts[transaction] = payout
        return payout

    def get_labour_certificates_payouts(self) -> LabourCertificatesPayoutResult:
        return LabourCertificatesPayoutResult(
            items=lambda: self.labour_certificates_payouts.values(),
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

    def create_account(self, account_type: AccountTypes) -> Account:
        account = Account(
            id=uuid4(),
            account_type=account_type,
        )
        self.accounts.append(account)
        return account

    def get_company_by_id(self, company: UUID) -> Optional[Company]:
        for model in self.companies.values():
            if model.id == company:
                return model
        return None

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
        return purchase

    def get_company_purchases(self) -> CompanyPurchaseResult:
        return CompanyPurchaseResult(entities=self, items=self.company_purchases.values)
