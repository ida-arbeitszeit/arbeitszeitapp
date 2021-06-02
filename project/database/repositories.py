from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, TypeVar, Union

from injector import inject

from arbeitszeit import entities, repositories
from project.extensions import db
from project.models import (
    Angebote,
    Company,
    Kaeufe,
    Member,
    Offer,
    Plan,
    SocialAccounting,
    TransactionsAccountingToCompany,
    TransactionsCompanyToCompany,
    TransactionsCompanyToMember,
    TransactionsMemberToCompany,
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


class MemberRepository:
    def get_member_by_id(self, id: int) -> Optional[entities.Member]:
        orm_object = Member.query.filter_by(id=id).first()
        return self.object_from_orm(orm_object) if orm_object else None

    def object_from_orm(self, orm_object: Member) -> entities.Member:
        return entities.Member(
            id=orm_object.id,
            change_credit=lambda amount: setattr(
                orm_object, "guthaben", orm_object.guthaben + amount
            ),
        )

    def object_to_orm(self, member: entities.Member) -> Member:
        return Member.query.get(member.id)


class CompanyRepository:
    def object_to_orm(self, company: entities.Company) -> Company:
        return Company.query.get(company.id)

    def object_from_orm(self, company_orm: Company) -> entities.Company:
        return entities.Company(
            id=company_orm.id,
            change_credit=lambda amount, account_type: setattr(
                company_orm, account_type, getattr(company_orm, account_type) + amount
            ),
        )

    def get_by_id(self, id: int) -> Optional[entities.Company]:
        company_orm = Company.query.filter_by(id=id).first()
        return self.object_from_orm(company_orm) if company_orm else None


class AccountingRepository:
    def object_from_orm(
        self, accounting_orm: SocialAccounting
    ) -> entities.SocialAccounting:
        return entities.SocialAccounting(
            id=accounting_orm.id,
        )

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
            purpose=purchase.purpose,
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
        price_per_unit = Decimal(plan.costs_p + plan.costs_r + plan.costs_a)
        return entities.ProductOffer(
            id=offer_orm.id,
            amount_available=offer_orm.amount_available,
            deactivate_offer_in_db=lambda: setattr(offer_orm, "active", False),
            decrease_amount_available=lambda amount: setattr(
                offer_orm,
                "amount_available",
                getattr(offer_orm, "amount_available") - amount,
            ),
            price_per_unit=price_per_unit,
            provider=self.company_repository.object_from_orm(plan.company),
        )


@inject
@dataclass
class PlanRepository(repositories.PlanRepository):
    company_repository: CompanyRepository

    def _approve(self, plan, decision, reason, approval_date):
        setattr(plan, "approved", decision)
        setattr(plan, "approval_reason", reason)
        setattr(plan, "approval_date", approval_date)

    def object_from_orm(self, plan: Plan) -> entities.Plan:
        return entities.Plan(
            id=plan.id,
            approve=lambda decision, reason, approval_date: self._approve(
                plan, decision, reason, approval_date
            ),
        )

    def object_to_orm(self, plan: entities.Plan) -> Plan:
        return Plan.query.get(plan.id)

    def get_by_id(self, id: int) -> Optional[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=id).first()
        return self.object_from_orm(plan_orm) if plan_orm else None

    def add(self, plan: entities.Plan) -> None:
        db.session.add(self.object_to_orm(plan))


@inject
@dataclass
class TransactionRepository(repositories.TransactionRepository):
    company_repository: CompanyRepository
    member_repository: MemberRepository
    accounting_repository: AccountingRepository

    def object_from_orm(
        self,
        transaction: Union[
            TransactionsMemberToCompany,
            TransactionsAccountingToCompany,
            TransactionsCompanyToCompany,
            TransactionsCompanyToMember,
        ],
    ) -> entities.Transaction:
        account_owner: Union[
            entities.Member, entities.Company, entities.SocialAccounting
        ]
        if isinstance(transaction, TransactionsMemberToCompany):
            account_owner = assert_is_not_none(
                self.member_repository.get_member_by_id(transaction.account_owner)
            )
        elif isinstance(transaction, TransactionsAccountingToCompany):
            account_owner = assert_is_not_none(
                self.accounting_repository.get_by_id(transaction.account_owner)
            )
        elif isinstance(
            transaction, (TransactionsCompanyToCompany, TransactionsCompanyToMember)
        ):
            account_owner = assert_is_not_none(
                self.company_repository.get_by_id(transaction.account_owner)
            )

        receiver: Union[entities.Member, entities.Company]
        if isinstance(transaction, TransactionsCompanyToMember):
            receiver = assert_is_not_none(
                self.member_repository.get_member_by_id(transaction.receiver_id)
            )
        else:
            receiver = assert_is_not_none(
                self.company_repository.get_by_id(transaction.receiver_id)
            )
        return entities.Transaction(
            account_owner=account_owner,
            receiver=receiver,
            amount=transaction.amount,
        )
