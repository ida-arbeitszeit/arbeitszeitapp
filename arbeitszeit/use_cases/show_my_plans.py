from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


@dataclass
class ShowMyPlansRequest:
    company_id: UUID


@dataclass
class PlanInfo:
    id: UUID
    prd_name: str
    description: str
    price_per_unit: Decimal
    is_public_service: bool
    plan_creation_date: Optional[datetime]
    activation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    expiration_relative: Optional[int]
    is_available: bool
    renewed: bool


@dataclass
class ShowMyPlansResponse:
    count_all_plans: int
    non_active_plans: List[PlanInfo]
    active_plans: List[PlanInfo]
    expired_plans: List[PlanInfo]


@inject
@dataclass
class ShowMyPlansUseCase:
    plan_repository: PlanRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, request: ShowMyPlansRequest) -> ShowMyPlansResponse:
        all_plans_of_company = [
            plan
            for plan in self.plan_repository.get_all_plans_for_company(
                request.company_id
            )
        ]
        count_all_plans = len(all_plans_of_company)

        non_active_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                description=plan.description,
                price_per_unit=self.plan_cooperation_repository.get_price_per_unit(
                    plan.id
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                expiration_relative=plan.expiration_relative,
                is_available=plan.is_available,
                renewed=plan.renewed,
            )
            for plan in all_plans_of_company
            if (plan.approved and not plan.is_active and not plan.expired)
        ]
        active_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                description=plan.description,
                price_per_unit=self.plan_cooperation_repository.get_price_per_unit(
                    plan.id
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                expiration_relative=plan.expiration_relative,
                is_available=plan.is_available,
                renewed=plan.renewed,
            )
            for plan in all_plans_of_company
            if (plan.approved and plan.is_active and not plan.expired)
        ]
        expired_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                description=plan.description,
                price_per_unit=self.plan_cooperation_repository.get_price_per_unit(
                    plan.id
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                expiration_relative=plan.expiration_relative,
                is_available=plan.is_available,
                renewed=plan.renewed,
            )
            for plan in all_plans_of_company
            if plan.expired
        ]
        return ShowMyPlansResponse(
            count_all_plans=count_all_plans,
            non_active_plans=non_active_plans,
            active_plans=active_plans,
            expired_plans=expired_plans,
        )
