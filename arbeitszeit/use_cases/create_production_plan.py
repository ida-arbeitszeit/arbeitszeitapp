from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.entities import ProductionCosts
from arbeitszeit.repositories import CompanyRepository, PlanDraftRepository


@dataclass
class PlanProposal:
    costs: ProductionCosts
    product_name: str
    production_unit: str
    production_amount: int
    description: str
    timeframe_in_days: int
    is_public_service: bool


@dataclass
class CreatePlanResponse:
    plan_id: UUID


@inject
@dataclass
class CreatePlan:
    plan_draft_repository: PlanDraftRepository
    datetime_service: DatetimeService
    company_repository: CompanyRepository

    def __call__(
        self, planner: UUID, plan_proposal: PlanProposal
    ) -> CreatePlanResponse:
        plan = self.plan_draft_repository.create_plan_draft(
            planner=planner,
            costs=plan_proposal.costs,
            product_name=plan_proposal.product_name,
            production_unit=plan_proposal.production_unit,
            amount=plan_proposal.production_amount,
            description=plan_proposal.description,
            timeframe_in_days=plan_proposal.timeframe_in_days,
            is_public_service=plan_proposal.is_public_service,
            creation_timestamp=self.datetime_service.now(),
        )
        return CreatePlanResponse(plan_id=plan.id)
