from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, Iterator, List, Union

from injector import inject, singleton

import arbeitszeit.repositories as interfaces
from arbeitszeit.entities import (
    Account,
    AccountTypes,
    Company,
    Member,
    Plan,
    ProductionCosts,
    ProductOffer,
    Purchase,
    SocialAccounting,
    Transaction,
)


@singleton
class PurchaseRepository(interfaces.PurchaseRepository):
    @inject
    def __init__(self):
        self.purchases = []

    def add(self, purchase: Purchase):
        self.purchases.append(purchase)

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

    def add(self, transaction: Transaction) -> None:
        assert transaction not in self.transactions
        self.transactions.append(transaction)

    def create_transaction(
        self,
        date: datetime,
        account_from: Account,
        account_to: Account,
        amount: Decimal,
        purpose: str,
    ) -> Transaction:
        transaction = Transaction(
            id=uuid.uuid4(),
            date=date,
            account_from=account_from,
            account_to=account_to,
            amount=amount,
            purpose=purpose,
        )
        self.transactions.append(transaction)
        return transaction

    def all_transactions_sent_by_account(self, account: Account) -> List[Transaction]:
        all_sent = []
        for transaction in self.transactions:
            if transaction.account_from == account:
                all_sent.append(transaction)
        return all_sent

    def all_transactions_received_by_account(
        self, account: Account
    ) -> List[Transaction]:
        all_received = []
        for transaction in self.transactions:
            if transaction.account_to == account:
                all_received.append(transaction)
        return all_received


@singleton
class OfferRepository(interfaces.OfferRepository):
    @inject
    def __init__(self, plan_repository: PlanRepository) -> None:
        self.offers: List[ProductOffer] = []
        self.plan_repository = plan_repository

    def all_active_offers(self) -> Iterator[ProductOffer]:
        yield from self.offers

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
        amount_available: int,
    ) -> ProductOffer:
        offer = ProductOffer(
            id=uuid.uuid4(),
            name=name,
            amount_available=amount_available,
            deactivate_offer_in_db=lambda: None,
            decrease_amount_available=lambda _: None,
            active=True,
            description=description,
            plan=plan,
        )
        self.offers.append(offer)
        return offer


@singleton
class CompanyWorkerRepository(interfaces.CompanyWorkerRepository):
    def add_worker_to_company(self, company: Company, worker: Member) -> None:
        if worker not in company.workers:
            company.workers.append(worker)

    def get_company_workers(self, company: Company) -> List[Member]:
        return company.workers


@singleton
class AccountRepository(interfaces.AccountRepository):
    @inject
    def __init__(self):
        self.accounts = []
        self.latest_id = 0

    def __contains__(self, account: object) -> bool:
        if not isinstance(account, Account):
            return False
        return account in self.accounts

    def add(self, account: Account) -> None:
        assert account not in self
        self.accounts.append(account)

    def create_account(self, account_type: AccountTypes) -> Account:
        account = Account(
            id=self.latest_id,
            balance=Decimal(0),
            account_type=account_type,
            change_credit=lambda _: None,
        )
        self.latest_id += 1
        self.accounts.append(account)
        return account


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
        for member in self.member_repository.members:
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
        self.members = []
        self.last_id = 0

    def create_member(
        self, email: str, name: str, password: str, account: Account
    ) -> Member:
        self.last_id += 1
        member = Member(
            id=self.last_id,
            name=name,
            email=email,
            account=account,
        )
        self.members.append(member)
        return member

    def has_member_with_email(self, email: str) -> bool:
        for member in self.members:
            if member.email == email:
                return True
        return False


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
            id=uuid.uuid4(),
            email=email,
            name=name,
            means_account=means_account,
            raw_material_account=resource_account,
            work_account=labour_account,
            product_account=products_account,
            workers=[],
        )
        self.companies[email] = new_company
        return new_company

    def has_company_with_email(self, email: str) -> bool:
        return email in self.companies


@singleton
class PlanRepository(interfaces.PlanRepository):
    def __init__(self) -> None:
        self.plans: Dict[uuid.UUID, Plan] = {}

    def create_plan(
        self,
        planner: Company,
        costs: ProductionCosts,
        product_name: str,
        production_unit: str,
        amount: int,
        description: str,
        timeframe_in_days: int,
        is_public_service: bool,
        is_active: bool,
        creation_timestamp: datetime,
        activation_timestamp: datetime,
    ) -> Plan:
        plan = Plan(
            id=uuid.uuid4(),
            plan_creation_date=creation_timestamp,
            planner=planner,
            production_costs=costs,
            prd_name=product_name,
            prd_unit=production_unit,
            prd_amount=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
            is_active=is_active,
            activation_date=activation_timestamp,
            approved=False,
            approval_date=None,
            approval_reason=None,
            approve=lambda _1, _2, _3: None,
            expired=False,
            renewed=False,
            expiration_relative=None,
            expiration_date=None,
            last_certificate_payout=None,
        )
        self.plans[planner.id] = plan
        return plan

    def get_plan_by_id(self, id: uuid.UUID) -> Plan:
        return self.plans[id]

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

    def all_plans_approved_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.approved and not plan.expired:
                yield plan

    def all_plans_approved_active_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.approved and plan.is_active and not plan.expired:
                yield plan

    def all_productive_plans_approved_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if not plan.is_public_service and plan.approved and not plan.expired:
                yield plan

    def all_public_plans_approved_and_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.is_public_service and plan.approved and not plan.expired:
                yield plan

    def all_plans_approved_not_active_not_expired(self) -> Iterator[Plan]:
        for plan in self.plans.values():
            if plan.approved and not plan.is_active and not plan.expired:
                yield plan
