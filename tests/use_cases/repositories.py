from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from statistics import StatisticsError, mean
from typing import Dict, Iterator, List, Optional, Set, Union
from uuid import UUID, uuid4

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    PlanDraft,
    ProductionCosts,
    ProductOffer,
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

    def create_purchase(
        self,
        purchase_date: datetime,
        plan: Plan,
        buyer: Union[Member, Company],
        price_per_unit: Decimal,
        amount: int,
        purpose: PurposesOfPurchases,
    ) -> Purchase:
        purchase = Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
        self.purchases.append(purchase)
        return purchase

    def get_purchases_descending_by_date(self, user: Union[Member, Company]):
        # order purchases by purchase_date
        self.purchases = sorted(
            self.purchases, key=lambda x: x.purchase_date, reverse=True
        )

        for purchase in self.purchases:
            if purchase.buyer is user:
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
        amount: Decimal,
        purpose: str,
    ) -> Transaction:
        transaction = Transaction(
            id=uuid4(),
            date=date,
            sending_account=sending_account,
            receiving_account=receiving_account,
            amount=amount,
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


@singleton
class OfferRepository(interfaces.OfferRepository):
    @inject
    def __init__(self, plan_repository: PlanRepository) -> None:
        self.offers: List[ProductOffer] = []
        self.plan_repository = plan_repository

    def get_all_offers(self) -> Iterator[ProductOffer]:
        yield from self.offers

    def count_all_offers_without_plan_duplicates(self) -> int:
        offers = []
        plans_associated = []
        for offer in self.offers:
            if offer.plan in plans_associated:
                pass
            else:
                offers.append(offer)
                plans_associated.append(offer.plan)
        return len(offers)

    def query_offers_by_name(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.name:
                yield offer

    def query_offers_by_description(self, query: str) -> Iterator[ProductOffer]:
        for offer in self.offers:
            if query in offer.description:
                yield offer

    def create_offer(
        self,
        plan: Plan,
        creation_datetime: datetime,
        name: str,
        description: str,
    ) -> ProductOffer:
        offer = ProductOffer(
            id=uuid4(),
            name=name,
            description=description,
            plan=plan,
        )
        self.offers.append(offer)
        return offer

    def get_by_id(self, id: UUID) -> ProductOffer:
        for offer in self.offers:
            if offer.id == id:
                return offer
        raise Exception("Offer not found, this exception is not meant to be caught")

    def delete_offer(self, id: UUID) -> None:
        offer = self.get_by_id(id)
        self.offers.remove(offer)

    def get_all_offers_belonging_to(self, plan_id: UUID) -> List[ProductOffer]:
        offers = []
        for offer in self.offers:
            if offer.plan.id == plan_id:
                offers.append(offer)
        return offers


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

    def get_company_workers(self, company: Company) -> List[Member]:
        return [
            self.member_repository.get_by_id(member)
            for member in self.company_workers[company.id]
        ]

    def get_member_workplaces(self, member: UUID) -> List[Company]:
        return [
            self.company_repository.get_by_id(company)
            for company, workers in self.company_workers.items()
            if member in workers
        ]


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
            transaction.amount for transaction in received_transactions
        ) - decimal_sum(transaction.amount for transaction in sent_transactions)

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
    def __init__(self):
        self.members: Dict[UUID, Member] = {}

    def create_member(
        self, email: str, name: str, password: str, account: Account
    ) -> Member:
        id = uuid4()
        member = Member(
            id=id,
            name=name,
            email=email,
            account=account,
        )
        self.members[id] = member
        return member

    def has_member_with_email(self, email: str) -> bool:
        for member in self.members.values():
            if member.email == email:
                return True
        return False

    def count_registered_members(self) -> int:
        return len(self.members)

    def get_by_id(self, id: UUID) -> Member:
        return self.members[id]


@singleton
class CompanyRepository(interfaces.CompanyRepository):
    @inject
    def __init__(self) -> None:
        self.companies: Dict[str, Company] = {}

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
        new_company = Company(
            id=uuid4(),
            email=email,
            name=name,
            means_account=means_account,
            raw_material_account=resource_account,
            work_account=labour_account,
            product_account=products_account,
        )
        self.companies[email] = new_company
        return new_company

    def has_company_with_email(self, email: str) -> bool:
        return email in self.companies

    def get_by_id(self, id: UUID) -> Company:
        for company in self.companies.values():
            if company.id == id:
                return company
        raise Exception("Company not found, this exception is not meant to be caught")

    def count_registered_companies(self) -> int:
        return len(self.companies)


@singleton
class PlanRepository(interfaces.PlanRepository):
    @inject
    def __init__(
        self,
        draft_repository: PlanDraftRepository,
        company_repository: CompanyRepository,
    ) -> None:
        self.plans: Dict[UUID, Plan] = {}
        self.draft_repository = draft_repository
        self.company_repository = company_repository

    def get_plan_by_id(self, id: UUID) -> Optional[Plan]:
        return self.plans.get(id)

    def approve_plan(self, draft: PlanDraft, approval_timestamp: datetime) -> Plan:
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
        plan.approved = True
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

    def renew_plan(self, plan: Plan) -> None:
        plan.renewed = True

    def set_expiration_date(self, plan: Plan, expiration_date: datetime) -> None:
        plan.expiration_date = expiration_date

    def set_expiration_relative(self, plan: Plan, days: int) -> None:
        plan.expiration_relative = days

    def set_last_certificate_payout(self, plan: Plan, last_payout) -> None:
        plan.last_certificate_payout = last_payout

    def all_active_plans(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active:
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
            if plan.approved and not plan.expired:
                yield plan

    def all_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.approved and plan.is_active and not plan.expired:
                yield plan

    def all_productive_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                not plan.is_public_service
                and plan.is_active
                and plan.approved
                and not plan.expired
            ):
                yield plan

    def all_public_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                plan.is_public_service
                and plan.is_active
                and plan.approved
                and not plan.expired
            ):
                yield plan

    def get_approved_plans_created_before(self, timestamp: datetime) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                plan.approved
                and not plan.is_active
                and not plan.expired
                and plan.plan_creation_date < timestamp
            ):
                yield plan

    def delete_plan(self, plan_id: UUID) -> None:
        del self.plans[plan_id]

    def get_all_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        for plan in self.plans.values():
            if str(plan.planner.id) == str(company_id):
                yield plan

    def get_non_active_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                plan.planner == company_id
                and plan.approved
                and not plan.is_active
                and not plan.expired
            ):
                yield plan

    def get_active_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        for plan in self.plans.values():
            if (
                plan.planner == company_id
                and plan.approved
                and plan.is_active
                and not plan.expired
            ):
                yield plan

    def get_expired_plans_for_company(self, company_id: UUID) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.planner == company_id and plan.expired:
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
            approved=False,
            approval_date=None,
            approval_reason=None,
            expired=False,
            renewed=False,
            expiration_relative=None,
            expiration_date=None,
            last_certificate_payout=None,
        )
        self.plans[plan.id] = plan
        return plan

    def query_active_plans_by_product_name(self, query: str) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active and (query in plan.prd_name):
                yield plan

    def query_active_plans_by_plan_id(self, query: str) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_active and (query in str(plan.id)):
                yield plan


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
