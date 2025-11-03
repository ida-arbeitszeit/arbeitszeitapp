from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.records import Plan
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListedPlan:
    id: UUID
    prd_name: str


@dataclass
class ListPlansResponse:
    plans: List[ListedPlan]


@dataclass
class ListActivePlansOfCompanyInteractor:
    database_gateway: DatabaseGateway
    datetime_service: DatetimeService

    def execute(self, company_id: UUID) -> ListPlansResponse:
        now = self.datetime_service.now()
        plans = [
            self._create_plan_response_model(plan)
            for plan in self.database_gateway.get_plans()
            .that_will_expire_after(now)
            .that_were_approved_before(now)
            .planned_by(company_id)
        ]
        if not plans:
            return ListPlansResponse(plans=[])
        return ListPlansResponse(plans=plans)

    def _create_plan_response_model(self, plan: Plan) -> ListedPlan:
        return ListedPlan(
            id=plan.id,
            prd_name=plan.prd_name,
        )
