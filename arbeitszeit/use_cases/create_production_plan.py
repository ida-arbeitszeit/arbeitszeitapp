from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import Company, Plan, ProductionCosts
from arbeitszeit.repositories import CompanyRepository, PlanRepository


@dataclass
class PlanProposal:
    costs: ProductionCosts
    product_name: str
    production_unit: str
    production_amount: int
    description: str
    timeframe_in_days: int
    is_public_service: bool


@inject
@dataclass
class CreatePlan:
    plan_repository: PlanRepository
    datetime_service: DatetimeService
    company_repository: CompanyRepository

    def __call__(self, planner: UUID, plan_proposal: PlanProposal) -> Plan:
        return self.plan_repository.create_plan(
            planner=self.company_repository.get_by_id(planner),
            costs=plan_proposal.costs,
            product_name=plan_proposal.product_name,
            production_unit=plan_proposal.production_unit,
            amount=plan_proposal.production_amount,
            description=plan_proposal.description,
            timeframe_in_days=plan_proposal.timeframe_in_days,
            is_public_service=plan_proposal.is_public_service,
            creation_timestamp=self.datetime_service.now(),
        )
