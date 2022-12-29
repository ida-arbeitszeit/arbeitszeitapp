from __future__ import annotations

from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Plan
from arbeitszeit.repositories import (
    CompanyRepository,
    CooperationRepository,
    PlanRepository,
)


@inject
@dataclass
class ListMyCooperatingPlansUseCase:
    @dataclass
    class Request:
        company: UUID

    @dataclass
    class CooperatingPlan:
        plan_id: UUID
        plan_name: str
        coop_id: UUID
        coop_name: str

    @dataclass
    class Response:
        cooperating_plans: List[ListMyCooperatingPlansUseCase.CooperatingPlan]

    class Failure(Exception):
        pass

    company_repository: CompanyRepository
    cooperation_repository: CooperationRepository
    plan_repository: PlanRepository

    def list_cooperations(self, request: Request) -> Response:
        if not self.company_repository.get_companies().with_id(request.company):
            raise self.Failure()
        plans = (
            self.plan_repository.get_active_plans()
            .planned_by(request.company)
            .that_are_cooperating()
        )
        return self.Response(
            cooperating_plans=[self._create_plan_object(plan) for plan in plans]
        )

    def _create_plan_object(self, plan: Plan) -> CooperatingPlan:
        assert plan.cooperation
        coop_name = self.cooperation_repository.get_cooperation_name(plan.cooperation)
        assert coop_name
        return self.CooperatingPlan(
            plan_id=plan.id,
            plan_name=plan.prd_name,
            coop_id=plan.cooperation,
            coop_name=coop_name,
        )
