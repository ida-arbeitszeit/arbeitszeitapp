from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator, List, Optional, TypeVar, Union
from uuid import UUID

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import desc, distinct, func
from werkzeug.security import generate_password_hash

from arbeitszeit import entities, repositories
from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.decimal import decimal_sum
from project.error import (
    CompanyNotFound,
    MemberNotFound,
    PlanNotFound,
    ProductOfferNotFound,
)
from project.models import (
    Account,
    Company,
    Purchase,
    Member,
    Offer,
    Plan,
    SocialAccounting,
    Transaction,
)

T = TypeVar("T")


@inject
@dataclass
class CompanyWorkerRepository(repositories.CompanyWorkerRepository):
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def add_worker_to_company(
        self, company: entities.Company, worker: entities.Member
    ) -> None:
        company_orm = self.company_repository.object_to_orm(company)
        worker_orm = self.member_repository.object_to_orm(worker)
        if worker_orm not in company_orm.workers:
            company_orm.workers.append(worker_orm)

    def get_company_workers(self, company: entities.Company) -> List[entities.Member]:
        company_orm = self.company_repository.object_to_orm(company)
        return [
            self.member_repository.object_from_orm(member)
            for member in company_orm.workers
        ]

    def get_member_workplaces(self, member: UUID) -> List[entities.Company]:
        member_orm = Member.query.filter_by(id=str(member)).first()
        if member_orm is None:
            return []
        workplaces_orm = member_orm.workplaces.all()
        return [
            self.company_repository.object_from_orm(workplace_orm)
            for workplace_orm in workplaces_orm
        ]


@inject
@dataclass
class MemberRepository(repositories.MemberRepository):
    account_repository: AccountRepository
    db: SQLAlchemy

    def get_member_by_id(self, id: UUID) -> entities.Member:
        orm_object = Member.query.filter_by(id=str(id)).first()
        if orm_object is None:
            raise MemberNotFound()
        else:
            return self.object_from_orm(orm_object)

    get_by_id = get_member_by_id

    def object_from_orm(self, orm_object: Member) -> entities.Member:
        member_account = self.account_repository.object_from_orm(orm_object.account)
        return entities.Member(
            id=UUID(orm_object.id),
            name=orm_object.name,
            account=member_account,
            email=orm_object.email,
        )

    def object_to_orm(self, member: entities.Member) -> Member:
        return Member.query.get(str(member.id))

    def create_member(
        self, email: str, name: str, password: str, account: entities.Account
    ) -> entities.Member:
        orm_account = self.account_repository.object_to_orm(account)
        orm_member = Member(
            email=email,
            name=name,
            password=generate_password_hash(password, method="sha256"),
            account=orm_account,
        )
        orm_account.account_owner_member = orm_member.id
        self.db.session.add(orm_member)
        self.db.session.commit()
        return self.object_from_orm(orm_member)

    def has_member_with_email(self, email: str) -> bool:
        return Member.query.filter_by(email=email).count()

    def count_registered_members(self) -> int:
        return int(self.db.session.query(func.count(Member.id)).one()[0])


@inject
@dataclass
class CompanyRepository(repositories.CompanyRepository):
    account_repository: AccountRepository
    member_repository: MemberRepository
    db: SQLAlchemy

    def object_to_orm(self, company: entities.Company) -> Company:
        return Company.query.get(str(company.id))

    def object_from_orm(self, company_orm: Company) -> entities.Company:
        return entities.Company(
            id=UUID(company_orm.id),
            email=company_orm.email,
            name=company_orm.name,
            means_account=self.account_repository.object_from_orm(
                self._get_means_account(company_orm)
            ),
            raw_material_account=self.account_repository.object_from_orm(
                self._get_resources_account(company_orm)
            ),
            work_account=self.account_repository.object_from_orm(
                self._get_labour_account(company_orm)
            ),
            product_account=self.account_repository.object_from_orm(
                self._get_products_account(company_orm)
            ),
        )

    def _get_means_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="p").first()
        assert account
        return account

    def _get_resources_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="r").first()
        assert account
        return account

    def _get_labour_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="a").first()
        assert account
        return account

    def _get_products_account(self, company: Company) -> Account:
        account = company.accounts.filter_by(account_type="prd").first()
        assert account
        return account

    def get_by_id(self, id: UUID) -> entities.Company:
        company_orm = Company.query.filter_by(id=str(id)).first()
        if company_orm is None:
            raise CompanyNotFound()
        else:
            return self.object_from_orm(company_orm)

    def create_company(
        self,
        email: str,
        name: str,
        password: str,
        means_account: entities.Account,
        labour_account: entities.Account,
        resource_account: entities.Account,
        products_account: entities.Account,
    ) -> entities.Company:
        company = Company(
            email=email,
            name=name,
            password=generate_password_hash(password, method="sha256"),
        )
        self.db.session.add(company)
        self.db.session.commit()
        for account in [
            means_account,
            labour_account,
            resource_account,
            products_account,
        ]:
            account_orm = self.account_repository.object_to_orm(account)
            account_orm.account_owner_company = company.id
        self.db.session.commit()
        return self.object_from_orm(company)

    def has_company_with_email(self, email: str) -> bool:
        return Company.query.filter_by(email=email).first() is not None

    def count_registered_companies(self) -> int:
        return int(self.db.session.query(func.count(Company.id)).one()[0])


@inject
@dataclass
class AccountRepository(repositories.AccountRepository):
    db: SQLAlchemy

    def object_from_orm(self, account_orm: Account) -> entities.Account:
        assert account_orm
        return entities.Account(
            id=UUID(account_orm.id),
            account_type=account_orm.account_type,
        )

    def object_to_orm(self, account: entities.Account) -> Account:
        account_orm = Account.query.filter_by(id=str(account.id)).first()
        assert account_orm
        return account_orm

    def create_account(self, account_type: entities.AccountTypes) -> entities.Account:
        account = Account(account_type=account_type.value)
        self.db.session.add(account)
        self.db.session.commit()
        return self.object_from_orm(account)

    def get_account_balance(self, account: entities.Account) -> Decimal:
        account_orm = self.object_to_orm(account)
        received = set(account_orm.transactions_received)
        sent = set(account_orm.transactions_sent)
        intersection = received & sent
        received -= intersection
        sent -= intersection
        return decimal_sum(t.amount for t in received) - decimal_sum(
            t.amount for t in sent
        )


@inject
@dataclass
class AccountOwnerRepository(repositories.AccountOwnerRepository):
    account_repository: AccountRepository
    member_repository: MemberRepository
    company_repository: CompanyRepository
    social_accounting_repository: AccountingRepository

    def get_account_owner(
        self, account: entities.Account
    ) -> Union[entities.Member, entities.Company, entities.SocialAccounting]:
        account_owner: Union[
            entities.Member, entities.Company, entities.SocialAccounting
        ]
        account_orm = self.account_repository.object_to_orm(account)
        if account_orm.account_owner_member:
            account_owner = self.member_repository.object_from_orm(account_orm.member)
        elif account_orm.account_owner_company:
            account_owner = self.company_repository.object_from_orm(account_orm.company)
        elif account_orm.account_owner_social_accounting:
            account_owner = self.social_accounting_repository.object_from_orm(
                account_orm.social_accounting
            )

        assert account_owner
        return account_owner


@inject
@dataclass
class AccountingRepository:
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_from_orm(
        self, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        accounting_account_orm = accounting_orm.account
        accounting_account = self.account_repository.object_from_orm(
            accounting_account_orm
        )
        return entities.SocialAccounting(account=accounting_account)

    def get_by_id(self, id: UUID) -> Optional[entities.SocialAccounting]:
        accounting_orm = SocialAccounting.query.filter_by(id=str(id)).first()
        return self.object_from_orm(accounting_orm) if accounting_orm else None

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        return self.object_from_orm(self.get_or_create_social_accounting_orm())

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = SocialAccounting.query.first()
        if not social_accounting:
            social_accounting = SocialAccounting()
            account = Account(
                account_owner_social_accounting=social_accounting.id,
                account_type="accounting",
            )
            social_accounting.account = account
            self.db.session.add(social_accounting, account)
            self.db.session.commit()
        return social_accounting


@inject
@dataclass
class PurchaseRepository(repositories.PurchaseRepository):
    member_repository: MemberRepository
    plan_repository: PlanRepository
    company_repository: CompanyRepository
    product_offer_repository: ProductOfferRepository
    db: SQLAlchemy

    def object_to_orm(self, purchase: entities.Purchase) -> Purchase:
        return Purchase(
            purchase_date=purchase.purchase_date,
            plan_id=str(purchase.plan.id),
            type_member=isinstance(purchase.buyer, entities.Member),
            company=(
                self.company_repository.object_to_orm(purchase.buyer).id
                if isinstance(purchase.buyer, entities.Company)
                else None
            ),
            member=(
                self.member_repository.object_to_orm(purchase.buyer).id
                if isinstance(purchase.buyer, entities.Member)
                else None
            ),
            price_per_unit=float(purchase.price_per_unit),
            amount=purchase.amount,
            purpose=purchase.purpose.value,
        )

    def object_from_orm(self, purchase: Purchase) -> entities.Purchase:
        plan = self.plan_repository.get_plan_by_id(purchase.plan_id)
        return entities.Purchase(
            purchase_date=purchase.purchase_date,
            plan=plan,
            buyer=self.member_repository.get_member_by_id(purchase.member)
            if purchase.type_member
            else self.company_repository.get_by_id(purchase.company),
            price_per_unit=purchase.price_per_unit,
            amount=purchase.amount,
            purpose=purchase.purpose,
        )

    def add(self, purchase: entities.Purchase) -> None:
        purchase_orm = self.object_to_orm(purchase)
        self.db.session.add(purchase_orm)

    def get_purchases_descending_by_date(
        self, user: Union[entities.Member, entities.Company]
    ) -> Iterator[entities.Purchase]:
        user_orm: Union[Member, Company]
        if isinstance(user, entities.Company):
            user_orm = self.company_repository.object_to_orm(user)
        else:
            user_orm = self.member_repository.object_to_orm(user)
        return (
            self.object_from_orm(purchase)
            for purchase in user_orm.purchases.order_by(desc("purchase_date")).all()
        )


@inject
@dataclass
class ProductOfferRepository(repositories.OfferRepository):
    company_repository: CompanyRepository
    plan_repository: PlanRepository
    db: SQLAlchemy

    def object_to_orm(self, product_offer: entities.ProductOffer) -> Offer:
        return Offer.query.get(str(product_offer.id))

    def object_from_orm(self, offer_orm: Offer) -> entities.ProductOffer:
        plan = self.plan_repository.object_from_orm(offer_orm.plan)
        return entities.ProductOffer(
            id=UUID(offer_orm.id),
            name=offer_orm.name,
            deactivate_offer_in_db=lambda: setattr(offer_orm, "active", False),
            active=offer_orm.active,
            description=offer_orm.description,
            plan=plan,
        )

    def get_by_id(self, id: UUID) -> entities.ProductOffer:
        offer_orm = Offer.query.filter_by(id=str(id)).first()
        if offer_orm is None:
            raise ProductOfferNotFound()
        else:
            return self.object_from_orm(offer_orm)

    def all_active_offers(self) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter_by(active=True).all()
        )

    def count_active_offers_without_plan_duplicates(self) -> int:
        return int(
            self.db.session.query(func.count(distinct(Offer.plan_id)))
            .filter_by(active=True)
            .one()[0]
        )

    def query_offers_by_name(self, query: str) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter(
                Offer.name.contains(query), Offer.active == True
            ).all()
        )

    def query_offers_by_description(
        self, query: str
    ) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter(
                Offer.description.contains(query), Offer.active == True
            ).all()
        )

    def create_offer(
        self,
        plan: entities.Plan,
        creation_datetime: datetime,
        name: str,
        description: str,
    ) -> entities.ProductOffer:
        offer = Offer(
            plan_id=self.plan_repository.object_to_orm(plan).id,
            cr_date=creation_datetime,
            name=name,
            description=description,
        )
        self.db.session.add(offer)
        self.db.session.commit()
        return self.object_from_orm(offer)

    def __len__(self) -> int:
        return len(Offer.query.all())


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository
    accounting_repository: AccountingRepository
    datetime_service: DatetimeService
    db: SQLAlchemy

    def _approve(self, plan, decision, reason, approval_date):
        plan.approved = decision
        plan.approval_reason = reason
        plan.approval_date = approval_date

    def object_from_orm(self, plan: Plan) -> entities.Plan:
        production_costs = entities.ProductionCosts(
            labour_cost=plan.costs_a,
            resource_cost=plan.costs_r,
            means_cost=plan.costs_p,
        )
        return entities.Plan(
            id=UUID(plan.id),
            plan_creation_date=plan.plan_creation_date,
            planner=self.company_repository.get_by_id(UUID(plan.planner)),
            production_costs=production_costs,
            prd_name=plan.prd_name,
            prd_unit=plan.prd_unit,
            prd_amount=plan.prd_amount,
            description=plan.description,
            timeframe=plan.timeframe,
            is_public_service=plan.is_public_service,
            approved=plan.approved,
            approval_date=plan.approval_date,
            approval_reason=plan.approval_reason,
            approve=lambda decision, reason, approval_date: self._approve(
                plan, decision, reason, approval_date
            ),
            is_active=plan.is_active,
            expired=plan.expired,
            renewed=plan.renewed,
            expiration_relative=plan.expiration_relative,
            expiration_date=plan.expiration_date,
            last_certificate_payout=plan.last_certificate_payout,
            activation_date=plan.activation_date,
        )

    def object_to_orm(self, plan: entities.Plan) -> Plan:
        return Plan.query.get(str(plan.id))

    def get_plan_by_id(self, id: UUID) -> entities.Plan:
        plan_orm = Plan.query.filter_by(id=str(id)).first()
        if plan_orm is None:
            raise PlanNotFound()
        else:
            return self.object_from_orm(plan_orm)

    def create_plan(
        self,
        planner: entities.Company,
        costs: entities.ProductionCosts,
        product_name: str,
        production_unit: str,
        amount: int,
        description: str,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> entities.Plan:
        plan = Plan(
            plan_creation_date=creation_timestamp,
            planner=self.company_repository.object_to_orm(planner).id,
            costs_p=costs.means_cost,
            costs_r=costs.resource_cost,
            costs_a=costs.labour_cost,
            prd_name=product_name,
            prd_unit=production_unit,
            prd_amount=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
            is_active=False,
            activation_date=None,
            expiration_date=None,
            social_accounting=self.accounting_repository.get_or_create_social_accounting_orm().id,
        )

        self.db.session.add(plan)
        self.db.session.commit()
        return self.object_from_orm(plan)

    def activate_plan(self, plan: entities.Plan, activation_date: datetime) -> None:
        plan.is_active = True
        plan.activation_date = activation_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.is_active = True
        plan_orm.activation_date = activation_date
        self.db.session.commit()

    def set_plan_as_expired(self, plan: entities.Plan) -> None:
        plan.expired = True
        plan.is_active = False

        plan_orm = self.object_to_orm(plan)
        plan_orm.expired = True
        plan_orm.is_active = False
        self.db.session.commit()

    def renew_plan(self, plan: entities.Plan) -> None:
        plan.renewed = True

        plan_orm = self.object_to_orm(plan)
        plan_orm.renewed = True
        self.db.session.commit()

    def set_expiration_date(
        self, plan: entities.Plan, expiration_date: datetime
    ) -> None:
        plan.expiration_date = expiration_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.expiration_date = expiration_date
        self.db.session.commit()

    def set_expiration_relative(self, plan: entities.Plan, days: int) -> None:
        plan.expiration_relative = days

        plan_orm = self.object_to_orm(plan)
        plan_orm.expiration_relative = days
        self.db.session.commit()

    def set_last_certificate_payout(
        self, plan: entities.Plan, last_payout: datetime
    ) -> None:
        plan.last_certificate_payout = last_payout

        plan_orm = self.object_to_orm(plan)
        plan_orm.last_certificate_payout = last_payout
        self.db.session.commit()

    def all_active_plans(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(is_active=True).all()
        )

    def count_active_plans(self) -> int:
        return int(
            self.db.session.query(func.count(Plan.id))
            .filter_by(is_active=True)
            .one()[0]
        )

    def count_active_public_plans(self) -> int:
        return int(
            self.db.session.query(func.count(Plan.id))
            .filter_by(is_active=True, is_public_service=True)
            .one()[0]
        )

    def avg_timeframe_of_active_plans(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.avg(Plan.timeframe))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_work(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_a))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_resources(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_r))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def sum_of_active_planned_means(self) -> Decimal:
        return Decimal(
            self.db.session.query(func.sum(Plan.costs_p))
            .filter_by(is_active=True)
            .one()[0]
            or 0
        )

    def all_plans_approved_and_not_expired(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(approved=True, expired=False).all()
        )

    def all_productive_plans_approved_active_and_not_expired(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                approved=True, is_active=True, expired=False, is_public_service=False
            ).all()
        )

    def all_public_plans_approved_active_and_not_expired(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                approved=True, is_active=True, expired=False, is_public_service=True
            ).all()
        )

    def all_plans_approved_active_and_not_expired(self) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                approved=True,
                is_active=True,
                expired=False,
            ).all()
        )

    def get_plans_suitable_for_activation(
        self,
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter_by(
                approved=True, is_active=False, expired=False
            ).all()
            if plan_orm.plan_creation_date
            < self.datetime_service.past_plan_activation_date()
        )


@inject
@dataclass
class TransactionRepository(repositories.TransactionRepository):
    account_repository: AccountRepository
    db: SQLAlchemy

    def object_to_orm(self, transaction: entities.Transaction) -> Transaction:
        return Transaction.query.get(str(transaction.id))

    def object_from_orm(self, transaction: Transaction) -> entities.Transaction:
        return entities.Transaction(
            id=UUID(transaction.id),
            date=transaction.date,
            sending_account=self.account_repository.object_from_orm(
                transaction.account_from
            ),
            receiving_account=self.account_repository.object_from_orm(
                transaction.account_to
            ),
            amount=Decimal(transaction.amount),
            purpose=transaction.purpose,
        )

    def create_transaction(
        self,
        date: datetime,
        sending_account: entities.Account,
        receiving_account: entities.Account,
        amount: Decimal,
        purpose: str,
    ) -> entities.Transaction:
        transaction = Transaction(
            date=date,
            sending_account=str(sending_account.id),
            receiving_account=str(receiving_account.id),
            amount=amount,
            purpose=purpose,
        )
        self.db.session.add(transaction)
        self.db.session.commit()
        return self.object_from_orm(transaction)

    def add(self, transaction: entities.Transaction) -> None:
        self.db.session.add(self.object_to_orm(transaction))

    def all_transactions_sent_by_account(
        self, account: entities.Account
    ) -> List[entities.Transaction]:
        account_orm = self.account_repository.object_to_orm(account)
        return [
            self.object_from_orm(transaction)
            for transaction in account_orm.transactions_sent.all()
        ]

    def all_transactions_received_by_account(
        self, account: entities.Account
    ) -> List[entities.Transaction]:
        account_orm = self.account_repository.object_to_orm(account)
        return [
            self.object_from_orm(transaction)
            for transaction in account_orm.transactions_received.all()
        ]
