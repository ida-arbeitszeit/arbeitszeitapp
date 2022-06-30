from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import PlanCooperationRepository, PlanRepository


@dataclass
class ShowMyPlansRequest:
    company_id: UUID


@dataclass
class PlanInfo:
    id: UUID
    prd_name: str
    price_per_unit: Decimal
    is_public_service: bool
    plan_creation_date: Optional[datetime]
    activation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    is_available: bool
    is_cooperating: bool
    cooperation: Optional[UUID]


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
            for plan in self.plan_repository.get_all_plans_for_company_descending(
                request.company_id
            )
        ]
        count_all_plans = len(all_plans_of_company)

        non_active_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                price_per_unit=calculate_price(
                    self.plan_cooperation_repository.get_cooperating_plans(plan.id)
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                is_available=plan.is_available,
                is_cooperating=bool(plan.cooperation),
                cooperation=plan.cooperation,
            )
            for plan in all_plans_of_company
            if (plan.is_approved and not plan.is_active and not plan.expired)
        ]
        active_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                price_per_unit=calculate_price(
                    self.plan_cooperation_repository.get_cooperating_plans(plan.id)
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                is_available=plan.is_available,
                is_cooperating=bool(plan.cooperation),
                cooperation=plan.cooperation,
            )
            for plan in all_plans_of_company
            if (plan.is_approved and plan.is_active and not plan.expired)
        ]
        expired_plans = [
            PlanInfo(
                id=plan.id,
                prd_name=plan.prd_name,
                price_per_unit=calculate_price(
                    self.plan_cooperation_repository.get_cooperating_plans(plan.id)
                ),
                is_public_service=plan.is_public_service,
                plan_creation_date=plan.plan_creation_date,
                activation_date=plan.activation_date,
                expiration_date=plan.expiration_date,
                is_available=plan.is_available,
                is_cooperating=bool(plan.cooperation),
                cooperation=plan.cooperation,
            )
            for plan in all_plans_of_company
            if plan.expired and (not plan.hidden_by_user)
        ]
        return ShowMyPlansResponse(
            count_all_plans=count_all_plans,
            non_active_plans=non_active_plans,
            active_plans=active_plans,
            expired_plans=expired_plans,
        )
