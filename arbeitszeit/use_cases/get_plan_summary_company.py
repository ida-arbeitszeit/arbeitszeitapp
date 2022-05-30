from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Company, Plan
from arbeitszeit.plan_summary import BusinessPlanSummary
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.repositories import (
    CompanyRepository,
    PlanCooperationRepository,
    PlanRepository,
)


@dataclass
class PlanSummaryCompanySuccess:
    plan_summary: BusinessPlanSummary
    current_user_is_planner: bool


PlanSummaryCompanyResponse = Optional[PlanSummaryCompanySuccess]


@inject
@dataclass
class GetPlanSummaryCompany:
    plan_repository: PlanRepository
    company_repository: CompanyRepository
    plan_cooperation_repository: PlanCooperationRepository

    def __call__(self, plan_id: UUID, company_id: UUID) -> PlanSummaryCompanyResponse:
        plan = self.plan_repository.get_plan_by_id(plan_id)
        company = self.company_repository.get_by_id(company_id)
        if plan is None:
            return None
        assert company
        current_user_is_planner = self.check_if_current_user_is_planner(plan, company)
        price_per_unit = calculate_price(
            self.plan_cooperation_repository.get_cooperating_plans(plan.id)
        )
        return PlanSummaryCompanySuccess(
            plan_summary=BusinessPlanSummary(
                plan_id=plan.id,
                is_active=plan.is_active,
                planner_id=plan.planner.id,
                planner_name=plan.planner.name,
                product_name=plan.prd_name,
                description=plan.description,
                timeframe=plan.timeframe,
                active_days=plan.active_days or 0,
                production_unit=plan.prd_unit,
                amount=plan.prd_amount,
                means_cost=plan.production_costs.means_cost,
                resources_cost=plan.production_costs.resource_cost,
                labour_cost=plan.production_costs.labour_cost,
                is_public_service=plan.is_public_service,
                price_per_unit=price_per_unit,
                is_available=plan.is_available,
                is_cooperating=bool(plan.cooperation),
                cooperation=plan.cooperation or None,
            ),
            current_user_is_planner=current_user_is_planner,
        )

    def check_if_current_user_is_planner(self, plan: Plan, company: Company) -> bool:
        return plan.planner == company
