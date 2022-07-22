from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from itertools import islice
from statistics import StatisticsError, mean
from typing import Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union
from uuid import UUID, uuid4

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
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
    Plan,
    PlanDraft,
    ProductionCosts,
    Purchase,
    PurposesOfPurchases,
    SocialAccounting,
    Transaction,
)


@singleton
class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def create_purchase_by_company(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        purchase = Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            is_buyer_a_member=False,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
        self.purchases.append(purchase)
        return purchase

    def create_purchase_by_member(
        self,
        purchase_date: datetime,
        plan: UUID,
        buyer: UUID,
        price_per_unit: Decimal,
        amount: int,
    ) -> Purchase:
        purchase = Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            is_buyer_a_member=True,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=PurposesOfPurchases.consumption,
        )
        self.purchases.append(purchase)
        return purchase

    def get_purchases_descending_by_date(self, user: Union[Member, Company]):
        # order purchases by purchase_date
        self.purchases = sorted(
            self.purchases, key=lambda x: x.purchase_date, reverse=True
        )

        for purchase in self.purchases:
            if purchase.buyer is user.id:
                yield purchase

    def get_purchases_of_company(self, company: UUID) -> Iterator[Purchase]:
        for purchase in self.purchases:
            if purchase.buyer is company:
                yield purchase


@singleton
class TransactionRepository(interfaces.TransactionRepository):
    @inject
    def __init__(self) -> None:
        self.transactions: List[Transaction] = []

    def create_transaction(
        self,
        date: datetime,
        sending_account: Account,
        receiving_account: Account,
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
        self.transactions.append(transaction)
        return transaction

    def all_transactions_sent_by_account(self, account: Account) -> List[Transaction]:
        all_sent = []
        for transaction in self.transactions:
            if transaction.sending_account == account:
                all_sent.append(transaction)
        return all_sent

    def all_transactions_received_by_account(
        self, account: Account
    ) -> List[Transaction]:
        all_received = []
        for transaction in self.transactions:
            if transaction.receiving_account == account:
                all_received.append(transaction)
        return all_received

    def get_sales_balance_of_plan(self, plan: Plan) -> Decimal:
        balance = Decimal(0)
        for transaction in self.transactions:
            if (transaction.receiving_account == plan.planner.product_account) and (
                str(plan.id) in transaction.purpose
            ):
                balance += transaction.amount_received
        return balance


@singleton
class CompanyWorkerRepository(interfaces.CompanyWorkerRepository):
    @inject
    def __init__(
        self, company_repository: CompanyRepository, member_repository: MemberRepository
    ) -> None:
        self.company_repository = company_repository
        self.member_repository = member_repository
        self.company_workers: Dict[UUID, Set[UUID]] = defaultdict(lambda: set())

    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        self.company_workers[company.id].add(worker.id)

    def get_company_workers(self, company: Company) -> Iterable[Member]:
        for member_id in self.company_workers[company.id]:
            member = self.member_repository.get_by_id(member_id)
            if member is not None:
                yield member

    def get_member_workplaces(self, member: UUID) -> Iterable[Company]:
        for company_id, workers in self.company_workers.items():
            if member not in workers:
                continue
            company = self.company_repository.get_by_id(company_id)
            if company is not None:
                yield company


@singleton
class AccountRepository(interfaces.AccountRepository):
    @inject
    def __init__(self, transaction_repository: TransactionRepository):
        self.accounts: List[Account] = []
        self.transaction_repository = transaction_repository

    def __contains__(self, account: object) -> bool:
        if not isinstance(account, Account):
            return False
        return account in self.accounts

    def create_account(self, account_type: AccountTypes) -> Account:
        account = Account(
            id=uuid4(),
            account_type=account_type,
        )
        self.accounts.append(account)
        return account

    def get_account_balance(self, account: Account) -> Decimal:
        received_transactions = (
            self.transaction_repository.all_transactions_received_by_account(account)
        )
        sent_transactions = (
            self.transaction_repository.all_transactions_sent_by_account(account)
        )
        self._remove_intersection(received_transactions, sent_transactions)
        return decimal_sum(
            transaction.amount_received for transaction in received_transactions
        ) - decimal_sum(transaction.amount_sent for transaction in sent_transactions)

    @classmethod
    def _remove_intersection(
        cls,
        transactions_received: List[Transaction],
        transactions_sent: List[Transaction],
    ) -> None:
        intersection = {transaction.id for transaction in transactions_received} & {
            transaction.id for transaction in transactions_sent
        }
        transactions_received[:] = [
            transaction
            for transaction in transactions_received
            if transaction.id not in intersection
        ]
        transactions_sent[:] = [
            transaction
            for transaction in transactions_sent
            if transaction.id not in intersection
        ]


@singleton
class AccountOwnerRepository(interfaces.AccountOwnerRepository):
    @inject
    def __init__(
        self,
        company_repository: CompanyRepository,
        member_repository: MemberRepository,
        social_accounting: SocialAccounting,
    ):
        self.member_repository = member_repository
        self.company_repository = company_repository
        self.social_accounting = social_accounting

    def get_account_owner(
        self, account: Account
    ) -> Union[Member, Company, SocialAccounting]:
        if account.account_type == AccountTypes.accounting:
            return self.social_accounting
        for member in self.member_repository.members.values():
            if account == member.account:
                return member
        for company in self.company_repository.companies.values():
            if account in company.accounts():
                return company
        # This exception is not meant to be caught. That's why we
        # raise a base exception
        raise Exception("Owner not found")


@singleton
class MemberRepository(interfaces.MemberRepository):
    @inject
    def __init__(self, datetime_service: DatetimeService):
        self.members: Dict[UUID, Member] = {}
        self.passwords: Dict[UUID, str] = {}
        self.datetime_service = datetime_service

    def create_member(
        self,
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
            account=account,
            registered_on=registered_on,
            confirmed_on=None,
        )
        self.members[id] = member
        self.passwords[id] = password
        return member

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        if member := self._get_member_by_email(email):
            if self.passwords[member.id] == password:
                return member.id
        return None

    def has_member_with_email(self, email: str) -> bool:
        return bool(self._get_member_by_email(email))

    def count_registered_members(self) -> int:
        return len(self.members)

    def confirm_member(self, member: UUID, confirmed_on: datetime) -> None:
        entity = self.members[member]
        entity.confirmed_on = confirmed_on

    def is_member_confirmed(self, member: UUID) -> bool:
        entity = self.members.get(member)
        if entity:
            return entity.confirmed_on is not None
        else:
            return False

    def get_by_id(self, id: UUID) -> Optional[Member]:
        return self.members.get(id)

    def get_by_email(self, email: str) -> Optional[Member]:
        return self._get_member_by_email(email)

    def get_all_members(self) -> Iterator[Member]:
        yield from self.members.values()

    def _get_member_by_email(self, email: str) -> Optional[Member]:
        for member in self.members.values():
            if member.email == email:
                return member
        return None


@singleton
class CompanyRepository(interfaces.CompanyRepository):
    @inject
    def __init__(self) -> None:
        self.companies: Dict[str, Company] = {}
        self.passwords: Dict[UUID, str] = {}

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
            means_account=means_account,
            raw_material_account=resource_account,
            work_account=labour_account,
            product_account=products_account,
            registered_on=registered_on,
            confirmed_on=None,
        )
        self.companies[email] = new_company
        self.passwords[new_company.id] = password
        return new_company

    def has_company_with_email(self, email: str) -> bool:
        return email in self.companies

    def get_by_id(self, id: UUID) -> Optional[Company]:
        for company in self.companies.values():
            if company.id == id:
                return company
        return None

    def get_by_email(self, email: str) -> Optional[Company]:
        for company in self.companies.values():
            if company.email == email:
                return company
        return None

    def count_registered_companies(self) -> int:
        return len(self.companies)

    def query_companies_by_name(self, query: str) -> Iterator[Company]:
        for company in self.companies.values():
            if query.lower() in company.name.lower():
                yield company

    def query_companies_by_email(self, query: str) -> Iterator[Company]:
        for email, company in self.companies.items():
            if query.lower() in email.lower():
                yield company

    def get_all_companies(self) -> Iterator[Company]:
        yield from self.companies.values()

    def validate_credentials(self, email_address: str, password: str) -> Optional[UUID]:
        if company := self.companies.get(email_address):
            if correct_password := self.passwords.get(company.id):
                if password == correct_password:
                    return company.id
        return None


@singleton
class PlanRepository(interfaces.PlanRepository):
    @inject
    def __init__(
        self,
        company_repository: CompanyRepository,
    ) -> None:
        self.plans: Dict[UUID, Plan] = {}
        self.company_repository = company_repository

    def get_all_plans_without_completed_review(self) -> Iterable[UUID]:
        for plan in self.plans.values():
            if plan.approval_date is None:
                yield plan.id

    def create_plan(self, plan: interfaces.PlanRepository.CreatePlan) -> UUID:
        planning_company = self.company_repository.get_by_id(plan.planner)
        assert planning_company
        model = self._create_plan(
            id=uuid4(),
            planner=planning_company,
            costs=plan.costs,
            product_name=plan.product_name,
            production_unit=plan.production_unit,
            amount=plan.amount,
            description=plan.description,
            timeframe_in_days=plan.timeframe_in_days,
            is_public_service=plan.is_public_service,
            creation_timestamp=plan.creation_timestamp,
        )
        return model.id

    def get_plan_by_id(self, id: UUID) -> Optional[Plan]:
        return self.plans.get(id)

    def set_plan_approval_date(
        self, draft: PlanDraft, approval_timestamp: datetime
    ) -> Plan:
        planner = self.company_repository.get_by_id(draft.planner.id)
        assert planner
        plan = self._create_plan(
            id=draft.id,
            planner=planner,
            costs=draft.production_costs,
            product_name=draft.product_name,
            production_unit=draft.unit_of_distribution,
            amount=draft.amount_produced,
            description=draft.description,
            timeframe_in_days=draft.timeframe,
            is_public_service=draft.is_public_service,
            creation_timestamp=draft.creation_date,
        )
        plan.approval_date = approval_timestamp
        plan.approval_reason = "approved"
        return plan

    def __len__(self) -> int:
        return len(self.plans)

    def activate_plan(self, plan: Plan, activation_date: datetime) -> None:
        plan.is_active = True
        plan.activation_date = activation_date

    def set_plan_as_expired(self, plan: Plan) -> None:
        plan.expired = True
        plan.is_active = False

    def set_expiration_date(self, plan: Plan, expiration_date: datetime) -> None:
        plan.expiration_date = expiration_date

    def set_active_days(self, plan: Plan, full_active_days: int) -> None:
        plan.active_days = full_active_days

    def increase_payout_count_by_one(self, plan: Plan) -> None:
        plan.payout_count += 1

    def get_active_plans(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active:
                yield plan

    def get_three_latest_active_plans_ordered_by_activation_date(
        self,
    ) -> Iterator[Plan]:
        active_plans = [plan for plan in self.plans.values() if plan.is_active]
        active_plans_sorted = sorted(
            active_plans,
            key=lambda x: x.activation_date if x.activation_date is not None else 0,
            reverse=True,
        )
        for plan in islice(active_plans_sorted, 3):
            yield plan

    def count_active_plans(self) -> int:
        return len([plan for plan in self.plans.values() if plan.is_active])

    def count_active_public_plans(self) -> int:
        return len(
            [
                plan
                for plan in self.plans.values()
                if (plan.is_active and plan.is_public_service)
            ]
        )

    def avg_timeframe_of_active_plans(self) -> Decimal:
        try:
            avg_timeframe = mean(
                (plan.timeframe for plan in self.plans.values() if plan.is_active)
            )
        except StatisticsError:
            avg_timeframe = 0
        return Decimal(avg_timeframe)

    def sum_of_active_planned_work(self) -> Decimal:
        return decimal_sum(
            (
                plan.production_costs.labour_cost
                for plan in self.plans.values()
                if plan.is_active
            )
        )

    def sum_of_active_planned_resources(self) -> Decimal:
        return decimal_sum(
            (
                plan.production_costs.resource_cost
                for plan in self.plans.values()
                if plan.is_active
            )
        )

    def sum_of_active_planned_means(self) -> Decimal:
        return decimal_sum(
            (
                plan.production_costs.means_cost
                for plan in self.plans.values()
                if plan.is_active
            )
        )

    def all_plans_approved_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_approved and not plan.expired:
                yield plan

    def all_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_approved and plan.is_active and not plan.expired:
                yield plan

    def all_productive_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                not plan.is_public_service
                and plan.is_active
                and plan.is_approved
                and not plan.expired
            ):
                yield plan

    def all_public_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                plan.is_public_service
                and plan.is_active
                and plan.is_approved
                and not plan.expired
            ):
                yield plan

    def hide_plan(self, plan_id: UUID) -> None:
        plan = self.plans.get(plan_id)
        assert plan
        plan.hidden_by_user = True

    def get_all_plans_for_company_descending(self, company_id: UUID) -> Iterator[Plan]:
        plans = self.plans.values()
        plans_ordered = sorted(plans, key=lambda x: x.plan_creation_date, reverse=True)
        for plan in plans_ordered:
            if str(plan.planner.id) == str(company_id):
                yield plan

    def get_all_active_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (str(plan.planner.id) == str(company_id)) and plan.is_active:
                yield plan

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
            planner=planner,
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
            approval_reason=None,
            expired=False,
            expiration_date=None,
            active_days=None,
            payout_count=0,
            requested_cooperation=None,
            cooperation=None,
            is_available=True,
            hidden_by_user=False,
        )
        self.plans[plan.id] = plan
        return plan

    def query_active_plans_by_product_name(self, query: str) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active and (query.lower() in plan.prd_name.lower()):
                yield plan

    def query_active_plans_by_plan_id(self, query: str) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active and (query in str(plan.id)):
                yield plan

    def toggle_product_availability(self, plan: Plan) -> None:
        plan.is_available = True if (plan.is_available == False) else False

    def get_plan_name_and_description(
        self, id: UUID
    ) -> interfaces.PlanRepository.NameAndDescription:
        plan = self.plans.get(id)
        assert plan
        name_and_description = interfaces.PlanRepository.NameAndDescription(
            name=plan.prd_name, description=plan.description
        )
        return name_and_description

    def get_planner_id(self, plan_id: UUID) -> Optional[UUID]:
        plan = self.plans.get(plan_id)
        if plan is None:
            return None
        return plan.planner.id


@singleton
class PlanDraftRepository(interfaces.PlanDraftRepository):
    @inject
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
        company = self.company_repository.get_by_id(planner)
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


class WorkerInviteRepository(interfaces.WorkerInviteRepository):
    @inject
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
        company = self.company_repository.get_by_id(company_id)
        if company is None:
            return None
        member = self.member_repository.get_by_id(worker_id)
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
    @inject
    def __init__(self) -> None:
        self.cooperations: Dict[UUID, Cooperation] = dict()

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
        self.cooperations[cooperation_id] = cooperation
        return cooperation

    def get_by_id(self, id: UUID) -> Optional[Cooperation]:
        return self.cooperations.get(id)

    def get_by_name(self, name: str) -> Iterator[Cooperation]:
        for cooperation in self.cooperations.values():
            if cooperation.name.lower() == name.lower():
                yield cooperation

    def get_cooperations_coordinated_by_company(
        self, company_id: UUID
    ) -> Iterator[Cooperation]:
        for cooperation in self.cooperations.values():
            if cooperation.coordinator.id == company_id:
                yield cooperation

    def get_cooperation_name(self, coop_id: UUID) -> Optional[str]:
        coop = self.cooperations.get(coop_id)
        if coop is None:
            return None
        return coop.name

    def get_all_cooperations(self) -> Iterator[Cooperation]:
        return (cooperation for cooperation in self.cooperations.values())

    def count_cooperations(self) -> int:
        return len(self.cooperations)

    def __len__(self) -> int:
        return len(self.cooperations)


@singleton
class PlanCooperationRepository(interfaces.PlanCooperationRepository):
    @inject
    def __init__(
        self,
        plan_repository: PlanRepository,
        cooperation_repository: CooperationRepository,
    ) -> None:
        self.plan_repository = plan_repository
        self.cooperation_repository = cooperation_repository

    def get_inbound_requests(self, coordinator_id: UUID) -> Iterator[Plan]:
        coops_of_company = list(
            self.cooperation_repository.get_cooperations_coordinated_by_company(
                coordinator_id
            )
        )
        for plan in self.plan_repository.plans.values():
            if plan.requested_cooperation in [coop.id for coop in coops_of_company]:
                yield plan

    def get_outbound_requests(self, requester_id: UUID) -> Iterator[Plan]:
        plans_of_company = self.plan_repository.get_all_plans_for_company_descending(
            requester_id
        )
        for plan in plans_of_company:
            if plan.requested_cooperation:
                yield plan

    def get_cooperating_plans(self, plan_id: UUID) -> List[Plan]:
        cooperating_plans = []
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan
        cooperation_id = plan.cooperation
        if cooperation_id:
            for p in self.plan_repository.plans.values():
                if p.cooperation == cooperation_id:
                    cooperating_plans.append(p)
            return cooperating_plans
        else:
            return [plan]

    def add_plan_to_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan
        plan.cooperation = cooperation_id

    def remove_plan_from_cooperation(self, plan_id: UUID) -> None:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan
        plan.cooperation = None

    def set_requested_cooperation(self, plan_id: UUID, cooperation_id: UUID) -> None:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan
        plan.requested_cooperation = cooperation_id

    def set_requested_cooperation_to_none(self, plan_id: UUID) -> None:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        assert plan
        plan.requested_cooperation = None

    def count_plans_in_cooperation(self, cooperation_id: UUID) -> int:
        count = 0
        for plan in self.plan_repository.plans.values():
            if plan.cooperation == cooperation_id:
                count += 1
        return count

    def get_plans_in_cooperation(self, cooperation_id: UUID) -> Iterable[Plan]:
        plans = self.plan_repository.plans.values()
        for plan in plans:
            if plan.cooperation == cooperation_id:
                yield plan


class AccountantRepositoryTestImpl:
    @dataclass
    class _AccountantRecord:
        email: str
        name: str
        password: str

    def __init__(self) -> None:
        self.accountants: Dict[
            UUID, AccountantRepositoryTestImpl._AccountantRecord
        ] = dict()

    def create_accountant(self, email: str, name: str, password: str) -> UUID:
        id = uuid4()
        record = self._AccountantRecord(
            email=email,
            name=name,
            password=password,
        )
        self.accountants[id] = record
        return id

    def has_accountant_with_email(self, email: str) -> bool:
        return any(record.email == email for record in self.accountants.values())

    def get_by_id(self, id: UUID) -> Optional[Accountant]:
        record = self.accountants.get(id)
        if record is None:
            return None
        return Accountant(email_address=record.email, name=record.name)

    def validate_credentials(self, email: str, password: str) -> Optional[UUID]:
        for uuid, record in self.accountants.items():
            if record.email == email:
                if record.password == password:
                    return uuid
                else:
                    return None
        return None


class FakeLanguageRepository:
    def __init__(self) -> None:
        self._language_codes: Set[str] = set()

    def add_language(self, language_code: str) -> None:
        self._language_codes.add(language_code)

    def get_available_language_codes(self) -> Iterable[str]:
        return self._language_codes
