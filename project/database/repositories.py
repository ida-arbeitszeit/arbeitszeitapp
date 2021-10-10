from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator, List, Optional, Union
from uuid import UUID, uuid4

from flask_sqlalchemy import SQLAlchemy
from injector import inject
from sqlalchemy import desc, distinct, func
from werkzeug.security import generate_password_hash

from arbeitszeit import entities, repositories
from arbeitszeit.decimal import decimal_sum
from project.error import PlanNotFound, ProductOfferNotFound
from project.models import (
    Account,
    Company,
    Member,
    Offer,
    Plan,
    PlanDraft,
    Purchase,
    SocialAccounting,
    Transaction,
)


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

    def get_by_id(self, id: UUID) -> Optional[entities.Member]:
        orm_object = Member.query.filter_by(id=str(id)).first()
        if orm_object is None:
            return None
        return self.object_from_orm(orm_object)

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
            id=str(uuid4()),
            email=email,
            name=name,
            password=generate_password_hash(password, method="sha256"),
            account=orm_account,
        )
        orm_account.account_owner_member = orm_member.id
        self.db.session.add(orm_member)
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

    def get_by_id(self, id: UUID) -> Optional[entities.Company]:
        company_orm = Company.query.filter_by(id=str(id)).first()
        if company_orm is None:
            return None
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
            id=str(uuid4()),
            email=email,
            name=name,
            password=generate_password_hash(password, method="sha256"),
        )
        self.db.session.add(company)
        for account in [
            means_account,
            labour_account,
            resource_account,
            products_account,
        ]:
            account_orm = self.account_repository.object_to_orm(account)
            account_orm.account_owner_company = company.id
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
        account = Account(id=str(uuid4()), account_type=account_type.value)
        self.db.session.add(account)
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

    def get_by_id(self, id: UUID) -> entities.Account:
        return self.object_from_orm(Account.query.get(str(id)))


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

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        return self.object_from_orm(self.get_or_create_social_accounting_orm())

    def get_or_create_social_accounting_orm(self) -> SocialAccounting:
        social_accounting = SocialAccounting.query.first()
        if not social_accounting:
            social_accounting = SocialAccounting(
                id=str(uuid4()),
            )
            account = Account(
                id=str(uuid4()),
                account_owner_social_accounting=social_accounting.id,
                account_type="accounting",
            )
            social_accounting.account = account
            self.db.session.add(social_accounting, account)
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
        assert plan is not None
        return entities.Purchase(
            purchase_date=purchase.purchase_date,
            plan=plan,
            buyer=self._get_buyer(purchase),
            price_per_unit=purchase.price_per_unit,
            amount=purchase.amount,
            purpose=purchase.purpose,
        )

    def _get_buyer(
        self, purchase: Purchase
    ) -> Union[entities.Company, entities.Member]:
        buyer: Union[None, entities.Company, entities.Member]
        if purchase.type_member:
            buyer = self.member_repository.get_by_id(purchase.member)
        else:
            buyer = self.company_repository.get_by_id(purchase.company)
        assert buyer is not None
        return buyer

    def create_purchase(
        self,
        purchase_date: datetime,
        plan: entities.Plan,
        buyer: Union[entities.Member, entities.Company],
        price_per_unit: Decimal,
        amount: int,
        purpose: entities.PurposesOfPurchases,
    ) -> entities.Purchase:
        purchase = entities.Purchase(
            purchase_date=purchase_date,
            plan=plan,
            buyer=buyer,
            price_per_unit=price_per_unit,
            amount=amount,
            purpose=purpose,
        )
        purchase_orm = self.object_to_orm(purchase)
        self.db.session.add(purchase_orm)
        return purchase

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
        plan = self.plan_repository.get_plan_by_id(UUID(offer_orm.plan_id))
        assert plan is not None
        return entities.ProductOffer(
            id=UUID(offer_orm.id),
            name=offer_orm.name,
            description=offer_orm.description,
            plan=plan,
        )

    def get_by_id(self, id: UUID) -> entities.ProductOffer:
        offer_orm = Offer.query.filter_by(id=str(id)).first()
        if offer_orm is None:
            raise ProductOfferNotFound()
        else:
            return self.object_from_orm(offer_orm)

    def get_all_offers(self) -> Iterator[entities.ProductOffer]:
        return (self.object_from_orm(offer) for offer in Offer.query.all())

    def count_all_offers_without_plan_duplicates(self) -> int:
        return int(self.db.session.query(func.count(distinct(Offer.plan_id))).one()[0])

    def query_offers_by_name(self, query: str) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter(Offer.name.contains(query)).all()
        )

    def query_offers_by_description(
        self, query: str
    ) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter(Offer.description.contains(query)).all()
        )

    def create_offer(
        self,
        plan: entities.Plan,
        creation_datetime: datetime,
        name: str,
        description: str,
    ) -> entities.ProductOffer:
        offer = Offer(
            id=str(uuid4()),
            plan_id=self.plan_repository.object_to_orm(plan).id,
            cr_date=creation_datetime,
            name=name,
            description=description,
        )
        self.db.session.add(offer)
        return self.object_from_orm(offer)

    def delete_offer(self, id: UUID) -> None:
        offer_orm = Offer.query.filter_by(id=str(id)).first()
        if offer_orm is None:
            raise ProductOfferNotFound()
        else:
            self.db.session.delete(offer_orm)

    def __len__(self) -> int:
        return len(Offer.query.all())

    def get_all_offers_belonging_to(self, plan_id: UUID) -> List[entities.ProductOffer]:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        if plan_orm is None:
            raise PlanNotFound()
        else:
            return [self.object_from_orm(offer) for offer in plan_orm.offers.all()]


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository
    accounting_repository: AccountingRepository
    db: SQLAlchemy

    def object_from_orm(self, plan: Plan) -> entities.Plan:
        production_costs = entities.ProductionCosts(
            labour_cost=plan.costs_a,
            resource_cost=plan.costs_r,
            means_cost=plan.costs_p,
        )
        planner = self.company_repository.get_by_id(UUID(plan.planner))
        assert planner is not None
        return entities.Plan(
            id=UUID(plan.id),
            plan_creation_date=plan.plan_creation_date,
            planner=planner,
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

    def get_plan_by_id(self, id: UUID) -> Optional[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=str(id)).first()
        if plan_orm is None:
            return None
        else:
            return self.object_from_orm(plan_orm)

    def _create_plan_from_draft(
        self,
        plan: entities.PlanDraft,
    ) -> Plan:
        costs = plan.production_costs
        plan = Plan(
            id=plan.id,
            plan_creation_date=plan.creation_date,
            planner=self.company_repository.object_to_orm(plan.planner).id,
            costs_p=costs.means_cost,
            costs_r=costs.resource_cost,
            costs_a=costs.labour_cost,
            prd_name=plan.product_name,
            prd_unit=plan.unit_of_distribution,
            prd_amount=plan.amount_produced,
            description=plan.description,
            timeframe=plan.timeframe,
            is_public_service=plan.is_public_service,
            is_active=False,
            activation_date=None,
            expiration_date=None,
        )
        self.db.session.add(plan)
        return plan

    def approve_plan(
        self, plan: entities.PlanDraft, approval_timestamp: datetime
    ) -> entities.Plan:
        orm_object = self._create_plan_from_draft(plan)
        orm_object.approved = True
        orm_object.approval_reason = "approved"
        orm_object.approval_date = approval_timestamp
        return self.object_from_orm(orm_object)

    def activate_plan(self, plan: entities.Plan, activation_date: datetime) -> None:
        plan.is_active = True
        plan.activation_date = activation_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.is_active = True
        plan_orm.activation_date = activation_date

    def set_plan_as_expired(self, plan: entities.Plan) -> None:
        plan.expired = True
        plan.is_active = False

        plan_orm = self.object_to_orm(plan)
        plan_orm.expired = True
        plan_orm.is_active = False

    def renew_plan(self, plan: entities.Plan) -> None:
        plan.renewed = True

        plan_orm = self.object_to_orm(plan)
        plan_orm.renewed = True

    def set_expiration_date(
        self, plan: entities.Plan, expiration_date: datetime
    ) -> None:
        plan.expiration_date = expiration_date

        plan_orm = self.object_to_orm(plan)
        plan_orm.expiration_date = expiration_date

    def set_expiration_relative(self, plan: entities.Plan, days: int) -> None:
        plan.expiration_relative = days

        plan_orm = self.object_to_orm(plan)
        plan_orm.expiration_relative = days

    def set_last_certificate_payout(
        self, plan: entities.Plan, last_payout: datetime
    ) -> None:
        plan.last_certificate_payout = last_payout

        plan_orm = self.object_to_orm(plan)
        plan_orm.last_certificate_payout = last_payout

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

    def get_approved_plans_created_before(
        self, timestamp: datetime
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(
                Plan.plan_creation_date < timestamp,
                Plan.approved == True,
                Plan.is_active == False,
                Plan.expired == False,
            )
        )

    def delete_plan(self, plan_id: UUID) -> None:
        plan_orm = Plan.query.filter_by(id=str(plan_id)).first()
        if plan_orm is None:
            raise PlanNotFound()
        else:
            self.db.session.delete(plan_orm)

    def query_active_plans_by_product_name(self, query: str) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan)
            for plan in Plan.query.filter(
                Plan.is_active == True, Plan.prd_name.contains(query)
            ).all()
        )

    def query_active_plans_by_plan_id(self, query: str) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan)
            for plan in Plan.query.filter(
                Plan.is_active == True, Plan.id.contains(query)
            ).all()
        )

    def get_all_plans_for_company(self, company_id: UUID) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(Plan.planner == str(company_id))
        )

    def get_non_active_plans_for_company(
        self, company_id: UUID
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(
                Plan.planner == str(company_id),
                Plan.approved == True,
                Plan.is_active == False,
                Plan.expired == False,
            )
        )

    def get_active_plans_for_company(self, company_id: UUID) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(
                Plan.planner == str(company_id),
                Plan.approved == True,
                Plan.is_active == True,
                Plan.expired == False,
            )
        )

    def get_expired_plans_for_company(
        self, company_id: UUID
    ) -> Iterator[entities.Plan]:
        return (
            self.object_from_orm(plan_orm)
            for plan_orm in Plan.query.filter(
                Plan.planner == str(company_id),
                Plan.expired == True,
            )
        )

    def __len__(self) -> int:
        return len(Plan.query.all())


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
            sending_account=self.account_repository.get_by_id(
                transaction.sending_account
            ),
            receiving_account=self.account_repository.get_by_id(
                transaction.receiving_account
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
            id=str(uuid4()),
            date=date,
            sending_account=str(sending_account.id),
            receiving_account=str(receiving_account.id),
            amount=amount,
            purpose=purpose,
        )
        self.db.session.add(transaction)
        return self.object_from_orm(transaction)

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


@inject
@dataclass
class PlanDraftRepository(repositories.PlanDraftRepository):
    db: SQLAlchemy
    company_repository: CompanyRepository

    def create_plan_draft(
        self,
        planner: UUID,
        product_name: str,
        description: str,
        costs: entities.ProductionCosts,
        production_unit: str,
        amount: int,
        timeframe_in_days: int,
        is_public_service: bool,
        creation_timestamp: datetime,
    ) -> entities.PlanDraft:
        orm = PlanDraft(
            id=str(uuid4()),
            plan_creation_date=creation_timestamp,
            planner=str(planner),
            costs_p=costs.means_cost,
            costs_r=costs.resource_cost,
            costs_a=costs.labour_cost,
            prd_name=product_name,
            prd_unit=production_unit,
            prd_amount=amount,
            description=description,
            timeframe=timeframe_in_days,
            is_public_service=is_public_service,
        )
        self.db.session.add(orm)
        return self._object_from_orm(orm)

    def get_by_id(self, id: UUID) -> Optional[entities.PlanDraft]:
        orm = PlanDraft.query.get(str(id))
        if orm is None:
            return None
        else:
            return self._object_from_orm(orm)

    def delete_draft(self, id: UUID) -> None:
        PlanDraft.query.filter_by(id=str(id)).delete()

    def _object_from_orm(self, orm: PlanDraft) -> entities.PlanDraft:
        planner = self.company_repository.get_by_id(orm.planner)
        assert planner is not None
        return entities.PlanDraft(
            id=orm.id,
            creation_date=orm.plan_creation_date,
            planner=planner,
            production_costs=entities.ProductionCosts(
                labour_cost=orm.costs_a,
                resource_cost=orm.costs_r,
                means_cost=orm.costs_p,
            ),
            product_name=orm.prd_name,
            unit_of_distribution=orm.prd_unit,
            amount_produced=orm.prd_amount,
            description=orm.description,
            timeframe=orm.timeframe,
            is_public_service=orm.is_public_service,
        )
