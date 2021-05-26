from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from injector import inject

from arbeitszeit import entities, repositories
from project.extensions import db
from project.models import Angebote, Company, Kaeufe, Member, Plan


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
            change_credit=lambda amount: setattr(
                company_orm, "guthaben", company_orm.guthaben + amount
            ),
        )

    def get_by_id(self, id: int) -> Optional[entities.Company]:
        company_orm = Company.query.filter_by(id=id).first()
        return self.object_from_orm(company_orm) if company_orm else None


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
        )

    def add(self, purchase: entities.Purchase) -> None:
        purchase_orm = self.object_to_orm(purchase)
        db.session.add(purchase_orm)


class ProductOfferRepository:
    def object_to_orm(self, product_offer: entities.ProductOffer) -> Angebote:
        return Angebote.query.get(product_offer.id)

    def object_from_orm(self, offer_orm: Angebote) -> entities.ProductOffer:
        return entities.ProductOffer(
            id=offer_orm.id,
            deactivate_offer_in_db=lambda: setattr(offer_orm, "aktiv", False),
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
        planner = self.company_repository.get_by_id(plan.planner)
        return entities.Plan(
            id=plan.id,
            plan_creation_date=plan.plan_creation_date,
            planner=planner,
            costs_p=plan.costs_p,
            costs_r=plan.costs_r,
            costs_a=plan.costs_a,
            prd_name=plan.prd_name,
            prd_unit=plan.prd_unit,
            prd_amount=plan.prd_amount,
            description=plan.description,
            timeframe=plan.timeframe,
            social_accounting=plan.social_accounting,
            approved=plan.approved,
            approval_date=plan.approval_date,
            approval_reason=plan.approval_reason,
            approve=lambda decision, reason, approval_date: self._approve(
                plan, decision, reason, approval_date
            ),
        )

    def object_to_orm(self, plan: entities.Plan) -> Plan:
        return Plan.query.get(plan.id)

    def get_by_id(self, id: int) -> Optional[entities.Plan]:
        plan_orm = Plan.query.filter_by(id=id).first()
        return self.object_from_orm(plan_orm) if plan_orm else None

    def add(self, plan_orm: Plan) -> None:
        db.session.add(plan_orm)
