from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import PlanRepository


@dataclass
class ShowMyPlansRequest:
    company_id: UUID


@dataclass
class QueriedPlan:
    id: UUID
    prd_name: str
    description: str
    means_cost: Decimal
    resource_cost: Decimal
    labour_cost: Decimal
    prd_amount: int
    price_per_unit: Decimal
    is_public_service: bool
    plan_creation_date: datetime
    activation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    expiration_relative: Optional[int]
    renewed: bool


@dataclass
class ShowMyPlansResponse:
    all_plans: List[QueriedPlan]
    non_active_plans: List[QueriedPlan]
    active_plans: List[QueriedPlan]
    expired_plans: List[QueriedPlan]


@inject
@dataclass
class ShowMyPlansUseCase:
    plan_repository: PlanRepository

    def __call__(self, request: ShowMyPlansRequest) -> ShowMyPlansResponse:
        all_plans = [
            self.__construct_queried_plan(plan)
            for plan in self.plan_repository.get_all_plans_for_company(
                request.company_id
            )
        ]
        non_active_plans = [
            self.__construct_queried_plan(plan)
            for plan in self.plan_repository.get_non_active_plans_for_company(
                request.company_id
            )
        ]
        active_plans = [
            self.__construct_queried_plan(plan)
            for plan in self.plan_repository.get_active_plans_for_company(
                request.company_id
            )
        ]
        expired_plans = [
            self.__construct_queried_plan(plan)
            for plan in self.plan_repository.get_expired_plans_for_company(
                request.company_id
            )
        ]
        return ShowMyPlansResponse(
            all_plans=all_plans,
            non_active_plans=non_active_plans,
            active_plans=active_plans,
            expired_plans=expired_plans,
        )

    @staticmethod
    def __construct_queried_plan(plan: Plan) -> QueriedPlan:
        return QueriedPlan(
            id=plan.id,
            prd_name=plan.prd_name,
            description=plan.description,
            means_cost=plan.production_costs.means_cost,
            resource_cost=plan.production_costs.resource_cost,
            labour_cost=plan.production_costs.labour_cost,
            prd_amount=plan.prd_amount,
            price_per_unit=plan.price_per_unit,
            is_public_service=plan.is_public_service,
            plan_creation_date=plan.plan_creation_date,
            activation_date=plan.activation_date,
            expiration_date=plan.expiration_date,
            expiration_relative=plan.expiration_relative,
            renewed=plan.renewed,
        )
