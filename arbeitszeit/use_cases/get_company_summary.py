from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from arbeitszeit.repositories import CompanyRepository, PlanRepository


@dataclass
class PlanDetails:
    id: UUID
    name: str


@dataclass
class GetCompanySummarySuccess:
    id: UUID
    name: str
    email: str
    registered_on: datetime
    active_plans: List[PlanDetails]


GetCompanySummaryResponse = Optional[GetCompanySummarySuccess]


@dataclass
class GetCompanySummary:
    company_respository: CompanyRepository
    plan_repository: PlanRepository

    def __call__(self, company_id: UUID) -> GetCompanySummaryResponse:
        company = self.company_respository.get_by_id(company_id)
        if company is None:
            return None
        plans = self.plan_repository.get_all_active_plans_for_company(company.id)
        return GetCompanySummarySuccess(
            company.id,
            company.name,
            company.email,
            company.registered_on,
            [PlanDetails(plan.id, plan.prd_name) for plan in plans],
        )
