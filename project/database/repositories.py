from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Iterator, List, Optional, TypeVar, Union

from injector import inject
from sqlalchemy import desc
from werkzeug.security import generate_password_hash

from arbeitszeit import entities, repositories
from project.error import CompanyNotFound, MemberNotFound, ProductOfferNotFound
from project.extensions import db
from project.models import (
    Account,
    Company,
    Kaeufe,
    Member,
    Offer,
    Plan,
    SocialAccounting,
    Transaction,
)

T = TypeVar("T")


def assert_is_not_none(candidate: Optional[T]) -> T:
    assert candidate is not None
    return candidate


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
        # add in database
        if worker_orm not in company_orm.workers:
            company_orm.workers.append(worker_orm)
        # add in object
        if worker not in company.workers:
            company.workers.append(worker)

    def get_company_workers(self, company: entities.Company) -> List[entities.Member]:
        return company.workers


@inject
@dataclass
class MemberRepository(repositories.MemberRepository):
    account_repository: AccountRepository

    def get_member_by_id(self, id: int) -> entities.Member:
        orm_object = Member.query.filter_by(id=id).first()
        if orm_object is None:
            raise MemberNotFound()
        else:
            return self.object_from_orm(orm_object)

    def object_from_orm(self, orm_object: Member) -> entities.Member:
        member_account = self.account_repository.object_from_orm(orm_object.account)
        return entities.Member(
            id=orm_object.id,
            name=orm_object.name,
            account=member_account,
            email=orm_object.email,
        )

    def object_to_orm(self, member: entities.Member) -> Member:
        return Member.query.get(member.id)

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
        db.session.add(orm_member)
        db.session.commit()
        return self.object_from_orm(orm_member)

    def has_member_with_email(self, email: str) -> bool:
        return Member.query.filter_by(email=email).count()


@inject
@dataclass
class CompanyRepository:
    account_repository: AccountRepository
    member_repository: MemberRepository

    def object_to_orm(self, company: entities.Company) -> Company:
        return Company.query.get(company.id)

    def object_from_orm(self, company_orm: Company) -> entities.Company:
        means_account_orm = company_orm.accounts.filter_by(account_type="p").first()
        raw_material_account_orm = company_orm.accounts.filter_by(
            account_type="r"
        ).first()
        work_account_orm = company_orm.accounts.filter_by(account_type="a").first()
        product_account_orm = company_orm.accounts.filter_by(account_type="prd").first()
        return entities.Company(
            id=company_orm.id,
            means_account=self.account_repository.object_from_orm(means_account_orm),
            raw_material_account=self.account_repository.object_from_orm(
                raw_material_account_orm
            ),
            work_account=self.account_repository.object_from_orm(work_account_orm),
            product_account=self.account_repository.object_from_orm(
                product_account_orm
            ),
            workers=[
                self.member_repository.object_from_orm(worker_orm)
                for worker_orm in company_orm.workers
            ],
        )

    def get_by_id(self, id: int) -> entities.Company:
        company_orm = Company.query.filter_by(id=id).first()
        if company_orm is None:
            raise CompanyNotFound()
        else:
            return self.object_from_orm(company_orm)


@inject
@dataclass
class AccountRepository(repositories.AccountRepository):
    def object_from_orm(self, account_orm: Account) -> entities.Account:
        return entities.Account(
            id=account_orm.id,
            account_type=account_orm.account_type,
            balance=account_orm.balance,
            change_credit=lambda amount: setattr(
                account_orm, "balance", account_orm.balance + amount
            ),
        )

    def object_to_orm(self, account: entities.Account) -> Account:
        account_orm = Account.query.filter_by(id=account.id).first()
        assert account_orm
        return account_orm

    def add(self, account: entities.Account) -> None:
        account_orm = Account(
            account_owner_social_accounting=None,
            account_owner_company=None,
            account_owner_member=None,
            account_type=account.account_type,
            balance=account.balance,
        )
        db.session.add(account_orm)
        db.session.commit()

    def create_account(self, account_type: entities.AccountTypes):
        account = Account(account_type=account_type.value)
        db.session.add(account)
        db.session.commit()
        return self.object_from_orm(account)


@inject
@dataclass
class AccountingRepository:
    account_repository: AccountRepository

    def object_from_orm(
        self, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        accounting_account_orm = accounting_orm.account
        accounting_account = self.account_repository.object_from_orm(
            accounting_account_orm
        )
        return entities.SocialAccounting(account=accounting_account)

    def get_by_id(self, id: int) -> Optional[entities.SocialAccounting]:
        accounting_orm = SocialAccounting.query.filter_by(id=id).first()
        return self.object_from_orm(accounting_orm) if accounting_orm else None

    def get_or_create_social_accounting(self) -> entities.SocialAccounting:
        social_accounting = SocialAccounting.query.filter_by(id=1).first()
        if not social_accounting:
            social_accounting = SocialAccounting(id=1)
            db.session.add(social_accounting)
            db.session.commit()
        return self.object_from_orm(social_accounting)


@inject
@dataclass
class PurchaseRepository(repositories.PurchaseRepository):
    member_repository: MemberRepository
    company_repository: CompanyRepository
    product_offer_repository: ProductOfferRepository

    def object_to_orm(self, purchase: entities.Purchase) -> Kaeufe:
        product_offer = self.product_offer_repository.object_to_orm(
            purchase.product_offer
        )
        return Kaeufe(
            kauf_date=purchase.purchase_date,
            angebot=product_offer.id,
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
            kaufpreis=float(purchase.price),
            amount=purchase.amount,
            purpose=purchase.purpose.value,
        )

    def object_from_orm(self, purchase: Kaeufe) -> entities.Purchase:
        return entities.Purchase(
            purchase_date=purchase.kauf_date,
            product_offer=self.product_offer_repository.get_by_id(purchase.angebot),
            buyer=self.member_repository.get_member_by_id(purchase.member)
            if purchase.type_member
            else self.company_repository.get_by_id(purchase.company),
            price=purchase.kaufpreis,
            amount=purchase.amount,
            purpose=purchase.purpose,
        )

    def add(self, purchase: entities.Purchase) -> None:
        purchase_orm = self.object_to_orm(purchase)
        db.session.add(purchase_orm)

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
            for purchase in user_orm.purchases.order_by(desc("kauf_date")).all()
        )


@inject
@dataclass
class ProductOfferRepository(repositories.OfferRepository):
    company_repository: CompanyRepository

    def object_to_orm(self, product_offer: entities.ProductOffer) -> Offer:
        return Offer.query.get(product_offer.id)

    def object_from_orm(self, offer_orm: Offer) -> entities.ProductOffer:
        plan = offer_orm.plan
        price_per_unit = Decimal(
            (plan.costs_p + plan.costs_r + plan.costs_a) / plan.prd_amount
        )
        return entities.ProductOffer(
            id=offer_orm.id,
            name=offer_orm.name,
            amount_available=offer_orm.amount_available,
            deactivate_offer_in_db=lambda: setattr(offer_orm, "active", False),
            decrease_amount_available=lambda amount: setattr(
                offer_orm,
                "amount_available",
                getattr(offer_orm, "amount_available") - amount,
            ),
            price_per_unit=price_per_unit,
            provider=self.company_repository.object_from_orm(plan.company),
            active=offer_orm.active,
            description=offer_orm.description,
        )

    def get_by_id(self, id: int) -> entities.ProductOffer:
        offer_orm = Offer.query.filter_by(id=id).first()
        if offer_orm is None:
            raise ProductOfferNotFound()
        else:
            return self.object_from_orm(offer_orm)

    def all_active_offers(self) -> Iterator[entities.ProductOffer]:
        return (
            self.object_from_orm(offer)
            for offer in Offer.query.filter_by(active=True).all()
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


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository

    def _approve(self, plan, decision, reason, approval_date):
        plan.approved = decision
        plan.approval_reason = reason
        plan.approval_date = approval_date

    def object_from_orm(self, plan: Plan) -> entities.Plan:
        return entities.Plan(
            id=plan.id,
            plan_creation_date=plan.plan_creation_date,
            planner=self.company_repository.get_by_id(plan.planner),
            costs_p=plan.costs_p,
            costs_r=plan.costs_r,
            costs_a=plan.costs_a,
            prd_name=plan.prd_name,
            prd_unit=plan.prd_unit,
            prd_amount=plan.prd_amount,
            description=plan.description,
            timeframe=plan.timeframe,
            approved=plan.approved,
            approval_date=plan.approval_date,
            approval_reason=plan.approval_reason,
            approve=lambda decision, reason, approval_date: self._approve(
                plan, decision, reason, approval_date
            ),
            expired=plan.expired,
            renewed=plan.renewed,
            set_as_expired=lambda: setattr(plan, "expired", True),
            set_as_renewed=lambda: setattr(plan, "renewed", True),
            expiration_relative=None,
            expiration_date=None,
        )

    def object_to_orm(self, plan: entities.Plan) -> Plan:
        return Plan.query.get(plan.id)

    def get_by_id(self, id: int) -> Optional[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=id).first()
        return self.object_from_orm(plan_orm) if plan_orm else None

    def add(self, plan: entities.Plan) -> None:
        db.session.add(self.object_to_orm(plan))


class TransactionRepository(repositories.TransactionRepository):
    def object_to_orm(self, transaction: entities.Transaction) -> Transaction:
        return Transaction(
            date=datetime.now(),
            account_from=transaction.account_from.id,
            account_to=transaction.account_to.id,
            amount=transaction.amount,
            purpose=transaction.purpose,
        )

    def add(self, transaction: entities.Transaction) -> None:
        db.session.add(self.object_to_orm(transaction))
