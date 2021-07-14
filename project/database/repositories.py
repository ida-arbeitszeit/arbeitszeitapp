from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TypeVar

from injector import inject

from arbeitszeit import entities, repositories
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
        if worker_orm not in company_orm.workers:
            company_orm.workers.append(worker_orm)

    def get_company_workers(self, company: entities.Company) -> List[entities.Member]:
        company_orm = self.company_repository.object_to_orm(company)
        return [
            self.member_repository.object_from_orm(member_orm)
            for member_orm in company_orm.workers
        ]


@inject
@dataclass
class MemberRepository:
    account_repository: AccountRepository

    def get_member_by_id(self, id: int) -> Optional[entities.Member]:
        orm_object = Member.query.filter_by(id=id).first()
        return self.object_from_orm(orm_object) if orm_object else None

    def object_from_orm(self, orm_object: Member) -> entities.Member:
        member_account = self.account_repository.object_from_orm(orm_object.account)
        return entities.Member(
            id=orm_object.id, name=orm_object.name, account=member_account
        )

    def object_to_orm(self, member: entities.Member) -> Member:
        return Member.query.get(member.id)


@inject
@dataclass
class CompanyRepository:
    account_repository: AccountRepository

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
        )

    def get_by_id(self, id: int) -> Optional[entities.Company]:
        company_orm = Company.query.filter_by(id=id).first()
        return self.object_from_orm(company_orm) if company_orm else None


@inject
@dataclass
class AccountRepository(repositories.AccountRepository):
    def object_from_orm(self, account_orm: Account) -> entities.Account:
        if account_orm.account_owner_social_accounting:
            account_owner_id = account_orm.account_owner_social_accounting
        elif account_orm.account_owner_company:
            account_owner_id = account_orm.account_owner_company
        else:
            account_owner_id = account_orm.account_owner_member
        return entities.Account(
            id=account_orm.id,
            account_owner_id=account_owner_id,
            account_type=account_orm.account_type,
            balance=account_orm.balance,
            change_credit=lambda amount: setattr(
                account_orm, "balance", account_orm.balance + amount
            ),
        )

    def object_to_orm(self, account: entities.Account) -> Account:
        account_owner_social_accounting, account_owner_member, account_owner_company = (
            None,
            None,
            None,
        )
        if account.account_type == "accounting":
            account_owner_social_accounting = 1
        elif account.account_type == "member":
            account_owner_member = account.account_owner_id
        else:  # if Company (p, r, a or prd)
            account_owner_company = account.account_owner_id

        return Account(
            account_owner_social_accounting=account_owner_social_accounting,
            account_owner_company=account_owner_company,
            account_owner_member=account_owner_member,
            account_type=account.account_type,
            balance=account.balance,
        )

    def add(self, account: entities.Account) -> None:
        account_orm = self.object_to_orm(account)
        db.session.add(account_orm)


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

    def add(self, purchase: entities.Purchase) -> None:
        purchase_orm = self.object_to_orm(purchase)
        db.session.add(purchase_orm)


@inject
@dataclass
class ProductOfferRepository:
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
        )

    def get_by_id(self, id: int) -> Optional[entities.ProductOffer]:
        offer_orm = Offer.query.filter_by(id=id).first()
        return self.object_from_orm(offer_orm) if offer_orm else None


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
